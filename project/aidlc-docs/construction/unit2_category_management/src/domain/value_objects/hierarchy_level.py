from dataclasses import dataclass

@dataclass(frozen=True)
class HierarchyLevel:
    value: int
    
    def __post_init__(self):
        if self.value < 1 or self.value > 3:
            raise ValueError("카테고리 계층은 1~3 레벨만 허용됩니다")
    
    def is_root_level(self) -> bool:
        return self.value == 1
    
    def is_max_level(self) -> bool:
        return self.value == 3
    
    def next_level(self):
        if self.is_max_level():
            raise ValueError("최대 계층 레벨에서는 하위 레벨을 생성할 수 없습니다")
        return HierarchyLevel(self.value + 1)
