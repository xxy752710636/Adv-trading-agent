from app.data.akshare_tx import (
    AkShareTencentDataAdapter,
)

from app.analysis.technical import (
    TechnicalAnalyzer,
)


adapter = AkShareTencentDataAdapter()

data = adapter.get_stock_kline(
    code="300750",
    market="SZ",
    days=60,
    adjustment="qfq",
)

analyzer = TechnicalAnalyzer()

result = analyzer.analyze(
    bars=data.bars,
    code=data.code,
    name=data.name,
    market=data.market,
    source_step="stock_kline",
)

print("\n========== TECHNICAL ANALYSIS ==========")

print(
    result.model_dump_json(
        indent=2,
        ensure_ascii=False,
    )
)