# mcp.py

# llm2json으로부터 파싱된 json을 받고 분기하는, DB와의 프로토콜을 정의하는 모듈입니다. (CRUD + conflict)

# 아직 DB를 만든게 아니라서, 그냥 함수 작동하는지 보려고 stub으로 만들었습니다.
# 아직 초기구현이라 많이 수정해야합니다!!!!

"""
MCP 서버 Stub (CRUD + 충돌 체크)
해야할일 1: SQLite 연동
해야할일 2: DB Server 연동(추후)
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
