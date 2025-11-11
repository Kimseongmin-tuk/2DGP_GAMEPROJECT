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
        self.action_timer += 0.01

        # 일정 시간마다 새로운 행동
        if self.action_timer >= self.next_action_time:
            self.decide_action()
            self.action_timer = 0
            self.next_action_time = random.uniform(0.3, 0.7)

        # 현재 행동 수행
        self.perform_action()

    def decide_action(self):
        distance = abs(self.character.x - self.opponent.x)

        # 상대와 거리에 따른 행동 결정
        if distance < 100: # 근거리
            self.decide_close_range_action()
        elif distance < 200: # 중거리
            self.decide_mid_range_action()
        else: # 원거리
            self.decide_long_range_action()

    def decide_close_range_action(self):
        rand = random.random()

        if self.opponent.is_attacking():
            # 상대가 공격 중이면 회피
            if random.random() < 0.7:
                self.current_action = 'back'
                self.action_duration = 0.3
            else:
                self.current_action = 'jump'
                self.action_duration = 0.2
        else:
            # 공격 또는 후퇴
            if rand < self.aggressiveness * 0.5:
                self.current_action = 'attack1'
                self.action_duration = 0.4
            elif rand < self.aggressiveness:
                self.current_action = 'attack2'
                self.action_duration = 0.4
            else:
                self.current_action = 'back'
                self.action_duration = 0.2

    def decide_mid_range_action(self):
        rand = random.random()

        forward_threshold = self.aggressiveness * 0.5  # 예: 0.3
        dash_attack_threshold = self.aggressiveness * 0.8  # 예: 0.48
        attack2_threshold = 0.9

        if rand < forward_threshold:
            self.current_action = 'forward'
            self.action_duration = 0.3
        elif rand < dash_attack_threshold:
            self.current_action = 'dash_attack'
            self.action_duration = 0.5
        elif rand < attack2_threshold:
            self.current_action = 'attack2'
            self.action_duration = 0.4
        else:
            self.current_action = 'idle'
            self.action_duration = 0.2

    def decide_long_range_action(self):
        rand = random.random()

        if rand < 0.7:
            self.current_action = 'forward'
            self.action_duration = 0.5
        elif rand < 0.85:
            self.current_action = 'dash'
            self.action_duration = 0.4
        else:
            self.current_action = 'jump_forward'
            self.action_duration = 0.3

    def perform_action(self):
        if self.current_action is None:
            return

        self.action_duration -= 0.01

        if self.action_duration <= 0:
            self.stop_all_movement()
            self.current_action = None
            return

        if self.current_action == 'forward':
            self.move_forward()
        elif self.current_action == 'back':
            self.move_backward()
        elif self.current_action == 'dash':
            self.dash_forward()
        elif self.current_action == 'dash_attack':
            self.dash_and_attack()
        elif self.current_action == 'attack1':
            self.perform_attack1()
        elif self.current_action == 'attack2':
            self.perform_attack2()
        elif self.current_action == 'jump':
            self.perform_jump()
        elif self.current_action == 'jump_forward':
            self.jump_and_move()
        elif self.current_action == 'idle':
            self.stop_all_movement()

    def stop_all_movement(self):
        self.character.moving_left = False
        self.character.moving_right = False
        self.character.running = False

    def move_forward(self):
        if self.character.facing_right:
            self.character.key_down('right')
        else:
            self.character.key_down('left')

    def move_backward(self):
        if self.character.facing_right:
            self.character.key_down('left')
        else:
            self.character.key_down('right')

    def dash_forward(self):
        if not self.character.running:
            direction = 'right' if self.character.facing_right else 'left'
            self.character.last_key_time[direction] = time.time() - 0.1
            self.character.key_down(direction)

        self.move_forward()

    def dash_and_attack(self):
        if self.action_duration > 0.2:
            self.dash_forward()
        else:
            self.perform_attack1()

    def perform_attack1(self):
        if not self.character.is_attacking() and not self.character.hurt:
            self.character.attack()

    def perform_attack2(self):
        if not self.character.is_attacking() and not self.character.hurt:
            self.character.attack2()

    def perform_jump(self):
        if not self.character.is_jumping() and not self.character.hurt:
            self.character.jump()

    def jump_and_move(self):
        if not self.character.jumping:
            self.character.jump()

        self.move_forward()

    def cleaning(self):
        self.stop_all_movement()