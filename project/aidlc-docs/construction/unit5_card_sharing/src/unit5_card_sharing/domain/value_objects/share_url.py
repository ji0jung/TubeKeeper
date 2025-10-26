from dataclasses import dataclass
from .share_token import ShareToken

@dataclass(frozen=True)
class ShareUrl:
    base_url: str
    token: ShareToken
    
    def __post_init__(self):
        if not self.base_url:
            raise ValueError("Base URL cannot be empty")
    
    @property
    def full_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/shared/{self.token.value}"
    
    def __str__(self) -> str:
        return self.full_url
