# llm2json.py

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # API 연동하기


# 유저 입력을 LLM에 보내 JSON 파싱
def classify_user_input(user_input: str) -> dict:

    prompt_text = f"""
    당신은 일정 관리 비서입니다.
    사용자의 입력을 읽고 반드시 JSON 형식으로 답하세요.

    규칙:
    - 여러 명령어가 있으면 actions 배열로 나눠서 넣으세요.
    - 필수 정보(title, date, time, location)가 빠졌거나 모호하면,
      해당 action에 "needs_clarification": true 와 "missing_fields": [...] 추가.

    JSON 스펙:
    {{
      "actions": [
        {{
          "action": "create" | "read" | "update" | "delete" | "none",
          "event": {{
            "title": string (optional),
            "date": string (YYYY-MM-DD, optional),
            "time": string (HH:MM, optional),
            "participants": [string] (optional),
            "location": string (optional)
          }},
          "needs_clarification": bool (optional),
          "missing_fields": [string] (optional)
        }}
      ]
    }}

    예시1)
    입력: "내일 저녁 7시에 민수랑 잠실 헬스장에서 운동 일정 추가해줘"
    출력: {{
      "actions": [
        {{
          "action": "create",
          "event": {{
            "title": "운동",
            "date": "2025-09-26",
            "time": "19:00",
            "participants": ["민수"],
            "location": "잠실 헬스장"
          }}
        }}
      ]
    }}

    예시2)
    입력: "내일 5시에 일정 잡아줘"
    출력: {{
      "actions": [
        {{
          "action": "create",
          "event": {{"date": "2025-09-26", "time": "17:00"}},
          "needs_clarification": true,
          "missing_fields": ["title","location"]
        }}
      ]
    }}

    예시3)
    입력: "내일 저녁 7시에 운동 추가하고, 모레 강남역에서 일정도 보여줘"
    출력: {{
      "actions": [
        {{
          "action": "create",
          "event": {{
            "title": "운동",
            "date": "2025-09-26",
            "time": "19:00"
          }},
          "needs_clarification": true,
          "missing_fields": ["location"]
        }},
        {{
          "action": "read",
          "event": {{"date": "2025-09-27","location":"강남역"}}
        }}
      ]
    }}

    예시4)
    입력: "나 요즘 너무 피곤해"
    출력: {{
      "actions": [
        {{"action": "none"}}
      ]
    }}

    ---
    입력: "{user_input}"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 JSON만 출력하는 일정 관리 비서입니다."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0
    )

    try:
        content = response.choices[0].message.content
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print("JSON 파싱 실패:", e)
        return {"actions": [{"action": "none"}]}
