# 프로덕션 레벨 통합 테스트 계획

## 🎯 목표
Unit2(카테고리) → Unit3(카드생성) → Unit4(검색) → Unit5(공유) 순차 통합 및 프로덕션 레벨 검증
**각 통합 단계마다 로컬 Docker 환경에서 필수 검증**

## 📋 통합 단계별 계획

### Phase 1: Unit2 + Unit3 통합 (현재)
**목표**: 카테고리 기반 카드 생성 워크플로우 검증

#### 🐳 로컬 Docker 테스트 (필수)
```bash
# 1. 로컬 환경 구성
cd integration
export YOUTUBE_API_KEY=your_key
docker compose up -d

# 2. 통합 테스트 실행
python tests/phase1/unit2_unit3_integration.py

# 3. 성능 테스트
python tests/phase1/performance_test.py

# 4. 데이터 일관성 검증
python tests/phase1/data_consistency_test.py
```

#### 핵심 시나리오:
1. **카테고리 생성 → 카드 생성**
   - Unit2에서 카테고리 생성
   - Unit3에서 해당 카테고리에 카드 생성
   - 카테고리-카드 연관관계 검증

2. **카테고리 삭제 안전장치**
   - 카드가 있는 카테고리 삭제 시도 → 차단
   - 카드 이동 후 카테고리 삭제 → 성공

3. **데이터 일관성**
   - 트랜잭션 롤백 테스트
   - 동시성 처리 검증

#### 성능 기준:
- API 응답시간: < 200ms
- 동시 사용자: 100명
- 데이터 일관성: 100%

### Phase 2: Unit4 추가 통합 (Unit2+3+4)
**목표**: 카드 검색 및 필터링 기능 통합

#### 🐳 로컬 Docker 테스트 (필수)
```bash
# 1. Phase2 환경 구성
cd integration
docker compose -f docker-compose.phase2.yml up -d

# 2. Unit4 통합 확인
curl http://localhost:8014/health  # Unit4 검색 서비스

# 3. 통합 테스트 실행
python tests/phase2/unit2_unit3_unit4_integration.py

# 4. 검색 성능 테스트
python tests/phase2/search_performance_test.py

# 5. 인덱싱 검증
python tests/phase2/search_indexing_test.py
```

#### Docker 구성 파일:
```yaml
# docker-compose.phase2.yml
version: '3.8'
services:
  unit2:
    ports: ["8012:8000"]
  unit3:
    ports: ["8013:8000"]
  unit4:
    build: ../unit4_card_search/src
    ports: ["8014:8000"]
    environment:
      - UNIT2_BASE_URL=http://unit2:8000
      - UNIT3_BASE_URL=http://unit3:8000
  elasticsearch:
    image: elasticsearch:8.8.0
    ports: ["9200:9200"]
```

#### 핵심 시나리오:
1. **통합 검색**
   - 카테고리별 카드 검색
   - 태그 기반 검색
   - 전문 검색 (제목, 내용)

2. **검색 성능**
   - 대량 데이터 검색 성능
   - 인덱싱 최적화 검증
   - 캐시 효율성 측정

3. **실시간 업데이트**
   - 카드 생성 시 검색 인덱스 업데이트
   - 카테고리 변경 시 검색 결과 반영

#### 성능 기준:
- 검색 응답시간: < 100ms
- 인덱싱 지연: < 5초
- 검색 정확도: > 95%

### Phase 3: Unit5 추가 통합 (Unit2+3+4+5)
**목표**: 전체 워크플로우 완성 및 공유 기능

#### 🐳 로컬 Docker 테스트 (필수)
```bash
# 1. 전체 통합 환경 구성
cd integration
docker compose -f docker-compose.full.yml up -d

# 2. 모든 서비스 상태 확인
curl http://localhost:8012/health  # Unit2
curl http://localhost:8013/health  # Unit3
curl http://localhost:8014/health  # Unit4
curl http://localhost:8015/health  # Unit5

# 3. 전체 워크플로우 테스트
python tests/phase3/full_workflow_integration.py

# 4. 공유 기능 테스트
python tests/phase3/sharing_integration_test.py

# 5. 알림 시스템 테스트
python tests/phase3/notification_test.py

# 6. 종합 성능 테스트
python tests/phase3/comprehensive_performance_test.py
```

#### Docker 구성 파일:
```yaml
# docker-compose.full.yml
version: '3.8'
services:
  unit2:
    ports: ["8012:8000"]
  unit3:
    ports: ["8013:8000"]
  unit4:
    ports: ["8014:8000"]
  unit5:
    build: ../unit5_card_sharing/src
    ports: ["8015:8000"]
    environment:
      - UNIT2_BASE_URL=http://unit2:8000
      - UNIT3_BASE_URL=http://unit3:8000
      - UNIT4_BASE_URL=http://unit4:8000
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
```

#### 핵심 시나리오:
1. **완전한 워크플로우**
   - 카테고리 생성 → 카드 생성 → 검색 → 공유
   - 공유된 카드의 카테고리 관리
   - 권한 기반 접근 제어

2. **공유 시나리오**
   - 개별 카드 공유
   - 카테고리 전체 공유
   - 공유 권한 관리

3. **알림 시스템**
   - 공유 알림
   - 카드 업데이트 알림
   - 실시간 알림 전달

#### 성능 기준:
- 전체 워크플로우: < 2초
- 공유 처리: < 500ms
- 알림 전달: < 1초

## 🧪 로컬 Docker 테스트 구조

### 테스트 디렉토리 구조
```
tests/
├── phase1/                     # Unit2+Unit3 통합
│   ├── unit2_unit3_integration.py
│   ├── performance_test.py
│   └── data_consistency_test.py
├── phase2/                     # Unit4 추가
│   ├── unit2_unit3_unit4_integration.py
│   ├── search_performance_test.py
│   └── search_indexing_test.py
├── phase3/                     # Unit5 추가 (전체)
│   ├── full_workflow_integration.py
│   ├── sharing_integration_test.py
│   ├── notification_test.py
│   └── comprehensive_performance_test.py
└── utils/
    ├── docker_manager.py       # Docker 환경 관리
    ├── test_data_generator.py  # 테스트 데이터 생성
    └── performance_monitor.py  # 성능 모니터링
```

### Docker 환경 관리 유틸리티
```python
# tests/utils/docker_manager.py
class DockerTestManager:
    def setup_phase1(self):
        """Unit2+Unit3 환경 구성"""
        
    def setup_phase2(self):
        """Unit2+Unit3+Unit4 환경 구성"""
        
    def setup_phase3(self):
        """전체 통합 환경 구성"""
        
    def cleanup(self):
        """테스트 환경 정리"""
```

## 📈 단계별 실행 계획

### Week 1-2: Phase 1 (Unit2+Unit3) 로컬 Docker 테스트
- [x] 기본 통합 환경 구축
- [ ] **로컬 Docker 환경에서 기능 테스트**
- [ ] **로컬 Docker 환경에서 성능 테스트**
- [ ] **로컬 Docker 환경에서 데이터 일관성 검증**
- [ ] 테스트 결과 문서화

### Week 3-4: Phase 2 (Unit4 추가) 로컬 Docker 테스트
- [ ] **Unit4 통합 Docker 환경 구축**
- [ ] **로컬에서 검색 기능 통합 테스트**
- [ ] **로컬에서 검색 성능 테스트**
- [ ] **로컬에서 인덱싱 전략 검증**
- [ ] Phase2 테스트 결과 분석

### Week 5-6: Phase 3 (Unit5 추가) 로컬 Docker 테스트
- [ ] **전체 통합 Docker 환경 구축**
- [ ] **로컬에서 완전한 워크플로우 테스트**
- [ ] **로컬에서 공유 기능 테스트**
- [ ] **로컬에서 알림 시스템 테스트**
- [ ] **로컬에서 종합 성능 검증**

### Week 7-8: 프로덕션 준비
- [ ] 로컬 테스트 결과 기반 최적화
- [ ] 프로덕션 환경 구성
- [ ] 최종 검수 및 배포 준비

## 🔧 로컬 Docker 테스트 가이드

### 환경 준비
```bash
# 1. 필수 환경 변수 설정
export YOUTUBE_API_KEY=your_actual_key

# 2. Docker 리소스 확인
docker system df
docker system prune  # 필요시 정리
```

### Phase별 테스트 실행
```bash
# Phase 1 테스트
cd integration
./scripts/test_phase1.sh

# Phase 2 테스트  
./scripts/test_phase2.sh

# Phase 3 테스트
./scripts/test_phase3.sh
```

### 테스트 스크립트 예시
```bash
#!/bin/bash
# scripts/test_phase1.sh

echo "🚀 Phase 1: Unit2+Unit3 통합 테스트 시작"

# 1. 환경 구성
docker compose up -d unit2 unit3 postgres redis
sleep 30

# 2. 헬스체크
curl -f http://localhost:8012/health || exit 1
curl -f http://localhost:8013/health || exit 1

# 3. 통합 테스트 실행
python tests/phase1/unit2_unit3_integration.py

# 4. 성능 테스트
python tests/phase1/performance_test.py

# 5. 정리
docker compose down

echo "✅ Phase 1 테스트 완료"
```

## 🎯 로컬 Docker 테스트 성공 기준

### 각 Phase별 필수 검증 항목
1. **모든 서비스 정상 기동** ✅
2. **헬스체크 통과** ✅  
3. **기능 테스트 100% 통과** ✅
4. **성능 기준 달성** ✅
5. **데이터 일관성 보장** ✅

### 실패 시 대응
- 로그 분석 및 문제 해결
- 다음 Phase 진행 전 반드시 해결
- 테스트 결과 문서화 및 공유

이 계획을 통해 각 통합 단계마다 로컬 Docker 환경에서 철저한 검증을 수행하여 안정적인 통합을 보장합니다.
