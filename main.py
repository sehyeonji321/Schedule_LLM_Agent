# main.py

from agent import handle_user_input

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

    print("=== 예시5: 삭제 ===")
    print(handle_user_input("내일 운동 일정 삭제해줘"))
    print()

    print("=== 예시6: 일반 대화 ===")
    print(handle_user_input("나 요즘 너무 피곤해"))
