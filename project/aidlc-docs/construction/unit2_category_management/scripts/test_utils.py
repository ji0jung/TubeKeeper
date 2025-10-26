#!/usr/bin/env python3
"""
테스트 공통 유틸리티

Unit2 카테고리 관리 테스트를 위한 공통 함수들
- 테스트 데이터 정리 및 초기화
- 반복적으로 사용되는 테스트 로직
- 테스트 환경 설정 및 정리

역할:
    - cleanup_all_categories: 사용자의 모든 카테고리 삭제
    - 테스트 간 데이터 격리 보장
    - 테스트 코드 중복 제거

사용법:
    await cleanup_all_categories(client, headers, BASE_URL)
"""

import sys
import os
import httpx
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.infrastructure.database import SessionLocal
from src.infrastructure.models.category_model import CategoryModel

async def cleanup_all_categories(client: httpx.AsyncClient, headers: dict, base_url: str):
    """모든 카테고리 완전 삭제"""
    print("\n🧹 모든 카테고리 완전 삭제 중...")
    
    try:
        # DB에서 모든 카테고리 강제 삭제
        db = SessionLocal()
        deleted = db.query(CategoryModel).delete()
        db.commit()
        db.close()
        print(f"✅ 모든 카테고리 {deleted}개 삭제 완료")
        
    except Exception as e:
        print(f"❌ 카테고리 삭제 실패: {e}")

def cleanup_all_categories_sync():
    """동기 버전 - 모든 카테고리 삭제"""
    try:
        db = SessionLocal()
        deleted = db.query(CategoryModel).delete()
        db.commit()
        db.close()
        print(f"✅ 모든 카테고리 {deleted}개 삭제 완료")
    except Exception as e:
        print(f"❌ 카테고리 삭제 실패: {e}")
