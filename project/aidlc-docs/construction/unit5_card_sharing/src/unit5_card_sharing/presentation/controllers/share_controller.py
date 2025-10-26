import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import Optional
from pydantic import BaseModel

from presentation.responses import success_response, error_response
from application.services.share_link_application_service import ShareLinkApplicationService
from application.dtos.commands import CreateShareLinkCommand, AccessShareLinkQuery, SaveSharedCardCommand
from presentation.middleware.auth_middleware import get_current_user_id
from presentation.middleware.rate_limit_middleware import check_rate_limit
from infrastructure.database import get_db_session
from infrastructure.repositories.postgresql_share_link_repository import PostgreSQLShareLinkRepository
from application.use_cases.create_share_link_use_case import CreateShareLinkUseCase
from application.use_cases.get_shared_card_use_case import GetSharedCardUseCase
from application.use_cases.save_shared_card_use_case import SaveSharedCardUseCase

router = APIRouter()

class SaveCardRequest(BaseModel):
    categoryId: Optional[str] = None

def get_service(db_session = Depends(get_db_session)) -> ShareLinkApplicationService:
    repository = PostgreSQLShareLinkRepository(db_session)
    create_use_case = CreateShareLinkUseCase(repository)
    get_use_case = GetSharedCardUseCase(repository)
    save_use_case = SaveSharedCardUseCase(repository)
    return ShareLinkApplicationService(create_use_case, get_use_case, save_use_case)

@router.post("/api/cards/{card_id}/share")
async def create_share_link(
    card_id: str,
    request: Request,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ShareLinkApplicationService = Depends(get_service)
):
    try:
        if not await check_rate_limit(f"share_create:{user_id}", 20, 3600):
            return error_response("SHARE_011", "Rate limit exceeded for share link creation")
        
        try:
            card_uuid = uuid.UUID(card_id)
        except ValueError:
            return error_response("CARD_009", "Invalid card data format")
        
        command = CreateShareLinkCommand(card_id=card_uuid, user_id=user_id)
        result = await service.create_share_link(command)
        
        return success_response(
            data={
                "shareUrl": result.share_url,
                "shareToken": result.share_token,
                "expiresAt": result.expires_at
            },
            message="Share link created successfully"
        )
        
    except ValueError as e:
        if "not found" in str(e).lower():
            return error_response("CARD_001", "Card not found")
        elif "access denied" in str(e).lower():
            return error_response("CARD_008", "Card access denied")
        else:
            return error_response("SHARE_007", "Share link creation failed")
    except Exception as e:
        return error_response("SHARE_007", "Share link creation failed")

@router.get("/api/shared/{share_token}")
async def get_shared_card(
    share_token: str,
    request: Request,
    service: ShareLinkApplicationService = Depends(get_service)
):
    try:
        user_agent = request.headers.get("user-agent", "")
        is_crawler = any(bot in user_agent.lower() for bot in [
            "facebookexternalhit", "twitterbot", "linkedinbot", 
            "whatsapp", "kakaotalk", "telegrambot", "slackbot"
        ])
        
        query = AccessShareLinkQuery(
            share_token=share_token,
            user_agent=user_agent,
            ip_address=request.client.host if request.client else None
        )
        result = await service.get_shared_card(query)
        
        if is_crawler:
            return HTMLResponse(content=generate_og_html(result))
        
        return success_response(
            data={
                "card": {
                    "title": result.card.title,
                    "thumbnail": result.card.thumbnail,
                    "youtubeUrl": result.card.youtube_url,
                    "summary": result.card.summary,
                    "tags": result.card.tags
                },
                "isExpired": result.is_expired,
                "expiresAt": result.expires_at,
                "accessCount": result.access_count
            },
            message="Shared card retrieved successfully"
        )
        
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            return error_response("SHARE_002", "Share link not found")
        elif "expired" in error_msg:
            return error_response("SHARE_001", "Share link expired")
        elif "invalid" in error_msg and "format" in error_msg:
            return error_response("SHARE_003", "Invalid share token format")
        else:
            return error_response("SHARE_002", "Share link not found")
    except Exception as e:
        return error_response("SHARE_002", "Share link not found")

@router.post("/api/shared/{share_token}/save")
async def save_shared_card(
    share_token: str,
    request_body: SaveCardRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ShareLinkApplicationService = Depends(get_service)
):
    try:
        category_id = None
        if request_body.categoryId:
            try:
                category_id = uuid.UUID(request_body.categoryId)
            except ValueError:
                return error_response("CATEGORY_001", "Category not found")
        
        command = SaveSharedCardCommand(
            share_token=share_token,
            user_id=user_id,
            category_id=category_id
        )
        result = await service.save_shared_card(command)
        
        if result.already_exists:
            return success_response(
                data={"alreadyExists": True},
                message="Card already exists in your collection"
            )
        
        return success_response(
            data={
                "newCard": {
                    "id": result.new_card.id,
                    "title": result.new_card.title,
                    "categoryId": result.new_card.category_id,
                    "categoryName": result.new_card.category_name
                }
            },
            message="Card saved successfully"
        )
        
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            return error_response("SHARE_002", "Share link not found")
        elif "expired" in error_msg:
            return error_response("SHARE_001", "Share link expired")
        elif "already exists" in error_msg:
            return error_response("SHARE_013", "Card already exists in user collection")
        else:
            return error_response("SHARE_002", "Share link not found")
    except Exception as e:
        return error_response("SHARE_007", "Share link creation failed")

def generate_og_html(shared_card) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="{shared_card.card.title}" />
        <meta property="og:description" content="{shared_card.card.summary[:160] if shared_card.card.summary else 'YouTube Keeper - AI로 정리하는 나만의 영상 컬렉션'}" />
        <meta property="og:image" content="{shared_card.card.thumbnail}" />
        <meta property="og:url" content="{shared_card.card.youtube_url}" />
        <meta property="og:site_name" content="YouTube Keeper" />
        <meta property="og:type" content="article" />
        <title>{shared_card.card.title}</title>
    </head>
    <body>
        <h1>{shared_card.card.title}</h1>
        <p>YouTube Keeper - AI로 정리하는 나만의 영상 컬렉션</p>
    </body>
    </html>
    """
