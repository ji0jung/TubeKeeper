import re
from dataclasses import dataclass

@dataclass(frozen=True)
class CategoryName:
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("카테고리 이름은 비어있을 수 없습니다")
        
        if len(self.value) > 10:
            raise ValueError("카테고리 이름은 10글자를 초과할 수 없습니다")
        
        if not re.match(r'^[a-zA-Z0-9가-힣_]+$', self.value):
            raise ValueError("카테고리 이름은 영어, 숫자, 한글, 밑줄(_)만 사용할 수 있습니다")
    
    def __str__(self) -> str:
        return self.value
