from pico2d import *


class MenuManager:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.font_large = None
        self.font_medium = None
        self.font_small = None

        # 메뉴 상태
        self.menu_state = 'mode_select'  # mode_select, character_select, difficulty_select, map_select

        # 선택 사항들
        self.game_mode = None  # '1P' or '2P'
        self.player1_character = None
        self.player2_character = None
        self.ai_difficulty = 'normal'  # easy, normal, hard
        self.selected_map = 'map1'

        # 커서 위치
        self.cursor_index = 0

        # 캐릭터 선택 진행도
        self.character_select_phase = 1  # 1: P1 선택, 2: P2 선택

        # 선택 가능한 옵션들
        self.characters = ['Fighter', 'Shinobi', 'Samurai']
        self.difficulties = ['Easy', 'Normal', 'Hard']
        self.maps = ['Training Ground', 'Dojo', 'Castle']

        # 이미지들 (나중에 로드)
        self.background = None
        self.character_images = {}

    def init(self):
        open_canvas(self.width, self.height)

        # 폰트 로드
        try:
            self.font_large = load_font('ENCR10B.TTF', 80)
            self.font_medium = load_font('ENCR10B.TTF', 50)
            self.font_small = load_font('ENCR10B.TTF', 30)
        except:
            print("폰트 로드 실패")

        # 캐릭터 미리보기 이미지 로드 시도
        try:
            for char in self.characters:
                self.character_images[char] = load_image(f'{char}/Idle.png')
        except:
            print("캐릭터 이미지 로드 실패")

    def handle_events(self):
        events = get_events()

        for event in events:
            if event.type == SDL_QUIT:
                return 'quit'

            elif event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    # ESC로 이전 메뉴로
                    if self.menu_state == 'mode_select':
                        return 'quit'
                    elif self.menu_state == 'character_select':
                        if self.character_select_phase == 2:
                            self.character_select_phase = 1
                            self.player1_character = None
                            self.cursor_index = 0
                        else:
                            self.menu_state = 'mode_select'
                            self.cursor_index = 0
                    elif self.menu_state == 'difficulty_select':
                        self.menu_state = 'character_select'
                        self.character_select_phase = 2
                        self.player2_character = None
                        self.cursor_index = 0
                    elif self.menu_state == 'map_select':
                        if self.game_mode == '1P':
                            self.menu_state = 'difficulty_select'
                        else:
                            self.menu_state = 'character_select'
                            self.character_select_phase = 2
                        self.cursor_index = 0

                elif event.key == SDLK_UP or event.key == SDLK_w:
                    self.cursor_index = max(0, self.cursor_index - 1)

                elif event.key == SDLK_DOWN or event.key == SDLK_s:
                    max_index = self.get_max_cursor_index()
                    self.cursor_index = min(max_index, self.cursor_index + 1)

                elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:
                    return self.confirm_selection()

        return 'continue'

    def get_max_cursor_index(self):
        if self.menu_state == 'mode_select':
            return 1  # 1P, 2P
        elif self.menu_state == 'character_select':
            return len(self.characters) - 1
        elif self.menu_state == 'difficulty_select':
            return len(self.difficulties) - 1
        elif self.menu_state == 'map_select':
            return len(self.maps) - 1
        return 0

    def confirm_selection(self):
        if self.menu_state == 'mode_select':
            # 모드 선택
            if self.cursor_index == 0:
                self.game_mode = '1P'
            else:
                self.game_mode = '2P'
            self.menu_state = 'character_select'
            self.character_select_phase = 1
            self.cursor_index = 0

        elif self.menu_state == 'character_select':
            # 캐릭터 선택
            selected_char = self.characters[self.cursor_index]

            if self.character_select_phase == 1:
                # P1 캐릭터 선택
                self.player1_character = selected_char

                if self.game_mode == '2P':
                    # 2P 모드면 P2 캐릭터 선택으로
                    self.character_select_phase = 2
                    self.cursor_index = 0
                else:
                    # 1P 모드면 P2는 랜덤, 난이도 선택으로
                    import random
                    self.player2_character = random.choice(self.characters)
                    self.menu_state = 'difficulty_select'
                    self.cursor_index = 1  # Normal 기본 선택

            elif self.character_select_phase == 2:
                # P2 캐릭터 선택
                self.player2_character = selected_char
                self.menu_state = 'map_select'
                self.cursor_index = 0

        elif self.menu_state == 'difficulty_select':
            # 난이도 선택
            difficulty_map = {0: 'easy', 1: 'normal', 2: 'hard'}
            self.ai_difficulty = difficulty_map[self.cursor_index]
            self.menu_state = 'map_select'
            self.cursor_index = 0

        elif self.menu_state == 'map_select':
            # 맵 선택 (현재는 선택만 하고 실제로는 사용 안 함)
            self.selected_map = self.maps[self.cursor_index]
            return 'start_game'  # 게임 시작!

        return 'continue'

    def draw(self):
        clear_canvas()

        if self.menu_state == 'mode_select':
            self.draw_mode_select()
        elif self.menu_state == 'character_select':
            self.draw_character_select()
        elif self.menu_state == 'difficulty_select':
            self.draw_difficulty_select()
        elif self.menu_state == 'map_select':
            self.draw_map_select()

        update_canvas()

    def draw_mode_select(self):
        if self.font_large:
            # 제목
            self.font_large.draw(self.width // 2 - 250, 600,
                                 "SELECT MODE", (255, 255, 255))

        if self.font_medium:
            # 1P 옵션
            color1 = (255, 255, 0) if self.cursor_index == 0 else (150, 150, 150)
            self.font_medium.draw(self.width // 2 - 150, 400,
                                  "1 PLAYER (vs AI)", color1)

            # 2P 옵션
            color2 = (255, 255, 0) if self.cursor_index == 1 else (150, 150, 150)
            self.font_medium.draw(self.width // 2 - 150, 300,
                                  "2 PLAYERS", color2)

        if self.font_small:
            self.font_small.draw(self.width // 2 - 200, 100,
                                 "Arrow Keys + Enter to Select", (200, 200, 200))

    def draw_character_select(self):
        if self.font_large:
            # 제목
            if self.character_select_phase == 1:
                title = "PLAYER 1 SELECT"
            else:
                title = "PLAYER 2 SELECT"
            self.font_large.draw(self.width // 2 - 300, 650, title, (255, 255, 255))

        if self.font_medium:
            # 캐릭터 목록
            y_start = 450
            for i, char in enumerate(self.characters):
                color = (255, 255, 0) if i == self.cursor_index else (150, 150, 150)
                self.font_medium.draw(self.width // 2 - 100, y_start - i * 80,
                                      char, color)

                # 캐릭터 설명
                if i == self.cursor_index and self.font_small:
                    desc = self.get_character_description(char)
                    self.font_small.draw(self.width // 2 - 200, y_start - i * 80 - 40,
                                         desc, (200, 200, 200))

        # P1이 이미 선택했으면 표시
        if self.player1_character and self.font_small:
            self.font_small.draw(100, 100,
                                 f"P1: {self.player1_character}", (255, 215, 0))

    def draw_difficulty_select(self):
        if self.font_large:
            self.font_large.draw(self.width // 2 - 350, 600,
                                 "SELECT DIFFICULTY", (255, 255, 255))

        if self.font_medium:
            # 난이도 목록
            y_start = 400
            for i, diff in enumerate(self.difficulties):
                color = (255, 255, 0) if i == self.cursor_index else (150, 150, 150)
                self.font_medium.draw(self.width // 2 - 100, y_start - i * 80,
                                      diff, color)

                # 난이도 설명
                if i == self.cursor_index and self.font_small:
                    desc = self.get_difficulty_description(diff)
                    self.font_small.draw(self.width // 2 - 200, y_start - i * 80 - 40,
                                         desc, (200, 200, 200))

    def draw_map_select(self):
        if self.font_large:
            self.font_large.draw(self.width // 2 - 250, 600,
                                 "SELECT STAGE", (255, 255, 255))

        if self.font_medium:
            # 맵 목록
            y_start = 400
            for i, map_name in enumerate(self.maps):
                color = (255, 255, 0) if i == self.cursor_index else (150, 150, 150)
                self.font_medium.draw(self.width // 2 - 150, y_start - i * 80,
                                      map_name, color)

        if self.font_small:
            # 선택된 정보 요약
            summary = f"P1: {self.player1_character} | "
            if self.game_mode == '1P':
                summary += f"AI: {self.ai_difficulty.upper()} | "
            summary += f"P2: {self.player2_character}"
            self.font_small.draw(self.width // 2 - 300, 150, summary, (200, 200, 200))

    def get_character_description(self, char):
        descriptions = {
            'Fighter': "Balanced - ATK:10/15 SPD:3",
            'Shinobi': "Fast - ATK:8/12 SPD:4",
            'Samurai': "Power - ATK:12/18 SPD:2.5"
        }
        return descriptions.get(char, "")

    def get_difficulty_description(self, diff):
        descriptions = {
            'Easy': "For Beginners - Slow & Passive AI",
            'Normal': "Balanced Challenge",
            'Hard': "Expert - Fast & Aggressive AI"
        }
        return descriptions.get(diff, "")

    def get_selections(self):
        return {
            'game_mode': self.game_mode,
            'player1_character': self.player1_character,
            'player2_character': self.player2_character,
            'ai_difficulty': self.ai_difficulty,
            'enable_ai': self.game_mode == '1P',
            'selected_map': self.selected_map
        }

    def close(self):
        close_canvas()