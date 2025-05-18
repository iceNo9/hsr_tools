import cv2
import numpy as np

import cv2
import numpy as np

import cv2
import numpy as np

def find_dark_background_mask_3ch(img, rgb_threshold=55, min_area=0, max_area=1500, min_aspect=1.5):
    """
    提取深色背景的掩码（数字背景），去除图标等零散或不规则区域，返回三通道掩码图。
    
    参数说明：
    - rgb_threshold：RGB阈值
    - min_area：最小有效面积
    - max_area：最大有效面积
    - min_aspect：最小长宽比（长边 / 短边）
    """
    # 1. 提取暗色区域：RGB三个通道都小于阈值
    mask = cv2.inRange(img, np.array([0, 0, 0]), np.array([rgb_threshold]*3))

    # 2. 闭运算：填补小孔
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 3. 找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_mask = np.zeros_like(mask)

    for cnt in contours:
        # area = cv2.contourArea(cnt)
        # if area < min_area or area > max_area:
        #     continue

        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = max(w / h, h / w)

        # 判断形状是否“细长”，排除接近正方形或扁平图标
        if aspect_ratio < min_aspect:
            continue

        # 填充保留的轮廓
        cv2.drawContours(filtered_mask, [cnt], -1, color=255, thickness=-1)

    # 4. 转为三通道 BGR 格式
    mask_3ch = cv2.cvtColor(filtered_mask, cv2.COLOR_GRAY2BGR)
    return mask_3ch


def find_dark_background_mask_3ch_origin(img, rgb_threshold=55):
    """
    找出图像中RGB都小于阈值的暗区域掩码，返回三通道掩码图。

    适合背景深色的数字定位。

    返回三通道掩码图（0或255，3通道BGR格式）。
    """
    # 生成单通道掩码，只保留所有通道值 <= rgb_threshold 的区域
    mask = cv2.inRange(img, np.array([0,0,0]), np.array([rgb_threshold]*3))

    # 形态学闭运算，填补小孔，连通区域更完整
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 转成三通道，方便后续与原图合并显示等操作
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # 绘制图像
    # img_show = img.copy()
    # img_show[mask == 0] = (0, 0, 255)  # 将掩码区域设为红色
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return mask_3ch


def draw_boxes(img, boxes):
    import cv2
    import numpy as np

    img_show = img.copy()
    for box_tuple in boxes:
        points, _ = box_tuple  # 解包得到坐标点列表
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(img_show, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    return img_show

def draw_boxes2(img, boxes, color=(0,255,0), thickness=2):
    img_draw = img.copy()
    for box in boxes:
        x1,y1,x2,y2 = box
        cv2.rectangle(img_draw, (x1,y1), (x2,y2), color, thickness)
    return img_draw

if __name__ == "__main__":
    img_path = "你的装备截图.png"
    img = cv2.imread(img_path)

    boxes, mask = find_dark_background_regions(img, rgb_threshold=50)

    print(f"检测到 {len(boxes)} 个暗背景区域候选")

    cv2.imshow("原图", img)
    cv2.imshow("暗背景掩码", mask)
    img_boxes = draw_boxes(img, boxes)
    cv2.imshow("候选框", img_boxes)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
