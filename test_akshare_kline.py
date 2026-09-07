import akshare as ak

print("开始获取剑桥科技历史K线...")

df = ak.stock_zh_a_hist_tx(
    symbol="sh603083",
    start_date="20260801",
    end_date="20260906",
    adjust="qfq",
)

print("\n数据类型：", type(df))
print("数据条数：", len(df))
print("\n最近10条：")
print(df.tail(10).to_string(index=False))