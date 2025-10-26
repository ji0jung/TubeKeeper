#!/usr/bin/env python3
"""
Docker 테스트 환경 관리 유틸리티

각 Phase별 Docker 환경을 자동으로 구성하고 관리하는 도구
- Phase별 서비스 조합 관리
- 헬스체크 및 상태 모니터링
- 테스트 데이터 초기화
- 환경 정리 및 리소스 관리
"""

import subprocess
import time
import requests
import json
from typing import List, Dict, Optional

class DockerTestManager:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.services = {
            "phase1": ["unit2", "unit3", "postgres", "redis", "localstack"],
            "phase2": ["unit2", "unit3", "unit4", "postgres", "redis", "localstack", "elasticsearch"],
            "phase3": ["unit2", "unit3", "unit4", "unit5", "postgres", "redis", "localstack", "elasticsearch", "rabbitmq"]
        }
        self.health_endpoints = {
            "unit2": "http://localhost:8012/health",
            "unit3": "http://localhost:8013/health", 
            "unit4": "http://localhost:8014/health",
            "unit5": "http://localhost:8015/health"
        }

    def setup_phase(self, phase: str) -> bool:
        """Phase별 Docker 환경 구성"""
        print(f"🚀 {phase.upper()} 환경 구성 시작")
        
        try:
            # 1. 기존 환경 정리
            self.cleanup()
            
            # 2. 서비스 시작
            services = self.services.get(phase, [])
            compose_file = self._get_compose_file(phase)
            
            cmd = ["docker", "compose", "-f", compose_file, "up", "-d"] + services
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Docker 서비스 시작 실패: {result.stderr}")
                return False
            
            # 3. 서비스 초기화 대기
            print("⏳ 서비스 초기화 대기 중...")
            time.sleep(30)
            
            # 4. 헬스체크
            if not self._health_check(phase):
                return False
                
            print(f"✅ {phase.upper()} 환경 구성 완료")
            return True
            
        except Exception as e:
            print(f"❌ 환경 구성 실패: {e}")
            return False

    def _get_compose_file(self, phase: str) -> str:
        """Phase별 Docker Compose 파일 경로 반환"""
        compose_files = {
            "phase1": "docker-compose.yml",
            "phase2": "docker-compose.phase2.yml", 
            "phase3": "docker-compose.full.yml"
        }
        return compose_files.get(phase, "docker-compose.yml")

    def _health_check(self, phase: str) -> bool:
        """서비스 헬스체크"""
        print("🔍 서비스 상태 확인 중...")
        
        # Phase별 확인할 서비스 결정
        services_to_check = []
        if phase in ["phase1", "phase2", "phase3"]:
            services_to_check.extend(["unit2", "unit3"])
        if phase in ["phase2", "phase3"]:
            services_to_check.append("unit4")
        if phase == "phase3":
            services_to_check.append("unit5")
        
        for service in services_to_check:
            endpoint = self.health_endpoints.get(service)
            if not endpoint:
                continue
                
            max_retries = 10
            for attempt in range(max_retries):
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {service} 서비스 정상")
                        break
                except requests.RequestException:
                    if attempt == max_retries - 1:
                        print(f"❌ {service} 헬스체크 실패")
                        return False
                    time.sleep(3)
        
        return True

    def cleanup(self) -> None:
        """Docker 환경 정리"""
        print("🧹 기존 환경 정리 중...")
        try:
            # 모든 compose 파일에 대해 정리 시도
            compose_files = [
                "docker-compose.yml",
                "docker-compose.phase2.yml", 
                "docker-compose.full.yml"
            ]
            
            for compose_file in compose_files:
                cmd = ["docker", "compose", "-f", compose_file, "down", "-v"]
                subprocess.run(cmd, capture_output=True, text=True)
                
        except Exception as e:
            print(f"⚠️ 정리 중 오류 (무시됨): {e}")

    def get_service_logs(self, phase: str, output_dir: str = "logs") -> None:
        """서비스 로그 수집"""
        print("📋 로그 수집 중...")
        
        import os
        os.makedirs(f"{output_dir}/{phase}", exist_ok=True)
        
        services = self.services.get(phase, [])
        compose_file = self._get_compose_file(phase)
        
        for service in services:
            try:
                cmd = ["docker", "compose", "-f", compose_file, "logs", service]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                with open(f"{output_dir}/{phase}/{service}.log", "w") as f:
                    f.write(result.stdout)
                    
            except Exception as e:
                print(f"⚠️ {service} 로그 수집 실패: {e}")

    def run_basic_api_test(self, phase: str) -> bool:
        """기본 API 테스트"""
        print("🧪 기본 API 테스트 실행 중...")
        
        try:
            # Unit2 카테고리 생성 테스트
            response = requests.post(
                "http://localhost:8012/api/categories",
                json={"name": "테스트카테고리"},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer test_token"
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print("✅ Unit2 API 테스트 성공")
                return True
            else:
                print(f"❌ Unit2 API 테스트 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API 테스트 실패: {e}")
            return False

# 사용 예시
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python docker_manager.py <phase1|phase2|phase3|cleanup>")
        sys.exit(1)
    
    manager = DockerTestManager()
    command = sys.argv[1]
    
    if command == "cleanup":
        manager.cleanup()
    elif command in ["phase1", "phase2", "phase3"]:
        success = manager.setup_phase(command)
        if success:
            manager.run_basic_api_test(command)
            manager.get_service_logs(command)
        manager.cleanup()
    else:
        print(f"알 수 없는 명령어: {command}")
        sys.exit(1)
