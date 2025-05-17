from utils.onnxocr.onnx_paddleocr import ONNXPaddleOcr
import numpy as np
import cv2 as cv
from utils.log import log
from functools import cmp_to_key
import time

# mode: bless1 bless2 strange

class My_TS:
    def __init__(self,lang='ch',father=None):
        self.lang=lang
        self.ts = ONNXPaddleOcr(use_angle_cls=False, cpu=False)
        self.res=[]
        self.forward_img = None
        self.father = father

    def ocr_one_row(self, img, box=None):
        if box is None:
            text = self.ts.text_recognizer([img])[0][0]
        else:
            x1, x2, y1, y2 = box
            text = self.ts.text_recognizer([img[y1:y2, x1:x2]])[0][0]
        return text.strip()

    def ocr_one_row_origin(self, img, box=None):
            if box is None:
                return self.ts.text_recognizer([img])[0][0]
            else:
                return self.ts.text_recognizer([img[box[2]:box[3],box[0]:box[1]]])[0][0]

    def is_edit_distance_at_most_one(self, str1, str2, ch):
        length = len(str1)
        diff_count = sum(1 for i in range(length) if str1[i] != str2[i])
        if diff_count <= 1:
            return 1
        i = 0
        j = 0
        diff_count = 0
        str2 += ch
        while i < length and j < length + 1:
            if str1[i] != str2[j]:
                diff_count += 1
                j += 1
            else:
                i += 1
                j += 1

        return diff_count <= 1
    
    def sort_text(self, text):
        def compare(item1, item2):
            x1, _, y1, _ = item1['box']
            x2, _, y2, _ = item2['box']
            if abs(y1 - y2) <= 7:
                return x1 - x2
            return y1 - y2
        text = sorted(text, key=cmp_to_key(compare))
        return text

    def merge(self, text):
        if len(text) == 0:
            return text
        text = self.sort_text(text)
        res = []
        merged = text[0]
        for i in range(1, len(text)):
            if abs(text[i]['box'][2] - merged['box'][2]) <= 10 and abs(text[i]['box'][3] - merged['box'][3]) <= 10 and abs(text[i]['box'][0] - merged['box'][1]) <= 35:
                merged['raw_text'] += text[i]['raw_text']
                merged['box'][1] = text[i]['box'][1]
            else:
                res.append(merged)
                merged = text[i]
        res.append(merged)
        return res
    
    def filter_non_white(self, image, mode=0):
        if not mode:
            return image
        hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 160])
        upper_white = np.array([180, 40, 255])
        mask = cv.inRange(hsv_image, lower_white, upper_white)
        if mode == 1:
            filtered_image = cv.bitwise_and(image, image, mask=mask)
            return filtered_image
        elif mode == 2:
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 40, 50])
            mask_black = cv.inRange(hsv_image, lower_black, upper_black)
            kernel = np.ones((5, 30), np.uint8)
            mask_black = cv.dilate(mask_black, kernel, iterations=1)
            filtered_image = cv.bitwise_and(image, image, mask=mask & mask_black)
            return filtered_image

    def forward(self, img):
        if self.forward_img is not None and self.forward_img.shape == img.shape and np.sum(np.abs(self.forward_img-img))<1e-6:
            return
        tm = time.time()
        self.forward_img = img
        self.res = []
        ocr_res = self.ts.ocrocr(img)
        for res in ocr_res:
            res = {'raw_text': res[1][0], 'box': np.array(res[0]), 'score': res[1][1]}
            res['box'] = [int(np.min(res['box'][:,0])),int(np.max(res['box'][:,0])),int(np.min(res['box'][:,1])),int(np.max(res['box'][:,1]))]
            self.res.append(res)
        self.res = self.merge(self.res)
        # time.sleep(max(0,0.5-(time.time()-tm)))

    def find_with_text(self, text=[]):
        ans = []
        for txt in text:
            for res in self.res:
                if res['raw_text'] in txt or txt in res['raw_text']:
                    print("识别到文本：",txt,"匹配文本：",self.text)
                    ans.append({'text':text, **res})
        return sorted(ans, key=lambda x: x['score'], reverse=True)

    def box_contain(self, box_out, box_in, redundancy):
        if type(redundancy) in [tuple, list]:
            r = redundancy
        else:
            r = (redundancy, redundancy)
        return box_out[0]<=box_in[0]+r[0] and box_out[1]>=box_in[1]-r[0] and box_out[2]<=box_in[2]+r[1] and box_out[3]>=box_in[3]-r[1]

    def find_with_box(self, box=None, redundancy=10, forward=0, mode=0):
        if forward and box is not None:
            self.forward(self.filter_non_white(self.father.get_screen()[box[2]:box[3],box[0]:box[1]], mode=mode))
            if box[3]==540 or box[3] == 350 and self.father.debug:
                tm = str(int(time.time()*100)%1000000)
                cv.imwrite('img/'+tm+'.jpg',self.father.screen[box[2]:box[3],box[0]:box[1]])
                cv.imwrite('img/'+tm+'w.jpg',self.filter_non_white(self.father.screen[box[2]:box[3],box[0]:box[1]], mode=mode))
        ans = []
        for res in self.res:
            if box is None:
                print(res['raw_text'], res['box'])
            elif forward == 0:
                if self.box_contain(box, res['box'], redundancy=redundancy):
                    ans.append(res)
            else:
                res['box'] = [box[0]+res['box'][0], box[0]+res['box'][1], box[2]+res['box'][2], box[2]+res['box'][3]]
                ans.append(res)
        return self.sort_text(ans)
