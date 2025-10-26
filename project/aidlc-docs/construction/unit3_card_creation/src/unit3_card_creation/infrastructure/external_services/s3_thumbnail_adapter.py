import boto3
import aiohttp
from PIL import Image
from io import BytesIO
from uuid import uuid4
from ...domain.value_objects.basic_types import Thumbnail
from ..config.settings import settings


class S3ThumbnailAdapter:
    # 기본 회색 썸네일 (480x360, SVG 형식)
    DEFAULT_THUMBNAIL_URL = "data:image/svg+xml,%3Csvg width='480' height='360' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='100%25' height='100%25' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='18' fill='%23999999' text-anchor='middle' dy='.3em'%3E비디오 없음%3C/text%3E%3C/svg%3E"
    
    def __init__(self):
        self._s3_client = boto3.client('s3', region_name=settings.aws_region)
        self._bucket_name = settings.s3_bucket_name
    
    async def process_thumbnail(self, youtube_url: str) -> Thumbnail:
        try:
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(youtube_url) as response:
                    if response.status != 200:
                        return Thumbnail(youtube_url=self.DEFAULT_THUMBNAIL_URL)
                    
                    image_data = await response.read()
            
            # Process and compress
            compressed_data = self._compress_image(image_data)
            
            # Upload to S3
            s3_key = f"thumbnails/{uuid4()}.webp"
            self._s3_client.put_object(
                Bucket=self._bucket_name,
                Key=s3_key,
                Body=compressed_data,
                ContentType='image/webp'
            )
            
            s3_url = f"s3://{self._bucket_name}/{s3_key}"
            return Thumbnail(s3_url=s3_url, youtube_url=youtube_url)
            
        except Exception:
            # Fallback to default thumbnail
            return Thumbnail(youtube_url=self.DEFAULT_THUMBNAIL_URL)
    
    def _compress_image(self, image_data: bytes) -> bytes:
        """Compress image to WebP format with 85% quality"""
        image = Image.open(BytesIO(image_data))
        
        # Resize to 480x360
        image = image.resize((480, 360), Image.Resampling.LANCZOS)
        
        # Convert to WebP
        output = BytesIO()
        image.save(output, format='WEBP', quality=85, optimize=True)
        
        return output.getvalue()
    
    def get_signed_url(self, s3_url: str, expires_in: int = 3600) -> str:
        """Generate signed URL for private S3 object"""
        if not s3_url.startswith('s3://'):
            return s3_url
        
        # Parse S3 URL
        s3_key = s3_url.replace(f's3://{self._bucket_name}/', '')
        
        try:
            signed_url = self._s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return signed_url
        except Exception:
            return s3_url
