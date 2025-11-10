from pico2d import *
from character import Character

# 캔버스 크기 설정
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


def handle_events():
    global running, character
    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            elif event.key == SDLK_a:
                character.moving_left = True
            elif event.key == SDLK_d:
                character.moving_right = True
            elif event.key == SDLK_f:
                character.attack()
            elif event.key == SDLK_g:
                character.attack2()
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_a:
                character.moving_left = False
            elif event.key == SDLK_d:
                character.moving_right = False


def update():
    character.update()


def draw():
    clear_canvas()
    character.draw()
    update_canvas()

global running, character

# 윈도우 생성
open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)

# 캐릭터 생성 - 원하는 캐릭터 이름을 입력
# 'Fighter', 'Shinobi', 'Samurai' 중 선택 가능
character = Character('Shinobi', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, speed=3)

running = True

# 게임 루프
while running:
    handle_events()
    update()
    draw()
    delay(0.01)  # 프레임 딜레이 (약 100 FPS)

# 종료
close_canvas()