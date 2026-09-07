import requests


def test_tencent_realtime():

    url = "https://qt.gtimg.cn/q=sz300750"

    print("=" * 60)
    print("腾讯实时行情接口测试")
    print("=" * 60)
    print(f"URL: {url}")

    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
    )

    print("\nHTTP Status:", response.status_code)
    print("Encoding:", response.encoding)
    print("\nRaw Response:")
    print(response.text[:1000])


if __name__ == "__main__":
    test_tencent_realtime()