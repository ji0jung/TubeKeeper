#!/usr/bin/env python3
"""
테스트 데이터 정리 함수
"""
import asyncio
import asyncpg


async def cleanup_test_data():
    """모든 테스트 데이터 삭제"""
    conn = await asyncpg.connect(
        "postgresql://postgres:password@localhost:5433/unit3_cards"
    )
    
    try:
        # 카드 수 확인
        count_before = await conn.fetchval("SELECT COUNT(*) FROM cards")
        print(f"🗑️  삭제 전 카드 수: {count_before}")
        
        # 모든 카드 삭제
        await conn.execute("DELETE FROM cards")
        
        # 삭제 후 확인
        count_after = await conn.fetchval("SELECT COUNT(*) FROM cards")
        print(f"✅ 삭제 후 카드 수: {count_after}")
        print(f"🧹 총 {count_before}개 카드 삭제 완료")
        
    except Exception as e:
        print(f"❌ 데이터 삭제 실패: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(cleanup_test_data())
