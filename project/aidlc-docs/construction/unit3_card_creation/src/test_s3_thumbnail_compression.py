#!/usr/bin/env python3
"""
S3 썸네일 압축 테스트

YouTube 썸네일을 S3에 업로드하고 압축하는 기능을 검증합니다.
- YouTube 썸네일 다운로드
- 이미지 압축 및 최적화
- S3 업로드 및 URL 생성
- 압축률 및 품질 검증
"""

YouTube 메타데이터 수집 후 썸네일을 다운로드하고 압축하여 S3에 업로드하는 기능을 테스트합니다.
"""

import asyncio
import aiohttp
import boto3
from PIL import Image
from io import BytesIO
from uuid import uuid4
from datetime import datetime, timedelta
from jose import jwt

# 설정
BASE_URL = "http://localhost:8001"
JWT_SECRET = "your-jwt-secret-key-for-unit3-cards"
JWT_ALGORITHM = "HS256"
S3_BUCKET = "youtube-keeper-thumbnails-dev"
AWS_REGION = "us-east-1"

def generate_test_token():
    """테스트용 JWT 토큰 생성"""
    user_id = str(uuid4())
    payload = {
        "user_id": user_id,
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, user_id

async def test_youtube_metadata_extraction():
    """YouTube 메타데이터 추출 테스트"""
    print("🎬 YouTube 메타데이터 추출 테스트...")
    
    # 테스트용 YouTube URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    video_id = "dQw4w9WgXcQ"
    
    api_key = "AIzaSyAYg4Idms011jQtF520LqpdAB3r7z0MO_M"
    base_url = "https://www.googleapis.com/youtube/v3"
    
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/videos"
        params = {
            "part": "snippet,contentDetails",
            "id": video_id,
            "key": api_key
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("items"):
                    item = data["items"][0]
                    snippet = item["snippet"]
                    
                    print(f"   ✅ 제목: {snippet['title']}")
                    print(f"   ✅ 썸네일 URL: {snippet['thumbnails']['high']['url']}")
                    print(f"   ✅ 발행일: {snippet['publishedAt']}")
                    
                    return snippet['thumbnails']['high']['url']
                else:
                    print("   ❌ 비디오를 찾을 수 없습니다")
                    return None
            else:
                print(f"   ❌ YouTube API 오류: {response.status}")
                return None

async def test_thumbnail_compression(thumbnail_url):
    """썸네일 이미지 압축 테스트"""
    print("\n🖼️  썸네일 이미지 압축 테스트...")
    
    if not thumbnail_url:
        print("   ❌ 썸네일 URL이 없습니다")
        return None
    
    try:
        # 1. 원본 이미지 다운로드
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as response:
                if response.status != 200:
                    print(f"   ❌ 이미지 다운로드 실패: {response.status}")
                    return None
                
                original_data = await response.read()
                print(f"   ✅ 원본 이미지 다운로드: {len(original_data)} bytes")
        
        # 2. 이미지 압축
        image = Image.open(BytesIO(original_data))
        print(f"   📏 원본 크기: {image.size}")
        
        # 480x360으로 리사이즈
        resized_image = image.resize((480, 360), Image.Resampling.LANCZOS)
        print(f"   📏 리사이즈: {resized_image.size}")
        
        # WebP 형식으로 압축
        output = BytesIO()
        resized_image.save(output, format='WEBP', quality=85, optimize=True)
        compressed_data = output.getvalue()
        
        compression_ratio = (1 - len(compressed_data) / len(original_data)) * 100
        print(f"   ✅ 압축 완료: {len(compressed_data)} bytes")
        print(f"   📊 압축률: {compression_ratio:.1f}%")
        
        return compressed_data
        
    except Exception as e:
        print(f"   ❌ 압축 실패: {e}")
        return None

async def test_s3_upload(compressed_data):
    """실제 AWS S3 업로드 테스트"""
    print("\n☁️  AWS S3 업로드 테스트...")
    
    if not compressed_data:
        print("   ❌ 압축된 데이터가 없습니다")
        return None
    
    try:
        # 실제 AWS S3 클라이언트 설정
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        # 버킷 존재 확인
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET)
            print(f"   ✅ 버킷 존재 확인: {S3_BUCKET}")
        except s3_client.exceptions.NoSuchBucket:
            print(f"   ❌ 버킷이 존재하지 않습니다: {S3_BUCKET}")
            return None
        except Exception as e:
            print(f"   ⚠️  버킷 확인 실패: {e}")
            return None
        
        # S3에 업로드
        s3_key = f"thumbnails/{uuid4()}.webp"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=compressed_data,
            ContentType='image/webp'
        )
        
        s3_url = f"s3://{S3_BUCKET}/{s3_key}"
        print(f"   ✅ AWS S3 업로드 성공: {s3_url}")
        
        # 업로드된 객체 확인
        response = s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
        print(f"   📊 업로드 크기: {response['ContentLength']} bytes")
        print(f"   📊 Content-Type: {response['ContentType']}")
        
        # Signed URL 생성 테스트
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=3600
        )
        print(f"   ✅ Signed URL 생성 성공")
        
        return s3_url
        
    except Exception as e:
        print(f"   ❌ AWS S3 업로드 실패: {e}")
        return None

async def test_card_creation_with_thumbnail():
    """썸네일 포함 카드 생성 테스트"""
    print("\n🎯 썸네일 포함 카드 생성 테스트...")
    
    token, user_id = generate_test_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    card_data = {
        "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "category_id": "550e8400-e29b-41d4-a716-446655440000",
        "memo": "S3 썸네일 압축 테스트",
        "tags": ["테스트", "S3", "썸네일", "압축"],
        "is_public": False
    }
    
    async with aiohttp.ClientSession() as session:
        # 카드 생성
        async with session.post(f"{BASE_URL}/api/cards/", headers=headers, json=card_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                card_id = result["card_id"]
                print(f"   ✅ 카드 생성: {card_id}")
                
                # 잠시 대기 (메타데이터 수집 시간)
                await asyncio.sleep(2)
                
                # 카드 상세 조회
                async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=headers) as detail_resp:
                    if detail_resp.status == 200:
                        detail = await detail_resp.json()
                        print(f"   ✅ 비디오 제목: {detail.get('video_title', 'N/A')}")
                        print(f"   ✅ 썸네일 URL: {detail.get('thumbnail_url', 'N/A')}")
                        print(f"   ✅ 상태: {detail.get('status', 'N/A')}")
                        
                        return card_id
                    else:
                        print(f"   ❌ 카드 상세 조회 실패: {detail_resp.status}")
            else:
                print(f"   ❌ 카드 생성 실패: {resp.status}")
                
    return None

async def cleanup_test_data(card_id):
    """테스트 데이터 정리"""
    print("\n🗑️  테스트 데이터 정리...")
    
    if card_id:
        try:
            import asyncpg
            conn = await asyncpg.connect("postgresql://postgres:password@localhost:5433/unit3_cards")
            await conn.execute("DELETE FROM cards WHERE id = $1", card_id)
            await conn.close()
            print(f"   ✅ 카드 삭제: {card_id}")
        except Exception as e:
            print(f"   ⚠️  카드 삭제 실패: {e}")

async def main():
    """메인 테스트 실행"""
    print("🚀 S3 썸네일 압축 업로드 테스트 시작\n")
    
    # 1. YouTube 메타데이터 추출
    thumbnail_url = await test_youtube_metadata_extraction()
    
    # 2. 썸네일 압축
    compressed_data = await test_thumbnail_compression(thumbnail_url)
    
    # 3. S3 업로드
    s3_url = await test_s3_upload(compressed_data)
    
    # 4. 카드 생성 (실제 API 테스트)
    card_id = await test_card_creation_with_thumbnail()
    
    # 5. 데이터 정리
    await cleanup_test_data(card_id)
    
    print("\n🎉 S3 썸네일 압축 업로드 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
