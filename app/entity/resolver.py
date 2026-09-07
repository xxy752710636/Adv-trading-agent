from app.entity.repository import EntityRepository
from app.entity.market_search import MarketEntitySearch
from app.entity.schema import (
    ResolvedEntity,
    EntityResolveResult,
    ResolveStatus,
)


class EntityResolver:
    """
    Entity Resolver

    解析策略：

        1. 本地 SQLite 代码精确匹配
        2. 本地 SQLite 名称精确匹配
        3. 本地 SQLite 模糊匹配
        4. 本地没有 → 外部真实市场源搜索
        5. 外部搜索成功 → 自动写入 SQLite
        6. 返回标准化实体

    核心原则：

        LLM 只负责理解用户说的是哪个实体。
        股票代码、市场等事实必须由真实数据源确认。
    """

    def __init__(self):

        self.repository = EntityRepository()
        self.market_search = MarketEntitySearch()

    # ==================================================
    # 股票解析
    # ==================================================

    def resolve_stock(
        self,
        name: str,
    ) -> EntityResolveResult:

        name = name.strip()

        if not name:

            return EntityResolveResult(
                status=ResolveStatus.NOT_FOUND,
                message="股票名称为空",
            )

        # ==================================================
        # 1. 本地数据库：代码精确匹配
        # ==================================================

        result = self.repository.get_stock_by_code(name)

        if result:

            return EntityResolveResult(
                status=ResolveStatus.RESOLVED,
                entity=result,
                message="通过本地股票代码匹配成功",
            )

        # ==================================================
        # 2. 本地数据库：名称精确匹配
        # ==================================================

        result = self.repository.get_stock_by_name(name)

        if result:

            return EntityResolveResult(
                status=ResolveStatus.RESOLVED,
                entity=result,
                message="通过本地股票名称匹配成功",
            )

        # ==================================================
        # 3. 本地数据库：模糊搜索
        # ==================================================

        candidates = self.repository.search_stock(name)

        if len(candidates) == 1:

            return EntityResolveResult(
                status=ResolveStatus.RESOLVED,
                entity=candidates[0],
                message="通过本地股票模糊搜索匹配成功",
            )

        if len(candidates) > 1:

            return EntityResolveResult(
                status=ResolveStatus.AMBIGUOUS,
                candidates=candidates,
                message=(
                    f"本地数据库找到多个股票候选，"
                    f"无法自动确定: {name}"
                ),
            )

        # ==================================================
        # 4. 本地没有 → 外部真实市场搜索
        # ==================================================

        try:

            external_result = self.market_search.search_stock(name)

        except Exception as e:

            return EntityResolveResult(
                status=ResolveStatus.ERROR,
                message=(
                    f"外部市场实体搜索失败: {e}"
                ),
            )

        # ==================================================
        # 5. 外部搜索没有找到
        # ==================================================

        if external_result is None:

            return EntityResolveResult(
                status=ResolveStatus.NOT_FOUND,
                message=(
                    f"本地数据库和外部市场数据源均未找到股票: {name}"
                ),
            )

        # ==================================================
        # 6. 外部搜索成功 → 自动写入 SQLite
        # ==================================================

        try:

            self.repository.save_stock(
                external_result
            )

        except Exception as e:

            return EntityResolveResult(
                status=ResolveStatus.ERROR,
                entity=external_result,
                message=(
                    f"股票已由外部市场源确认，"
                    f"但写入本地数据库失败: {e}"
                ),
            )

        # ==================================================
        # 7. 返回标准实体
        # ==================================================

        return EntityResolveResult(
            status=ResolveStatus.RESOLVED,
            entity=external_result,
            message=(
                "本地数据库未命中，"
                "已通过真实市场数据源确认并自动缓存"
            ),
        )

    # ==================================================
    # 通用实体解析
    # ==================================================

    def resolve(
        self,
        name: str,
        entity_type: str,
    ) -> EntityResolveResult:

        if entity_type == "stock":

            return self.resolve_stock(name)

        return EntityResolveResult(
            status=ResolveStatus.ERROR,
            message=(
                f"暂不支持的实体类型: {entity_type}"
            ),
        )