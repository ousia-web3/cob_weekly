"""
로컬 접속 시 화면보호기/잠금 방지 (localhost:5173 대시보드 실행 시 함께 동작).
Windows에서만 F5 키를 주기적으로 시뮬레이션하여 유휴 타이머를 리셋합니다.
Ctrl+C로 종료.
"""
import sys
import time
import signal

def main():
    if sys.platform != "win32":
        print("  [keep_awake] Windows 전용 기능입니다. 다른 OS에서는 무시됩니다.")
        return
    try:
        import ctypes
    except ImportError:
        print("  [keep_awake] ctypes 사용 불가")
        return

    VK_F5 = 0x74  # F5 Virtual Key (화면보호기 제어용)
    KEYEVENTF_KEYUP = 2
    stop = [False]  # list so closure can mutate

    def on_signal(*_):
        stop[0] = True

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    print("  🛡️  화면보호기 제어 루프 시작 (F5 키 입력 시뮬레이션) — 잠기지 않음")
    try:
        while not stop[0]:
            try:
                ctypes.windll.user32.keybd_event(VK_F5, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_F5, 0, KEYEVENTF_KEYUP, 0)
            except Exception as e:
                print(f"  [Warning] Keep awake error: {e}")
            # 60초 대기 (매 1초마다 stop 확인)
            for _ in range(60):
                if stop[0]:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    print("  🛡️  화면보호기 제어 루프 종료")

if __name__ == "__main__":
    main()
