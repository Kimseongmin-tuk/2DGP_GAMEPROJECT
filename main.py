from pico2d import *

# 캔버스 크기 설정
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

def update():
    pass

def draw():
    clear_canvas()
    # 여기에 그리기 코드를 추가하세요
    update_canvas()

def main():
    global running

    # 윈도우 생성
    open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)

    running = True

    # 게임 루프
    while running:
        handle_events()
        update()
        draw()
        delay(0.01)  # 프레임 딜레이 (약 100 FPS)

    # 종료
    close_canvas()

if __name__ == '__main__':
    main()