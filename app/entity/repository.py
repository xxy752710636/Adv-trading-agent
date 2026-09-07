import sqlite3
import os
from datetime import datetime
from typing import Optional, List

from app.entity.schema import ResolvedEntity

DB_PATH = "data/market.db"


class EntityRepository:

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

        # 自动创建 data 目录
        db_dir = os.path.dirname(os.path.abspath(self.db_path))

        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._connect()

        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stocks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                market TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'stock',
                aliases TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.commit()
        conn.close()

    # --------------------------------------------------
    # 根据股票代码查询
    # --------------------------------------------------

    def get_stock_by_code(
        self,
        code: str,
    ) -> Optional[ResolvedEntity]:

        code = code.strip()

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT code, name, market, type, aliases
            FROM stocks
            WHERE code = ?
            """,
            (code,),
        )

        row = cursor.fetchone()

        conn.close()

        if not row:
            return None

        return self._row_to_entity(row)

    # --------------------------------------------------
    # 根据股票名称查询
    # --------------------------------------------------

    def get_stock_by_name(
        self,
        name: str,
    ) -> Optional[ResolvedEntity]:

        name = name.strip()

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT code, name, market, type, aliases
            FROM stocks
            WHERE name = ?
            """,
            (name,),
        )

        row = cursor.fetchone()

        conn.close()

        if not row:
            return None

        return self._row_to_entity(row)

    # --------------------------------------------------
    # 模糊搜索
    # --------------------------------------------------

    def search_stock(
        self,
        keyword: str,
    ) -> List[ResolvedEntity]:

        keyword = keyword.strip()

        if not keyword:
            return []

        conn = self._connect()
        cursor = conn.cursor()

        pattern = f"%{keyword}%"

        cursor.execute(
            """
            SELECT code, name, market, type, aliases
            FROM stocks
            WHERE name LIKE ?
               OR code LIKE ?
               OR aliases LIKE ?
            LIMIT 20
            """,
            (
                pattern,
                pattern,
                pattern,
            ),
        )

        rows = cursor.fetchall()

        conn.close()

        return [
            self._row_to_entity(row)
            for row in rows
        ]

    # --------------------------------------------------
    # 保存股票
    # --------------------------------------------------

    def save_stock(
        self,
        stock: ResolvedEntity,
    ):

        if stock.type != "stock":
            raise ValueError(
                "EntityRepository.save_stock 只允许保存股票实体"
            )

        if not stock.code:
            raise ValueError(
                "股票实体必须存在 code"
            )

        if not stock.market:
            raise ValueError(
                "股票实体必须存在 market"
            )

        conn = self._connect()
        cursor = conn.cursor()

        aliases = ""

        if isinstance(stock, ResolvedEntity):
            aliases = ""

        cursor.execute(
            """
            INSERT INTO stocks (
                code,
                name,
                market,
                type,
                aliases,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(code)
            DO UPDATE SET
                name = excluded.name,
                market = excluded.market,
                type = excluded.type,
                aliases = excluded.aliases,
                updated_at = excluded.updated_at
            """,
            (
                stock.code,
                stock.name,
                stock.market,
                stock.type,
                aliases,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    # --------------------------------------------------
    # 内部转换
    # --------------------------------------------------

    @staticmethod
    def _row_to_entity(row) -> ResolvedEntity:

        code, name, market, entity_type, aliases = row

        return ResolvedEntity(
            name=name,
            type=entity_type,
            code=code,
            market=market,
            confidence=1.0,
        )