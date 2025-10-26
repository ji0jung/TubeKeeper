-- Unit3 Cards 테이블 생성
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    category_id UUID NOT NULL,
    content_url VARCHAR(500) NOT NULL,
    
    -- Video metadata
    video_title VARCHAR(200),
    thumbnail_s3_url VARCHAR(500),
    thumbnail_youtube_url VARCHAR(500),
    duration INTEGER DEFAULT 0,
    published_at TIMESTAMP WITH TIME ZONE,
    
    -- Card info
    memo TEXT,
    tags JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'CREATING',
    
    -- Favorite
    is_favorite BOOLEAN DEFAULT FALSE,
    favorited_at TIMESTAMP WITH TIME ZONE,
    
    -- Public
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
CREATE INDEX IF NOT EXISTS idx_cards_category_id ON cards(category_id);
CREATE INDEX IF NOT EXISTS idx_cards_created_at ON cards(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cards_is_favorite ON cards(is_favorite) WHERE is_favorite = TRUE;

-- 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cards_updated_at 
    BEFORE UPDATE ON cards 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
