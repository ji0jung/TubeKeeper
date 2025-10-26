"""Unit4: Card Search & Display - FastAPI Application"""

import asyncpg
import os
from typing import Optional, List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Minimal app for testing
app = FastAPI(
    title="Unit4: Card Search & Display API",
    description="검색 및 카드 조회 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/aidlc_db").replace("postgresql+asyncpg://", "postgresql://")

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "Unit4 Card Search"}

@app.get("/")
async def root():
    """서비스 정보"""
    return {
        "service": "Unit4 Card Search & Display System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/my-cards")
async def get_my_cards(
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """내 카드 목록 (실제 DB 쿼리)"""
    try:
        conn = await get_db_connection()
        
        # Base query for user 1 (test user)
        query = """
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags, 
               cat.name as category_name, c.is_favorite, c.created_at
        FROM cards c
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE c.user_id = '550e8400-e29b-41d4-a716-446655440000' AND c.deleted_at IS NULL
        """
        params = []
        param_count = 0
        
        # Add search conditions
        if search:
            query += f" AND (c.title ILIKE ${param_count + 1} OR c.summary ILIKE ${param_count + 1})"
            params.append(f"%{search}%")
            param_count += 1
        
        if tag:
            query += f" AND ${param_count + 1} = ANY(c.tags)"
            params.append(tag)
            param_count += 1
        
        if category_id:
            query += f" AND c.category_id = ${param_count + 1}"
            params.append(category_id)
            param_count += 1
        
        query += f" ORDER BY c.created_at DESC LIMIT ${param_count + 1}"
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
        await conn.close()
        
        cards = []
        for row in rows:
            cards.append({
                "id": str(row['id']),
                "title": row['title'],
                "thumbnail": row['thumbnail'],
                "summary": row['summary'] or "",
                "tags": row['tags'] or [],
                "categoryName": row['category_name'],
                "isFavorite": row['is_favorite'],
                "createdAt": row['created_at'].isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "cards": cards,
                "nextCursor": None,
                "hasMore": len(cards) == limit
            },
            "message": "Success"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SEARCH_009",
                "message": f"Search service error: {str(e)}"
            }
        }

@app.get("/api/my-cards/favorites")
async def get_favorite_cards(limit: int = Query(20, ge=1, le=100)):
    """즐겨찾기 카드 목록 (실제 DB 쿼리)"""
    try:
        conn = await get_db_connection()
        
        query = """
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags, 
               cat.name as category_name, c.is_favorite, c.created_at
        FROM cards c
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE c.user_id = '550e8400-e29b-41d4-a716-446655440000' 
          AND c.is_favorite = true AND c.deleted_at IS NULL
        ORDER BY c.favorited_at DESC LIMIT $1
        """
        
        rows = await conn.fetch(query, limit)
        await conn.close()
        
        cards = []
        for row in rows:
            cards.append({
                "id": str(row['id']),
                "title": row['title'],
                "thumbnail": row['thumbnail'],
                "summary": row['summary'] or "",
                "tags": row['tags'] or [],
                "categoryName": row['category_name'],
                "isFavorite": row['is_favorite'],
                "createdAt": row['created_at'].isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "cards": cards,
                "nextCursor": None,
                "hasMore": len(cards) == limit
            },
            "message": "Success"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SEARCH_009",
                "message": f"Search service error: {str(e)}"
            }
        }

@app.get("/api/public-cards")
async def search_public_cards(
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """공개 카드 검색 (실제 DB 쿼리)"""
    try:
        # 공개 카드 검색 제약 검증
        if search and tag:
            return {
                "success": False,
                "error": {
                    "code": "SEARCH_001",
                    "message": "Cannot use both search keyword and tag simultaneously"
                }
            }
        
        if not search and not tag:
            return {
                "success": False,
                "error": {
                    "code": "SEARCH_001", 
                    "message": "Either search keyword or tag is required"
                }
            }
        
        conn = await get_db_connection()
        
        # Base query
        base_query = """
        FROM cards c
        JOIN users u ON c.user_id = u.id
        WHERE c.is_public = true AND c.user_id != '550e8400-e29b-41d4-a716-446655440000' AND c.deleted_at IS NULL
        """
        params = []
        param_count = 0
        
        # Add search conditions
        if search:
            base_query += f" AND (c.title ILIKE ${param_count + 1} OR c.summary ILIKE ${param_count + 1})"
            params.append(f"%{search}%")
            param_count += 1
        elif tag:
            base_query += f" AND ${param_count + 1} = ANY(c.tags)"
            params.append(tag)
            param_count += 1
        
        # Count query
        count_query = "SELECT COUNT(*) " + base_query
        total_count = await conn.fetchval(count_query, *params)
        
        # Data query
        offset = (page - 1) * limit
        data_query = f"""
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags,
               u.name as owner_name, c.created_at
        {base_query}
        ORDER BY c.created_at DESC
        OFFSET ${param_count + 1} LIMIT ${param_count + 2}
        """
        params.extend([offset, limit])
        
        rows = await conn.fetch(data_query, *params)
        await conn.close()
        
        cards = []
        for row in rows:
            cards.append({
                "id": str(row['id']),
                "title": row['title'],
                "thumbnail": row['thumbnail'],
                "summary": row['summary'] or "",
                "tags": row['tags'] or [],
                "ownerName": row['owner_name'],
                "isPublic": True,
                "createdAt": row['created_at'].isoformat()
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "data": {
                "cards": cards,
                "totalCount": total_count,
                "currentPage": page,
                "totalPages": total_pages
            },
            "message": "Success"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SEARCH_009",
                "message": f"Search service error: {str(e)}"
            }
        }

@app.post("/api/public-cards/{card_id}/save")
async def save_public_card(card_id: str):
    """공개 카드 저장 (테스트용)"""
    return {
        "success": True,
        "data": {
            "newCard": None,
            "alreadyExists": False
        },
        "message": "Card saved successfully"
    }

@app.get("/api/search/suggestions")
async def get_search_suggestions():
    """검색 제안 (테스트용)"""
    return {
        "success": True,
        "data": {
            "suggestions": [
                {"type": "recent", "value": "React"},
                {"type": "tag", "value": "javascript"},
                {"type": "popular", "value": "Docker"}
            ]
        },
        "message": "Success"
    }

@app.get("/api/tags")
async def get_tags(scope: str = Query("my")):
    """태그 목록 (실제 DB 쿼리)"""
    try:
        conn = await get_db_connection()
        
        if scope == "my":
            query = """
            SELECT tag, COUNT(*) as count
            FROM (
                SELECT unnest(tags) as tag
                FROM cards 
                WHERE user_id = '550e8400-e29b-41d4-a716-446655440000' AND deleted_at IS NULL
            ) tag_usage
            GROUP BY tag
            ORDER BY count DESC, tag ASC
            """
        else:  # public
            query = """
            SELECT tag, COUNT(*) as count
            FROM (
                SELECT unnest(tags) as tag
                FROM cards 
                WHERE is_public = true AND deleted_at IS NULL
            ) tag_usage
            GROUP BY tag
            ORDER BY count DESC, tag ASC
            """
        
        rows = await conn.fetch(query)
        await conn.close()
        
        tags = []
        for row in rows:
            tags.append({
                "name": row['tag'],
                "count": row['count']
            })
        
        return {
            "success": True,
            "data": {
                "tags": tags
            },
            "message": "Success"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "SEARCH_009",
                "message": f"Search service error: {str(e)}"
            }
        }
