from pico2d import *
from character import Character
from ai_controller import *
import time


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

        # HP바 이미지
        self.hp_images = {}

        # 폰트 (나중에 로드)
        self.font = None

    def init(self, character1_name='Fighter', character2_name='Samurai', character_speed=3, enable_ai=True,
             ai_difficulty='normal'):
        # 윈도우 생성
        open_canvas(self.width, self.height)

        # 폰트 로드
        try:
            self.font = load_font('Font/ENCR10B.TTF', 60)
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

        # 승리 배경 로드
        try:
            self.victory_bg = load_image('Background/victory_background.png')
        except:
            print("승리 배경 로드 실패")
            self.victory_bg = None

        # 캐릭터 초기 위치 설정
        self.character1 = Character(character1_name, self.width // 4, self.height // 2, character_speed,
                                    facing_right=True)
        self.character2 = Character(character2_name, self.width * 3 // 4, self.height // 2, character_speed,
                                    facing_right=False)

        self.ai_enable = enable_ai
        if self.ai_enable:
            self.ai_controller = AIController(self.character2, self.character1, ai_difficulty)

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

        # 플레이어1이 플레이어2를 공격했는지 확인
        if self.character2.check_hit(self.character1):
            if self.character1.attacking and not self.character1.attack1_hit_applied:
                self.character2.get_hit(self.character1.attack_damage)
                self.character1.attack1_hit_applied = True  # 이번 공격으로 이미 맞췄음
            elif self.character1.attacking2 and not self.character1.attack2_hit_applied:
                self.character2.get_hit(self.character1.attack2_damage)
                self.character1.attack2_hit_applied = True  # 이번 공격으로 이미 맞췄음

        # 플레이어2가 플레이어1을 공격했는지 확인
        if self.character1.check_hit(self.character2):
            if self.character2.attacking and not self.character2.attack1_hit_applied:
                self.character1.get_hit(self.character2.attack_damage)
                self.character2.attack1_hit_applied = True  # 이번 공격으로 이미 맞췄음
            elif self.character2.attacking2 and not self.character2.attack2_hit_applied:
                self.character1.get_hit(self.character2.attack2_damage)
                self.character2.attack2_hit_applied = True  # 이번 공격으로 이미 맞췄음

        # 승패 체크 (KO)
        if self.character1.is_dead() and not self.character1.dead:
            # Player 1 사망 - Dead 애니메이션 시작
            self.character1.dead = True
            self.character1.frame = 0
            self.character1.frame_time = 0
            self.character1.death_animation_finished = False

        if self.character2.is_dead() and not self.character2.dead:
            # Player 2 사망 - Dead 애니메이션 시작
            self.character2.dead = True
            self.character2.frame = 0
            self.character2.frame_time = 0
            self.character2.death_animation_finished = False

    def end_game_by_time(self):
        """시간 종료로 라운드 종료"""
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
        """라운드 종료 처리"""
        self.round_end = True
        self.round_winner = winner
        self.round_end_time = 0

        # 승수 증가
        if winner == 1:
            self.player1_wins += 1
        elif winner == 2:
            self.player2_wins += 1

    def start_next_round(self):
        """다음 라운드 시작"""
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

    def draw_hp_bar(self, x, y, hp, max_hp, is_player1=True):
        """HP 바 그리기"""
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
        """타이머 그리기"""
        if self.font:
            # 시간이 10초 이하면 빨간색, 아니면 흰색
            if self.time_left <= 10:
                self.font.draw(self.width // 2 - 30, 730, f'{self.time_left:02d}', (255, 0, 0))
            else:
                self.font.draw(self.width // 2 - 30, 730, f'{self.time_left:02d}', (255, 255, 255))

    def draw_round_info(self):
        """라운드 정보 및 승수 표시"""
        if self.font:
            # 라운드 번호 (중앙 하단)
            round_text = f'ROUND {self.round_number}'
            self.font.draw(self.width // 2 - 100, 670, round_text, (255, 255, 255))

            # 승수 표시 (동그라미)
            self.draw_win_indicators()

    def draw_win_indicators(self):
        """승수 표시 (동그라미)"""
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
        """라운드 결과 표시"""
        if self.font is None:
            return

        if self.round_winner == 1:
            message = "PLAYER 1 WINS ROUND!"
            self.font.draw(self.width // 2 - 250, self.height // 2, message, (255, 215, 0))
        elif self.round_winner == 2:
            message = "PLAYER 2 WINS ROUND!"
            self.font.draw(self.width // 2 - 250, self.height // 2, message, (255, 215, 0))
        else:
            message = "DRAW!"
            self.font.draw(self.width // 2 - 80, self.height // 2, message, (255, 255, 255))

    def draw_game_over(self):
        """매치 종료 화면 그리기"""
        if not self.match_over or self.font is None:
            return

        # 최종 승자 메시지
        if self.winner == 1:
            message = "PLAYER 1 WINS!"
            self.font.draw(self.width // 2 - 200, self.height // 2 + 50, message, (255, 215, 0))
        elif self.winner == 2:
            message = "PLAYER 2 WINS!"
            self.font.draw(self.width // 2 - 200, self.height // 2 + 50, message, (255, 215, 0))

        # 재시작 안내
        try:
            restart_font = load_font('Font/ENCR10B.TTF', 30)
            restart_font.draw(self.width // 2 - 150, self.height // 2 - 50,
                              "Press SPACE to restart", (200, 200, 200))
        except:
            pass

    def draw(self):
        clear_canvas()

        # 승리 화면일 때 승리 배경
        if self.match_over and self.victory_bg:
            self.victory_bg.draw(self.width // 2, self.height // 2)

        # 캐릭터 그리기
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

        update_canvas()

    def reset_game(self):
        """게임 완전 리셋"""
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

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            delay(0.01)

    def close(self):
        if self.ai_enable:
            self.ai_controller.cleaning()
        close_canvas()