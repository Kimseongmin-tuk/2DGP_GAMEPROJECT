from game_manager import GameManager

# 게임 매니저 생성
game = GameManager(width=1200, height=800)

# 게임 초기화
game.init()

# 게임 실행
game.run()

# 게임 종료
game.close()