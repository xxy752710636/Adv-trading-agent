def normalize_intent(data):
    entities = data.get("entities",[])
    normalized = []

    # targets = data.get("targets", [])

    for e in entities:

        # 情况1:
        # "半导体"

        if isinstance(e, str):

            normalized.append(
                {
                    "name": e,
                    "type": "unknown"
                }
            )


        # 情况2:
        # {"value":"AI算力","type":"板块"}

        elif isinstance(e, dict):

            if "name" not in e:

                if "value" in e:
                    e["name"] = e.pop("value")

            # 中文类型映射
            type_map = {

                "板块": "sector",

                "行业": "industry",

                "概念": "concept",

                "股票": "stock",

                "公司": "company"

            }

            if e.get("type") in type_map:
                e["type"] = type_map[
                    e["type"]
                ]

            normalized.append(e)

    data["entities"] = normalized

    return data
