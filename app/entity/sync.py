import akshare as ak
from datetime import datetime

from app.entity.repository import EntityRepository
from app.entity.schema import ResolvedEntity


class StockDatabaseSync:
    """
    A股股票基础信息同步器。

    数据来源：
    AkShare 股票列表接口。

    作用：
    将全市场股票代码、名称、市场写入 SQLite。
    """

    def __init__(self):
        self.repository = EntityRepository()

    def sync(self):
        print("\n========== 开始同步 A 股股票池 ==========")

        try:
            df = ak.stock_info_a_code_name()
        except Exception as e:
            raise RuntimeError(
                f"A股股票列表获取失败: {e}"
            )

        if df is None or df.empty:
            raise RuntimeError(
                "A股股票列表为空"
            )

        print(f"获取到股票数量: {len(df)}")

        success = 0
        failed = 0
        failed_items = []

        for _, row in df.iterrows():

            try:
                code = str(row["code"]).strip()
                name = str(row["name"]).strip()

                if not code or not name:
                    failed += 1
                    continue

                market = self._detect_market(code)

                if market is None:
                    failed += 1

                    failed_items.append({
                        "code": code,
                        "name": name,
                        "reason": "无法识别市场",
                    })

                    continue

                entity = ResolvedEntity(
                    name=name,
                    type="stock",
                    code=code,
                    market=market,
                    confidence=1.0,
                )

                self.repository.save_stock(entity)

                success += 1

            except Exception as e:
                failed += 1
                print(
                    f"同步失败: {row} -> {e}"
                )

        print("\n========== A 股股票池同步完成 ==========")
        print(f"总数量: {len(df)}")
        print(f"成功: {success}")
        print(f"失败: {failed}")
        if failed_items:
            print("\n========== 前 50 个失败实体 ==========")

            for item in failed_items[:50]:
                print(
                    f"{item['code']} | "
                    f"{item['name']} | "
                    f"{item['reason']}"
                )
        print(f"完成时间: {datetime.now().isoformat()}")

    @staticmethod
    def _detect_market(code: str):
        """
        根据A股证券代码判断交易所。

        SH = 上海证券交易所
        SZ = 深圳证券交易所
        BJ = 北京证券交易所

        注意：
        这里只用于股票池同步阶段。
        最终市场实体仍以真实市场数据源为准。
        """

        code = code.strip()

        # =========================
        # 上海证券交易所
        # =========================

        if code.startswith((
                "600",
                "601",
                "603",
                "605",
                "688",
                "689",
        )):
            return "SH"

        # =========================
        # 深圳证券交易所
        # =========================

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

        # =========================
        # 北京证券交易所
        # =========================

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


if __name__ == "__main__":
    sync = StockDatabaseSync()
    sync.sync()