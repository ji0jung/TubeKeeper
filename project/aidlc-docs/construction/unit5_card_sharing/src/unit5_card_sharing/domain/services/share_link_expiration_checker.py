from datetime import datetime
from ..entities.share_link import ShareLink

class ShareLinkExpirationChecker:
    @staticmethod
    def is_expired(share_link: ShareLink) -> bool:
        return share_link.expires_at.is_expired()
    
    @staticmethod
    def validate_not_expired(share_link: ShareLink) -> None:
        if ShareLinkExpirationChecker.is_expired(share_link):
            raise ValueError("Share link has expired")
