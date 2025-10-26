import pytest
from unit3_card_creation.domain.value_objects.content_url import ContentUrl


class TestContentUrl:
    def test_valid_youtube_urls(self):
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            content_url = ContentUrl(url)
            assert content_url.is_valid()
            assert content_url.get_video_id() == "dQw4w9WgXcQ"
    
    def test_invalid_youtube_url(self):
        with pytest.raises(ValueError):
            ContentUrl("https://example.com/invalid")
    
    def test_normalize_url(self):
        url = ContentUrl("https://youtu.be/dQw4w9WgXcQ")
        normalized = url.normalize()
        assert normalized.value == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
