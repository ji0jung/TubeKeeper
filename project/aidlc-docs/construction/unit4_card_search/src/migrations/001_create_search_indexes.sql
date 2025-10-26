-- Unit4: Card Search & Display - Search Indexes Migration

-- 1. Full-text search index for Korean content
CREATE INDEX IF NOT EXISTS idx_cards_fts_korean 
ON cards USING gin(to_tsvector('korean', title || ' ' || coalesce(summary, '')));

-- 2. Tags search index (GIN for array operations)
CREATE INDEX IF NOT EXISTS idx_cards_tags_gin 
ON cards USING gin(tags);

-- 3. My cards search indexes (cursor-based pagination)
CREATE INDEX IF NOT EXISTS idx_cards_user_created_desc 
ON cards(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cards_user_category_created 
ON cards(user_id, category_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cards_user_favorite_created 
ON cards(user_id, favorited_at DESC) 
WHERE is_favorite = true;

-- 4. Public cards search indexes
CREATE INDEX IF NOT EXISTS idx_cards_public_created_desc 
ON cards(is_public, created_at DESC) 
WHERE is_public = true;

-- 5. Search statistics table
CREATE TABLE IF NOT EXISTS search_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    search_query TEXT NOT NULL,
    search_scope VARCHAR(20) NOT NULL,
    result_count INTEGER NOT NULL DEFAULT 0,
    response_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_stats_user_created 
ON search_statistics(user_id, created_at DESC);
