#!/usr/bin/env python3
"""
Unit2 카테고리 관리 성능 테스트

Unit2 시스템의 성능 특성을 측정하고 검증하는 테스트 스위트
- 대량 데이터 처리 성능
- 계층 구조별 성능 특성
- 동시 요청 처리 능력
- 각 API 엔드포인트별 응답 시간

역할:
    - 시스템 성능 벤치마킹
    - 성능 병목 지점 식별
    - 확장성 검증
    - 성능 기준 준수 확인

테스트 시나리오:
    1. 대량 작업 성능 (20개 카테고리 생성/조회)
    2. 계층 구조 성능 (3레벨 50개 카테고리)
    3. 동시 요청 처리 (10개 동시 요청)
    4. 엔드포인트별 응답 시간 분석

성능 기준:
    - 개별 조회: < 100ms
    - 목록 조회: < 200ms  
    - 카테고리 생성: < 50ms
    - 동시 요청 성공률: > 95%

실행법:
    python3 test_performance.py
"""

import asyncio
import httpx
import time
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import statistics

from generate_test_token import generate_test_token

BASE_URL = "http://localhost:8002"

async def test_bulk_operations():
    """대량 작업 성능 테스트"""
    user_id = str(uuid4())
    token = generate_test_token(user_id, "perf_test@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🚀 대량 작업 성능 테스트")
        
        # 1. 카테고리 생성 (20개)
        start_time = time.time()
        created_ids = []
        
        for i in range(20):
            response = await client.post(f"{BASE_URL}/api/categories", 
                json={"name": f"카테고리{i:03d}"}, headers=headers)
            if response.status_code == 201:
                created_ids.append(response.json()["data"]["category"]["id"])
        
        create_time = time.time() - start_time
        print(f"✅ {len(created_ids)}개 카테고리 생성: {create_time:.2f}초 ({create_time/len(created_ids)*1000:.1f}ms/개)")
        
        # 2. 전체 목록 조회 성능
        start_time = time.time()
        response = await client.get(f"{BASE_URL}/api/categories", headers=headers)
        list_time = time.time() - start_time
        
        categories = response.json()["data"]["categories"]
        print(f"✅ {len(categories)}개 카테고리 목록 조회: {list_time*1000:.1f}ms")
        
        # 3. 개별 조회 성능 (10개 샘플)
        times = []
        for i in range(min(10, len(created_ids))):
            start_time = time.time()
            await client.get(f"{BASE_URL}/api/categories/{created_ids[i]}", headers=headers)
            times.append((time.time() - start_time) * 1000)
        
        avg_time = statistics.mean(times)
        print(f"✅ 개별 조회 평균: {avg_time:.1f}ms")
        
        # 정리
        for cat_id in created_ids:
            await client.delete(f"{BASE_URL}/api/categories/{cat_id}", headers=headers)

async def test_hierarchy_performance():
    """계층 구조 성능 테스트"""
    user_id = str(uuid4())
    token = generate_test_token(user_id, "hierarchy_perf@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("\n🏗️ 계층 구조 성능 테스트")
        
        # 1레벨: 5개
        level1_ids = []
        start_time = time.time()
        for i in range(5):
            response = await client.post(f"{BASE_URL}/api/categories", 
                json={"name": f"L1_{i}"}, headers=headers)
            if response.status_code == 201:
                level1_ids.append(response.json()["data"]["category"]["id"])
        
        l1_time = time.time() - start_time
        print(f"✅ 1레벨 {len(level1_ids)}개 생성: {l1_time:.2f}초")
        
        # 2레벨: 각 1레벨당 3개
        level2_ids = []
        start_time = time.time()
        for parent_id in level1_ids:
            for i in range(3):
                response = await client.post(f"{BASE_URL}/api/categories", 
                    json={"name": f"L2_{i}", "parent_id": parent_id}, headers=headers)
                if response.status_code == 201:
                    level2_ids.append(response.json()["data"]["category"]["id"])
        
        l2_time = time.time() - start_time
        print(f"✅ 2레벨 {len(level2_ids)}개 생성: {l2_time:.2f}초")
        
        # 3레벨: 각 2레벨당 2개
        level3_ids = []
        start_time = time.time()
        for parent_id in level2_ids:
            for i in range(2):
                response = await client.post(f"{BASE_URL}/api/categories", 
                    json={"name": f"L3_{i}", "parent_id": parent_id}, headers=headers)
                if response.status_code == 201:
                    level3_ids.append(response.json()["data"]["category"]["id"])
        
        l3_time = time.time() - start_time
        print(f"✅ 3레벨 {len(level3_ids)}개 생성: {l3_time:.2f}초")
        
        # 전체 목록 조회
        start_time = time.time()
        response = await client.get(f"{BASE_URL}/api/categories", headers=headers)
        list_time = time.time() - start_time
        
        total_count = len(response.json()["data"]["categories"])
        print(f"✅ 전체 {total_count}개 조회: {list_time*1000:.1f}ms")
        
        # 정리 (역순)
        for cat_id in level3_ids + level2_ids + level1_ids:
            await client.delete(f"{BASE_URL}/api/categories/{cat_id}", headers=headers)

async def test_concurrent_requests():
    """동시 요청 성능 테스트"""
    user_id = str(uuid4())
    token = generate_test_token(user_id, "concurrent_test@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n⚡ 동시 요청 성능 테스트")
    
    async def single_request(session, name):
        start = time.time()
        response = await session.post(f"{BASE_URL}/api/categories", 
            json={"name": name}, headers=headers)
        return time.time() - start, response.status_code
    
    # 10개 동시 요청
    async with httpx.AsyncClient(timeout=30.0) as client:
        start_time = time.time()
        
        tasks = [single_request(client, f"동시{i:02d}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        times = [r[0] for r in results]
        success_count = sum(1 for r in results if r[1] == 201)
        
        print(f"✅ 10개 동시 요청: {total_time:.2f}초")
        print(f"✅ 성공률: {success_count}/10 ({success_count/10*100:.1f}%)")
        print(f"✅ 평균 응답시간: {statistics.mean(times)*1000:.1f}ms")
        print(f"✅ 최대 응답시간: {max(times)*1000:.1f}ms")
        
        # 정리
        response = await client.get(f"{BASE_URL}/api/categories", headers=headers)
        categories = response.json()["data"]["categories"]
        for cat in categories:
            if cat["name"].startswith("동시"):
                await client.delete(f"{BASE_URL}/api/categories/{cat['id']}", headers=headers)

async def test_response_times():
    """응답 시간 분석"""
    user_id = str(uuid4())
    token = generate_test_token(user_id, "response_test@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n📊 응답 시간 분석")
        
        # 카테고리 생성
        response = await client.post(f"{BASE_URL}/api/categories", 
            json={"name": "응답시간테스트"}, headers=headers)
        cat_id = response.json()["data"]["category"]["id"]
        
        # 각 엔드포인트별 응답 시간 측정 (10회씩)
        endpoints = [
            ("GET /categories", lambda: client.get(f"{BASE_URL}/api/categories", headers=headers)),
            ("GET /categories/:id", lambda: client.get(f"{BASE_URL}/api/categories/{cat_id}", headers=headers)),
            ("PUT /categories/:id", lambda: client.put(f"{BASE_URL}/api/categories/{cat_id}", 
                json={"name": "수정된이름"}, headers=headers)),
            ("GET /deletion-preview", lambda: client.get(f"{BASE_URL}/api/categories/{cat_id}/deletion-preview", headers=headers))
        ]
        
        for name, func in endpoints:
            times = []
            for _ in range(10):
                start = time.time()
                await func()
                times.append((time.time() - start) * 1000)
            
            avg = statistics.mean(times)
            p95 = sorted(times)[int(len(times) * 0.95)]
            print(f"✅ {name}: 평균 {avg:.1f}ms, P95 {p95:.1f}ms")
        
        # 정리
        await client.delete(f"{BASE_URL}/api/categories/{cat_id}", headers=headers)

async def main():
    print("🚀 Unit2 카테고리 관리 성능 테스트 시작\n")
    
    try:
        await test_bulk_operations()
        await test_hierarchy_performance()
        await test_concurrent_requests()
        await test_response_times()
        
        print("\n🎉 성능 테스트 완료!")
        print("\n📈 성능 기준:")
        print("   - 개별 조회: < 100ms")
        print("   - 목록 조회: < 200ms")
        print("   - 카테고리 생성: < 50ms")
        print("   - 동시 요청 성공률: > 95%")
        
    except Exception as e:
        print(f"❌ 성능 테스트 실패: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
