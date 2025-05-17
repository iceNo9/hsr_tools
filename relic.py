import difflib
from typing import Dict, List, Tuple, Union, Any
import re

class ValidationError(Exception):
    """自定义异常：用于无效字段值的报错"""
    def __init__(self, field: str, value: str, candidates: List[str]):
        message = (
            f"字段 '{field}' 的值 '{value}' 不在允许列表中。\n"
            f"可能想输入的是: {Relic.suggest_similar(value, candidates)}"
        )
        super().__init__(message)


class Relic:
    """
    遗器类，表示一个具备主词条、副词条、等级、编号、来源等信息的遗器。
    """

    # 支持的合法项列表（可在外部进行替换或扩展）
    valid_locations: List[str] = []
    valid_items: List[str] = []  # 合并主词条、副词条的合法词条名
    valid_sets: List[str] = []
    valid_names_by_set: Dict[str, List[str]] = {}  # 套装名 -> 有效名字列表

    def __init__(
        self,
        name: str,
        location: str,
        level: int,
        item_detail: Dict[str, Union[Dict[str, Any], List[Tuple[str, Any]]]],
        from_set: str,
        threshold: float = 0.8
    ):
        self.threshold = threshold

        if from_set:
            # 正推逻辑：先校验套装名，再校验名字是否属于该套装
            self.from_set = self._validate("from_set", from_set, self.valid_sets)
            valid_names_for_set = self.valid_names_by_set.get(self.from_set, [])
            self.name = self._validate("name", name, valid_names_for_set)
        else:
            # 未传套装名，先验证名字合法性
            all_valid_names = sum(self.valid_names_by_set.values(), [])
            self.name = self._validate("name", name, all_valid_names)

            # 然后反推套装名
            matched_sets = [
                set_name for set_name, names in self.valid_names_by_set.items()
                if self.name in names
            ]
            if len(matched_sets) == 1:
                self.from_set = matched_sets[0]
            elif len(matched_sets) > 1:
                raise ValidationError(
                    "name", name,
                    all_valid_names,
                    hint="该名字对应多个套装，请指定 from_set 参数"
                )
            else:
                raise ValidationError(
                    "name", name,
                    all_valid_names,
                    hint="该名字不属于任何已知套装"
                )

        # 继续验证其他字段
        self.location = self._validate("location", location, self.valid_locations)
        self.level = level

        # 主词条
        main_name, main_value = self._parse_single_kv(item_detail.get("main", {}))
        normalized_main = self._normalize_stat_name_by_value(main_name, main_value)
        self.main_stat = {
            "name": self._validate("item_detail.main.name", normalized_main, self.valid_items),
            "value": main_value
        }

        # 副词条
        sub_input = item_detail.get("sub", {})
        sub_stats = {}

        if isinstance(sub_input, list):
            from collections import defaultdict
            counts = defaultdict(int)

            for sub_name, sub_val in sub_input:
                normalized_sub = self._normalize_stat_name_by_value(sub_name, sub_val)
                valid_name = self._validate("item_detail.sub.name", normalized_sub, self.valid_items)

                count = counts[valid_name]
                key = f"{valid_name}#{count+1}" if count else valid_name
                sub_stats[key] = sub_val
                counts[valid_name] += 1

        elif isinstance(sub_input, dict):
            for sub_name, sub_val in sub_input.items():
                normalized_sub = self._normalize_stat_name_by_value(sub_name, sub_val)
                valid_name = self._validate("item_detail.sub.name", normalized_sub, self.valid_items)
                sub_stats[valid_name] = sub_val

        else:
            raise ValueError("item_detail.sub 必须是 dict 或 list 格式")

        self.sub_stats = sub_stats   

        self.item_number = 1 + len(self.sub_stats)  # 主词条 1 个 + 副词条数量
   
        
    def _validate(self, field: str, value: str, valid_list: List[str]) -> str:
        """
        验证字段值是否合法，使用相似度建议替换，不抛异常仅打印提示。
        仅当没有任何推荐时才抛出异常。
        """
        matches = difflib.get_close_matches(value, valid_list, n=1, cutoff=self.threshold)
        if matches:
            if matches[0] != value:
                print(f"警告: 字段 '{field}' 的值 '{value}' 无效，自动替换为最接近的合法值 '{matches[0]}'。")
            return matches[0]
        else:
            suggestions = self.suggest_similar(value, valid_list)
            if suggestions == "无推荐":
                raise ValidationError(field, value, valid_list)
            else:
                print(f"警告: 字段 '{field}' 的值 '{value}' 无效，没有完全匹配，但推荐了类似词: {suggestions}，"
                    f"默认替换为 '{suggestions.split(',')[0].strip()}'。")
                return suggestions.split(",")[0].strip()
            
    def _validate_origin(self, field: str, value: str, valid_list: List[str]) -> str:
        """
        验证字段值是否合法，并使用相似度建议替换。
        """
        matches = difflib.get_close_matches(value, valid_list, n=1, cutoff=self.threshold)
        if matches:
            return matches[0]
        else:
            raise ValidationError(field, value, valid_list)

    @staticmethod
    def suggest_similar(value: str, valid_list: List[str]) -> str:
        """提供相似词条建议"""
        suggestions = difflib.get_close_matches(value, valid_list, n=3, cutoff=0.5)
        return ", ".join(suggestions) if suggestions else "无推荐"

    @staticmethod
    def _parse_single_kv(d: Dict[str, float]) -> Tuple[str, float]:
        """从单键字典中解析键值对"""
        if len(d) != 1:
            raise ValueError("主词条 item_detail.main 必须包含一个且仅一个属性")
        return next(iter(d.items()))

    def _normalize_stat_name_by_value(self, name: str, value) -> str:
        """
        根据值是否含 '%' 判断是否为百分比词条。
        - 若值是字符串且包含 %，则尝试匹配 name + '%'
        - 否则尝试直接使用原始名称 name
        """
        if isinstance(value, str) and "%" in value:
            percent_name = f"{name}百分比"
            if percent_name in self.valid_items:
                return percent_name
        return name

    def _clean_value(self, value: str) -> str:
        """
        去除字符串中的百分号、加号、减号等特殊符号，保留数值部分。
        例如："-12.5%" -> "12.5"
        """
        if isinstance(value, str):
            # 提取数字和小数点部分
            match = re.search(r'[\d.]+', value)
            if match:
                return match.group(0)
            else:
                return ""  # 如果没有数字，返回空字符串
        return value

    def _clean_value_origin(self, value: str) -> str:
        """
        去除字符串中的百分号（用于导出），保留数值部分。
        你也可以选择转成 float 返回。
        """
        if isinstance(value, str) and "%" in value:
            return value.replace("%", "")
        return value

    def to_dict(self) -> Dict:
        """导出为字典结构，移除百分号"""
        return {
            "name": self.name,
            "location": self.location,
            "level": self._clean_value(self.level),
            "item_number": self.item_number,
            "item_detail": {
                "main": {
                    self.main_stat["name"]: self._clean_value(self.main_stat["value"])
                },
                "sub": {
                    name: self._clean_value(val) for name, val in self.sub_stats.items()
                }
            },
            "from_set": self.from_set
        }

    def __repr__(self):
        return f"<Relic {self.name} ({self.location}) Lv.{self.level} #{self.item_number}>"

# 示例使用
if __name__ == "__main__":
    from config import *

    config = RelicConfig.load_from_yaml("config/relic.yaml")
    Relic.valid_locations = config.valid_locations
    Relic.valid_items = config.valid_items
    Relic.valid_sets = config.valid_sets
    Relic.valid_names_by_set = config.set_to_names
    
    # Relic.valid_sets = ["战狂", "角斗士", "流浪大地"]
    # Relic.valid_names_by_set = {
    #     "战狂": ["K1", "K2", "K3"],
    #     "角斗士": ["圣遗物", "K2", "K3", "K4"],
    #     "流浪大地": ["K1", "K2"]
    # }   
    # Relic.valid_locations = ["头部", "身体", "脚"]
    # Relic.valid_items = ["攻击力", "攻击力%", "生命值", "生命值%", "暴击率%", "暴击伤害%", "元素精通"]

    try:
        r = Relic(
            name="英豪的赴火护胫",
            location="脚部",
            level="+15",
            item_detail={
                "main": {"攻击力": "9%"},
                "sub": {"攻击力": "4780", "暴击率": "20%"}
            },
            from_set=""
        )
        print("创建成功:", r)
        print("导出数据:", r.to_dict())

    except ValidationError as e:
        print("创建失败：", e)
