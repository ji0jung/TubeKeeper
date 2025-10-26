#!/usr/bin/env python3
"""
Unit5 도메인 레이어 단위 테스트

이 모듈은 Unit5 카드 공유 시스템의 도메인 레이어 컴포넌트들을 테스트합니다.
비즈니스 로직의 정확성과 도메인 규칙 준수를 검증합니다.

테스트 대상:
- 값 객체 (Value Objects): ShareToken, ExpirationDate, ShareUrl
- 엔티티 (Entities): ShareLink
- 애그리게이트 (Aggregates): ShareLinkAggregate

테스트 범위:
- 객체 생성 및 유효성 검증
- 비즈니스 규칙 준수
- 도메인 이벤트 발생
- 만료 처리 로직

실행 방법:
    pytest tests/unit/test_domain.py -v
"""

import pytest
import uuid
from datetime import datetime, timedelta

from ...unit5_card_sharing.domain.value_objects.share_token import ShareToken
from ...unit5_card_sharing.domain.value_objects.share_url import ShareUrl
from ...unit5_card_sharing.domain.value_objects.expiration_date import ExpirationDate
from ...unit5_card_sharing.domain.entities.share_link import ShareLink
from ...unit5_card_sharing.domain.entities.share_link_aggregate import ShareLinkAggregate

class TestValueObjects:
    """값 객체 테스트 클래스"""
    
    def test_share_token_creation(self):
        """ShareToken 생성 및 유효성 테스트"""
        token_value = str(uuid.uuid4())
        token = ShareToken(token_value)
        assert token.value == token_value
    
    def test_share_token_generate(self):
        """ShareToken 자동 생성 테스트"""
        token = ShareToken.generate()
        assert len(token.value) == 36
    
    def test_share_token_invalid(self):
        """잘못된 ShareToken 생성 시 예외 발생 테스트"""
        with pytest.raises(ValueError):
            ShareToken("invalid-token")
    
    def test_expiration_date_creation(self):
        """ExpirationDate 생성 및 만료 검사 테스트"""
        expiration = ExpirationDate.create_from_now(7)
        assert not expiration.is_expired()
        
        past_date = datetime.utcnow() - timedelta(days=1)
        past_expiration = ExpirationDate(past_date)
        assert past_expiration.is_expired()

class TestEntities:
    """엔티티 테스트 클래스"""
    
    def test_share_link_creation(self):
        """ShareLink 엔티티 생성 테스트"""
        card_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        share_link = ShareLink(card_id=card_id, user_id=user_id)
        
        assert share_link.card_id == card_id
        assert share_link.user_id == user_id
        assert share_link.access_count == 0
        assert not share_link.is_expired()
    
    def test_share_link_increment_access(self):
        """ShareLink 접근 횟수 증가 테스트"""
        share_link = ShareLink(card_id=uuid.uuid4(), user_id=uuid.uuid4())
        share_link.increment_access_count()
        assert share_link.access_count == 1

class TestAggregates:
    """애그리게이트 테스트 클래스"""
    
    def test_share_link_aggregate_creation(self):
        """ShareLinkAggregate 생성 및 도메인 이벤트 테스트"""
        card_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        aggregate = ShareLinkAggregate.create(card_id, user_id)
        
        assert aggregate.share_link.card_id == card_id
        assert len(aggregate.domain_events) == 1
    
    def test_share_link_aggregate_access(self):
        """ShareLinkAggregate 접근 처리 및 이벤트 발생 테스트"""
        aggregate = ShareLinkAggregate.create(uuid.uuid4(), uuid.uuid4())
        aggregate.access("test-agent", "127.0.0.1")
        assert aggregate.share_link.access_count == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
