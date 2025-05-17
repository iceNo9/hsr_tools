import yaml
from typing import List, Dict, Tuple

class RelicConfig:
    def __init__(
        self,
        valid_locations: List[str],
        valid_items: List[str],
        valid_sets: List[str],
        set_to_names: Dict[str, List[str]]
    ):
        self.valid_locations = valid_locations
        self.valid_items = valid_items
        self.valid_sets = valid_sets
        self.set_to_names = set_to_names

    @classmethod
    def load_from_yaml(cls, filepath: str) -> 'RelicConfig':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        relic_data = data.get('Relic', {})
        return cls(
            valid_sets=relic_data.get('valid_sets', []),
            set_to_names=relic_data.get('set_to_names', {}),
            valid_locations=relic_data.get('valid_locations', []),
            valid_items=relic_data.get('valid_items', [])
        )

    def save_to_yaml(self, filepath: str):
        data = {
            'Relic': {
                'valid_sets': self.valid_sets,
                'set_to_names': self.set_to_names,
                'valid_locations': self.valid_locations,
                'valid_items': self.valid_items,
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)


# 简单示例用法：
if __name__ == "__main__":
    # 加载配置
    config = RelicConfig.load_from_yaml("config/relic.yaml")

    # 修改配置示例

    # 保存回文件
    config.save_to_yaml("config.yaml")
