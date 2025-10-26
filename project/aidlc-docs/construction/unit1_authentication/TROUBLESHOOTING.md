# Unit1 인증 서비스 트러블슈팅 가이드

## 🚨 주요 트러블슈팅 사례

### 1. Redis 연결 문제 해결

**문제**: 인증 코드가 Redis에 저장되지 않거나 조회되지 않음

**원인**: 메모리 기반 저장소(`MemoryVerificationCodeRepository`) 사용으로 인한 데이터 손실

**해결 과정**:
1. Redis 기반 저장소 구현 (`RedisVerificationCodeRepository`)
2. TTL 설정 (15분 자동 만료)
3. 의존성 주입 수정
4. Timezone 처리 통일 (`utc_now()` 사용)

**핵심 코드**:
```python
# Redis 저장소 구현
await self._redis.setex(key, ttl_seconds, json.dumps(data))

# TTL 계산
ttl_seconds = int((verification_code.expires_at - utc_now()).total_seconds())
```

### 2. PostgreSQL 연결 문제 해결

**문제**: `no pg_hba.conf entry for host "10.0.12.203", user "postgres", database "aidlc_auth", no encryption`

**원인**: RDS PostgreSQL 인스턴스의 SSL 인증 설정 문제

**해결 과정**:
1. Secrets Manager 기반 DB 연결 정보 관리
2. SSL 모드 조정 (`ssl='require'` → `ssl='prefer'`)
3. 커스텀 파라미터 그룹 생성 및 적용
4. 환경 변수 의존성 제거

**핵심 코드**:
```python
# SSL 연결 설정
return await asyncpg.connect(database_url, ssl='prefer')

# Secrets Manager 사용
response = client.get_secret_value(SecretId=secret_arn)
secret = json.loads(response['SecretString'])
```

### 3. Docker 이미지 의존성 문제

**문제**: `ImportError: No module named 'email_validator'`

**원인**: Pydantic의 이메일 검증 기능에 필요한 의존성 누락

**해결**: requirements.txt에 `email-validator==2.1.0` 추가

### 4. ECS 포트 설정 문제

**문제**: 로드 밸런서에서 애플리케이션 연결 실패

**원인**: 애플리케이션 포트(8001)와 인프라 설정 불일치

**해결**: 모든 설정에서 포트 8001로 통일

### 5. CloudFormation 스택 배포 실패

**문제**: 스택 간 의존성 및 파라미터 참조 오류

**원인**: Export/Import 값 불일치, 파라미터 기본값 문제

**해결**: 
- Export 이름 표준화
- 파라미터 기본값 제거
- 스택 배포 순서 정의

## 🔧 배포 시 주의사항

### 1. 배포 순서
1. VPC 및 네트워크 인프라
2. 보안 그룹
3. 데이터베이스 (RDS + ElastiCache)
4. IAM 역할
5. VPC 엔드포인트
6. Docker 이미지 빌드 및 푸시
7. ECS 클러스터 및 서비스
8. ALB 및 모니터링

### 2. 환경 변수 설정
- `DATABASE_URL`: Secrets Manager에서 자동 생성
- `REDIS_URL`: CloudFormation Export에서 참조
- `AWS_DEFAULT_REGION`: us-east-1
- `ENVIRONMENT`: staging

### 3. 보안 설정
- ECS 태스크는 private subnet에서 실행
- VPC 엔드포인트를 통한 ECR 접근
- Secrets Manager를 통한 DB 크리덴셜 관리
- 보안 그룹 간 최소 권한 원칙

## 🧪 테스트 시나리오

### 1. 회원가입 플로우
```bash
curl -X POST "http://ALB_DNS/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "pass123", "full_name": "Test User"}'
```

### 2. 인증 코드 검증
```bash
curl -X POST "http://ALB_DNS/api/auth/verify-registration" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "verification_code": "123456"}'
```

### 3. 로그인 플로우
```bash
curl -X POST "http://ALB_DNS/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## 📊 모니터링 및 로그

### CloudWatch 로그 그룹
- `/ecs/staging-aidlc-auth`: 애플리케이션 로그
- ECS 태스크 ID 기반 로그 스트림

### 주요 로그 패턴
- `📧 이메일 발송 시뮬레이션`: 인증 코드 생성 확인
- `✅ DB 연결 URL 생성`: PostgreSQL 연결 성공
- `INFO: Application startup complete`: 서비스 시작 완료

## 🔍 디버깅 명령어

### ECS 서비스 상태 확인
```bash
aws ecs describe-services --cluster staging-aidlc-cluster --services staging-aidlc-auth-service --region us-east-1
```

### 로그 확인
```bash
aws logs describe-log-streams --log-group-name "/ecs/staging-aidlc-auth" --region us-east-1
aws logs get-log-events --log-group-name "/ecs/staging-aidlc-auth" --log-stream-name "STREAM_NAME" --region us-east-1
```

### Redis 연결 테스트
```bash
# ECS 태스크에서 Redis 연결 확인
aws ecs execute-command --cluster staging-aidlc-cluster --task TASK_ID --container aidlc-auth --interactive --command "/bin/bash"
```

## 🚀 성능 최적화

### 1. Redis TTL 설정
- 인증 코드: 15분 (900초)
- 사용자 세션: 24시간 (86400초)

### 2. ECS 리소스 할당
- CPU: 256 units
- Memory: 512 MB
- 필요시 Auto Scaling 설정

### 3. 데이터베이스 최적화
- 인덱스: email, status, created_at
- 연결 풀링 설정
- 읽기 전용 복제본 고려

## 📝 체크리스트

### 배포 전 확인사항
- [ ] Docker 이미지 빌드 성공
- [ ] ECR 푸시 완료
- [ ] CloudFormation 템플릿 검증
- [ ] 환경 변수 설정 확인
- [ ] 보안 그룹 규칙 검토

### 배포 후 확인사항
- [ ] ECS 서비스 RUNNING 상태
- [ ] ALB 헬스 체크 통과
- [ ] API 엔드포인트 응답 확인
- [ ] Redis 연결 및 데이터 저장 확인
- [ ] PostgreSQL 연결 및 테이블 생성 확인
- [ ] CloudWatch 로그 정상 출력

## 🆘 긴급 복구 절차

### 1. 서비스 롤백
```bash
aws ecs update-service --cluster staging-aidlc-cluster --service staging-aidlc-auth-service --task-definition PREVIOUS_TASK_DEFINITION --region us-east-1
```

### 2. 스택 롤백
```bash
aws cloudformation cancel-update-stack --stack-name STACK_NAME --region us-east-1
```

### 3. 임시 메모리 저장소 사용
컨트롤러에서 `MemoryUserRepository()` 및 `MemoryVerificationCodeRepository()` 사용으로 임시 복구
