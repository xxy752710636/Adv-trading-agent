from datetime import datetime, timezone, timedelta
from typing import Any, Dict

import requests
from requests import Response

from app.data.schema import (
    KlineBar,
    MarketDataMeta,
    StockKlineData,
)


class EastmoneyDataAdapter:
    """
    东方财富数据适配器。

    负责：
    1. 请求 Eastmoney
    2. 解析原始 JSON
    3. 转换成统一 StockKlineData
    """

    BASE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

        self.session = requests.Session()

        # 禁止 requests 使用系统环境代理
        self.session.trust_env = False

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Referer": "https://quote.eastmoney.com/",
            "Connection": "keep-alive",
        })

    @staticmethod
    def _build_secid(code: str, market: str) -> str:
        market = market.upper()

        if market == "SH":
            return f"1.{code}"

        if market == "SZ":
            return f"0.{code}"

        raise ValueError(f"不支持的市场: {market}")

    def _request(
            self,
            url: str,
            params: Dict[str, Any],
    ) -> Response:

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response

        except requests.exceptions.Timeout as exc:
            raise RuntimeError(
                f"Eastmoney 请求超时: {url}"
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                f"Eastmoney 网络连接失败: {url}\n"
                f"错误: {exc}"
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Eastmoney HTTP 请求失败: {url}\n"
                f"错误: {exc}"
            ) from exc

    # def get_stock_kline(
    #         self,
    #         code: str,
    #         market: str,
    #         days: int = 60,
    #         adjustment: str = "qfq"
    # ) -> StockKlineData:
    #
    #     secid = self._build_secid(code, market)
    #
    #     adjustment_map = {
    #         "none": "0",
    #         "qfq": "1",
    #         "hfq": "2",
    #     }
    #
    #     fqt = adjustment_map.get(adjustment, "1")
    #
    #     query_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    #     params = {
    #         "fields1": "f1,f2,f3,f4,f5,f6",
    #         "fields2": (
    #             "f51,f52,f53,f54,f55,f56,f57,"
    #             "f58,f59,f60,f61"
    #         ),
    #         "ut": "7eea3edcaed734bea9cbfc24409ed989",
    #         "rtntype": "6",
    #         "klt": "101",
    #         "fqt": fqt,
    #         "secid": secid,
    #
    #         # 不使用当天日期作为 end
    #         "beg": "0",
    #         "end": "20500101",
    #
    #         # 多取一些，保证 MA5 / 后续指标计算有足够数据
    #         "lmt": str(max(days, 60)),
    #     }
    #
    #     headers = {
    #         "User-Agent": (
    #             "Mozilla/5.0 "
    #             "(Windows NT 10.0; Win64; x64) "
    #             "AppleWebKit/537.36 "
    #             "(KHTML, like Gecko) "
    #             "Chrome/120.0.0.0 Safari/537.36"
    #         ),
    #         "Accept": "*/*",
    #         "Accept-Language": "zh-CN,zh;q=0.9",
    #         "Referer": "https://quote.eastmoney.com/",
    #         "Connection": "keep-alive",
    #     }
    #
    #     try:
    #
    #         session = requests.Session()
    #
    #         # 不使用系统 HTTP/HTTPS 代理
    #         session.trust_env = False
    #
    #         response = session.get(
    #             self.BASE_URL,
    #             params=params,
    #             headers=headers,
    #             timeout=self.timeout,
    #         )
    #
    #         response.raise_for_status()
    #
    #         result = response.json()
    #
    #     except requests.RequestException as e:
    #         raise RuntimeError(
    #             f"Eastmoney 网络连接失败: {self.BASE_URL}\n"
    #             f"错误: {e}"
    #         ) from e
    #
    #     except ValueError as e:
    #         raise RuntimeError(
    #             "Eastmoney 返回的数据不是有效 JSON"
    #         ) from e
    #
    #     if not result:
    #         raise RuntimeError(
    #             "Eastmoney 返回空数据"
    #         )
    #
    #     if result.get("rc") != 0:
    #         raise RuntimeError(
    #             f"Eastmoney API 返回错误: {result}"
    #         )
    #
    #     data = result.get("data")
    #
    #     if not data:
    #         raise RuntimeError(
    #             f"Eastmoney 没有返回股票数据: {code}"
    #         )
    #
    #     klines = data.get("klines", [])
    #
    #     if not klines:
    #         raise RuntimeError(
    #             f"Eastmoney 没有返回 K 线数据: {code}"
    #         )
    #
    #     bars = []
    #
    #     for item in klines[-days:]:
    #         parts = item.split(",")
    #
    #         if len(parts) < 11:
    #             continue
    #
    #         bars.append(
    #             KlineBar(
    #                 date=parts[0],
    #                 open=float(parts[1]),
    #                 close=float(parts[2]),
    #                 high=float(parts[3]),
    #                 low=float(parts[4]),
    #                 volume=float(parts[5]),
    #                 amount=float(parts[6]),
    #                 amplitude=float(parts[7]),
    #                 pct_change=float(parts[8]),
    #                 change=float(parts[9]),
    #                 turnover=float(parts[10]),
    #             )
    #         )
    #
    #     if not bars:
    #         raise RuntimeError(
    #             f"Eastmoney K线解析失败: {code}"
    #         )
    #
    #     data_timestamp = bars[-1].date
    #
    #     meta = MarketDataMeta(
    #         source="eastmoney",
    #         timestamp=query_timestamp,
    #         market_status="unknown",
    #         timezone="Asia/Shanghai",
    #         data_quality="real",
    #         adjustment=adjustment,
    #     )
    #
    #     return StockKlineData(
    #         code=code,
    #         name=data.get("name", ""),
    #         market=market,
    #         period="daily",
    #         bars=bars,
    #         meta=meta,
    #     )
    import requests
    from datetime import datetime

    class EastmoneyDataAdapter:

        BASE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

        def get_stock_kline(
                self,
                code: str,
                market: str,
                days: int = 60,
                adjustment: str = "qfq"
        ):
            secid = self._build_secid(code, market)

            fqt_map = {
                "none": 0,
                "qfq": 1,
                "hfq": 2,
            }

            params = {
                "secid": secid,
                "klt": 101,
                "fqt": fqt_map.get(adjustment, 1),
                "lmt": days,
                "end": "20500101",
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            }

            try:
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    timeout=10
                )

                response.raise_for_status()

                data = response.json()

                if not data.get("data"):
                    raise RuntimeError(
                        f"Eastmoney 返回空数据: {data}"
                    )

                return self._parse_kline(data, code, market, adjustment)

            except requests.RequestException as e:
                raise RuntimeError(
                    f"Eastmoney 网络连接失败: {self.BASE_URL}\n"
                    f"错误: {e}"
                )
