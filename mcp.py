# mcp.py

"""
MCP 서버 Stub (CRUD + 충돌 체크)
실제 DB 서버와 연결 시 이 부분을 교체하면 됨.
"""

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


def call_mcp_update_event(event: dict):
    print(f"[MCP-Stub] 일정 수정 요청: {event}")
    return {"status": "updated"}


def call_mcp_delete_event(event: dict):
    print(f"[MCP-Stub] 일정 삭제 요청: {event}")
    return {"status": "deleted"}


def call_mcp_check_conflict(event: dict):
    """
    같은 시간대에 이미 일정이 있는지 확인
    """
    print(f"[MCP-Stub] 일정 충돌 확인 요청: {event}")
    if event.get("date") == "2025-09-26" and event.get("time") == "19:00":
        return {
            "conflict": True,
            "existing_event": {"title": "회의", "date": "2025-09-26", "time": "19:00"}
        }
    return {"conflict": False}
