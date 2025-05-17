import pyautogui
import pygetwindow as gw
import time
import numpy as np

def switch_to_window(title):
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        print(f"没找到标题包含 '{title}' 的窗口")
        return False
    win = windows[0]
    win.activate()
    time.sleep(0.5)  # 等待窗口激活
    return True

def press_key(key, delay=0.1):
    pyautogui.keyDown(key)
    time.sleep(delay)
    pyautogui.keyUp(key)
    time.sleep(0.2)  # 按键间隔

def click_at(x, y):
    pyautogui.click(x, y)
    time.sleep(0.3)

def capture_fullscreen():
    # 直接截全屏，返回PIL图片对象
    img = pyautogui.screenshot()
    img_np = np.array(img)
    return img_np

def screenshot_fullscreen(filename="screenshot_full.png"):
    # 截取全屏
    img = pyautogui.screenshot()
    img.save(filename)
    print(f"全屏截图已保存为 {filename}")

def main():
    game_title = "你的游戏窗口标题"  # 请替换成你的游戏窗口标题
    total_equipment = 10  # 你要操作的装备数量

    if not switch_to_window(game_title):
        return

    for i in range(total_equipment):
        print(f"正在操作第 {i+1} 个装备")

        # 模拟按键切换装备（除了第一个外每次按右键）
        if i > 0:
            press_key('right')

        # 模拟点击装备（示例坐标，替换成你装备位置）
        # click_at(500, 500)

        # 等待游戏响应
        time.sleep(1)

    print("已操作完最后一个装备")

if __name__ == "__main__":
    main()
