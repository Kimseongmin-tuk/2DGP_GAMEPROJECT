from pico2d import *
from character import Character
from ai_controller import *
import time
import random


class GameManager:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.running = False
        self.character1 = None
        self.character2 = None
        self.ai_controller = None
        self.ai_enable = False

        # 게임 상태
        self.game_over = False
        self.winner = None
        self.ko_time = 0

        # 라운드 시스템 (3판 2선승)
        self.round_number = 1  # 현재 라운드
        self.max_rounds = 3  # 최대 라운드
        self.player1_wins = 0  # P1 승수
        self.player2_wins = 0  # P2 승수
        self.round_winner = None  # 현재 라운드 승자
        self.round_end = False  # 라운드 종료 여부
        self.round_end_time = 0  # 라운드 종료 후 대기 시간
        self.match_over = False  # 전체 매치 종료

        # 타이머 설정
        self.game_time = 99  # 게임 시간 (초)
        self.time_left = 99  # 남은 시간
        self.last_time_update = 0  # 마지막 시간 업데이트

        # KO 연출 관련 변수
        self.stop_frames = 0
        self.slow_motion_frames = 0
        self.shake_frames = 0
        self.shake_magnitude = 0

        # KO 텍스트 표시 시간
        self.ko_text_frames = 0

        # HP바 이미지
        self.hp_images = {}

        # 폰트 (나중에 로드)
        self.font = None

        # 캐릭터 선택용 목록
        self.character_list = ['Fighter', 'Shinobi', 'Samurai']

    def init(self,
             character1_name='Fighter',
             character2_name='Samurai',
             character_speed=3,
             enable_ai=True,
             use_character_select=True):
        # 윈도우 생성
        open_canvas(self.width, self.height)

        # 폰트 로드
        try:
            self.font = load_font('font/NanumGothic.ttf', 60)
        except:
            print("폰트 로드 실패 - 기본 폰트 사용")
            self.font = None

        # HP바용 이미지 로드
        try:
            self.hp_images['green'] = load_image('HP_BAR/green.png')
            self.hp_images['yellow'] = load_image('HP_BAR/yellow.png')
            self.hp_images['red'] = load_image('HP_BAR/red.png')
            self.hp_images['dark_red'] = load_image('HP_BAR/dark_red.png')
            self.hp_images['white'] = load_image('HP_BAR/white.png')
        except:
            print("HP바 이미지 로드 실패 - 기본 그리기 사용")
            self.hp_images = None

        self.ai_enable = enable_ai

        # 🔹 캐릭터 선택 화면 (폰트가 있을 때만)
        if use_character_select and self.font is not None:
            character1_name, character2_name = self.character_select_screen()

        # 캐릭터 초기 위치 설정
        self.character1 = Character(character1_name, self.width // 4, self.height // 2, character_speed,
                                    facing_right=True)
        self.character2 = Character(character2_name, self.width * 3 // 4, self.height // 2, character_speed,
                                    facing_right=False)

        if self.ai_enable:
            self.ai_controller = AIController(self.character2, self.character1)

        # 타이머 시작
        self.time_left = self.game_time
        self.last_time_update = time.time()

        self.running = True

    def handle_events(self):
        events = get_events()

        for event in events:
            if event.type == SDL_QUIT:
                self.running = False
            elif event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    self.running = False

                # 게임 오버 시 재시작
                if self.match_over and event.key == SDLK_SPACE:
                    self.reset_game()

                # 플레이어1
                elif event.key == SDLK_a:
                    self.character1.key_down('left')
                elif event.key == SDLK_d:
                    self.character1.key_down('right')
                elif event.key == SDLK_f:
                    self.character1.attack()
                elif event.key == SDLK_g:
                    self.character1.attack2()
                elif event.key == SDLK_w:
                    self.character1.jump()

                # 플레이어2
                elif not self.ai_enable:
                    if event.key == SDLK_LEFT:
                        self.character2.key_down('left')
                    elif event.key == SDLK_RIGHT:
                        self.character2.key_down('right')
                    elif event.key == SDLK_k:
                        self.character2.attack()
                    elif event.key == SDLK_l:
                        self.character2.attack2()
                    elif event.key == SDLK_UP:
                        self.character2.jump()

            elif event.type == SDL_KEYUP:
                # 플레이어1
                if event.key == SDLK_a:
                    self.character1.key_up('left')
                elif event.key == SDLK_d:
                    self.character1.key_up('right')

                # 플레이어2
                elif not self.ai_enable:
                    if event.key == SDLK_LEFT:
                        self.character2.key_up('left')
                    elif event.key == SDLK_RIGHT:
                        self.character2.key_up('right')

    def update(self):
        # 매치가 완전히 끝났으면 업데이트 중지
        if self.match_over:
            self.ko_time += 1
            return

        # KO 시 잠깐 멈춤 효과
        if self.stop_frames > 0:
            self.stop_frames -= 1
            return

        # 라운드 종료 후 대기 중
        if self.round_end:
            self.round_end_time += 1

            # Dead 애니메이션은 계속 진행
            self.character1.update(opponent_x=self.character2.x)
            self.character2.update(opponent_x=self.character1.x)

            # 3초 대기 후 다음 라운드 또는 매치 종료
            if self.round_end_time >= 300:  # 3초 (100 FPS 기준)
                if self.player1_wins >= 2 or self.player2_wins >= 2:
                    # 매치 종료 (2승 달성)
                    self.match_over = True
                    self.game_over = True
                    self.winner = 1 if self.player1_wins >= 2 else 2
                else:
                    # 다음 라운드 시작
                    self.start_next_round()
            return

        # 게임 오버 상태면 업데이트 중지
        if self.game_over:
            self.ko_time += 1
            return

        if self.slow_motion_frames > 0:
            self.slow_motion_frames -= 1

        # 타이머 업데이트
        current_time = time.time()
        if current_time - self.last_time_update >= 1.0:  # 1초마다
            self.time_left -= 1
            self.last_time_update = current_time

            # 시간 종료 체크
            if self.time_left <= 0:
                self.time_left = 0
                self.end_game_by_time()

        # Dead 애니메이션이 진행 중이면 캐릭터 업데이트만 (다른 로직 스킵)
        if self.character1.dead or self.character2.dead:
            self.character1.update(opponent_x=self.character2.x)
            self.character2.update(opponent_x=self.character1.x)

            # Dead 애니메이션이 끝났는지 체크
            if self.character1.dead and self.character1.death_animation_finished:
                self.end_round(2)  # Player 2 승리
            elif self.character2.dead and self.character2.death_animation_finished:
                self.end_round(1)  # Player 1 승리
            return

        if self.ai_enable:
            self.ai_controller.update()

        self.character1.update(opponent_x=self.character2.x)
        self.character2.update(opponent_x=self.character1.x)

        # 캐릭터 충돌 처리
        self.character1.resolve_collision(self.character2)

        # 플레이어1이 플레이어2를 공격했는지 확인 (한 공격당 한 번만 데미지)
        if self.character2.check_hit(self.character1):
            if self.character1.attacking and not self.character1.attack1_hit_applied:
                self.character2.get_hit(self.character1.attack_damage)
                self.character1.attack1_hit_applied = True
            elif self.character1.attacking2 and not self.character1.attack2_hit_applied:
                self.character2.get_hit(self.character1.attack2_damage)
                self.character1.attack2_hit_applied = True

        # 플레이어2가 플레이어1을 공격했는지 확인 (한 공격당 한 번만 데미지)
        if self.character1.check_hit(self.character2):
            if self.character2.attacking and not self.character2.attack1_hit_applied:
                self.character1.get_hit(self.character2.attack_damage)
                self.character2.attack1_hit_applied = True
            elif self.character2.attacking2 and not self.character2.attack2_hit_applied:
                self.character1.get_hit(self.character2.attack2_damage)
                self.character2.attack2_hit_applied = True

        # 승패 체크 (KO)
        if self.character1.is_dead() and not self.character1.dead:
            # KO 연출 시작
            self.trigger_ko_effect()

            # Player 1 사망
            self.character1.dead = True
            self.character1.frame = 0
            self.character1.frame_time = 0
            self.character1.death_animation_finished = False

        if self.character2.is_dead() and not self.character2.dead:
            # KO 연출 시작
            self.trigger_ko_effect()

            # Player 2 사망
            self.character2.dead = True
            self.character2.frame = 0
            self.character2.frame_time = 0
            self.character2.death_animation_finished = False

    def trigger_ko_effect(self):
        # 히트스톱: 약 0.15초 (100 FPS 기준 15프레임)
        self.stop_frames = 15

        # 슬로모션: 약 1.5초
        self.slow_motion_frames = 150

        # 화면 흔들림: 약 0.3초
        self.shake_frames = 30

        # KO 텍스트: 약 0.9초
        self.ko_text_frames = 90

    def end_game_by_time(self):
        # HP 비교하여 패자 결정 후 Dead 애니메이션
        if self.character1.hp > self.character2.hp:
            # Player 2 패배
            self.character2.dead = True
            self.character2.frame = 0
            self.character2.frame_time = 0
            self.character2.death_animation_finished = False
            self.round_winner = 1
        elif self.character2.hp > self.character1.hp:
            # Player 1 패배
            self.character1.dead = True
            self.character1.frame = 0
            self.character1.frame_time = 0
            self.character1.death_animation_finished = False
            self.round_winner = 2
        else:
            # 동점인 경우 양쪽 다 패배 (무승부 라운드)
            self.round_winner = 0
            self.end_round(0)

    def end_round(self, winner):
        self.round_end = True
        self.round_winner = winner
        self.round_end_time = 0

        # 승수 증가
        if winner == 1:
            self.player1_wins += 1
        elif winner == 2:
            self.player2_wins += 1

    def start_next_round(self):
        self.round_number += 1
        self.round_end = False
        self.round_winner = None
        self.round_end_time = 0

        # HP 초기화
        self.character1.hp = self.character1.max_hp
        self.character2.hp = self.character2.max_hp

        # 위치 초기화
        self.character1.x = self.width // 4
        self.character2.x = self.width * 3 // 4
        self.character1.y = self.character1.ground_y
        self.character2.y = self.character2.ground_y

        # 상태 초기화
        self.character1.hurt = False
        self.character1.blocking = False
        self.character1.attacking = False
        self.character1.attacking2 = False
        self.character1.jumping = False
        self.character1.dead = False
        self.character1.death_animation_finished = False

        self.character2.hurt = False
        self.character2.blocking = False
        self.character2.attacking = False
        self.character2.attacking2 = False
        self.character2.jumping = False
        self.character2.dead = False
        self.character2.death_animation_finished = False

        # 타이머 초기화
        self.time_left = self.game_time
        self.last_time_update = time.time()

        # KO 연출 변수 초기화
        self.stop_frames = 0
        self.slow_motion_frames = 0
        self.shake_frames = 0
        self.ko_text_frames = 0

    def draw_hp_bar(self, x, y, hp, max_hp, is_player1=True):
        if self.hp_images is None:
            return

        bar_width = 400
        bar_height = 30

        # HP 비율 계산
        hp_ratio = hp / max_hp
        if hp_ratio < 0:
            hp_ratio = 0
        hp_width = int(bar_width * hp_ratio)

        # HP 색상 결정
        if hp_ratio > 0.5:
            hp_color = 'green'
        elif hp_ratio > 0.25:
            hp_color = 'yellow'
        else:
            hp_color = 'red'

        # 배경 (어두운 빨간색)
        self.hp_images['dark_red'].draw(x, y, bar_width, bar_height)

        # HP 바 (색상)
        if hp_width > 0:
            if is_player1:
                # 왼쪽 정렬
                hp_x = x - bar_width // 2 + hp_width // 2
                self.hp_images[hp_color].draw(hp_x, y, hp_width, bar_height - 4)
            else:
                # 오른쪽 정렬
                hp_x = x + bar_width // 2 - hp_width // 2
                self.hp_images[hp_color].draw(hp_x, y, hp_width, bar_height - 4)

        # 테두리 (흰색)
        self.hp_images['white'].draw(x, y + bar_height // 2, bar_width + 4, 2)
        self.hp_images['white'].draw(x, y - bar_height // 2, bar_width + 4, 2)
        self.hp_images['white'].draw(x - bar_width // 2, y, 2, bar_height)
        self.hp_images['white'].draw(x + bar_width // 2, y, 2, bar_height)

    def draw_timer(self):
        if self.font:
            # 시간이 10초 이하면 빨간색, 아니면 흰색
            if self.time_left <= 10:
                self.font.draw(self.width // 2 - 30, 730, f'{self.time_left:02d}', (255, 0, 0))
            else:
                self.font.draw(self.width // 2 - 30, 730, f'{self.time_left:02d}', (255, 255, 255))

    def draw_round_info(self):
        if self.font:
            # 라운드 번호 (중앙 하단)
            round_text = f'ROUND {self.round_number}'
            self.font.draw(self.width // 2 - 100, 670, round_text, (255, 255, 255))

            # 승수 표시 (동그라미)
            self.draw_win_indicators()

    def draw_win_indicators(self):
        if self.hp_images is None:
            return

        circle_size = 20
        spacing = 30

        # Player 1 승수 (왼쪽)
        for i in range(2):  # 최대 2승
            x = 100 + i * spacing
            y = 720
            if i < self.player1_wins:
                # 승리한 라운드 (노란색)
                self.hp_images['yellow'].draw(x, y, circle_size, circle_size)
            else:
                # 아직 승리하지 않은 라운드 (회색)
                self.hp_images['dark_red'].draw(x, y, circle_size, circle_size)

        # Player 2 승수 (오른쪽)
        for i in range(2):
            x = 1100 - i * spacing
            y = 720
            if i < self.player2_wins:
                # 승리한 라운드 (노란색)
                self.hp_images['yellow'].draw(x, y, circle_size, circle_size)
            else:
                # 아직 승리하지 않은 라운드 (회색)
                self.hp_images['dark_red'].draw(x, y, circle_size, circle_size)

    def draw_round_result(self):
        if self.font is None:
            return

        if self.round_winner == 1:
            message = "PLAYER 1 WINS ROUND!"
            self.font.draw(self.width // 2 - 320, self.height // 2, message, (255, 215, 0))
        elif self.round_winner == 2:
            message = "PLAYER 2 WINS ROUND!"
            self.font.draw(self.width // 2 - 320, self.height // 2, message, (255, 215, 0))
        else:
            message = "DRAW!"
            self.font.draw(self.width // 2 - 80, self.height // 2, message, (255, 255, 255))

    def draw_game_over(self):
        if not self.match_over or self.font is None:
            return

        # 최종 승자 메시지
        if self.winner == 1:
            message = "PLAYER 1 WINS!"
            self.font.draw(self.width // 2 - 240, self.height // 2 + 50, message, (255, 215, 0))
        elif self.winner == 2:
            message = "PLAYER 2 WINS!"
            self.font.draw(self.width // 2 - 240, self.height // 2 + 50, message, (255, 215, 0))

        # 재시작 안내
        try:
            restart_font = load_font('ENCR10B.TTF', 30)
            restart_font.draw(self.width // 2 - 180, self.height // 2 - 50,
                              "Press SPACE to restart", (0, 0, 0))
        except:
            pass

    def draw_ko_text(self):
        if self.font is None:
            return

        if self.ko_text_frames > 0:
            self.ko_text_frames -= 1

            text = "K.O."

            self.font.draw(self.width // 2 - 120,
                           self.height // 2 + 100,
                           text,
                           (255, 215, 0))

    def draw(self):
        clear_canvas()

        # 화면 흔들림 오프셋 계산
        shake_x = 0
        shake_y = 0
        if self.shake_frames > 0:
            self.shake_frames -= 1
            shake_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            shake_y = random.randint(-self.shake_magnitude, self.shake_magnitude)

        # 캐릭터 그리기 (그리는 동안만 위치를 잠깐 이동시켰다가 되돌림)
        if shake_x != 0 or shake_y != 0:
            orig_x1, orig_y1 = self.character1.x, self.character1.y
            orig_x2, orig_y2 = self.character2.x, self.character2.y

            self.character1.x += shake_x
            self.character1.y += shake_y
            self.character2.x += shake_x
            self.character2.y += shake_y

            self.character1.draw()
            self.character2.draw()

            self.character1.x, self.character1.y = orig_x1, orig_y1
            self.character2.x, self.character2.y = orig_x2, orig_y2
        else:
            self.character1.draw()
            self.character2.draw()

        # HP 바 그리기
        self.draw_hp_bar(250, 750, self.character1.hp, self.character1.max_hp, is_player1=True)
        self.draw_hp_bar(950, 750, self.character2.hp, self.character2.max_hp, is_player1=False)

        # 타이머 그리기
        self.draw_timer()

        # 라운드 정보 그리기
        self.draw_round_info()

        # 라운드 종료 메시지
        if self.round_end and not self.match_over:
            self.draw_round_result()

        # 매치 종료 메시지
        if self.match_over:
            self.draw_game_over()

        # KO 텍스트 그리기
        self.draw_ko_text()

        update_canvas()

    def reset_game(self):
        # 라운드 초기화
        self.round_number = 1
        self.player1_wins = 0
        self.player2_wins = 0
        self.round_winner = None
        self.round_end = False
        self.round_end_time = 0
        self.match_over = False

        # HP 초기화
        self.character1.hp = self.character1.max_hp
        self.character2.hp = self.character2.max_hp

        # 위치 초기화
        self.character1.x = self.width // 4
        self.character2.x = self.width * 3 // 4
        self.character1.y = self.character1.ground_y
        self.character2.y = self.character2.ground_y

        # 상태 초기화
        self.character1.hurt = False
        self.character1.blocking = False
        self.character1.attacking = False
        self.character1.attacking2 = False
        self.character1.jumping = False
        self.character1.dead = False
        self.character1.death_animation_finished = False

        self.character2.hurt = False
        self.character2.blocking = False
        self.character2.attacking = False
        self.character2.attacking2 = False
        self.character2.jumping = False
        self.character2.dead = False
        self.character2.death_animation_finished = False

        # 게임 상태 초기화
        self.game_over = False
        self.winner = None
        self.ko_time = 0

        # 타이머 초기화
        self.time_left = self.game_time
        self.last_time_update = time.time()

        # KO 연출 변수 초기화
        self.stop_frames = 0
        self.slow_motion_frames = 0
        self.shake_frames = 0
        self.ko_text_frames = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            # 슬로모션 중이면 프레임 간격을 조금 늘려서 느리게 보이게
            if self.slow_motion_frames > 0:
                delay(0.02)  # 평소보다 2배 느리게
            else:
                delay(0.01)

    def close(self):
        if self.ai_enable:
            self.ai_controller.cleaning()
        close_canvas()

    def character_select_screen(self):
        """간단한 캐릭터 선택 화면: P1, P2 캐릭터 선택"""
        characters = self.character_list
        p1_index = 0
        p2_index = 1 if len(characters) > 1 else 0

        selecting_p1 = True
        running = True

        while running:
            clear_canvas()

            if self.font:
                # 제목
                self.font.draw(self.width // 2 - 280,
                               self.height - 150,
                               'CHARACTER SELECT',
                               (255, 255, 255))

                # Player 1 영역
                self.font.draw(150,
                               self.height // 2 + 80,
                               'PLAYER 1',
                               (255, 255, 0))
                self.font.draw(150,
                               self.height // 2,
                               characters[p1_index],
                               (255, 255, 255))

                # Player 2 영역
                self.font.draw(self.width - 350,
                               self.height // 2 + 80,
                               'PLAYER 2',
                               (0, 255, 255))
                self.font.draw(self.width - 350,
                               self.height // 2,
                               characters[p2_index],
                               (255, 255, 255))

                # 현재 선택중인 쪽에 화살표 표시
                if selecting_p1:
                    self.font.draw(80,
                                   self.height // 2,
                                   '->',
                                   (255, 255, 0))
                else:
                    self.font.draw(self.width - 420,
                                   self.height // 2,
                                   '->',
                                   (0, 255, 255))

                # 조작 설명
                self.font.draw(0,
                               150,
                               '<- -> : 캐릭터 변경   ENTER : 확정   ESC : 종료',
                               (0, 0, 0))

            update_canvas()

            events = get_events()
            for e in events:
                if e.type == SDL_QUIT:
                    close_canvas()
                    exit(0)

                if e.type == SDL_KEYDOWN:
                    if e.key == SDLK_ESCAPE:
                        close_canvas()
                        exit(0)

                    # 왼쪽/오른쪽으로 캐릭터 변경
                    if e.key == SDLK_LEFT:
                        if selecting_p1:
                            p1_index = (p1_index - 1) % len(characters)
                        else:
                            p2_index = (p2_index - 1) % len(characters)

                    elif e.key == SDLK_RIGHT:
                        if selecting_p1:
                            p1_index = (p1_index + 1) % len(characters)
                        else:
                            p2_index = (p2_index + 1) % len(characters)

                    # ENTER / SPACE 로 확정
                    elif e.key == SDLK_RETURN or e.key == SDLK_SPACE:
                        if selecting_p1:
                            # 이제 P2 선택 단계로 넘어감
                            selecting_p1 = False
                        else:
                            # 둘 다 고르면 선택 종료
                            running = False

            delay(0.01)

        return characters[p1_index], characters[p2_index]
