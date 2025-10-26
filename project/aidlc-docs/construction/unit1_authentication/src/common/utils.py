import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4


def generate_uuid() -> UUID:
    """UUID 생성"""
    return uuid4()


def generate_verification_code() -> str:
    """6자리 인증 코드 생성"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


def create_device_fingerprint(user_agent: str, screen_resolution: str, 
                            timezone: str, language: str) -> str:
    """디바이스 핑거프린트 생성"""
    fingerprint_data = f"{user_agent}|{screen_resolution}|{timezone}|{language}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]


def utc_now() -> datetime:
    """현재 UTC 시간 반환"""
    return datetime.utcnow()


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """시간에 분 추가"""
    return dt + timedelta(minutes=minutes)


def add_days(dt: datetime, days: int) -> datetime:
    """시간에 일 추가"""
    return dt + timedelta(days=days)
