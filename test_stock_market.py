from app.data.stock_market import TencentRealtimeAdapter


def main():

    adapter = TencentRealtimeAdapter()

    print("=" * 60)
    print("TEST: TencentRealtimeAdapter")
    print("=" * 60)

    data = adapter.get_stock_market(
        code="300750",
        market="SZ",
    )

    print("\n========== RESULT ==========")

    print(
        data.model_dump_json(
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()