from pico2d import *

# 캔버스 크기 설정
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

class Character:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.speed = 3
        self.idle_image = load_image('Fighter/Idle.png')
        self.walk_image = load_image('Fighter/Walk.png')
        self.frame = 0
        self.idle_frame_width = self.idle_image.w // 6
        self.walk_frame_width = self.walk_image.w // 8
        self.frame_height = self.walk_image.h
        self.moving_left = False
        self.moving_right = False
        self.frame_time = 0

    def update(self):
        # 좌우 이동
        if self.moving_left:
            self.x -= self.speed
        if self.moving_right:
            self.x += self.speed

        # 화면 경계 처리
        if self.x < 0:
            self.x = 0
        elif self.x > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH

        # 프레임 업데이트
        self.frame_time += 1

        if self.moving_left or self.moving_right:
            if self.frame_time >= 8:
                self.frame = (self.frame + 1) % 8
                self.frame_time = 0
        else:
            if self.frame_time >= 8:
                self.frame = (self.frame + 1) % 6
                self.frame_time = 0

    def draw(self):
        if self.moving_left or self.moving_right:
            self.walk_image.clip_draw(self.frame * self.walk_frame_width, 0, self.walk_frame_width, self.frame_height, self.x, self.y, 200, 200)
        else:
            self.idle_image.clip_draw(self.frame * self.idle_frame_width, 0, self.idle_frame_width, self.frame_height, self.x, self.y, 200, 200)

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

def main():
    global running, character

    # 윈도우 생성
    open_canvas(WINDOW_WIDTH, WINDOW_HEIGHT)

    character = Character()

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