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
        self.round_number = 1
        self.max_rounds = 3
        self.player1_wins = 0
        self.player2_wins = 0
        self.round_winner = None
        self.round_end = False
        self.round_end_time = 0
        self.match_over = False

        # 타이머
        self.game_time = 99
        self.time_left = 99
        self.last_time_update = 0

        # KO 연출
        self.stop_frames = 0
        self.slow_motion_frames = 0
        self.shake_frames = 0
        self.shake_magnitude = 0
        self.ko_text_frames = 0

        # HP바 이미지
        self.hp_images = {}

        # 폰트
        self.font = None

        # 캐릭터 선택용 목록
        self.character_list = ['Fighter', 'Shinobi', 'Samurai']

        # ===== 맵(스테이지) 관련 =====
        self.stage_list = [
            'Airport',
            'Korean Town',
            'Night Village',
            'Racing Circuit',
            'Underpass Street'
        ]
        self.stage_images = {}          # 이름 -> 이미지
        self.current_stage_name = None  # 선택된 맵 이름
        self.current_stage_image = None # 선택된 맵 이미지

    def init(self,
             character1_name='Fighter',
             character2_name='Samurai',
             character_speed=3,
             enable_ai=True,
             use_character_select=True,
             use_stage_select=True):

        open_canvas(self.width, self.height)

        # 폰트
        try:
            self.font = load_font('Font/NanumGothic.ttf', 60)
        except:
            print("폰트 로드 실패")
            self.font = None

        # HP바 이미지
        try:
            self.hp_images['green'] = load_image('HP_BAR/green.png')
            self.hp_images['yellow'] = load_image('HP_BAR/yellow.png')
            self.hp_images['red'] = load_image('HP_BAR/red.png')
            self.hp_images['dark_red'] = load_image('HP_BAR/dark_red.png')
            self.hp_images['white'] = load_image('HP_BAR/white.png')
        except:
            print("HP바 이미지 로드 실패")
            self.hp_images = None

        self.ai_enable = enable_ai

        # 1) 캐릭터 선택 화면
        if use_character_select and self.font is not None:
            character1_name, character2_name = self.character_select_screen()

        # 2) 맵 이미지 로드
        self.stage_images = {}
        try:
            self.stage_images['Airport'] = load_image('Background/airport_map.gif')
            self.stage_images['Korean Town'] = load_image('Background/koreanTown_map.gif')
            self.stage_images['Night Village'] = load_image('Background/night_map.gif')
            self.stage_images['Racing Circuit'] = load_image('Background/racing_map.gif')
            self.stage_images['Underpass Street'] = load_image('Background/street_map.gif')
        except:
            print("스테이지 이미지 로드 실패")
            self.stage_images = {}

        # 3) 맵 선택 화면 (캐릭터 선택 후에 실행)
        if use_stage_select and len(self.stage_images) > 0:
            self.current_stage_name = self.stage_select_screen()
        else:
            self.current_stage_name = self.stage_list[0]

        self.current_stage_image = self.stage_images.get(self.current_stage_name, None)

        # 캐릭터 생성
        self.character1 = Character(character1_name, self.width // 4, 100, character_speed,
                                    facing_right=True)
        self.character2 = Character(character2_name, self.width * 3 // 4, 100, character_speed,
                                    facing_right=False)

        if self.ai_enable:
            self.ai_controller = AIController(self.character2, self.character1)

        # 타이머
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

                if self.match_over and event.key == SDLK_SPACE:
                    self.reset_game()

                # P1
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

                # P2
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
                if event.key == SDLK_a:
                    self.character1.key_up('left')
                elif event.key == SDLK_d:
                    self.character1.key_up('right')
                elif not self.ai_enable:
                    if event.key == SDLK_LEFT:
                        self.character2.key_up('left')
                    elif event.key == SDLK_RIGHT:
                        self.character2.key_up('right')

    def update(self):
        if self.match_over:
            self.ko_time += 1
            return

        if self.stop_frames > 0:
            self.stop_frames -= 1
            return

        if self.round_end:
            self.round_end_time += 1

            self.character1.update(opponent_x=self.character2.x)
            self.character2.update(opponent_x=self.character1.x)

            if self.round_end_time >= 300:
                if self.player1_wins >= 2 or self.player2_wins >= 2:
                    self.match_over = True
                    self.game_over = True
                    self.winner = 1 if self.player1_wins >= 2 else 2
                else:
                    self.start_next_round()
            return

        if self.game_over:
            self.ko_time += 1
            return

        if self.slow_motion_frames > 0:
            self.slow_motion_frames -= 1

        current_time = time.time()
        if current_time - self.last_time_update >= 1.0:
            self.time_left -= 1
            self.last_time_update = current_time
            if self.time_left <= 0:
                self.time_left = 0
                self.end_game_by_time()

        if self.character1.dead or self.character2.dead:
            self.character1.update(opponent_x=self.character2.x)
            self.character2.update(opponent_x=self.character1.x)

            if self.character1.dead and self.character1.death_animation_finished:
                self.end_round(2)
            elif self.character2.dead and self.character2.death_animation_finished:
                self.end_round(1)
            return

        if self.ai_enable:
            self.ai_controller.update()

        self.character1.update(opponent_x=self.character2.x)
        self.character2.update(opponent_x=self.character1.x)

        self.character1.resolve_collision(self.character2)

        if self.character2.check_hit(self.character1):
            if self.character1.attacking and not self.character1.attack1_hit_applied:
                self.character2.get_hit(self.character1.attack_damage)
                self.character1.attack1_hit_applied = True
            elif self.character1.attacking2 and not self.character1.attack2_hit_applied:
                self.character2.get_hit(self.character1.attack2_damage)
                self.character1.attack2_hit_applied = True

        if self.character1.check_hit(self.character2):
            if self.character2.attacking and not self.character2.attack1_hit_applied:
                self.character1.get_hit(self.character2.attack_damage)
                self.character2.attack1_hit_applied = True
            elif self.character2.attacking2 and not self.character2.attack2_hit_applied:
                self.character1.get_hit(self.character2.attack2_damage)
                self.character2.attack2_hit_applied = True

        if self.character1.is_dead() and not self.character1.dead:
            self.trigger_ko_effect()
            self.character1.dead = True
            self.character1.frame = 0
            self.character1.frame_time = 0
            self.character1.death_animation_finished = False

        if self.character2.is_dead() and not self.character2.dead:
            self.trigger_ko_effect()
            self.character2.dead = True
            self.character2.frame = 0
            self.character2.frame_time = 0
            self.character2.death_animation_finished = False

    def trigger_ko_effect(self):
        self.stop_frames = 15
        self.slow_motion_frames = 150
        self.shake_frames = 30
        self.ko_text_frames = 90

    def end_game_by_time(self):
        if self.character1.hp > self.character2.hp:
            self.character2.dead = True
            self.character2.frame = 0
            self.character2.frame_time = 0
            self.character2.death_animation_finished = False
            self.round_winner = 1
        elif self.character2.hp > self.character1.hp:
            self.character1.dead = True
            self.character1.frame = 0
            self.character1.frame_time = 0
            self.character1.death_animation_finished = False
            self.round_winner = 2
        else:
            self.round_winner = 0
            self.end_round(0)

    def end_round(self, winner):
        self.round_end = True
        self.round_winner = winner
        self.round_end_time = 0

        if winner == 1:
            self.player1_wins += 1
        elif winner == 2:
            self.player2_wins += 1

    def start_next_round(self):
        self.round_number += 1
        self.round_end = False
        self.round_winner = None
        self.round_end_time = 0

        self.character1.hp = self.character1.max_hp
        self.character2.hp = self.character2.max_hp

        self.character1.x = self.width // 4
        self.character2.x = self.width * 3 // 4
        self.character1.y = self.character1.ground_y
        self.character2.y = self.character2.ground_y

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

        self.time_left = self.game_time
        self.last_time_update = time.time()

        self.stop_frames = 0
        self.slow_motion_frames = 0
        self.shake_frames = 0
        self.ko_text_frames = 0

    def draw_hp_bar(self, x, y, hp, max_hp, is_player1=True):
        if self.hp_images is None:
            return

        bar_width = 400
        bar_height = 30

        hp_ratio = hp / max_hp
        if hp_ratio < 0:
            hp_ratio = 0
        hp_width = int(bar_width * hp_ratio)

        if hp_ratio > 0.5:
            hp_color = 'green'
        elif hp_ratio > 0.25:
            hp_color = 'yellow'
        else:
            hp_color = 'red'

        self.hp_images['dark_red'].draw(x, y, bar_width, bar_height)

        if hp_width > 0:
            if is_player1:
                hp_x = x - bar_width // 2 + hp_width // 2
                self.hp_images[hp_color].draw(hp_x, y, hp_width, bar_height - 4)
            else:
                hp_x = x + bar_width // 2 - hp_width // 2
                self.hp_images[hp_color].draw(hp_x, y, hp_width, bar_height - 4)

        self.hp_images['white'].draw(x, y + bar_height // 2, bar_width + 4, 2)
        self.hp_images['white'].draw(x, y - bar_height // 2, bar_width + 4, 2)
        self.hp_images['white'].draw(x - bar_width // 2, y, 2, bar_height)
        self.hp_images['white'].draw(x + bar_width // 2, y, 2, bar_height)

    def draw_timer(self):
        if self.font:
            if self.time_left <= 10:
                self.font.draw(self.width // 2 - 30, 730, f'{self.time_left:02d}', (255, 0, 0))
            else:
                self.font.draw(self.width // 2 - 30, 730, f'{self.time_left:02d}', (255, 255, 255))

    def draw_round_info(self):
        if self.font:
            round_text = f'ROUND {self.round_number}'
            self.font.draw(self.width // 2 - 100, 670, round_text, (255, 255, 255))
            self.draw_win_indicators()

    def draw_win_indicators(self):
        if self.hp_images is None:
            return

        circle_size = 20
        spacing = 30

        for i in range(2):
            x = 100 + i * spacing
            y = 720
            if i < self.player1_wins:
                self.hp_images['yellow'].draw(x, y, circle_size, circle_size)
            else:
                self.hp_images['dark_red'].draw(x, y, circle_size, circle_size)

        for i in range(2):
            x = 1100 - i * spacing
            y = 720
            if i < self.player2_wins:
                self.hp_images['yellow'].draw(x, y, circle_size, circle_size)
            else:
                self.hp_images['dark_red'].draw(x, y, circle_size, circle_size)

    def draw_round_result(self):
        if self.font is None:
            return

        if self.round_winner == 1:
            msg = "PLAYER 1 WINS ROUND!"
            self.font.draw(self.width // 2 - 320, self.height // 2, msg, (255, 215, 0))
        elif self.round_winner == 2:
            msg = "PLAYER 2 WINS ROUND!"
            self.font.draw(self.width // 2 - 320, self.height // 2, msg, (255, 215, 0))
        else:
            msg = "DRAW!"
            self.font.draw(self.width // 2 - 80, self.height // 2, msg, (255, 255, 255))

    def draw_game_over(self):
        if not self.match_over or self.font is None:
            return

        if self.winner == 1:
            msg = "PLAYER 1 WINS!"
            self.font.draw(self.width // 2 - 240, self.height // 2 + 50, msg, (255, 215, 0))
        elif self.winner == 2:
            msg = "PLAYER 2 WINS!"
            self.font.draw(self.width // 2 - 240, self.height // 2 + 50, msg, (255, 215, 0))

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
            self.font.draw(self.width // 2 - 120,
                           self.height // 2 + 100,
                           "K.O.",
                           (255, 0, 0))

    def draw(self):
        clear_canvas()

        # 1) 맵(배경) 먼저
        if self.current_stage_image is not None:
            self.current_stage_image.draw(self.width // 2,
                                          self.height // 2,
                                          self.width,
                                          self.height)

        # 2) 캐릭터, HP, 메시지 등은 전부 그 뒤에 그림
        shake_x = 0
        shake_y = 0
        if self.shake_frames > 0:
            self.shake_frames -= 1
            shake_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            shake_y = random.randint(-self.shake_magnitude, self.shake_magnitude)

        if shake_x or shake_y:
            ox1, oy1 = self.character1.x, self.character1.y
            ox2, oy2 = self.character2.x, self.character2.y

            self.character1.x += shake_x
            self.character1.y += shake_y
            self.character2.x += shake_x
            self.character2.y += shake_y

            self.character1.draw()
            self.character2.draw()

            self.character1.x, self.character1.y = ox1, oy1
            self.character2.x, self.character2.y = ox2, oy2
        else:
            self.character1.draw()
            self.character2.draw()

        self.draw_hp_bar(250, 750, self.character1.hp, self.character1.max_hp, True)
        self.draw_hp_bar(950, 750, self.character2.hp, self.character2.max_hp, False)

        self.draw_timer()
        self.draw_round_info()

        if self.round_end and not self.match_over:
            self.draw_round_result()

        if self.match_over:
            self.draw_game_over()

        self.draw_ko_text()

        update_canvas()

    def reset_game(self):
        self.round_number = 1
        self.player1_wins = 0
        self.player2_wins = 0
        self.round_winner = None
        self.round_end = False
        self.round_end_time = 0
        self.match_over = False

        self.character1.hp = self.character1.max_hp
        self.character2.hp = self.character2.max_hp

        self.character1.x = self.width // 4
        self.character2.x = self.width * 3 // 4
        self.character1.y = self.character1.ground_y
        self.character2.y = self.character2.ground_y

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

        self.game_over = False
        self.winner = None
        self.ko_time = 0

        self.time_left = self.game_time
        self.last_time_update = time.time()

        self.stop_frames = 0
        self.slow_motion_frames = 0
        self.shake_frames = 0
        self.ko_text_frames = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            if self.slow_motion_frames > 0:
                delay(0.02)
            else:
                delay(0.01)

    def close(self):
        if self.ai_enable:
            self.ai_controller.cleaning()
        close_canvas()

    # ================= 선택 화면들 =================

    def character_select_screen(self):
        characters = self.character_list
        p1_index = 0
        p2_index = 1 if len(characters) > 1 else 0

        selecting_p1 = True
        running = True

        while running:
            clear_canvas()

            if self.font:
                self.font.draw(self.width // 2 - 220,
                               self.height - 150,
                               'CHARACTER SELECT',
                               (255, 255, 255))

                self.font.draw(150,
                               self.height // 2 + 80,
                               'PLAYER 1',
                               (255, 255, 0))
                self.font.draw(150,
                               self.height // 2,
                               characters[p1_index],
                               (255, 255, 255))

                self.font.draw(self.width - 350,
                               self.height // 2 + 80,
                               'PLAYER 2',
                               (0, 255, 255))
                self.font.draw(self.width - 350,
                               self.height // 2,
                               characters[p2_index],
                               (255, 255, 255))

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

                    elif e.key == SDLK_RETURN or e.key == SDLK_SPACE:
                        if selecting_p1:
                            selecting_p1 = False
                        else:
                            running = False

            delay(0.01)

        return characters[p1_index], characters[p2_index]

    def stage_select_screen(self):
        """맵 선택 화면: 썸네일 여러 개를 보여주고 방향키로 선택"""
        if len(self.stage_list) == 0:
            return None

        index = 0
        running = True
        thumb_w = 220
        thumb_h = 120

        while running:
            clear_canvas()

            n = len(self.stage_list)
            margin = 100
            step = (self.width - 2 * margin) // (n - 1) if n > 1 else 0
            center_y = self.height // 2

            for i, name in enumerate(self.stage_list):
                img = self.stage_images.get(name, None)
                cx = margin + i * step

                if img is not None:
                    img.draw(cx, center_y, thumb_w, thumb_h)

                if i == index:
                    left = cx - thumb_w // 2 - 5
                    right = cx + thumb_w // 2 + 5
                    bottom = center_y - thumb_h // 2 - 5
                    top = center_y + thumb_h // 2 + 5
                    draw_rectangle(left, bottom, right, top)

            if self.font:
                self.font.draw(self.width // 2 - 220,
                               self.height - 120,
                               'STAGE SELECT',
                               (255, 255, 255))

                selected_name = self.stage_list[index]
                self.font.draw(self.width // 2 - 150,
                               120,
                               selected_name,
                               (255, 255, 0))

                self.font.draw(50,
                               60,
                               '<- -> : 맵 변경   ENTER : 확정   ESC : 종료',
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
                    if e.key == SDLK_LEFT:
                        index = (index - 1) % len(self.stage_list)
                    elif e.key == SDLK_RIGHT:
                        index = (index + 1) % len(self.stage_list)
                    elif e.key == SDLK_RETURN or e.key == SDLK_SPACE:
                        running = False

            delay(0.01)

        return self.stage_list[index]
