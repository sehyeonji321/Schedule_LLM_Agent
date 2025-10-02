# agent.py

# 클라이언트와 직접 상호작용하며, llm2json에게 자연어를 파싱시키거나, 파싱된 json을 자연어로 변환하는 역할입니다.

from llm2json import classify_user_input
from mcp import (
    call_mcp_create_event,
    call_mcp_read_events,
    call_mcp_update_event,
    call_mcp_delete_event,
    call_mcp_check_conflict,
)


# create을 받아서 처리하려는데, 유저가 정보를 덜 줬을 경우 다시 쿼리
# create을 받아서 처리하려는데, 기존 일정이랑 충돌할 경우 확인 -> update에도 구현해야함
# delete할 때 바로삭제하는데, 한 번 물어보고 삭제하기

# 그 외 세부기능 생각날때마다 추가해주세용

def handle_user_input(user_input: str) -> str:
    parsed = classify_user_input(user_input)
    actions = parsed.get("actions", [])
    responses = []

    for a in actions:
        action = a.get("action", "none")

        # 부족한 정보 확인
        if a.get("needs_clarification"):
            missing = ", ".join(a.get("missing_fields", []))
            responses.append(f"❓ 일정을 추가하려면 '{missing}' 정보가 필요합니다. 알려주시겠어요?")
            continue

        if action == "create":
            # 충돌 확인
            conflict_resp = call_mcp_check_conflict(a["event"])
            if conflict_resp.get("conflict"):
                ex = conflict_resp["existing_event"]
                responses.append(
                    f"⚠️ 이미 같은 시간에 '{ex['title']}' 일정이 있습니다.\n"
                    f"👉 새 일정을 그냥 추가할까요, 기존 일정을 삭제하고 추가할까요?"
                )
                continue

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

        elif action == "update": # update에 충돌확인 아직 구현 미완
            resp = call_mcp_update_event(a["event"])
            responses.append("✏️ 일정 수정 완료" if resp.get("status") == "updated" else "❌ 수정 실패")

        elif action == "delete":
            resp = call_mcp_delete_event(a["event"])
            responses.append("🗑️ 일정 삭제 완료" if resp.get("status") == "deleted" else "❌ 삭제 실패")

        else:
            responses.append(f"🤖 Scheduler: '{user_input}'")

    return "\n\n".join(responses)
