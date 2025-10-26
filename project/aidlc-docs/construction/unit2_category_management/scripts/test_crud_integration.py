#!/usr/bin/env python3
"""
Unit2 카테고리 관리 완전 통합 테스트

Unit2의 모든 기능을 검증하는 종합 테스트 스위트
- 기본 CRUD 작업 (생성, 조회, 수정, 삭제)
- 시스템 카테고리 보호 기능
- 계층 구조 관리 (3레벨 제한)
- 삭제 안전장치 (미리보기, 하위 카테고리 보호)
- 입력 검증 및 오류 처리
- 인증 및 권한 검증

역할:
    - Unit2의 모든 요구사항 검증
    - 비즈니스 규칙 준수 확인
    - 에러 시나리오 처리 검증
    - Integration Contract 표준 준수 확인

테스트 시나리오:
    1. 시스템 카테고리 생성 및 보호
    2. 일반 카테고리 CRUD
    3. 계층 구조 제한 (4레벨 차단)
    4. 입력 검증 (빈 이름, 긴 이름, 중복 이름)
    5. 404/401 오류 처리
    6. 삭제 미리보기 및 안전장치
    7. 계층 순서 삭제

실행법:
    python3 test_crud_integration.py
"""

import sys
import os
import asyncio
import httpx
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scripts.generate_test_token import generate_test_token

BASE_URL = "http://localhost:8002"

async def test_category_crud():
    # Unit2 단독 테스트용 - 로컬에서 JWT 토큰 생성
    user_id = str(uuid4())
    token = generate_test_token(user_id, "crud_test@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🧪 카테고리 CRUD 통합 테스트 시작")
        
        try:
            # 1. 초기 상태 확인
            response = await client.get(f"{BASE_URL}/api/categories", headers=headers)
            response_data = response.json()
            initial_count = len(response_data["data"]["categories"])
            print(f"✅ 초기 카테고리 수: {initial_count}")
            
            # 2. 시스템 카테고리 생성
            print("\n📋 시스템 카테고리 테스트")
            from scripts.init_system_categories import create_system_categories_for_user
            shared_id, temp_id = create_system_categories_for_user(user_id)
            print(f"✅ 시스템 카테고리 생성: 공유받은카드({shared_id}), 임시({temp_id})")
            
            # 시스템 카테고리 삭제 시도 (실패해야 함)
            response = await client.delete(f"{BASE_URL}/api/categories/{shared_id}", headers=headers)
            print(f"   시스템 카테고리 삭제 응답: {response.status_code}")
            if response.status_code != 400:
                print(f"   응답 내용: {response.text}")
            assert response.status_code == 400
            print("✅ 시스템 카테고리 삭제 방지 확인")
            
            # 3. 루트 카테고리 생성
            print("\n📋 일반 카테고리 CRUD 테스트")
            root_data = {"name": "루트카테고리"}
            response = await client.post(f"{BASE_URL}/api/categories", json=root_data, headers=headers)
            assert response.status_code == 201
            root_response = response.json()
            root_category = root_response["data"]["category"]
            print(f"✅ 루트 카테고리 생성: {root_category['name']}")
            
            # 4. 하위 카테고리 생성
            child_data = {"name": "하위카테고리", "parent_id": root_category["id"]}
            response = await client.post(f"{BASE_URL}/api/categories", json=child_data, headers=headers)
            assert response.status_code == 201
            child_response = response.json()
            child_category = child_response["data"]["category"]
            print(f"✅ 하위 카테고리 생성: {child_category['name']}")
            
            # 5. 3레벨 계층 테스트
            print("\n📋 계층 레벨 제한 테스트")
            level3_data = {"name": "레벨3", "parent_id": child_category["id"]}
            response = await client.post(f"{BASE_URL}/api/categories", json=level3_data, headers=headers)
            assert response.status_code == 201
            level3_response = response.json()
            level3_category = level3_response["data"]["category"]
            assert level3_category["hierarchy_level"] == 3
            print(f"✅ 레벨3 카테고리 생성: {level3_category['name']}")
            
            # 6. 4레벨 생성 시도 (실패해야 함)
            level4_data = {"name": "레벨4", "parent_id": level3_category["id"]}
            response = await client.post(f"{BASE_URL}/api/categories", json=level4_data, headers=headers)
            assert response.status_code == 400
            print("✅ 레벨4 생성 차단 확인")
            
            # 6-1. 입력 검증 오류 테스트
            print("\n📋 입력 검증 오류 테스트")
            
            # 빈 이름
            response = await client.post(f"{BASE_URL}/api/categories", 
                json={"name": ""}, headers=headers)
            assert response.status_code == 422
            print("✅ 빈 이름 차단")
            
            # 너무 긴 이름
            response = await client.post(f"{BASE_URL}/api/categories", 
                json={"name": "너무긴카테고리이름입니다"}, headers=headers)
            assert response.status_code == 422
            print("✅ 긴 이름 차단")
            
            # 중복 이름
            response = await client.post(f"{BASE_URL}/api/categories", 
                json={"name": "루트카테고리"}, headers=headers)
            assert response.status_code == 400
            print("✅ 중복 이름 차단")
            
            # 6-2. 404 오류 테스트
            print("\n📋 404 오류 테스트")
            fake_id = str(uuid4())
            
            # 존재하지 않는 카테고리 조회
            response = await client.get(f"{BASE_URL}/api/categories/{fake_id}", headers=headers)
            assert response.status_code == 404
            print("✅ 존재하지 않는 카테고리 조회 404")
            
            # 존재하지 않는 카테고리 수정
            response = await client.put(f"{BASE_URL}/api/categories/{fake_id}", 
                json={"name": "수정시도"}, headers=headers)
            assert response.status_code == 404
            print("✅ 존재하지 않는 카테고리 수정 404")
            
            # 존재하지 않는 카테고리 삭제
            response = await client.delete(f"{BASE_URL}/api/categories/{fake_id}", headers=headers)
            assert response.status_code == 404
            print("✅ 존재하지 않는 카테고리 삭제 404")
            
            # 6-3. 인증 오류 테스트
            print("\n📋 인증 오류 테스트")
            bad_headers = {"Authorization": "Bearer invalid_token"}
            response = await client.get(f"{BASE_URL}/api/categories", headers=bad_headers)
            assert response.status_code == 401
            print("✅ 잘못된 토큰 401")
            
            # 8. 계층 구조 확인
            response = await client.get(f"{BASE_URL}/api/categories", headers=headers)
            response_data = response.json()
            categories = response_data["data"]["categories"]
            print(f"✅ 계층 구조 확인: 총 {len(categories)}개 카테고리")
            
            # 9. 카테고리 이름 수정
            rename_data = {"name": "수정된루트"}
            response = await client.put(f"{BASE_URL}/api/categories/{root_category['id']}", json=rename_data, headers=headers)
            assert response.status_code == 200
            print("✅ 카테고리 이름 수정 완료")
            
            # 10. 삭제 미리보기 (하위 카테고리가 있는 경우)
            response = await client.get(f"{BASE_URL}/api/categories/{root_category['id']}/deletion-preview", headers=headers)
            preview_response = response.json()
            preview = preview_response["data"]
            assert not preview["can_delete"]  # 하위 카테고리가 있으므로 삭제 불가
            print("✅ 삭제 미리보기: 하위 카테고리로 인해 삭제 불가 확인")
            
            # 11. 역순 삭제 (레벨3 → 레벨2 → 레벨1)
            await client.delete(f"{BASE_URL}/api/categories/{level3_category['id']}", headers=headers)
            print("✅ 레벨3 카테고리 삭제 완료")
            
            await client.delete(f"{BASE_URL}/api/categories/{child_category['id']}", headers=headers)
            print("✅ 하위 카테고리 삭제 완료")
            
            await client.delete(f"{BASE_URL}/api/categories/{root_category['id']}", headers=headers)
            print("✅ 루트 카테고리 삭제 완료")
            
            # 12. 최종 상태 확인 (시스템 카테고리만 남아있어야 함)
            response = await client.get(f"{BASE_URL}/api/categories", headers=headers)
            final_response = response.json()
            final_categories = final_response["data"]["categories"]
            system_only = [c for c in final_categories if not c["is_deletable"]]
            assert len(system_only) == 2  # 시스템 카테고리 2개만
            print(f"✅ 최종 상태: 시스템 카테고리 {len(system_only)}개만 남음")
            
            print("\n🎉 카테고리 CRUD 통합 테스트 완료!")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
            raise
        finally:
            # 테스트 데이터 완전 정리
            print("\n🧹 테스트 데이터 완전 정리 중...")
            try:
                response = await client.get(f"{BASE_URL}/api/categories", headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    categories = response_data["data"]["categories"]
                    
                    # 모든 카테고리 삭제 (계층 구조 고려하여 역순)
                    level3_cats = [c for c in categories if c.get("hierarchy_level") == 3]
                    level2_cats = [c for c in categories if c.get("hierarchy_level") == 2] 
                    level1_cats = [c for c in categories if c.get("hierarchy_level") == 1]
                    
                    deleted_count = 0
                    for cats in [level3_cats, level2_cats, level1_cats]:
                        for category in cats:
                            try:
                                await client.delete(f"{BASE_URL}/api/categories/{category['id']}", headers=headers)
                                deleted_count += 1
                            except:
                                pass  # 삭제 실패 무시
                    
                    print(f"✅ 정리 완료: {deleted_count}개 카테고리 삭제")
            except Exception as cleanup_error:
                print(f"⚠️ 정리 중 오류 (무시됨): {cleanup_error}")

if __name__ == "__main__":
    asyncio.run(test_category_crud())
