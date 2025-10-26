-- Unit4 Test Data for Search Functionality

-- Insert additional users
INSERT INTO users (id, email, name) VALUES 
('550e8400-e29b-41d4-a716-446655440010', 'user2@example.com', 'User Two'),
('550e8400-e29b-41d4-a716-446655440020', 'user3@example.com', 'User Three')
ON CONFLICT (email) DO NOTHING;

-- Insert additional categories
INSERT INTO categories (id, user_id, name) VALUES 
('550e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440000', '개발'),
('550e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440000', '디자인'),
('550e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440010', '마케팅')
ON CONFLICT DO NOTHING;

-- Insert test cards for search functionality
INSERT INTO cards (id, user_id, category_id, title, content_url, thumbnail, summary, memo, tags, is_favorite, is_public, created_at) VALUES 

-- User 1 cards (for my-cards search)
('550e8400-e29b-41d4-a716-446655440100', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440011', 
 'React 완벽 가이드', 'https://youtube.com/watch?v=react-guide', 'https://img.youtube.com/vi/react-guide/maxresdefault.jpg',
 'React 기초부터 고급까지 완벽 정리', 'React hooks 중요', ARRAY['react', 'javascript', 'frontend'], true, true, NOW() - INTERVAL '1 day'),

('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440011',
 'Node.js 백엔드 개발', 'https://youtube.com/watch?v=nodejs-backend', 'https://img.youtube.com/vi/nodejs-backend/maxresdefault.jpg',
 'Express와 MongoDB를 활용한 백엔드 구축', 'API 설계 패턴 참고', ARRAY['nodejs', 'backend', 'express'], false, true, NOW() - INTERVAL '2 days'),

('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440012',
 'UI/UX 디자인 원칙', 'https://youtube.com/watch?v=uiux-design', 'https://img.youtube.com/vi/uiux-design/maxresdefault.jpg',
 '사용자 경험을 고려한 디자인 방법론', '색상 이론 중요', ARRAY['design', 'ui', 'ux'], true, false, NOW() - INTERVAL '3 days'),

('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440011',
 'Docker 컨테이너 기초', 'https://youtube.com/watch?v=docker-basics', 'https://img.youtube.com/vi/docker-basics/maxresdefault.jpg',
 'Docker를 활용한 개발 환경 구축', 'docker-compose 활용', ARRAY['docker', 'devops', 'container'], false, true, NOW() - INTERVAL '4 days'),

-- User 2 cards (for public cards search)
('550e8400-e29b-41d4-a716-446655440200', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440013',
 'Python 머신러닝 입문', 'https://youtube.com/watch?v=python-ml', 'https://img.youtube.com/vi/python-ml/maxresdefault.jpg',
 'scikit-learn으로 시작하는 머신러닝', 'pandas 데이터 전처리', ARRAY['python', 'ml', 'data'], false, true, NOW() - INTERVAL '5 days'),

('550e8400-e29b-41d4-a716-446655440201', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440013',
 'AWS 클라우드 아키텍처', 'https://youtube.com/watch?v=aws-architecture', 'https://img.youtube.com/vi/aws-architecture/maxresdefault.jpg',
 'EC2, RDS, S3를 활용한 웹 서비스 구축', 'VPC 설정 주의', ARRAY['aws', 'cloud', 'architecture'], false, true, NOW() - INTERVAL '6 days'),

-- User 3 cards
('550e8400-e29b-41d4-a716-446655440300', '550e8400-e29b-41d4-a716-446655440020', NULL,
 'JavaScript ES6+ 문법', 'https://youtube.com/watch?v=js-es6', 'https://img.youtube.com/vi/js-es6/maxresdefault.jpg',
 '최신 JavaScript 문법과 활용법', 'async/await 패턴', ARRAY['javascript', 'es6', 'frontend'], false, true, NOW() - INTERVAL '7 days')

ON CONFLICT DO NOTHING;

-- Update favorited_at for favorite cards
UPDATE cards SET favorited_at = created_at WHERE is_favorite = true;
