import re
import requests

from datetime import datetime, timezone, timedelta
from typing import Optional

from pydantic import BaseModel


class StockMarketData(BaseModel):
    """
    腾讯实时股票行情数据

    数据来源：
        Tencent Finance qt.gtimg.cn

    注意：
        Tencent 实时接口返回的是文本格式，
        不是 JSON。

    主要字段：
        price
        previous_close
        open
        high
        low
        change
        pct_change
        volume
        amount

    时间：
        query_timestamp
            本地程序实际发起查询的时间

        data_timestamp
            腾讯行情数据自身的行情时间
    """

    code: str
    name: str = ""
    market: str = ""

    price: float
    previous_close: float = 0
    open: float = 0
    high: float = 0
    low: float = 0

    change: float = 0
    pct_change: float = 0

    volume: float = 0
    amount: float = 0

    query_timestamp: str
    data_timestamp: str = ""

    source: str = "tencent"
    data_quality: str = "real"

    # ==========================================================
    # 数据单位说明
    # ==========================================================
    data_freshness: str = "unknown"

    volume_unit: str = "share"
    amount_unit: str = "CNY"



class TencentRealtimeAdapter:
    """
    腾讯财经实时行情 Adapter

    接口：

        https://qt.gtimg.cn/q=

    示例：

        sz300750
        sh600519

    返回格式：

        v_sz300750="字段1~字段2~字段3~...";

    """

    API_URL = "https://qt.gtimg.cn/q="

    TIMEZONE = timezone(
        timedelta(hours=8)
    )

    # ==========================================================
    # 对外接口
    # ==========================================================

    def get_stock_market(
        self,
        code: str,
        market: str,
    ) -> StockMarketData:

        code = code.strip()
        market = market.upper().strip()

        # ------------------------------------------------------
        # 参数检查
        # ------------------------------------------------------

        if not code:

            raise ValueError(
                "缺少股票代码 code"
            )

        if market not in {
            "SH",
            "SZ",
            "BJ",
        }:

            raise ValueError(
                f"不支持的市场: {market}"
            )

        # ------------------------------------------------------
        # 构造腾讯股票代码
        # ------------------------------------------------------

        symbol = self._build_symbol(
            code,
            market,
        )

        # ------------------------------------------------------
        # 查询时间
        # ------------------------------------------------------

        query_time = datetime.now(
            self.TIMEZONE
        )

        # ------------------------------------------------------
        # 请求
        # ------------------------------------------------------

        url = (
            f"{self.API_URL}{symbol}"
        )

        print("\n[TencentRealtimeAdapter]")
        print(
            f"请求地址: {url}"
        )

        try:

            response = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/131.0 Safari/537.36"
                    ),
                },
            )

            response.raise_for_status()

        except requests.RequestException as e:

            raise RuntimeError(
                "腾讯实时行情请求失败: "
                f"{e}"
            )

        # ------------------------------------------------------
        # 腾讯接口通常返回 GBK / GB18030
        # ------------------------------------------------------

        raw_text = self._decode_response(
            response
        )

        print(
            "\n[TencentRealtimeAdapter] "
            "Raw Response:"
        )

        print(
            raw_text[:500]
        )

        # ------------------------------------------------------
        # 解析
        # ------------------------------------------------------

        fields = self._parse_response(
            raw_text=raw_text,
            symbol=symbol,
        )

        if not fields:

            raise RuntimeError(
                "腾讯实时行情返回为空: "
                f"{symbol}"
            )

        # ------------------------------------------------------
        # 基础字段
        # ------------------------------------------------------

        name = self._get_field(
            fields,
            1,
            "",
        )

        returned_code = self._get_field(
            fields,
            2,
            code,
        )

        # ------------------------------------------------------
        # 腾讯字段
        #
        # 0  未知
        # 1  股票名称
        # 2  股票代码
        # 3  当前价格
        # 4  昨收
        # 5  今开
        # 6  成交量
        #
        # 30 时间
        # 31 涨跌
        # 32 涨跌%
        # 33 最高
        # 34 最低
        #
        # 36 成交量
        # 37 成交额
        # 38 换手率
        # 43 振幅
        # ------------------------------------------------------

        price = self._safe_float(
            self._get_field(
                fields,
                3,
            )
        )

        previous_close = self._safe_float(
            self._get_field(
                fields,
                4,
            )
        )

        open_price = self._safe_float(
            self._get_field(
                fields,
                5,
            )
        )

        volume = self._safe_float(
            self._get_field(
                fields,
                6,
            )
        )

        change = self._safe_float(
            self._get_field(
                fields,
                31,
            )
        )

        pct_change = self._safe_float(
            self._get_field(
                fields,
                32,
            )
        )

        high = self._safe_float(
            self._get_field(
                fields,
                33,
            )
        )

        low = self._safe_float(
            self._get_field(
                fields,
                34,
            )
        )

        # ------------------------------------------------------
        # 时间
        # ------------------------------------------------------

        raw_data_timestamp = self._get_field(
            fields,
            30,
            "",
        )

        data_timestamp = self._normalize_data_timestamp(
            raw_data_timestamp
        )

        data_freshness = self._get_data_freshness(
            query_time=query_time,
            data_timestamp=data_timestamp,
        )

        # ------------------------------------------------------
        # 成交额
        #
        # 腾讯字段 37 通常以“万元”为单位。
        #
        # 转换成 CNY。
        # ------------------------------------------------------

        amount_wan = self._safe_float(
            self._get_field(
                fields,
                37,
            )
        )

        amount = (
            amount_wan * 10000
            if amount_wan
            else 0
        )

        # ------------------------------------------------------
        # 基础数据完整性检查
        # ------------------------------------------------------

        if price <= 0:

            raise RuntimeError(
                "腾讯实时行情返回了无效价格: "
                f"{price}"
            )

        # ------------------------------------------------------
        # 构造结果
        # ------------------------------------------------------

        return StockMarketData(

            code=(
                returned_code
                or code
            ),

            name=name,

            market=market,

            price=price,

            previous_close=(
                previous_close
            ),

            open=open_price,

            high=high,

            low=low,

            change=change,

            pct_change=pct_change,

            volume=volume,

            amount=amount,

            query_timestamp=(
                query_time.isoformat()
            ),

            data_timestamp=(
                data_timestamp
            ),

            source="tencent",

            data_quality="real",

            volume_unit="share",

            amount_unit="CNY",

            data_freshness=data_freshness,
        )

    # ==========================================================
    # 构造腾讯股票代码
    # ==========================================================

    @staticmethod
    def _build_symbol(
        code: str,
        market: str,
    ) -> str:

        if market == "SH":

            return f"sh{code}"

        if market == "SZ":

            return f"sz{code}"

        if market == "BJ":

            return f"bj{code}"

        raise ValueError(
            f"无法构造腾讯股票代码: "
            f"{market} {code}"
        )

    # ==========================================================
    # 解码响应
    # ==========================================================

    @staticmethod
    def _decode_response(
        response: requests.Response,
    ) -> str:

        # ------------------------------------------------------
        # 优先尝试 GB18030
        # ------------------------------------------------------

        content = response.content

        for encoding in (
            "gb18030",
            "gbk",
            "utf-8",
        ):

            try:

                return content.decode(
                    encoding
                )

            except UnicodeDecodeError:

                continue

        # ------------------------------------------------------
        # 最后兜底
        # ------------------------------------------------------

        return content.decode(
            "utf-8",
            errors="replace",
        )

    # ==========================================================
    # 解析腾讯响应
    # ==========================================================

    @staticmethod
    def _parse_response(
        raw_text: str,
        symbol: str,
    ):

        # ------------------------------------------------------
        # 典型：
        #
        # v_sz300750="...";
        # ------------------------------------------------------

        pattern = (
            rf'v_{re.escape(symbol)}="(.*?)";'
        )

        match = re.search(
            pattern,
            raw_text,
        )

        if not match:

            # 某些情况下返回格式可能略有不同
            # 再尝试直接提取引号内容

            fallback = re.search(
                r'="(.*?)";',
                raw_text,
            )

            if not fallback:

                raise RuntimeError(
                    "无法解析腾讯实时行情响应: "
                    f"{raw_text[:300]}"
                )

            value = fallback.group(1)

        else:

            value = match.group(1)

        fields = value.split("~")

        return fields

    # ==========================================================
    # 安全读取字段
    # ==========================================================

    @staticmethod
    def _get_field(
        fields,
        index: int,
        default: str = "",
    ) -> str:

        if index < 0:
            return default

        if index >= len(fields):
            return default

        value = fields[index]

        if value is None:
            return default

        return str(value).strip()

    # ==========================================================
    # 安全转换 float
    # ==========================================================

    @staticmethod
    def _safe_float(
        value: str,
        default: float = 0,
    ) -> float:

        if value is None:
            return default

        value = str(value).strip()

        if not value:
            return default

        try:

            return float(value)

        except (
            ValueError,
            TypeError,
        ):

            return default

    @classmethod
    def _normalize_data_timestamp(
            cls,
            value: str,
    ) -> str:

        value = str(value).strip()

        if not value:
            return ""

        if re.fullmatch(r"\d{14}", value):
            dt = datetime.strptime(
                value,
                "%Y%m%d%H%M%S",
            ).replace(
                tzinfo=cls.TIMEZONE
            )

            return dt.isoformat()

        return value

    @staticmethod
    def _get_data_freshness(
            query_time,
            data_timestamp: str,
    ) -> str:

        if not data_timestamp:
            return "unknown"

        try:
            data_time = datetime.fromisoformat(
                data_timestamp
            )
        except ValueError:
            return "unknown"

        query_date = query_time.date()
        data_date = data_time.date()

        if data_date == query_date:
            return "same_day"

        if data_date < query_date:
            return "previous_trading_day"

        return "unknown"