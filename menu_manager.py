from pico2d import *
from sound_manager import sound_manager


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
        self.maps = ['Airport', 'Korean Town', 'Night Street', 'Racing Track', 'City Street']

        # 이미지들 (나중에 로드)
        self.background = None
        self.character_images = {}

    def get_text_width(self, text, font_size):
        """텍스트를 중앙 정렬하기 위한 x 좌표 계산"""
        return len(text) * font_size * 0.6

    def get_centered_x(self, text, font_size):
        text_width = self.get_text_width(text, font_size)
        return int((self.width - text_width) / 2)

    def init(self):
        """메뉴 초기화"""
        open_canvas(self.width, self.height)

        # 사운드 로드 및 메뉴 BGM 재생 (반복)
        sound_manager.load_sounds()
        sound_manager.load_bgm()
        sound_manager.play_bgm('menu', repeat=True)

        # 폰트 로드
        try:
            self.font_large = load_font('Font/ENCR10B.TTF', 80)
            self.font_medium = load_font('Font/ENCR10B.TTF', 50)
            self.font_small = load_font('Font/ENCR10B.TTF', 30)
        except:
            print("폰트 로드 실패")

        # 배경 이미지 로드
        try:
            self.menu_bg = load_image('Background/menu_background.png')
            self.character_select_bg = load_image('Background/character_select_background.png')
            print("배경 이미지 로드 완료")
        except:
            print("배경 이미지 로드 실패 - 기본 배경 사용")
            self.menu_bg = None
            self.character_select_bg = None

        # 캐릭터 미리보기 이미지 로드 시도
        try:
            for char in self.characters:
                self.character_images[char] = load_image(f'{char}/Idle.png')
        except:
            print("캐릭터 이미지 로드 실패")

    def handle_events(self):
        """키 입력 처리"""
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
        """현재 메뉴의 최대 커서 인덱스"""
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
        """선택 확정"""
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
            # 맵 선택 (실제 맵 ID로 저장)
            map_ids = {
                0: 'airport_map',
                1: 'koreanTown_map',
                2: 'night_map',
                3: 'racing_map',
                4: 'street_map'
            }
            self.selected_map = map_ids[self.cursor_index]
            return 'start_game'  # 게임 시작!

        return 'continue'

    def draw(self):
        """메뉴 그리기"""
        clear_canvas()

        # 배경 그리기
        if self.menu_state in ['mode_select', 'difficulty_select', 'map_select'] and self.menu_bg:
            self.menu_bg.draw(self.width // 2, self.height // 2)
        elif self.menu_state == 'character_select' and self.character_select_bg:
            self.character_select_bg.draw(self.width // 2, self.height // 2)

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
        """모드 선택 화면"""
        if self.font_large:
            # 제목
            title = "SELECT MODE"
            x = self.get_centered_x(title, 80)
            self.font_large.draw(x, 600, title, (255, 255, 255))

        if self.font_medium:
            # 1P 옵션
            text1 = "1 PLAYER (vs AI)"
            x1 = self.get_centered_x(text1, 50)
            color1 = (255, 255, 0) if self.cursor_index == 0 else (150, 150, 150)
            self.font_medium.draw(x1, 400, text1, color1)

            # 2P 옵션
            text2 = "2 PLAYERS"
            x2 = self.get_centered_x(text2, 50)
            color2 = (255, 255, 0) if self.cursor_index == 1 else (150, 150, 150)
            self.font_medium.draw(x2, 300, text2, color2)

        if self.font_small:
            instruction = "Arrow Keys + Enter to Select"
            x_inst = self.get_centered_x(instruction, 30)
            self.font_small.draw(x_inst, 100, instruction, (200, 200, 200))

    def draw_character_select(self):
        """캐릭터 선택 화면"""
        if self.font_large:
            # 제목
            if self.character_select_phase == 1:
                title = "PLAYER 1 SELECT"
            else:
                title = "PLAYER 2 SELECT"
            x = self.get_centered_x(title, 80)
            self.font_large.draw(x, 650, title, (255, 255, 255))

        if self.font_medium:
            # 캐릭터 목록
            y_start = 450
            for i, char in enumerate(self.characters):
                color = (255, 255, 0) if i == self.cursor_index else (150, 150, 150)
                x = self.get_centered_x(char, 50)
                self.font_medium.draw(x, y_start - i * 80, char, color)

                # 캐릭터 설명
                if i == self.cursor_index and self.font_small:
                    desc = self.get_character_description(char)
                    x_desc = self.get_centered_x(desc, 30)
                    self.font_small.draw(x_desc, y_start - i * 80 - 40, desc, (200, 200, 200))

        # P1이 이미 선택했으면 표시
        if self.player1_character and self.font_small:
            p1_text = f"P1: {self.player1_character}"
            self.font_small.draw(100, 100, p1_text, (255, 215, 0))

    def draw_difficulty_select(self):
        """난이도 선택 화면"""
        if self.font_large:
            title = "SELECT DIFFICULTY"
            x = self.get_centered_x(title, 80)
            self.font_large.draw(x, 600, title, (255, 255, 255))

        if self.font_medium:
            # 난이도 목록
            y_start = 400
            for i, diff in enumerate(self.difficulties):
                color = (255, 255, 0) if i == self.cursor_index else (150, 150, 150)
                x = self.get_centered_x(diff, 50)
                self.font_medium.draw(x, y_start - i * 80, diff, color)

                # 난이도 설명
                if i == self.cursor_index and self.font_small:
                    desc = self.get_difficulty_description(diff)
                    x_desc = self.get_centered_x(desc, 30)
                    self.font_small.draw(x_desc, y_start - i * 80 - 40, desc, (200, 200, 200))

    def draw_map_select(self):
        """맵 선택 화면"""
        if self.font_large:
            title = "SELECT STAGE"
            x = self.get_centered_x(title, 80)
            self.font_large.draw(x, 600, title, (255, 255, 255))

        if self.font_medium:
            # 맵 목록
            y_start = 500
            for i, map_name in enumerate(self.maps):
                color = (255, 255, 0) if i == self.cursor_index else (150, 150, 150)
                x = self.get_centered_x(map_name, 50)
                self.font_medium.draw(x, y_start - i * 80, map_name, color)

        if self.font_small:
            # 선택된 정보 요약
            summary = f"P1: {self.player1_character} | "
            if self.game_mode == '1P':
                summary += f"AI: {self.ai_difficulty.upper()} | "
            summary += f"P2: {self.player2_character}"
            x_summary = self.get_centered_x(summary, 30)
            self.font_small.draw(x_summary, 100, summary, (200, 200, 200))

    def get_character_description(self, char):
        """캐릭터 설명"""
        descriptions = {
            'Fighter': "Balanced - ATK:10/15 SPD:3",
            'Shinobi': "Fast - ATK:8/12 SPD:4",
            'Samurai': "Power - ATK:12/18 SPD:2.5"
        }
        return descriptions.get(char, "")

    def get_difficulty_description(self, diff):
        """난이도 설명"""
        descriptions = {
            'Easy': "For Beginners - Slow & Passive AI",
            'Normal': "Balanced Challenge",
            'Hard': "Expert - Fast & Aggressive AI"
        }
        return descriptions.get(diff, "")

    def get_selections(self):
        """선택된 옵션들 반환"""
        return {
            'game_mode': self.game_mode,
            'player1_character': self.player1_character,
            'player2_character': self.player2_character,
            'ai_difficulty': self.ai_difficulty,
            'enable_ai': self.game_mode == '1P',
            'selected_map': self.selected_map
        }

    def close(self):
        """메뉴 종료"""
        close_canvas()