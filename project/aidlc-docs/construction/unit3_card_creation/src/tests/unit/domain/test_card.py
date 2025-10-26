import pytest
from uuid import uuid4
from unit3_card_creation.domain.entities.card import Card
from unit3_card_creation.domain.value_objects.content_url import ContentUrl


class TestCard:
    def test_create_card_with_defaults(self):
        user_id = uuid4()
        category_id = uuid4()
        content_url = ContentUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        card = Card.create(user_id, category_id, content_url)
        
        assert card.user_id == user_id
        assert card.category_id == category_id
        assert card.content_url == content_url
        assert not card.is_favorite
        assert not card.is_public
        assert card.memo.content == ""
        assert card.tags.items == []
    
    def test_create_card_with_memo_and_tags(self):
        user_id = uuid4()
        category_id = uuid4()
        content_url = ContentUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        memo = "테스트 메모"
        tags = ["개발", "유튜브", "테스트"]
        
        card = Card.create(user_id, category_id, content_url, memo, tags)
        
        assert card.memo.content == memo
        assert card.tags.items == tags
    
    def test_toggle_favorite(self):
        user_id = uuid4()
        category_id = uuid4()
        content_url = ContentUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        card = Card.create(user_id, category_id, content_url)
        
        # Toggle to favorite
        card.toggle_favorite()
        assert card.is_favorite
        assert card.favorited_at is not None
        
        # Toggle back
        card.toggle_favorite()
        assert not card.is_favorite
        assert card.favorited_at is None
    
    def test_toggle_public(self):
        user_id = uuid4()
        category_id = uuid4()
        content_url = ContentUrl("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        card = Card.create(user_id, category_id, content_url)
        
        # Initially private
        assert not card.is_public
        
        # Toggle to public
        card.toggle_public()
        assert card.is_public
        
        # Toggle back to private
        card.toggle_public()
        assert not card.is_public
