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

        # 캐릭터별 히트박스 / 공격 박스 및 공격 속도(쿨타임) 기본 값 설정
        if character_name == 'Fighter':
            # 기본 파라미터
            self.attack_range = 90
            self.attack2_range = 85
            self.hitbox_width = 100
            self.hitbox_height = 100
            self.attack_damage = 10  # 일반 공격 데미지
            self.attack2_damage = 15  # 강 공격 데미지
            self.attack_cooldown_time = 30  # 파이터: 중간 정도 공격 속도 (약 0.3초)

            # 몸통 바운딩 박스 (조금 더 세밀하게 설정)
            self.body_hitbox = {
                'offset_x': 0,
                'offset_y': 5,   # 살짝 위로
                'width': 90,
                'height': 110
            }

            # 공격 1 히트박스
            self.attack1_hitbox = {
                'offset_x_right': 60,   # 오른쪽 공격 시 중심에서 +60
                'offset_x_left': -60,   # 왼쪽 공격 시 중심에서 -60
                'offset_y': 0,
                'width': self.attack_range,
                'height': 80
            }

            # 공격 2 히트박스 (조금 더 멀고 조금 더 큼)
            self.attack2_hitbox = {
                'offset_x_right': 65,
                'offset_x_left': -65,
                'offset_y': 0,
                'width': self.attack2_range,
                'height': 90
            }

        elif character_name == 'Shinobi':
            self.attack_range = 110
            self.attack2_range = 130
            self.hitbox_width = 85
            self.hitbox_height = 95
            self.attack_damage = 6  # 빠르지만 약함
            self.attack2_damage = 9
            self.attack_cooldown_time = 18  # 시노비: 빠른 공격 속도 (약 0.18초)

            # 몸통은 조금 더 슬림하게
            self.body_hitbox = {
                'offset_x': 0,
                'offset_y': 5,
                'width': 80,
                'height': 100
            }

            # 빠른 공격 1 : 짧고 얇은 범위
            self.attack1_hitbox = {
                'offset_x_right': 55,
                'offset_x_left': -55,
                'offset_y': -5,
                'width': self.attack_range,
                'height': 75
            }

            # 긴 공격 2 : 전방으로 많이 뻗음
            self.attack2_hitbox = {
                'offset_x_right': 70,
                'offset_x_left': -70,
                'offset_y': 0,
                'width': self.attack2_range,
                'height': 85
            }

        elif character_name == 'Samurai':
            self.attack_range = 120
            self.attack2_range = 100
            self.hitbox_width = 95
            self.hitbox_height = 105
            self.attack_damage = 16  # 강력함
            self.attack2_damage = 20
            self.attack_cooldown_time = 50  # 사무라이: 느리지만 강한 공격 (약 0.6초)

            # 사무라이 몸통은 약간 크고 위로
            self.body_hitbox = {
                'offset_x': 0,
                'offset_y': 8,
                'width': 95,
                'height': 115
            }

            # 공격 1 : 기본 베기
            self.attack1_hitbox = {
                'offset_x_right': 65,
                'offset_x_left': -65,
                'offset_y': 0,
                'width': self.attack_range,
                'height': 90
            }

            # 공격 2 : 조금 더 위/아래까지 커버
            self.attack2_hitbox = {
                'offset_x_right': 60,
                'offset_x_left': -60,
                'offset_y': 5,
                'width': self.attack2_range,
                'height': 100
            }

        else:
            # 기타 캐릭터 기본값
            self.attack_range = 80
            self.attack2_range = 80
            self.hitbox_width = 100
            self.hitbox_height = 100
            self.attack_damage = 10
            self.attack2_damage = 15
            self.attack_cooldown_time = 25

            self.body_hitbox = {
                'offset_x': 0,
                'offset_y': 0,
                'width': self.hitbox_width,
                'height': self.hitbox_height
            }

            self.attack1_hitbox = {
                'offset_x_right': self.attack_range // 2,
                'offset_x_left': -self.attack_range // 2,
                'offset_y': 0,
                'width': self.attack_range,
                'height': self.hitbox_height
            }

            self.attack2_hitbox = {
                'offset_x_right': self.attack2_range // 2,
                'offset_x_left': -self.attack2_range // 2,
                'offset_y': 0,
                'width': self.attack2_range,
                'height': self.hitbox_height
            }

        # HP 시스템
        self.max_hp = 100
        self.hp = 100

        # 이미지 로드
        self.idle_image = load_image(f'{character_name}/Idle.png')
        self.walk_image = load_image(f'{character_name}/Walk.png')
        self.run_image = load_image(f'{character_name}/Run.png')
        self.attack_image = load_image(f'{character_name}/Attack_1.png')
        self.attack2_image = load_image(f'{character_name}/Attack_3.png')
        self.jump_image = load_image(f'{character_name}/Jump.png')
        self.hurt_image = load_image(f'{character_name}/Hurt.png')
        self.shield_image = load_image(f'{character_name}/Shield.png')
        self.dead_image = load_image(f'{character_name}/Dead.png')
        self.frame = 0

        # 캐릭터별 프레임 수 설정
        if character_name == 'Fighter':
            self.attack_frame_count = 4
            self.attack2_frame_count = 4
            self.jump_frame_count = 10
            self.hurt_frame_count = 3
            self.shield_frame_count = 2
            self.dead_frame_count = 3
        elif character_name == 'Shinobi':
            self.attack_frame_count = 5
            self.attack2_frame_count = 4
            self.jump_frame_count = 12
            self.hurt_frame_count = 2
            self.shield_frame_count = 4
            self.dead_frame_count = 4
        elif character_name == 'Samurai':
            self.attack_frame_count = 6
            self.attack2_frame_count = 4
            self.jump_frame_count = 12
            self.hurt_frame_count = 2
            self.shield_frame_count = 2
            self.dead_frame_count = 3
        else:
            self.attack_frame_count = 4
            self.attack2_frame_count = 4
            self.jump_frame_count = 10
            self.hurt_frame_count = 3
            self.shield_frame_count = 2
            self.dead_frame_count = 4

        # 이미지 프레임 크기 계산
        self.idle_frame_width = self.idle_image.w // 6
        self.walk_frame_width = self.walk_image.w // 8
        self.run_frame_width = self.run_image.w // 8
        self.attack_frame_width = self.attack_image.w // self.attack_frame_count
        self.attack2_frame_width = self.attack2_image.w // self.attack2_frame_count
        self.jump_frame_width = self.jump_image.w // self.jump_frame_count
        self.hurt_frame_width = self.hurt_image.w // self.hurt_frame_count
        self.shield_frame_width = self.shield_image.w // self.shield_frame_count
        self.dead_frame_width = self.dead_image.w // self.dead_frame_count
        self.frame_height = self.walk_image.h

        # 행동 상태 초기화
        self.moving_left = False
        self.moving_right = False
        self.running = False
        self.attacking = False
        self.attacking2 = False
        # 한 번의 공격 모션당 한 번만 데미지를 주기 위한 플래그
        self.attack1_hit_applied = False
        self.attack2_hit_applied = False
        self.jumping = False
        self.hurt = False
        self.blocking = False  # 막기 상태 추가
        self.dead = False  # 사망 상태
        self.death_animation_finished = False  # 사망 애니메이션 완료

        # 뒤로 대쉬 상태
        self.back_dashing = False
        self.back_dash_frames = 0
        self.back_dash_total_frames = 10  # 대쉬에 사용할 프레임 수
        self.back_dash_speed = 9  # 프레임당 이동 거리
        self.back_dash_cooldown = 0  # 백대쉬 쿨다운
        self.back_dash_cooldown_time = 50  # 백대쉬 사이 딜레이

        # 더블탭 감지를 위한 변수
        self.last_key_time = {'left': 0, 'right': 0}
        self.double_tap_threshold = 0.3

        # 프레임 타이머 초기화
        self.frame_time = 0

        # 공격 쿨타임 설정
        self.attack_cooldown = 0  # 남은 쿨타임 (프레임)

    def key_down(self, direction):
        current_time = time.time()

        if not self.jumping and not self.hurt and not self.blocking:
            # 더블 탭 판단
            if current_time - self.last_key_time[direction] < self.double_tap_threshold:
                # 현재 바라보는 방향 기준으로 앞으로/뒤로 판별
                is_backward = (
                    (self.facing_right and direction == 'left') or
                    (not self.facing_right and direction == 'right')
                )

                if is_backward:
                    # 뒤로 이동 키를 두 번 빠르게 입력하면 뒤로 대쉬
                    self.back_dash()
                else:
                    # 앞으로 이동 키 더블 탭이면 달리기 (기존 동작 유지)
                    self.running = True

        self.last_key_time[direction] = current_time

        if direction == 'left':
            self.moving_left = True
        elif direction == 'right':
            self.moving_right = True

    def back_dash(self):
        if (self.back_dashing or self.back_dash_cooldown > 0 or
                self.attacking or self.attacking2 or self.hurt or
                self.blocking or self.jumping or self.dead):
            return False

        # 대쉬 상태 세팅
        self.back_dashing = True
        self.back_dash_frames = 0
        # 대쉬 중에는 일반 이동/달리기 입력과 섞이지 않도록 정지
        self.moving_left = False
        self.moving_right = False
        self.running = False
        self.back_dash_cooldown = self.back_dash_cooldown_time
        return True

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
        if not self.jumping and not self.blocking:
            self.jumping = True
            self.jump_speed = self.jump_power
            self.frame = 0
            self.frame_time = 0

    def get_hit(self, damage=10):
        # 이미 피격 모션 중이거나 막는 중이면 무시
        if self.hurt or self.blocking or self.dead:
            return

        # 피격 직전의 움직임 방향을 기억해서
        # '뒤로 이동 중이면 가드' 판정을 유지
        was_moving_backward = self.is_moving_backward()

        # 피격 순간에는 이동/달리기/백대쉬 상태를 모두 정지
        # -> P1, CPU 모두 동일한 조건에서 넉백 적용
        self.moving_left = False
        self.moving_right = False
        self.running = False
        self.back_dashing = False
        self.back_dash_frames = 0

        if was_moving_backward:
            # 뒤로 이동 중이면 자동 가드
            self.blocking = True
            self.hurt = False

            # 방어 시 데미지 50% 감소
            self.hp -= damage * 0.5

            # 가드 넉백 (살짝 밀림)
            if self.facing_right:
                self.x -= 5
            else:
                self.x += 5
        else:
            # 정면/전진 중 피격
            self.blocking = False
            self.hurt = True

            # 전체 데미지 적용
            self.hp -= damage

            # 피격 넉백 (공격자 반대 방향으로 밀림)
            if self.facing_right:
                self.x -= 10
            else:
                self.x += 10

        # HP는 0 아래로 내려가지 않게
        if self.hp < 0:
            self.hp = 0

        # 피격 애니메이션 초기화
        self.frame = 0
        self.frame_time = 0

    def is_dead(self):
        return self.hp <= 0

    def is_attacking(self):
        return self.attacking or self.attacking2

    def get_attacking_hitbox(self):
        if not self.is_attacking():
            return None

        if self.attacking:
            cfg = self.attack1_hitbox
        else:
            cfg = self.attack2_hitbox

        if self.facing_right:
            hitbox_x = self.x + cfg['offset_x_right']
        else:
            hitbox_x = self.x + cfg['offset_x_left']

        return {
            'x': hitbox_x,
            'y': self.y + cfg['offset_y'],
            'width': cfg['width'],
            'height': cfg['height']
        }

    def get_body_hitbox(self):
        return {
            'x': self.x + self.body_hitbox['offset_x'],
            'y': self.y + self.body_hitbox['offset_y'],
            'width': self.body_hitbox['width'],
            'height': self.body_hitbox['height']
        }

    def check_hit(self, opponent_hitbox):
        if self.hurt or self.blocking:
            return False

        attack_box = opponent_hitbox.get_attacking_hitbox()

        if attack_box is None:
            return False

        body_box = self.get_body_hitbox()

        if abs(attack_box['x'] - body_box['x']) < (attack_box['width'] + body_box['width']) / 2 and abs(
                attack_box['y'] - body_box['y']) < (attack_box['height'] + body_box['height']) / 2:
            return True

        return False

    def check_collision_with(self, opponent):
        if self.jumping or opponent.jumping:
            return False

        # 캐릭터별 몸통 바운딩 박스를 기준으로 충돌 폭 계산
        collision_width_self = self.body_hitbox['width'] * 0.4
        collision_width_opponent = opponent.body_hitbox['width'] * 0.4

        distance = abs(self.x - opponent.x)
        min_distance = (collision_width_self + collision_width_opponent) / 2

        if distance < min_distance:
            return True

        return False

    def resolve_collision(self, opponent):
        if not self.check_collision_with(opponent):
            return

        collision_width_self = self.hitbox_width * 0.4
        collision_width_opponent = opponent.hitbox_width * 0.4

        distance = abs(self.x - opponent.x)
        min_distance = (collision_width_self + collision_width_opponent) / 2
        overlap = min_distance - distance

        if overlap < 0.5:
            return

        self_moving = self.moving_left or self.moving_right
        opponent_moving = opponent.moving_left or opponent.moving_right

        if self.x < opponent.x:
            if self_moving and not opponent_moving:
                self.x -= overlap
            elif opponent_moving and not self_moving:
                opponent.x += overlap
            else:
                self.x -= overlap / 2
                opponent.x += overlap / 2
        else:
            if self_moving and not opponent_moving:
                self.x += overlap
            elif opponent_moving and not self_moving:
                opponent.x -= overlap
            else:
                self.x += overlap / 2
                opponent.x -= overlap / 2

        self.x = max(0, min(1200, self.x))
        opponent.x = max(0, min(1200, opponent.x))

    def is_moving_backward(self):
        if self.facing_right and self.moving_left:
            return True
        elif not self.facing_right and self.moving_right:
            return True
        return False

    def update(self, opponent_x=None):
        # 사망 애니메이션 중이면
        if self.dead:
            # 바닥에 떨어지는 중력 적용
            if self.y > self.ground_y:
                self.y += self.jump_speed
                self.jump_speed -= self.gravity

                if self.y <= self.ground_y:
                    self.y = self.ground_y
                    self.jump_speed = 0

            # 바닥에 도달한 후에만 Dead 애니메이션 재생
            if self.y <= self.ground_y:
                self.frame_time += 1
                if self.frame_time >= 10:
                    self.frame += 1
                    self.frame_time = 0
                    if self.frame >= self.dead_frame_count:
                        self.frame = self.dead_frame_count - 1  # 마지막 프레임 유지
                        self.death_animation_finished = True
            return  # 다른 업데이트 중지

        # 공격 쿨타임 감소
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.back_dash_cooldown > 0:
            self.back_dash_cooldown -= 1

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

        # 뒤로 대쉬 처리 (짧은 시간 동안 빠르게 이동)
        if self.back_dashing:
            if self.facing_right:
                self.x -= self.back_dash_speed
            else:
                self.x += self.back_dash_speed

            self.back_dash_frames += 1

            if self.back_dash_frames >= self.back_dash_total_frames:
                self.back_dashing = False

        # 좌우 이동 (대쉬 중이 아닐 때만)
        if (not self.back_dashing and
                not self.attacking and not self.attacking2 and
                not self.blocking and not self.hurt):
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

        if self.blocking:
            # 방어 애니메이션
            if self.frame_time >= 10:
                self.frame += 1
                self.frame_time = 0
                if self.frame >= self.shield_frame_count:
                    self.frame = 0
                    self.blocking = False
        elif self.hurt:
            # 피격 애니메이션
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
                    self.attack_cooldown = self.attack_cooldown_time  # 쿨타임 시작
        elif self.attacking2:
            if self.frame_time >= 10:
                self.frame += 1
                self.frame_time = 0
                if self.frame >= self.attack2_frame_count:
                    self.frame = 0
                    self.attacking2 = False
                    self.attack_cooldown = self.attack_cooldown_time  # 쿨타임 시작
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
        if (not self.attacking and not self.attacking2 and not self.blocking and
                not self.hurt and self.attack_cooldown <= 0):
            self.attacking = True
            self.attack1_hit_applied = False  # 새 공격 시작: 아직 맞춘 적 없음
            self.frame = 0
            self.frame_time = 0

    def attack2(self):
        if (not self.attacking and not self.attacking2 and not self.blocking and
                not self.hurt and self.attack_cooldown <= 0):
            self.attacking2 = True
            self.attack2_hit_applied = False  # 새 공격 시작: 아직 맞춘 적 없음
            self.frame_time = 0
            self.frame = 0

    def draw(self):
        if self.facing_right:
            flip = ''
        else:
            flip = 'h'

        if self.dead:
            # 바닥에 도달하지 않았으면 Hurt 이미지 (떨어지는 모습)
            if self.y > self.ground_y:
                if self.facing_right:
                    self.hurt_image.clip_draw(
                        (self.hurt_frame_count - 1) * self.hurt_frame_width, 0,
                        self.hurt_frame_width, self.frame_height,
                        self.x, self.y, 200, 200
                    )
                else:
                    self.hurt_image.clip_composite_draw(
                        (self.hurt_frame_count - 1) * self.hurt_frame_width, 0,
                        self.hurt_frame_width, self.frame_height,
                        0, flip, self.x, self.y, 200, 200
                    )
            else:
                # 바닥에 도달하면 Dead 애니메이션 출력
                if self.facing_right:
                    self.dead_image.clip_draw(
                        self.frame * self.dead_frame_width, 0,
                        self.dead_frame_width, self.frame_height,
                        self.x, self.y, 200, 200
                    )
                else:
                    self.dead_image.clip_composite_draw(
                        self.frame * self.dead_frame_width, 0,
                        self.dead_frame_width, self.frame_height,
                        0, flip, self.x, self.y, 200, 200
                    )
        elif self.blocking:
            # 방어 이미지 출력
            if self.facing_right:
                self.shield_image.clip_draw(
                    self.frame * self.shield_frame_width, 0,
                    self.shield_frame_width, self.frame_height,
                    self.x, self.y, 200, 200
                )
            else:
                self.shield_image.clip_composite_draw(
                    self.frame * self.shield_frame_width, 0,
                    self.shield_frame_width, self.frame_height,
                    0, flip, self.x, self.y, 200, 200
                )
        elif self.hurt:
            # 피격 이미지 출력
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