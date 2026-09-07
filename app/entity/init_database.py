from app.entity.repository import EntityRepository
from app.entity.schema import ResolvedEntity


def init_database():

    repository = EntityRepository()

    stocks = [
        ResolvedEntity(
            name="剑桥科技",
            type="stock",
            code="603083",
            market="SH",
            confidence=1.0,
        ),

        ResolvedEntity(
            name="东山精密",
            type="stock",
            code="002384",
            market="SZ",
            confidence=1.0,
        ),
    ]

    for stock in stocks:
        repository.save_stock(stock)

    print("市场实体数据库初始化完成")


if __name__ == "__main__":
    init_database()