import argparse
import ctypes
import time
import threading
import sys
from pynput import keyboard

# ── 命令行参数解析 ──────────────────────────────────
parser = argparse.ArgumentParser(description="硬核连点器 (按 F8 切换)")
parser.add_argument('--cps', type=int, default=1000, help='设置每秒点击次数 (默认: 1000)')

# 使用互斥组，确保只能选择一种按键
btn_group = parser.add_mutually_exclusive_group()
btn_group.add_argument('--left',  action='store_true', help='点击鼠标左键 (默认)')
btn_group.add_argument('--mid',   action='store_true', help='点击鼠标中键 (滚轮)')
btn_group.add_argument('--right', action='store_true', help='点击鼠标右键')

args = parser.parse_args()

# 1. 处理 CPS
CPS = args.cps
if CPS <= 0:
    print("❌ 错误: CPS 必须大于 0！")
    sys.exit(1)
INTERVAL = 1.0 / CPS

# 2. 处理鼠标按键映射 (Windows API 常量)
if args.mid:
    DOWN, UP = 0x0020, 0x0040  # MIDDLEDOWN, MIDDLEUP
    BTN_NAME = "中键"
elif args.right:
    DOWN, UP = 0x0008, 0x0010  # RIGHTDOWN, RIGHTUP
    BTN_NAME = "右键"
else:
    DOWN, UP = 0x0002, 0x0004  # LEFTDOWN, LEFTUP (默认)
    BTN_NAME = "左键"
# ──────────────────────────────────────────────────

# 直接加载 Windows 底层 API
user32 = ctypes.windll.user32
clicking = False

def click_loop():
    """底层高精度点击循环"""
    while clicking:
        # 直接调用 Windows API 注入点击
        user32.mouse_event(DOWN, 0, 0, 0, 0)
        user32.mouse_event(UP, 0, 0, 0, 0)
        
        # 高精度忙等待 (Busy-wait) 保证微秒级精度
        start_time = time.perf_counter()
        while (time.perf_counter() - start_time) < INTERVAL:
            pass  

def on_press(key):
    global clicking
    if key == keyboard.Key.f8:
        clicking = not clicking
        if clicking:
            print(f"▶ 开始连点 | 目标 CPS: {CPS} | 按键: {BTN_NAME} | 间隔: {INTERVAL*1000:.3f}ms")
            t = threading.Thread(target=click_loop, daemon=True)
            t.start()
        else:
            print("■ 已停止连点")

def main():
    print("=" * 55)
    print(f"  硬核连点器已就绪 | 设定: {CPS} CPS / {BTN_NAME}")
    print("  [注意] 高 CPS 模式下会占用较高单核 CPU 资源")
    print("  F8      → 开始 / 停止")
    print("  Ctrl+C  → 退出程序")
    print("=" * 55)

    with keyboard.Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\n程序已退出")

if __name__ == "__main__":
    main()