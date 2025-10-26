#!/usr/bin/env python3
"""
AIDLC Authentication API 테스트 스크립트

실제 API 엔드포인트를 테스트합니다.
"""

import asyncio
import httpx
import json


BASE_URL = "http://localhost:8000"


async def test_registration_flow():
    """회원가입 플로우 테스트"""
    print("=== 회원가입 플로우 테스트 ===")
    
    async with httpx.AsyncClient() as client:
        # 1. 회원가입 요청
        register_data = {
            "email": "test@example.com",
            "gender": "male",
            "birth_year": 1990
        }
        
        print("1. 회원가입 요청...")
        response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"응답: {response.status_code}")
        print(f"내용: {response.json()}")
        
        if response.status_code != 200:
            print("❌ 회원가입 요청 실패")
            return
        
        # 2. 콘솔에서 인증 코드 확인 후 입력 받기
        print("\n📧 콘솔에 출력된 인증 코드를 확인하세요.")
        verification_code = input("인증 코드를 입력하세요: ")
        
        # 3. 회원가입 인증
        verify_data = {
            "email": "test@example.com",
            "verification_code": verification_code
        }
        
        print("2. 회원가입 인증...")
        response = await client.post(f"{BASE_URL}/api/auth/verify-registration", json=verify_data)
        print(f"응답: {response.status_code}")
        print(f"내용: {response.json()}")
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ 회원가입 완료!")
            return True
        else:
            print("❌ 회원가입 인증 실패")
            return False


async def test_login_flow():
    """로그인 플로우 테스트"""
    print("\n=== 로그인 플로우 테스트 ===")
    
    async with httpx.AsyncClient() as client:
        # 1. 로그인 요청
        login_data = {
            "email": "test@example.com"
        }
        
        print("1. 로그인 요청...")
        response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"응답: {response.status_code}")
        print(f"내용: {response.json()}")
        
        if response.status_code != 200:
            print("❌ 로그인 요청 실패")
            return
        
        # 2. 콘솔에서 인증 코드 확인 후 입력 받기
        print("\n📧 콘솔에 출력된 인증 코드를 확인하세요.")
        verification_code = input("인증 코드를 입력하세요: ")
        
        # 3. 로그인 인증
        verify_data = {
            "email": "test@example.com",
            "verification_code": verification_code
        }
        
        print("2. 로그인 인증...")
        response = await client.post(f"{BASE_URL}/api/auth/verify-login", json=verify_data)
        print(f"응답: {response.status_code}")
        print(f"내용: {response.json()}")
        
        if response.status_code == 200 and response.json().get("success"):
            print("✅ 로그인 완료!")
            token = response.json().get("token")
            print(f"토큰: {token}")
            return token
        else:
            print("❌ 로그인 인증 실패")
            return None


async def test_health_check():
    """헬스 체크 테스트"""
    print("=== 헬스 체크 테스트 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"응답: {response.status_code}")
        print(f"내용: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 서버 정상 작동")
            return True
        else:
            print("❌ 서버 오류")
            return False


async def main():
    """메인 테스트 실행"""
    print("AIDLC Authentication API 테스트")
    print("=" * 50)
    
    # 서버 실행 확인
    print("서버가 http://localhost:8000 에서 실행 중인지 확인하세요.")
    input("준비되면 Enter를 누르세요...")
    
    try:
        # 헬스 체크
        if not await test_health_check():
            return
        
        # 회원가입 플로우
        if await test_registration_flow():
            # 로그인 플로우
            token = await test_login_flow()
            
            if token:
                print("\n" + "=" * 50)
                print("✅ 모든 API 테스트가 성공적으로 완료되었습니다!")
                print(f"발급된 토큰: {token}")
            else:
                print("\n❌ 로그인 테스트 실패")
        else:
            print("\n❌ 회원가입 테스트 실패")
            
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
