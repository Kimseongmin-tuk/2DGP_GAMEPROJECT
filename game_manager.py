from pico2d import *
from character import Character

class GameManager:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.running = False
        self.character = None

    def init(self, character_name='Fighter', character_x=None, character_y=None, character_speed=3):
        # 윈도우 생성
        open_canvas(self.width, self.height)

        # 캐릭터 초기 위치 설정
        if character_x is None:
            character_x = self.width // 2
        if character_y is None:
            character_y = self.height // 2

        # 캐릭터 생성
        self.character = Character(character_name, character_x, character_y, character_speed)

        self.running = True

    def handle_events(self):
        events = get_events()

        for event in events:
            if event.type == SDL_QUIT:
                self.running = False
            elif event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    self.running = False
                elif event.key == SDLK_a:
                    self.character.moving_left = True
                elif event.key == SDLK_d:
                    self.character.moving_right = True
                elif event.key == SDLK_f:
                    self.character.attack()
                elif event.key == SDLK_g:
                    self.character.attack2()
            elif event.type == SDL_KEYUP:
                if event.key == SDLK_a:
                    self.character.moving_left = False
                elif event.key == SDLK_d:
                    self.character.moving_right = False

    def update(self):
        self.character.update()

    def draw(self):
        clear_canvas()
        self.character.draw()
        update_canvas()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            delay(0.01)  # 프레임 딜레이 (약 100 FPS)

    def close(self):
        close_canvas()