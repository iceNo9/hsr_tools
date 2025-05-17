from ocr import *
from coordinate_manage import *
from relic import *
from config import *
from simulation import *
import cv2


def preprocess_image(img, mode=1):
    """
    对图像进行增强处理，并确保返回的是三通道图像。
    mode:
        0 - 原图
        1 - 灰度 + 二值化 + 转BGR
        2 - 灰度 + 自适应阈值 + 转BGR
        3 - 模糊降噪 + 二值化 + 转BGR
    """
    if mode == 0:
        return img  # 原图，三通道

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    if mode == 1:
        # 简单阈值处理
        _, binary = cv.threshold(gray, 150, 255, cv.THRESH_BINARY)
    elif mode == 2:
        # 自适应阈值（适用于光照不均）
        binary = cv.adaptiveThreshold(
            gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2
        )
    elif mode == 3:
        # 去噪+二值化
        blurred = cv.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    else:
        binary = gray

    # 转回 BGR 三通道，适配 OCR 模型输入
    binary_bgr = cv.cvtColor(binary, cv.COLOR_GRAY2BGR)
    return binary_bgr

def ocr_test(manager, img):
   
    # Initialize the OCR model
    ocr_model = My_TS(lang='ch')
    
    # Load an image
    img_path = 'test4.png'
    # img = cv2.imread(img_path)
    
    box = manager.format_box_scaled("relic_area")

    # Perform OCR on the image
    result = ocr_model.ocr_one_row(img)
    
    # Print the OCR result
    print("OCR Result:", result)
    

def parse(manager, ocr_model, img):

    # 识别名字
    box = manager.format_box_scaled("relic_name")
    name = ocr_model.ocr_one_row(img, box)

    # 识别位置
    box = manager.format_box_scaled("relic_location")
    location = ocr_model.ocr_one_row(img, box)

    # 识别等级
    box = manager.format_box_scaled("relic_level")
    level = ocr_model.ocr_one_row(img, box)

    # 识别主词条
    box = manager.format_box_scaled("relic_main_name")
    main_name = ocr_model.ocr_one_row(img, box)

    # 识别主词条数值
    box = manager.format_box_scaled("relic_main_value")
    main_value = ocr_model.ocr_one_row(img, box)

    # 识别副词条1
    box = manager.format_box_scaled("relic_sub1_name")
    sub1_name = ocr_model.ocr_one_row(img, box)

    # 识别副词条1数值
    box = manager.format_box_scaled("relic_sub1_value")
    sub1_value = ocr_model.ocr_one_row(img, box)

    # 识别副词条2
    box = manager.format_box_scaled("relic_sub2_name")
    sub2_name = ocr_model.ocr_one_row(img, box)

    # 识别副词条2数值
    box = manager.format_box_scaled("relic_sub2_value")
    sub2_value = ocr_model.ocr_one_row(img, box)

    # 识别副词条3
    box = manager.format_box_scaled("relic_sub3_name")
    sub3_name = ocr_model.ocr_one_row(img, box)

    # 识别副词条3数值
    box = manager.format_box_scaled("relic_sub3_value")
    sub3_value = ocr_model.ocr_one_row(img, box)

    # 识别副词条4数值
    box = manager.format_box_scaled("relic_sub4_value")
    sub4_value = ocr_model.ocr_one_row(img, box)
    # 如果不存在副词条4数值，则不再识别副词条4
    if sub4_value == "":
        sub4_name = ""
    else:
        box = manager.format_box_scaled("relic_sub4_name")
        sub4_name = ocr_model.ocr_one_row(img, box)

    subs = [
        (sub1_name, sub1_value),
        (sub2_name, sub2_value),
        (sub3_name, sub3_value),
        (sub4_name, sub4_value),
    ]

    # 过滤掉副词条名或值是空字符串的条目
    subs = [(n, v) for n, v in subs if n != "" and v != ""]

    # 组合Relic对象
    relic = Relic(
        name=name,
        location=location,
        level=level,
        item_detail={
            "main": {
                main_name: main_value,
            },
            "sub": subs,
        },
        from_set="",
    )

    return relic

def enter_relic(manager, ocr_model):
    # 切换到游戏窗口
    switch_to_window("崩坏：星穹铁道")

    # 进入背包
    press_key('b', delay=1)

    # 循环按E,OCR识别backpack_type区域数值和"遗器"相似度高为止,使用截图capture_fullscreen
    while True:
        # 截取全屏
        img = capture_fullscreen()

        # 识别背包类型
        box = manager.format_box_scaled("backpack_type")
        backpack_type = ocr_model.ocr_one_row(img, box)

        # 判断是否为遗器
        if backpack_type == "遗器":
            break

        # 按E键切换到下一个背包类型
        press_key('e', delay=1)

    # 进入遗器界面
    print("已进入遗器界面")

def traversal_ralic(manager, ocr_model):

    # 进入遗器界面
    # enter_relic(manager, ocr_model)

    # 循环按E,遍历遗器,如果连续三次识别结果和上次相同则停止
    last_relic = None
    count = 0
    relics = []

    switch_to_window("崩坏：星穹铁道")
    while True:
        # 截取全屏
        img = capture_fullscreen()

        # 识别遗器
        relic = parse(manager, ocr_model, img)
        if last_relic and last_relic.to_dict() == relic.to_dict():
            count += 1
            if count >= 3:
                print("已遍历完所有遗器")
                break
        else:
            count = 0
            relics.append(relic)

        # 打印识别结果
        print(relic.to_dict())
        last_relic = relic

        # 按D键切换到下一个遗器
        press_key('d')

    # 保存数据到文件，确保中文正常显示
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump([relic.to_dict() for relic in relics], f, indent=4, ensure_ascii=False)




if __name__ == "__main__":
    # 初始化 Box 管理器并导入定义好的 boxes.json
    manager = BoxManager(resolution=(1920, 1080))
    manager.import_from_yaml("boxes.yaml")

    # 初始化配置
    config = RelicConfig.load_from_yaml("config/relic.yaml")

    # 初始化遗器依赖参数
    Relic.valid_locations = config.valid_locations
    Relic.valid_items = config.valid_items
    Relic.valid_sets = config.valid_sets
    Relic.valid_names_by_set = config.set_to_names
    
    # 初始化 OCR 模型
    ocr_model = My_TS(lang='ch')
    # traversal_ralic(manager, ocr_model)
    
    # 读取图像
    # 转为灰度图
    img = cv.imread('test4.png')  # 替换为你的图片路径
    # x1, y1, x2, y2 = 130, 310, 245, 335,
    x1, y1, x2, y2 = 127, 200, 1250, 940,
    roi = img[y1:y2, x1:x2]  # 注意：先 y 后 x（行列顺序）

    img_ret = preprocess_image(roi, mode=3)

    # 显示图像
    cv.imshow("Original", img)
    cv.imshow("Process", img_ret)

    ocr_test(manager, img_ret)

    # 等待按键关闭
    cv.waitKey(0)
    cv.destroyAllWindows()

    # result = parse(manager, ocr_model, img)
    # print(result.to_dict())


    # # 遍历每一个 box，进行 OCR 识别
    # for box_name, box in manager.box_list.items():
    #     scaled_box = manager.format_box_scaled(box_name)
    #     result = ocr_model.ocr_one_row(img, scaled_box)
    #     print(f"区域[{box_name}] OCR结果:{result}")

