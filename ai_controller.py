import random
import time

class AIController:
    def __init__(self, character, opponent):
        self.character = character # 컴퓨터가 조종할 캐릭터
        self.opponent = opponent # 상대 캐릭터

        # 컴퓨터 행동 타이머
        self.action_timer = 0
        self.next_action_time = 0.5

        # 현재 행동 상태
        self.current_action = None
        self.action_duration = 0

        # 컴퓨터 성향
        self.aggressiveness = 0.7 # 공격 성향 (0~1)
        self.defensiveness = 0.3 # 방어 성향 (0~1)
        self.reaction_time = 0.3 # 반응 속도 (초)

        # 마지막 행동 시간 기록
        self.last_action_time = time.time()

    def update(self):
        pass