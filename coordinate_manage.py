import yaml
import json
from typing import Tuple, Dict

class Box:
    """
    单个坐标区域对象，包含名称、分辨率、起止坐标。
    """

    def __init__(self, name: str, resolution: Tuple[int, int], position_start: Tuple[int, int], position_end: Tuple[int, int]):
        """
        初始化 Box 对象。

        :param name: 区域名称
        :param resolution: 坐标对应的原始分辨率，例如 (1920, 1080)
        :param position_start: 区域起始点坐标 (x, y)
        :param position_end: 区域终点坐标 (x, y)
        """
        self.name = name
        self.resolution = resolution
        self.position_start = position_start
        self.position_end = position_end

    def format_output(self) -> Tuple[int, int, int, int]:
        """
        返回格式化坐标，输出为 [x1, x2, y1, y2]，并保证 x1 < x2，y1 < y2。
        """
        x1, y1 = self.position_start
        x2, y2 = self.position_end
        return (min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2))

    def to_dict(self) -> Dict:
        """
        将 Box 转为可序列化的字典格式，用于保存到 JSON 或 YAML。
        这里将所有 tuple 转为 list，避免导出带有 !!python/tuple 标签。
        """
        return {
            "name": self.name,
            "resolution": list(self.resolution),
            "position_start": list(self.position_start),
            "position_end": list(self.position_end)
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Box':
        """
        从字典创建一个 Box 对象，通常用于从 JSON/YAML 恢复。
        这里将列表转换回元组。
        """
        return Box(
            name=data["name"],
            resolution=tuple(data["resolution"]),
            position_start=tuple(data["position_start"]),
            position_end=tuple(data["position_end"])
        )
    
class BoxManager:
    """
    坐标管理类，统一管理多个 Box 区域，并提供导入导出功能。
    """

    def __init__(self, resolution: Tuple[int, int]):
        """
        初始化 BoxManager。

        :param resolution: 当前使用的基准分辨率（目标分辨率）
        """
        self.resolution = resolution
        self.box_list: Dict[str, Box] = {}  # 存储多个 Box 对象，键为 box.name

    def add_box(self, box: Box):
        """
        向管理器中添加一个 Box 对象。

        :param box: Box 实例
        """
        self.box_list[box.name] = box
    
    def export_to_yaml(self, filepath: str):
        data = {
            "resolution": list(self.resolution),  # 转成 list
            "boxes": {name: box.to_dict() for name, box in self.box_list.items()}
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def import_from_yaml(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        self.resolution = tuple(data["resolution"])  # 转回 tuple
        self.box_list = {
            name: Box.from_dict(box_data)
            for name, box_data in data["boxes"].items()
        }

    def export_to_json(self, filepath: str):
        """
        将所有 Box 区域导出为 JSON 文件。

        :param filepath: 保存的文件路径
        """
        data = {
            "resolution": self.resolution,
            "boxes": {name: box.to_dict() for name, box in self.box_list.items()}
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def import_from_json(self, filepath: str):
        """
        从 JSON 文件导入所有 Box 区域，并设置分辨率。

        :param filepath: JSON 文件路径
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.resolution = tuple(data["resolution"])
        self.box_list = {
            name: Box.from_dict(box_data)
            for name, box_data in data["boxes"].items()
        }

    def format_box_scaled(self, name: str) -> Tuple[int, int, int, int]:
        """
        返回指定名称 Box 的缩放坐标，按照当前管理器分辨率进行等比缩放。

        :param name: Box 名称
        :return: 缩放后的坐标 [x1, x2, y1, y2]
        """
        if name not in self.box_list:
            raise ValueError(f"Box '{name}' not found.")

        box = self.box_list[name]
        box_x1, box_x2, box_y1, box_y2 = box.format_output()

        # 计算缩放因子（目标分辨率 / Box 原始分辨率）
        scale_x = self.resolution[0] / box.resolution[0]
        scale_y = self.resolution[1] / box.resolution[1]

        # 返回等比缩放后的坐标
        return (
            int(box_x1 * scale_x),
            int(box_x2 * scale_x),
            int(box_y1 * scale_y),
            int(box_y2 * scale_y)
        )
    
    def to_dict(self) -> Dict:
        return {
            "resolution": list(self.resolution),  # 转成列表
            "boxes": {name: box.to_dict() for name, box in self.box_list.items()}
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'BoxManager':
        manager = BoxManager(resolution=tuple(data["resolution"]))
        for name, box_data in data["boxes"].items():
            manager.box_list[name] = Box.from_dict(box_data)
        return manager

if __name__ == "__main__":
    # 创建一个 Box 区域，原始分辨率是 1280x720
    

    # 初始化一个管理器，目标分辨率是 1920x1080
    manager = BoxManager(resolution=(1920, 1080))

    box = Box(
        name="relic_name",
        resolution=(1920, 1080),
        position_start=(1400, 130),
        position_end=(1650, 160)
    )
    manager.add_box(box)

    box = Box(
        name="relic_location",
        resolution=(1920, 1080),
        position_start=(1410, 280),
        position_end=(1500, 310)
    )
    manager.add_box(box)

    box = Box(
        name="relic_level",
        resolution=(1920, 1080),
        position_start=(1410, 311),
        position_end=(1500, 345)
    )
    manager.add_box(box)

    box = Box(
        name="relic_main_name",
        resolution=(1920, 1080),
        position_start=(1440, 395),
        position_end=(1700, 433)
    )
    manager.add_box(box)

    box = Box(
        name="relic_main_value",
        resolution=(1920, 1080),
        position_start=(1701, 395),
        position_end=(1842, 433)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub1_name",
        resolution=(1920, 1080),
        position_start=(1440, 439),
        position_end=(1700, 477)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub1_value",
        resolution=(1920, 1080),
        position_start=(1701, 439),
        position_end=(1842, 477)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub2_name",
        resolution=(1920, 1080),
        position_start=(1440, 478),
        position_end=(1700, 515)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub2_value",
        resolution=(1920, 1080),
        position_start=(1701, 478),
        position_end=(1842, 515)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub3_name",
        resolution=(1920, 1080),
        position_start=(1440, 516),
        position_end=(1700, 553)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub3_value",
        resolution=(1920, 1080),
        position_start=(1701, 516),
        position_end=(1842, 553)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub4_name",
        resolution=(1920, 1080),
        position_start=(1440, 554),
        position_end=(1700, 591)
    )
    manager.add_box(box)

    box = Box(
        name="relic_sub4_value",
        resolution=(1920, 1080),
        position_start=(1701, 554),
        position_end=(1842, 591)
    )
    manager.add_box(box)

    box = Box(
        name="backpack_type",
        resolution=(1920, 1080),
        position_start=(100, 65),
        position_end=(210, 95)
    )
    manager.add_box(box)

    box = Box(
        name="relic_area",
        resolution=(1920, 1080),
        position_start=(127, 200),
        position_end=(1250, 940)
    )
    manager.add_box(box)


    # 打印缩放后的坐标
    # print("Scaled output:", manager.format_box_scaled("example"))

    # 导出
    manager.export_to_yaml("boxes.yaml")

    # 从文件读取到新的管理器对象
    new_manager = BoxManager(resolution=(1, 1))  # 初始分辨率会被文件内容覆盖
    # new_manager.import_from_json("boxes.json")

    # 再次打印缩放后的坐标，验证数据一致性
    # print("Imported scaled output:", new_manager.format_box_scaled("example"))
