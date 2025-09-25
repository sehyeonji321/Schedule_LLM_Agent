"""
scheduler_agent.py
------------------
LLM + MCP 서버 연동을 위한 일정 관리 에이전트 (업그레이드 버전).

특징:
1. 유저 입력 → LLM 분류 (멀티 액션 지원, needs_clarification 감지)
2. 부족한 정보가 있으면 needs_clarification 플래그로 감지 → 유저에게 질문
3. 일정 충돌 처리: 같은 시간대 기존 일정이 있으면 → 유저에게 선택 요청
4. MCP 서버 호출 부분은 Stub (실제 API 스펙 나오면 교체)

⚠️ 해야할 일!
- 현재 LLM은 OpenAI GPT API 기준.
-> Gemini, Claude 등으로 교체할 경우 classify_user_input() 함수만 수정하면 됨.
- MCP 서버 스펙에 맞게 명령어 조절 필요
"""

import os
import json
from openai import OpenAI

# ---------------------------
# LLM 클라이언트 초기화
# ---------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_user_input(user_input: str) -> dict:
    """
    유저 입력을 LLM에 보내서 액션 분류 + JSON 생성.
    여러 명령이 있으면 actions 배열에 담음.
    부족한 정보가 있으면 needs_clarification 표시.
    """

    prompt_text = f"""
    당신은 일정 관리 비서입니다.  
    사용자의 입력을 읽고, 반드시 JSON 형식으로 답하세요.  

    규칙:
    - 사용자의 입력에는 여러 명령이 있을 수 있습니다 → actions 배열에 나눠 담으세요.
    - 필수 정보(title, date, time)가 빠져 있거나 모호하면,
      해당 action 안에 "needs_clarification": true 와 "missing_fields": [...] 를 넣으세요.

    JSON 스펙:
    {{
      "actions": [
        {{
          "action": "create" | "read" | "none",
          "event": {{
            "title": string (optional),
            "date": string (YYYY-MM-DD, optional),
            "time": string (HH:MM, optional),
            "participants": [string] (optional)
          }},
          "needs_clarification": bool (optional),
          "missing_fields": [string] (optional)
        }}
      ]
    }}

    예시1)
    입력: "내일 저녁 7시에 민수랑 운동 일정 추가해줘"
    출력: {{
      "actions": [
        {{
          "action": "create",
          "event": {{
            "title": "운동",
            "date": "2025-09-26",
            "time": "19:00",
            "participants": ["민수"]
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
          "missing_fields": ["title"]
        }}
      ]
    }}

    예시3)
    입력: "내일 저녁 7시에 운동 추가하고, 모레 일정도 보여줘"
    출력: {{
      "actions": [
        {{
          "action": "create",
          "event": {{
            "title": "운동",
            "date": "2025-09-26",
            "time": "19:00"
          }}
        }},
        {{
          "action": "read",
          "event": {{"date": "2025-09-27"}}
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

    사용자의 입력: "{user_input}"
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
        print("❌ JSON 파싱 실패:", e)
        return {"actions": [{"action": "none"}]}


# ---------------------------
# MCP 서버 Stub (실제 API 스펙 나오면 교체 필요)
# ---------------------------

def call_mcp_create_event(event: dict):
    print(f"[MCP-Stub] 일정 생성 요청: {event}")
    return {"status": "success"}


def call_mcp_read_events(query: dict):
    print(f"[MCP-Stub] 일정 조회 요청: {query}")
    return {
        "events": [
            {"title": "운동", "date": "2025-09-26", "time": "19:00", "participants": ["민수"]},
            {"title": "회의", "date": "2025-09-26", "time": "21:00", "participants": ["팀"]}
        ]
    }


def call_mcp_check_conflict(event: dict):
    """
    MCP 서버의 '일정 충돌 확인' API 호출 Stub.
    같은 시간대에 이미 일정이 있는지 확인.
    """
    print(f"[MCP-Stub] 일정 충돌 확인 요청: {event}")

    # 데모: date/time이 2025-09-26 19:00 이면 충돌 있다고 가정
    if event.get("date") == "2025-09-26" and event.get("time") == "19:00":
        return {
            "conflict": True,
            "existing_event": {"title": "회의", "date": "2025-09-26", "time": "19:00"}
        }
    return {"conflict": False}


# ---------------------------
# 메인 로직
# ---------------------------

def handle_user_input(user_input: str) -> str:
    parsed = classify_user_input(user_input)
    actions = parsed.get("actions", [])
    responses = []

    for a in actions:
        action = a.get("action", "none")

        # 부족한 정보 체크
        if a.get("needs_clarification"):
            missing = ", ".join(a.get("missing_fields", []))
            responses.append(f"❓ 일정을 추가하려면 '{missing}' 정보가 더 필요합니다. 알려주시겠어요?")
            continue

        if action == "create":
            # 충돌 체크
            conflict_resp = call_mcp_check_conflict(a["event"])
            if conflict_resp.get("conflict"):
                ex = conflict_resp["existing_event"]
                responses.append(
                    f"⚠️ 이미 같은 시간에 '{ex['title']}' 일정이 있습니다.\n"
                    f"👉 새 일정을 그냥 추가하시겠습니까, 기존 일정을 삭제하고 추가하시겠습니까?"
                )
                continue

            # 일정 생성 진행
            resp = call_mcp_create_event(a["event"])
            if resp.get("status") == "success":
                e = a["event"]
                participants = f" (참석자: {', '.join(e['participants'])})" if e.get("participants") else ""
                responses.append(f"✅ 일정 추가: {e.get('title')} - {e.get('date')} {e.get('time')}{participants}")
            else:
                responses.append("❌ 일정 추가 실패")

        elif action == "read":
            resp = call_mcp_read_events(a["event"])
            events = resp.get("events", [])
            if not events:
                responses.append("📭 해당 날짜에는 일정이 없습니다.")
            else:
                event_texts = []
                for e in events:
                    participants = f" (참석자: {', '.join(e['participants'])})" if e.get("participants") else ""
                    event_texts.append(f"{e['date']} {e['time']} → {e['title']}{participants}")
                responses.append("📅 일정:\n" + "\n".join(event_texts))

        else:
            responses.append(f"🤖 : '{user_input}'")

    return "\n\n".join(responses)


# ---------------------------
# 실행 예시
# ---------------------------
if __name__ == "__main__":
    print("=== 예시1: 정상 일정 추가 ===")
    print(handle_user_input("내일 저녁 8시에 민수랑 저녁식사 일정 추가해줘"))
    print()

    print("=== 예시2: 부족한 정보 ===")
    print(handle_user_input("내일 5시에"))
    print()

    print("=== 예시3: 충돌 상황 ===")
    print(handle_user_input("내일 저녁 7시에 운동 일정 추가해줘"))
    print()

    print("=== 예시4: 조회 ===")
    print(handle_user_input("내일 일정 뭐 있어?"))
    print()

    print("=== 예시5: 일반 대화 ===")
    print(handle_user_input("나 요즘 너무 피곤해"))
