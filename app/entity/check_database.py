import sqlite3

from app.entity.repository import DB_PATH


def check_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 总数量
    cursor.execute(
        "SELECT COUNT(*) FROM stocks"
    )

    total = cursor.fetchone()[0]

    print("\n========== 市场实体数据库 ==========")
    print(f"股票总数: {total}")

    # 按市场统计
    cursor.execute(
        """
        SELECT market, COUNT(*)
        FROM stocks
        GROUP BY market
        ORDER BY market
        """
    )

    rows = cursor.fetchall()

    print("\n按市场统计:")

    for market, count in rows:
        print(f"{market}: {count}")

    # 随机/示例查询
    cursor.execute(
        """
        SELECT code, name, market
        FROM stocks
        WHERE name IN (
            '剑桥科技',
            '东山精密',
            '宁德时代',
            '贵州茅台',
            '比亚迪',
            '中际旭创'
        )
        ORDER BY code
        """
    )

    rows = cursor.fetchall()

    print("\n重点股票检查:")

    for code, name, market in rows:
        print(
            f"{name} | {code} | {market}"
        )

    conn.close()


if __name__ == "__main__":
    check_database()