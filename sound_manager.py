from pico2d import *


class SoundManager:
    """게임 사운드 관리 클래스"""

    def __init__(self):
        self.sounds = {}
        self.bgm = {}
        self.current_bgm = None
        self.sound_enabled = True
        self.bgm_enabled = True

    def load_sounds(self):
        """효과음 로드"""
        try:
            # 공격 효과음
            self.sounds['punch'] = load_wav('Sound/punch.wav')  # Fighter용
            self.sounds['sword'] = load_wav('Sound/sword.wav')  # Shinobi, Samurai용

            # 라운드 효과음
            self.sounds['first_round'] = load_wav('Sound/first_round.wav')
            self.sounds['second_round'] = load_wav('Sound/second_round.wav')
            self.sounds['final_round'] = load_wav('Sound/final_round.wav')

            # 게임 효과음
            self.sounds['ko'] = load_wav('Sound/KO.wav')

            # 기본 볼륨 설정
            for sound_name, sound in self.sounds.items():
                if sound_name == 'ko':
                    sound.set_volume(15)  # KO는 15%로 더 낮게
                else:
                    sound.set_volume(64)  # 나머지는 50%

            print("효과음 로드 완료")
        except Exception as e:
            print(f"효과음 로드 실패: {e}")

    def load_bgm(self):
        """배경음악 로드"""
        try:
            # 메뉴 BGM
            self.bgm['menu'] = load_music('Sound/start_menu.wav')

            print("BGM 로드 완료")
        except Exception as e:
            print(f"BGM 로드 실패: {e}")

    def play_sound(self, sound_name):
        """효과음 재생"""
        if not self.sound_enabled:
            return

        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"효과음 '{sound_name}' 없음")

    def play_bgm(self, bgm_name, repeat=True):
        """배경음악 재생"""
        if not self.bgm_enabled:
            return

        # 현재 재생 중인 BGM 정지
        if self.current_bgm:
            self.current_bgm.stop()

        if bgm_name in self.bgm:
            self.bgm[bgm_name].set_volume(32)  # 32단계 (0~128)
            if repeat:
                self.bgm[bgm_name].repeat_play()
            else:
                self.bgm[bgm_name].play()
            self.current_bgm = self.bgm[bgm_name]
        else:
            print(f"BGM '{bgm_name}' 없음")

    def stop_bgm(self):
        """배경음악 정지"""
        if self.current_bgm:
            self.current_bgm.stop()
            self.current_bgm = None

    def pause_bgm(self):
        """배경음악 일시정지"""
        if self.current_bgm:
            self.current_bgm.pause()

    def resume_bgm(self):
        """배경음악 재개"""
        if self.current_bgm:
            self.current_bgm.resume()

    def toggle_sound(self):
        """효과음 ON/OFF"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

    def toggle_bgm(self):
        """배경음악 ON/OFF"""
        self.bgm_enabled = not self.bgm_enabled
        if not self.bgm_enabled:
            self.stop_bgm()
        return self.bgm_enabled

    def set_sound_volume(self, volume):
        """효과음 볼륨 설정 (0~100)"""
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def set_bgm_volume(self, volume):
        """BGM 볼륨 설정 (0~128)"""
        if self.current_bgm:
            self.current_bgm.set_volume(volume)


# 전역 사운드 매니저 인스턴스
sound_manager = SoundManager()