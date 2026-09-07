def analyze_market(index_data):


    price = index_data["price"]

    change = index_data["change"]


    result = {

        "trend":"",
        "risk":"",
        "summary":""

    }


    if change > 0:

        result["trend"]="偏强"

        result["risk"]="中低"

        result["summary"] = (
            "指数当前上涨，市场情绪偏积极"
        )


    else:

        result["trend"]="偏弱"

        result["risk"]="中等"

        result["summary"] = (
            "指数走弱，需要关注风险"
        )


    return result