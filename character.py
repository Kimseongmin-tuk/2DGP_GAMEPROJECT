from pico2d import *
import time


class Character:
    def __init__(self, character_name, x, y, speed=3, facing_right=True):
        # 캐릭터 이름 저장
        self.character_name = character_name

        # 캐릭터 초기 위치 및 속도 설정
        self.x = x
        self.y = y
        self.ground_y = y  # 땅 위치 저장
        self.speed = speed
        self.run_speed = speed * 2  # 달릴 때 속도 (2배)
        self.facing_right = facing_right

        # 점프 관련 변수
        self.jump_speed = 0
        self.gravity = 0.8
        self.jump_power = 15

        # 피격 히트박스 설정
        self.attack_range = 80
        self.hitbox_width = 100
        self.hitbox_height = 100

        # 이미지 로드 (캐릭터 이름에 따라 다른 폴더에서 로드)
        self.idle_image = load_image(f'{character_name}/Idle.png')
        self.walk_image = load_image(f'{character_name}/Walk.png')
        self.run_image = load_image(f'{character_name}/Run.png')
        self.attack_image = load_image(f'{character_name}/Attack_1.png')
        self.attack2_image = load_image(f'{character_name}/Attack_3.png')
        self.jump_image = load_image(f'{character_name}/Jump.png')
        self.hurt_image = load_image(f'{character_name}/Hurt.png')
        self.frame = 0

        # 캐릭터별 프레임 수 설정
        if character_name == 'Fighter':
            self.attack_frame_count = 4
            self.attack2_frame_count = 4
            self.jump_frame_count = 10
            self.hurt_frame_count = 3
        elif character_name == 'Shinobi':
            self.attack_frame_count = 5
            self.attack2_frame_count = 4
            self.jump_frame_count = 12
            self.hurt_frame_count = 2
        elif character_name == 'Samurai':
            self.attack_frame_count = 6
            self.attack2_frame_count = 4
            self.jump_frame_count = 12
            self.hurt_frame_count = 2
        else:
            # 기본값
            self.attack_frame_count = 4
            self.attack2_frame_count = 4

        # 이미지 프레임 크기 계산
        self.idle_frame_width = self.idle_image.w // 6
        self.walk_frame_width = self.walk_image.w // 8
        self.run_frame_width = self.run_image.w // 8
        self.attack_frame_width = self.attack_image.w // self.attack_frame_count
        self.attack2_frame_width = self.attack2_image.w // self.attack2_frame_count
        self.jump_frame_width = self.jump_image.w // self.jump_frame_count
        self.hurt_frame_width = self.hurt_image.w // self.hurt_frame_count
        self.frame_height = self.walk_image.h

        # 행동 상태 초기화
        self.moving_left = False
        self.moving_right = False
        self.running = False
        self.attacking = False
        self.attacking2 = False
        self.jumping = False
        self.hurt = False

        # 더블탭 감지를 위한 변수
        self.last_key_time = {'left': 0, 'right': 0}
        self.double_tap_threshold = 0.3

        # 프레임 타이머 초기화
        self.frame_time = 0

    def key_down(self, direction):
        current_time = time.time()

        if not self.jumping and not self.hurt:
            if current_time - self.last_key_time[direction] < self.double_tap_threshold:
                self.running = True

        self.last_key_time[direction] = current_time

        if direction == 'left':
            self.moving_left = True
        elif direction == 'right':
            self.moving_right = True

    def key_up(self, direction):
        if direction == 'left':
            self.moving_left = False
            if not self.moving_right:
                self.running = False
        elif direction == 'right':
            self.moving_right = False
            if not self.moving_left:
                self.running = False

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_speed = self.jump_power
            self.frame = 0
            self.frame_time = 0

    def get_hit(self):
        if not self.hurt:
            self.hurt = True
            self.frame = 0
            self.frame_time = 0

            if self.facing_right:
                self.x -= 10
            else:
                self.x += 10

    def is_attacking(self):
        return self.attacking or self.attacking2

    def get_attacking_hitbox(self):
        if not self.is_attacking():
            return None

        if self.facing_right:
            hitbox_x = self.x + self.attack_range // 2
        else:
            hitbox_x = self.x - self.attack_range // 2

        return {'x': hitbox_x, 'y': self.y, 'width': self.attack_range, 'height': self.hitbox_height}

    def get_body_hitbox(self):
        return {'x': self.x, 'y': self.y, 'width': self.hitbox_width, 'height': self.hitbox_height}

    def check_hit(self, opponent_hitbox):
        if self.hurt:
            return False

        attack_box = opponent_hitbox.get_attacking_hitbox()

        if attack_box is None:
            return False

        body_box = self.get_body_hitbox()

        if abs(attack_box['x'] - body_box['x']) < (attack_box['width'] + body_box['width']) / 2 and abs(
                attack_box['y'] - body_box['y']) < (attack_box['height'] + body_box['height']) / 2:
            return True

        return False

    def is_moving_backward(self):
        if self.facing_right and self.moving_left:
            return True
        elif not self.facing_right and self.moving_right:
            return True
        return False

    def update(self, opponent_x=None):
        # 항상 상대와 마주보도록 설정
        if opponent_x is not None:
            if opponent_x > self.x:
                self.facing_right = True
            else:
                self.facing_right = False

        # 점프 처리
        if self.jumping:
            self.y += self.jump_speed
            self.jump_speed -= self.gravity

            if self.y <= self.ground_y:
                self.y = self.ground_y
                self.jumping = False
                self.jump_speed = 0
                self.running = False

        # 좌우 이동
        if not self.attacking and not self.attacking2:
            # 뒤로 이동 중이면 달리기 해제
            if self.is_moving_backward():
                self.running = False

            current_speed = self.run_speed if self.running else self.speed

            if self.moving_left:
                self.x -= current_speed
            if self.moving_right:
                self.x += current_speed

        # 화면 경계 처리
        if self.x < 0:
            self.x = 0
        elif self.x > 1200:
            self.x = 1200

        # 프레임 업데이트
        self.frame_time += 1

        if self.hurt:
            if self.frame_time >= 10:
                self.frame += 1
                self.frame_time = 0
                if self.frame >= self.hurt_frame_count:
                    self.frame = 0
                    self.hurt = False
        elif self.jumping:
            if self.frame_time >= 8:
                self.frame = (self.frame + 1) % self.jump_frame_count
                self.frame_time = 0
        elif self.attacking:
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
            frame_delay = 5 if (self.running and not self.is_moving_backward()) else 8
            if self.frame_time >= frame_delay:
                self.frame = (self.frame + 1) % 8
                self.frame_time = 0
        else:
            if self.frame_time >= 8:
                self.frame = (self.frame + 1) % 6
                self.frame_time = 0

    def attack(self):
        if not self.attacking and not self.attacking2:
            self.attacking = True
            self.frame = 0
            self.frame_time = 0

    def attack2(self):
        if not self.attacking and not self.attacking2:
            self.attacking2 = True
            self.frame_time = 0
            self.frame = 0

    def draw(self):
        if self.facing_right:
            flip = ''
        else:
            flip = 'h'

        if self.hurt:
            if self.facing_right:
                self.hurt_image.clip_draw(
                    self.frame * self.hurt_frame_width, 0,
                    self.hurt_frame_width, self.frame_height,
                    self.x, self.y, 200, 200
                )
            else:
                self.hurt_image.clip_composite_draw(
                    self.frame * self.hurt_frame_width, 0,
                    self.hurt_frame_width, self.frame_height,
                    0, flip, self.x, self.y, 200, 200
                )
        elif self.jumping and not self.attacking and not self.attacking2:
            if self.facing_right:
                self.jump_image.clip_draw(
                    self.frame * self.jump_frame_width, 0,
                    self.jump_frame_width, self.frame_height,
                    self.x, self.y, 200, 200)
            else:
                self.jump_image.clip_composite_draw(
                    self.frame * self.jump_frame_width, 0,
                    self.jump_frame_width, self.frame_height,
                    0, flip, self.x, self.y, 200, 200
                )
        elif self.attacking:
            if self.facing_right:
                self.attack_image.clip_draw(
                    self.frame * self.attack_frame_width, 0,
                    self.attack_frame_width, self.frame_height,
                    self.x, self.y, 200, 200
                )
            else:
                self.attack_image.clip_composite_draw(
                    self.frame * self.attack_frame_width, 0,
                    self.attack_frame_width, self.frame_height,
                    0, flip, self.x, self.y, 200, 200
                )
        elif self.attacking2:
            if self.facing_right:
                self.attack2_image.clip_draw(
                    self.frame * self.attack2_frame_width, 0,
                    self.attack2_frame_width, self.frame_height,
                    self.x, self.y, 200, 200
                )
            else:
                self.attack2_image.clip_composite_draw(
                    self.frame * self.attack2_frame_width, 0,
                    self.attack2_frame_width, self.frame_height,
                    0, flip, self.x, self.y, 200, 200
                )
        elif self.moving_left or self.moving_right:
            # 앞으로 달리는 중일 때만 Run 이미지 사용
            if self.running and not self.is_moving_backward():
                if self.facing_right:
                    self.run_image.clip_draw(
                        self.frame * self.run_frame_width, 0,
                        self.run_frame_width, self.frame_height,
                        self.x, self.y, 200, 200
                    )
                else:
                    self.run_image.clip_composite_draw(
                        self.frame * self.run_frame_width, 0,
                        self.run_frame_width, self.frame_height,
                        0, flip, self.x, self.y, 200, 200
                    )
            else:
                if self.facing_right:
                    self.walk_image.clip_draw(
                        self.frame * self.walk_frame_width, 0,
                        self.walk_frame_width, self.frame_height,
                        self.x, self.y, 200, 200
                    )
                else:
                    self.walk_image.clip_composite_draw(
                        self.frame * self.walk_frame_width, 0,
                        self.walk_frame_width, self.frame_height,
                        0, flip, self.x, self.y, 200, 200
                    )
        else:
            if self.facing_right:
                self.idle_image.clip_draw(
                    self.frame * self.idle_frame_width, 0,
                    self.idle_frame_width, self.frame_height,
                    self.x, self.y, 200, 200
                )
            else:
                self.idle_image.clip_composite_draw(
                    self.frame * self.idle_frame_width, 0,
                    self.idle_frame_width, self.frame_height,
                    0, flip, self.x, self.y, 200, 200
                )