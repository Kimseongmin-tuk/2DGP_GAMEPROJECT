from pico2d import *
from character import Character

class GameManager:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.running = False
        self.character1 = None
        self.character2 = None

    def init(self, character1_name='Fighter', character2_name = 'Samurai', character_speed=3):
        # 윈도우 생성
        open_canvas(self.width, self.height)

        # 캐릭터 초기 위치 설정
        self.character1 = Character(character1_name, self.width // 4, self.height // 2, character_speed, facing_right=True)
        self.character2 = Character(character2_name, self.width * 3 // 4, self.height // 2, character_speed, facing_right=False)

        self.running = True

    def handle_events(self):
        events = get_events()

        for event in events:
            if event.type == SDL_QUIT:
                self.running = False
            elif event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    self.running = False

                # 플레이어1
                elif event.key == SDLK_a:
                    # 더블탭 감지를 위해 key_down 메서드 호출
                    self.character1.key_down('left')
                elif event.key == SDLK_d:
                    # 더블탭 감지를 위해 key_down 메서드 호출
                    self.character1.key_down('right')
                elif event.key == SDLK_f:
                    self.character1.attack()
                elif event.key == SDLK_g:
                    self.character1.attack2()
                elif event.key == SDLK_w:
                    self.character1.jump()

                # 플레이어2
                elif event.key == SDLK_LEFT:
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

                #플레이어2
                elif event.key == SDLK_LEFT:
                    self.character2.key_up('left')
                elif event.key == SDLK_RIGHT:
                    self.character2.key_up('right')

    def update(self):
        self.character1.update(opponent_x = self.character2.x)
        self.character2.update(opponent_x = self.character1.x)

        # 캐릭터 충돌 처리
        self.character1.resolve_collision(self.character2)

        # 플레이어2가 플레이어1을 공격했는지 확인
        if self.character2.check_hit(self.character1):
            self.character2.get_hit()

        # 플레이어1이 플레이어2를 공격했는지 확인
        if self.character1.check_hit(self.character2):
            self.character1.get_hit()

    def draw(self):
        clear_canvas()
        self.character1.draw()
        self.character2.draw()
        update_canvas()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            delay(0.01)  # 프레임 딜레이 (약 100 FPS)

    def close(self):
        close_canvas()