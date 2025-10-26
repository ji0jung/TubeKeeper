import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInfo:
    """디바이스 정보 값 객체"""
    user_agent: str
    ip_address: str
    device_fingerprint: str
    
    @classmethod
    def create(cls, user_agent: str, ip_address: str, 
               screen_resolution: str, timezone: str, language: str) -> 'DeviceInfo':
        """디바이스 핑거프린트 생성으로 고유 식별"""
        fingerprint_data = f"{user_agent}|{screen_resolution}|{timezone}|{language}"
        device_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
        return cls(user_agent, ip_address, device_fingerprint)
    
    def is_same_device(self, other: 'DeviceInfo') -> bool:
        """동일 디바이스 여부 확인"""
        return self.device_fingerprint == other.device_fingerprint
