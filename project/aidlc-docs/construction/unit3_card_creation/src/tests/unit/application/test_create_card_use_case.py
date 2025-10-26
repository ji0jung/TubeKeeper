import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from unit3_card_creation.application.use_cases.create_card_use_case import CreateCardUseCase
from unit3_card_creation.application.commands.commands import CreateCardCommand


class TestCreateCardUseCase:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_duplication_checker(self):
        return AsyncMock()
    
    @pytest.fixture
    def use_case(self, mock_repository, mock_duplication_checker):
        return CreateCardUseCase(mock_repository, mock_duplication_checker)
    
    @pytest.mark.asyncio
    async def test_create_card_success(self, use_case, mock_duplication_checker, mock_repository):
        # Given
        command = CreateCardCommand(
            user_id=uuid4(),
            category_id=uuid4(),
            content_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            memo="테스트 메모",
            tags=["테스트", "유튜브"]
        )
        mock_duplication_checker.check_duplicate.return_value = None
        
        # When
        result = await use_case.execute(command)
        
        # Then
        assert result.status == "CREATED"
        assert result.message == "카드가 생성되었습니다"
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_card_with_empty_memo_and_tags(self, use_case, mock_duplication_checker, mock_repository):
        # Given
        command = CreateCardCommand(
            user_id=uuid4(),
            category_id=uuid4(),
            content_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        mock_duplication_checker.check_duplicate.return_value = None
        
        # When
        result = await use_case.execute(command)
        
        # Then
        assert result.status == "CREATED"
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_card_duplicate(self, use_case, mock_duplication_checker):
        # Given
        command = CreateCardCommand(
            user_id=uuid4(),
            category_id=uuid4(),
            content_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        existing_card = AsyncMock()
        existing_card.card_id = uuid4()
        mock_duplication_checker.check_duplicate.return_value = existing_card
        
        # When
        result = await use_case.execute(command)
        
        # Then
        assert result.status == "DUPLICATE"
        assert "이미 동일한 URL" in result.message
