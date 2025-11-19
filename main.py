from menu_manager import MenuManager
from game_manager import GameManager


def main():
    # 메뉴 시스템 시작
    menu = MenuManager(width=1200, height=800)
    menu.init()

    # 메뉴 루프
    while True:
        result = menu.handle_events()

        if result == 'quit':
            menu.close()
            break

        elif result == 'start_game':
            # 선택 사항 가져오기
            selections = menu.get_selections()

            # 메뉴 종료
            menu.close()

            # 게임 시작
            game = GameManager(width=1200, height=800)
            game.init(
                character1_name=selections['player1_character'],
                character2_name=selections['player2_character'],
                enable_ai=selections['enable_ai'],
                ai_difficulty=selections['ai_difficulty'],
                selected_map=selections['selected_map']
            )

            game.run()
            game.close()

            # 게임 종료 후 메뉴로 돌아가기
            menu = MenuManager(width=1200, height=800)
            menu.init()

        menu.draw()


if __name__ == '__main__':
    main()