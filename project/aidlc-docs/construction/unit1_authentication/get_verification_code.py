#!/usr/bin/env python3
"""
인증 코드 추출 스크립트

CloudWatch 로그에서 최신 인증 코드를 추출합니다.
"""

import boto3
import json
import re
from datetime import datetime, timedelta
import sys


def get_latest_verification_code(email: str = None, minutes_back: int = 10):
    """
    CloudWatch 로그에서 최신 인증 코드를 추출
    
    Args:
        email: 특정 이메일의 코드만 찾기 (None이면 모든 코드)
        minutes_back: 몇 분 전까지 로그를 확인할지
    """
    
    # CloudWatch Logs 클라이언트 생성
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    # 로그 그룹명
    log_group_name = '/ecs/staging-aidlc-auth'
    
    # 시간 범위 설정 (UTC)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=minutes_back)
    
    # 밀리초로 변환
    start_timestamp = int(start_time.timestamp() * 1000)
    end_timestamp = int(end_time.timestamp() * 1000)
    
    print(f"🔍 {minutes_back}분 전부터 현재까지의 로그를 검색합니다...")
    if email:
        print(f"📧 이메일: {email}")
    
    try:
        # 로그 이벤트 검색
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=start_timestamp,
            endTime=end_timestamp,
            filterPattern='verification_code' if not email else f'verification_code {email}'
        )
        
        verification_codes = []
        
        for event in response.get('events', []):
            message = event['message']
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            
            # 인증 코드 패턴 찾기
            # 예: "Verification code for test@example.com: 123456"
            # 또는 JSON 형태의 로그에서 추출
            
            # 패턴 1: 직접 텍스트
            pattern1 = r'verification code.*?(\d{6})'
            match1 = re.search(pattern1, message, re.IGNORECASE)
            
            # 패턴 2: JSON 로그
            try:
                if message.strip().startswith('{'):
                    log_data = json.loads(message)
                    if 'verification_code' in str(log_data).lower():
                        # JSON에서 6자리 숫자 찾기
                        code_match = re.search(r'\b(\d{6})\b', str(log_data))
                        if code_match:
                            verification_codes.append({
                                'code': code_match.group(1),
                                'timestamp': timestamp,
                                'message': message[:200] + '...' if len(message) > 200 else message
                            })
            except json.JSONDecodeError:
                pass
            
            # 패턴 1 결과 처리
            if match1:
                verification_codes.append({
                    'code': match1.group(1),
                    'timestamp': timestamp,
                    'message': message[:200] + '...' if len(message) > 200 else message
                })
        
        # 시간순 정렬 (최신순)
        verification_codes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if verification_codes:
            print(f"\n✅ {len(verification_codes)}개의 인증 코드를 찾았습니다:")
            print("-" * 80)
            
            for i, code_info in enumerate(verification_codes[:5]):  # 최신 5개만 표시
                print(f"{i+1}. 코드: {code_info['code']}")
                print(f"   시간: {code_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   로그: {code_info['message']}")
                print()
            
            # 가장 최신 코드 강조
            latest_code = verification_codes[0]['code']
            print(f"🎯 가장 최신 인증 코드: {latest_code}")
            return latest_code
            
        else:
            print("❌ 인증 코드를 찾을 수 없습니다.")
            print("💡 다음을 확인해보세요:")
            print("   - 회원가입/로그인 요청을 먼저 보냈는지")
            print("   - 이메일 주소가 정확한지")
            print("   - 시간 범위를 늘려보세요 (--minutes 옵션)")
            return None
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CloudWatch 로그에서 인증 코드 추출')
    parser.add_argument('--email', help='특정 이메일의 코드만 찾기')
    parser.add_argument('--minutes', type=int, default=10, help='몇 분 전까지 검색할지 (기본: 10분)')
    
    args = parser.parse_args()
    
    print("🔐 AIDLC 인증 코드 추출기")
    print("=" * 50)
    
    code = get_latest_verification_code(args.email, args.minutes)
    
    if code:
        print(f"\n📋 클립보드 복사용: {code}")


if __name__ == "__main__":
    main()
