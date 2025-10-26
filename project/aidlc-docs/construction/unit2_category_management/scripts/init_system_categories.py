#!/usr/bin/env python3
"""
시스템 카테고리 초기화 유틸리티

Unit2 테스트를 위한 시스템 카테고리 생성기
- "공유받은카드" 시스템 카테고리 생성
- "임시" 시스템 카테고리 생성
- 테스트 환경에서 시스템 카테고리 초기화

역할:
    - create_system_categories_for_user: 사용자별 시스템 카테고리 생성
    - 시스템 카테고리 자동 생성 시뮬레이션
    - 테스트 데이터 초기 설정

사용법:
    shared_id, temp_id = create_system_categories_for_user(user_id)

참고:
    실제 운영에서는 회원가입 시 자동 생성되어야 함
"""

import sys
import os
from uuid import uuid4
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.infrastructure.database import SessionLocal
from src.infrastructure.models.category_model import CategoryModel
from src.domain.value_objects.category_type import CategoryTypeEnum

def create_system_categories_for_user(user_id: str):
    """특정 사용자를 위한 시스템 카테고리 생성"""
    db = SessionLocal()
    
    try:
        # 공유받은 카드 카테고리
        shared_category = CategoryModel(
            id=uuid4(),
            user_id=user_id,
            name="공유받은카드",
            category_type=CategoryTypeEnum.SHARED_CARDS,
            parent_id=None,
            hierarchy_level=1
        )
        
        # 임시 카테고리
        temp_category = CategoryModel(
            id=uuid4(),
            user_id=user_id,
            name="임시",
            category_type=CategoryTypeEnum.TEMPORARY,
            parent_id=None,
            hierarchy_level=1
        )
        
        db.add(shared_category)
        db.add(temp_category)
        db.commit()
        
        print(f"✅ 사용자 {user_id}의 시스템 카테고리 생성 완료")
        print(f"   - 공유받은카드: {shared_category.id}")
        print(f"   - 임시: {temp_category.id}")
        
        return shared_category.id, temp_category.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ 시스템 카테고리 생성 실패: {e}")
        return None, None
    finally:
        db.close()

if __name__ == "__main__":
    # 테스트용 사용자 ID
    test_user_id = "41693b34-c7b4-45d8-a9f2-941bf0cf54ba"
    create_system_categories_for_user(test_user_id)
