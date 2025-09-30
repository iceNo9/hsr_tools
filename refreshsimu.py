from collections import defaultdict
import json
from ocr import My_TS
import time
import win32api
import pyautogui
import win32gui
from mss import mss


from utils.log import log, set_debug
from utils.log import my_print as print
from utils.log import print_exc
from utils.screenshot import Screen

class RefreshSimu:
    def __init__(self):
        self.default_json_path = "data/default.json"
        self.default_json = self.load_actions(self.default_json_path)
        self.ts = My_TS(lang='ch')
        self.sct = Screen()

    def click(self, points, click=1):
        x, y = points
        # 如果是浮点数表示，则计算实际坐标
        if isinstance(x, float) and isinstance(y, float):
            win32api.SetCursorPos((x, y))
            if click:
                for _ in range(click):
                    pyautogui.click()
        else:
            raise ValueError("正在退出")
        time.sleep(0.3)

    def click_box(self, box, click=1):
        x = (box[0] + box[1]) / 2
        y = (box[2] + box[3]) / 2
        self.click((x, y), click)
        

    def click_position(self, position):
        self.click_box([position[0], position[0], position[1], position[1]])

    def clean_text(self, text, char=1):
        symbols = r"[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~—“”‘’«»„…·¿¡£¥€©®™°±÷×¶§‰]，。！？；：（）【】「」《》、￥ "
        if char:
            symbols += r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        translator = str.maketrans('', '', symbols)
        return text.translate(translator)
    
    def merge_text(self, text, char=1):
        return self.clean_text(''.join([i['raw_text'] for i in self.ts.sort_text(text)]), char)
    
    def load_actions(self, json_path):
        res = defaultdict(list)
        with open(json_path, "r", encoding="utf-8") as f:
            for i in json.load(f):
                res[i["name"]].append(i)
        return res

    def sleep(self, tm=2):
        time.sleep(tm)

    def do_action(self, action) -> int:
        if type(action) == str:
            return getattr(self, action)()
        if "text" in action:
            if "box" in action:
                box = action["box"]
            else:
                box = [0, 1920, 0, 1080]
            text = self.ts.find_with_box(box, redundancy=action.get("redundancy", 30))
            for i in text:
                if action["text"] in i["raw_text"]:
                    log.info(f"点击 {action['text']}:{i['box']}")
                    self.click_box(i["box"])
                    return 1
        elif "position" in action:
            log.info(f"点击 {action['position']}")
            self.click_position(action["position"])
            return 1
        elif "sleep" in action:
            self.sleep(action["sleep"])
            return 1
        elif "press" in action:
            # self.press(action["press"], action["time"] if "time" in action else 0)
            return 1
        return 0
    
    def run_static(self, json_path=None, json_file=None, action_list=[], skip_check=0) -> str:
        if json_file is None:
            if json_path is None:
                json_file = self.default_json
            else:
                json_file = self.load_actions(json_path)
        for j in action_list if len(action_list) else json_file:
            for i in json_file[j]:
                trigger = i["trigger"]
                text = self.ts.find_with_box(trigger["box"], redundancy=trigger.get("redundancy", 30))
                if skip_check or (len(text) and trigger["text"] in self.merge_text(text)):
                    log.info(f"触发 {i['name']}:{trigger['text']}")
                    for j in i["actions"]:
                        self.do_action(j)
                    self.action_history.append(i["name"])
                    self.action_history = self.action_history[-10:]
                    return i['name']
        return ''
    
    def get_screen(self):
        hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
        Text = win32gui.GetWindowText(hwnd)
        while Text != "崩坏：星穹铁道" and Text != "云·星穹铁道" and not self._stop:
            log.warning("等待游戏窗口")
            time.sleep(0.5)
            hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
            Text = win32gui.GetWindowText(hwnd)
        self.screen = self.sct.grab(self.x0, self.y0)
        return self.screen
    
    def loop(self):
            self.ts.forward(self.get_screen())
            # self.ts.find_with_box()
            # exit()
            res = self.run_static()
            # self.click_target("imgs/c.jpg", threshold=0.9, flag=False)
            if res == '':
                area_text = self.clean_text(self.ts.ocr_one_row(self.screen, [50, 350, 3, 35]), char=0)
                if '位面' in area_text or '区域' in area_text or '第' in area_text:
                    self.area()
                    self.last_action_time = time.time()

                elif self.check("c", 0.988, 0.1028, threshold=0.925):
                    # 未检查到自动战斗,已经入站,清除秘技持续
                    self.da_hei_ta_effecting = False
                    self.press('v')
                else:
                    text = self.merge_text(self.ts.find_with_box([400, 1920, 100, 600], redundancy=0))
                    if self.speed and '转化' in text and '继续战斗' not in text and ('数据' in text or '过量' in text):
                        print('ready to stop')
                        time.sleep(6)
                        tm = time.time()
                        while time.time() - tm < 15:
                            print('trying to stop')
                            self.press('esc')
                            time.sleep(2)
                            self.ts.forward(self.get_screen())
                            static_res = self.run_static(action_list=['过量转化'])
                            if static_res != '':
                                print(static_res)
                                break
                    else:
                        if time.time() - self.last_action_time > 60:
                            self.click((0.5, 0.1))
                            self.click((0.5, 0.25))
                            self.last_action_time = time.time()
            else:
                self.last_action_time = time.time()
            if self.end and res == '加载界面':
                self.press('esc')
                time.sleep(2)
                self.press('esc')
                self._stop = True