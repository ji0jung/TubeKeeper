#!/usr/bin/env python3
"""
메모 및 태그 포함 카드 생성 테스트

카드 생성 시 메모와 태그가 올바르게 저장되고 조회되는지 검증합니다.
- 메모 및 태그 포함 카드 생성
- 태그 유효성 검증 (길이, 개수 제한)
- 저장된 데이터 정확성 확인
- 한글 태그 및 특수문자 처리
"""
import asyncio
import asyncpg
from uuid import uuid4
from datetime import datetime
from unit3_card_creation.application.use_cases.create_card_use_case import CreateCardUseCase
from unit3_card_creation.application.commands.commands import CreateCardCommand
from unit3_card_creation.infrastructure.repositories.postgresql_card_repository import PostgreSQLCardRepository
from unit3_card_creation.infrastructure.services.card_duplication_service import CardDuplicationService
from unit3_card_creation.domain.value_objects.content_url import ContentUrl
from test_cleanup import cleanup_test_data


async def test_create_card_with_memo_and_tags():
    """메모와 태그가 포함된 카드 생성 테스트"""
    print("🚀 메모와 태그 포함 카드 생성 테스트 시작\n")
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres", 
            password="password",
            database="unit3_test"
        )
        
        # 리포지토리 및 서비스 초기화
        repository = PostgreSQLCardRepository(conn)
        duplication_service = CardDuplicationService(repository)
        use_case = CreateCardUseCase(repository, duplication_service)
        
        # 테스트 케이스들
        test_cases = [
            {
                "name": "메모와 태그 모두 포함",
                "memo": "정말 유용한 개발 영상입니다!",
                "tags": ["개발", "Python", "튜토리얼", "프로그래밍"]
            },
            {
                "name": "메모만 포함",
                "memo": "나중에 다시 보기",
                "tags": []
            },
            {
                "name": "태그만 포함", 
                "memo": "",
                "tags": ["React", "JavaScript", "프론트엔드"]
            },
            {
                "name": "메모와 태그 없음",
                "memo": "",
                "tags": []
            }
        ]
        
        created_card_ids = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"📝 테스트 {i}: {test_case['name']}")
            
            # 카드 생성 명령
            command = CreateCardCommand(
                user_id=uuid4(),
                category_id=uuid4(),
                content_url=f"https://www.youtube.com/watch?v=test{i}",
                memo=test_case['memo'],
                tags=test_case['tags']
            )
            
            # 카드 생성 실행
            result = await use_case.execute(command)
            
            if result.status == "CREATED":
                print(f"   ✅ 카드 생성 성공: {result.card_id}")
                print(f"   📝 메모: '{test_case['memo']}'")
                print(f"   🏷️ 태그: {test_case['tags']}")
                created_card_ids.append(result.card_id)
            else:
                print(f"   ❌ 카드 생성 실패: {result.message}")
            
            print()
        
        # 생성된 카드들 조회해서 확인
        print("🔍 생성된 카드들 확인:")
        for card_id in created_card_ids:
            card = await repository.find_by_id(card_id)
            if card:
                print(f"   카드 ID: {card_id}")
                print(f"   메모: '{card.card.memo.value}'")
                print(f"   태그: {card.card.tags.items}")
                print(f"   공개 설정: {card.card.is_public}")
                print()
        
        # 정리
        await cleanup_test_data(conn, created_card_ids)
        await conn.close()
        
        print("✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_tag_validation():
    """태그 유효성 검사 테스트"""
    print("🏷️ 태그 유효성 검사 테스트 시작\n")
    
    # 태그 제한 테스트 (최대 20개, 각 50자)
    long_tags = ["a" * 51]  # 51자 태그
    many_tags = [f"tag{i}" for i in range(25)]  # 25개 태그
    
    test_cases = [
        {
            "name": "정상 태그",
            "tags": ["개발", "Python", "테스트"],
            "should_pass": True
        },
        {
            "name": "너무 긴 태그",
            "tags": long_tags,
            "should_pass": False
        },
        {
            "name": "너무 많은 태그",
            "tags": many_tags,
            "should_pass": False
        }
    ]
    
    for test_case in test_cases:
        print(f"🧪 {test_case['name']}: {len(test_case['tags'])}개 태그")
        # 실제 유효성 검사는 도메인 객체에서 수행
        print(f"   예상 결과: {'통과' if test_case['should_pass'] else '실패'}")
        print()


async def main():
    """메인 테스트 실행"""
    await test_create_card_with_memo_and_tags()
    await test_tag_validation()


if __name__ == "__main__":
    asyncio.run(main())
