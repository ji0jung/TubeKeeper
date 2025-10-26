-- 태그 검색 성능 향상을 위한 GIN 인덱스 추가
CREATE INDEX CONCURRENTLY idx_cards_user_tags ON cards USING GIN (user_id, tags);

-- 태그만으로 검색하는 경우를 위한 추가 인덱스
CREATE INDEX CONCURRENTLY idx_cards_tags_only ON cards USING GIN (tags);
