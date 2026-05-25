# ai_service.py
import requests
import json
from config import Config

def get_ai_analysis(behavior_stats, anomalies, duration):
    """
    调用 DeepSeek API 生成养殖建议
    """
    API_KEY = Config.DEEPSEEK_API_KEY
    if not API_KEY or API_KEY == "sk-xxxxxxxxxxxxxxxxxxxxx":
        return "API 密钥未配置，无法生成 AI 建议。"
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构造详细的提示词
    prompt = f"""
你是一位专业的养猪技术专家。请根据以下猪只行为数据，生成一份简要的养殖分析报告。

视频总时长: {duration} 秒

## 行为统计（每头猪的行为次数）
{json.dumps(behavior_stats, ensure_ascii=False, indent=2)}

## 检测到的异常事件列表
{json.dumps(anomalies, ensure_ascii=False, indent=2)}

要求：
1. 总结视频中的关键问题。
2. 请根据视频时长、联系养殖科学，针对异常行为给出一针见血的建议。
3. 语言通俗易懂，不超过200字。
"""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个严谨的养猪专家，提供专业建议。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"DeepSeek API 调用失败: {e}")
        return "AI 分析服务暂时不可用。"