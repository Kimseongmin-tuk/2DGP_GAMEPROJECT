from pico2d import *


class Character:
    def __init__(self, character_name, x, y, speed=3):
        # 캐릭터 이름 저장
        self.character_name = character_name

        # 캐릭터 초기 위치 및 속도 설정
        self.x = x
        self.y = y
        self.speed = speed

        # 이미지 로드 (캐릭터 이름에 따라 다른 폴더에서 로드)
        self.idle_image = load_image(f'{character_name}/Idle.png')
        self.walk_image = load_image(f'{character_name}/Walk.png')
        self.attack_image = load_image(f'{character_name}/Attack_1.png')
        self.attack2_image = load_image(f'{character_name}/Attack_3.png')
        self.frame = 0

        # 캐릭터별 프레임 수 설정
        if character_name == 'Fighter':
            self.attack_frame_count = 4
            self.attack2_frame_count = 4
        elif character_name == 'Shinobi':
            self.attack_frame_count = 4  # Attack_1: 4프레임
            self.attack2_frame_count = 5  # Attack_3: 5프레임
        elif character_name == 'Samurai':
            self.attack_frame_count = 6  # Attack_1: 6프레임
            self.attack2_frame_count = 3  # Attack_3: 3프레임
        else:
            # 기본값
            self.attack_frame_count = 4
            self.attack2_frame_count = 4

        # 이미지 프레임 크기 계산
        self.idle_frame_width = self.idle_image.w // 6
        self.walk_frame_width = self.walk_image.w // 8
        self.attack_frame_width = self.attack_image.w // self.attack_frame_count
        self.attack2_frame_width = self.attack2_image.w // self.attack2_frame_count
        self.frame_height = self.walk_image.h

        # 행동 상태 초기화
        self.moving_left = False
        self.moving_right = False
        self.attacking = False
        self.attacking2 = False

        # 프레임 타이머 초기화
        self.frame_time = 0

    def update(self):
        # 좌우 이동(공격 중이 아닐 때만)
        if not self.attacking and not self.attacking2:
            if self.moving_left:
                self.x -= self.speed
            if self.moving_right:
                self.x += self.speed

        # 화면 경계 처리
        if self.x < 0:
            self.x = 0
        elif self.x > 1200:  # WINDOW_WIDTH
            self.x = 1200

        # 프레임 업데이트
        self.frame_time += 1

        if self.attacking:
            if self.frame_time >= 10:
                self.frame += 1
                self.frame_time = 0
                if self.frame >= self.attack_frame_count:
                    self.frame = 0
                    self.attacking = False
        elif self.attacking2:
            if self.frame_time >= 10:
                self.frame += 1
                self.frame_time = 0
                if self.frame >= self.attack2_frame_count:
                    self.frame = 0
                    self.attacking2 = False
        elif self.moving_left or self.moving_right:
            if self.frame_time >= 8:
                self.frame = (self.frame + 1) % 8
                self.frame_time = 0
        else:
            if self.frame_time >= 8:
                self.frame = (self.frame + 1) % 6
                self.frame_time = 0

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.frame = 0
            self.frame_time = 0

    def attack2(self):
        if not self.attacking2:
            self.attacking2 = True
            self.frame_time = 0
            self.frame = 0

    def draw(self):
        if self.attacking:
            self.attack_image.clip_draw(
                self.frame * self.attack_frame_width, 0,
                self.attack_frame_width, self.frame_height,
                self.x, self.y, 200, 200
            )
        elif self.attacking2:
            self.attack2_image.clip_draw(
                self.frame * self.attack2_frame_width, 0,
                self.attack2_frame_width, self.frame_height,
                self.x, self.y, 200, 200
            )
        elif self.moving_left or self.moving_right:
            self.walk_image.clip_draw(
                self.frame * self.walk_frame_width, 0,
                self.walk_frame_width, self.frame_height,
                self.x, self.y, 200, 200
            )
        else:
            self.idle_image.clip_draw(
                self.frame * self.idle_frame_width, 0,
                self.idle_frame_width, self.frame_height,
                self.x, self.y, 200, 200
            )