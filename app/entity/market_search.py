import akshare as ak
from typing import Optional

from app.entity.schema import ResolvedEntity


class MarketEntitySearch:
    """
    外部市场实体搜索。

    当前使用 AkShare A 股股票列表作为真实市场实体数据源。

    注意：
    这里只负责确认：
        股票名称
        股票代码
        市场

    不使用 LLM 猜测股票代码。
    """

    def search_stock(
        self,
        name: str,
    ) -> Optional[ResolvedEntity]:

        name = name.strip()

        if not name:
            return None

        try:
            df = ak.stock_info_a_code_name()

        except Exception as e:

            raise RuntimeError(
                f"外部市场实体搜索失败: {e}"
            )

        if df is None or df.empty:
            return None

        # 精确名称匹配
        matches = df[
            df["name"].astype(str).str.strip() == name
        ]

        if matches.empty:
            return None

        # 理论上股票名称应该唯一。
        # 如果存在多个候选，不强行猜。
        if len(matches) > 1:
            return None

        row = matches.iloc[0]

        code = str(row["code"]).strip()
        stock_name = str(row["name"]).strip()

        market = self._detect_market(code)

        if market is None:
            return None

        return ResolvedEntity(
            name=stock_name,
            type="stock",
            code=code,
            market=market,
            confidence=1.0,
        )

    @staticmethod
    def _detect_market(code: str):

        code = code.strip()

        # 上海
        if code.startswith((
            "600",
            "601",
            "603",
            "605",
            "688",
            "689",
        )):
            return "SH"

        # 深圳
        if code.startswith((
            "000",
            "001",
            "002",
            "003",
            "300",
            "301",
            "302",
        )):
            return "SZ"

        # 北京
        if code.startswith((
            "430",
            "440",
            "830",
            "831",
            "832",
            "833",
            "834",
            "835",
            "836",
            "837",
            "838",
            "839",
            "870",
            "871",
            "872",
            "873",
            "874",
            "875",
            "876",
            "920",
        )):
            return "BJ"

        return None