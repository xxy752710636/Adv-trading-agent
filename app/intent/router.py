from app.intent.classifier import classify_intent
from app.intent.llm_classifier import llm_classify



def intent_router(text):


    # 第一层规则


    result = classify_intent(text)


    # 高置信度直接返回


    if result.confidence >= 0.9:

        return result



    # 复杂情况进入LLM


    return llm_classify(text)
