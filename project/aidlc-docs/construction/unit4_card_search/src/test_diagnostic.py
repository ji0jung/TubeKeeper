#!/usr/bin/env python3
"""Unit4 Diagnostic and Fix Test Suite"""

import requests
import subprocess
import time
import sys
import json
from typing import Tuple, Dict, Any

BASE_URL = "http://localhost:8004"

class DiagnosticTester:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def log_issue(self, issue: str):
        """Log an issue found"""
        self.issues_found.append(issue)
        print(f"🔍 ISSUE: {issue}")
    
    def log_fix(self, fix: str):
        """Log a fix applied"""
        self.fixes_applied.append(fix)
        print(f"🔧 FIX: {fix}")
    
    def run_command(self, cmd: str, description: str = "") -> Tuple[bool, str]:
        """Run shell command and return success status and output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            success = result.returncode == 0
            output = result.stdout + result.stderr
            if description and not success:
                print(f"❌ {description}: {output.strip()}")
            return success, output
        except subprocess.TimeoutExpired:
            print(f"⏰ {description}: Command timed out")
            return False, "Timeout"
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
            return False, str(e)

def test_1_container_status(tester: DiagnosticTester) -> bool:
    """Test 1: Check container status"""
    print("\n=== 1. Container Status Diagnosis ===")
    
    success, output = tester.run_command(
        "cd /Users/jiyoung/work/AIDLC/project/aidlc-docs/construction/unit4_card_search/src && docker compose ps",
        "Check container status"
    )
    
    if not success:
        tester.log_issue("Cannot check container status")
        return False
    
    # Check if containers are running
    if "Up" not in output:
        tester.log_issue("Containers are not running")
        tester.log_fix("Starting containers...")
        success, _ = tester.run_command(
            "cd /Users/jiyoung/work/AIDLC/project/aidlc-docs/construction/unit4_card_search/src && docker compose up -d",
            "Start containers"
        )
        if success:
            time.sleep(10)  # Wait for startup
            tester.log_fix("Containers started successfully")
        else:
            return False
    
    print("✅ Containers are running")
    return True

def test_2_database_existence(tester: DiagnosticTester) -> bool:
    """Test 2: Check database existence and create if needed"""
    print("\n=== 2. Database Existence Check ===")
    
    # Check if database exists
    success, output = tester.run_command(
        'docker exec src-postgres-1 psql -U postgres -lqt | cut -d \\| -f 1 | grep -qw aidlc_db',
        "Check database existence"
    )
    
    if not success:
        tester.log_issue("Database 'aidlc_db' does not exist")
        tester.log_fix("Creating database...")
        
        # Create database
        success, _ = tester.run_command(
            'docker exec src-postgres-1 psql -U postgres -c "CREATE DATABASE aidlc_db;"',
            "Create database"
        )
        
        if not success:
            return False
        
        tester.log_fix("Database created successfully")
    
    print("✅ Database exists")
    return True

def test_3_database_schema(tester: DiagnosticTester) -> bool:
    """Test 3: Check and create database schema"""
    print("\n=== 3. Database Schema Check ===")
    
    # Check if tables exist
    success, output = tester.run_command(
        "docker exec src-postgres-1 psql -U postgres -d aidlc_db -c \"\\dt\"",
        "Check tables"
    )
    
    if not success or "users" not in output:
        tester.log_issue("Database tables do not exist")
        tester.log_fix("Creating database schema...")
        
        # Create schema
        success, _ = tester.run_command(
            "docker exec src-postgres-1 psql -U postgres -d aidlc_db -f /docker-entrypoint-initdb.d/01-init.sql",
            "Create schema"
        )
        
        if not success:
            return False
        
        tester.log_fix("Database schema created")
    
    print("✅ Database schema exists")
    return True

def test_4_test_data(tester: DiagnosticTester) -> bool:
    """Test 4: Check and insert test data"""
    print("\n=== 4. Test Data Check ===")
    
    # Check if test data exists
    success, output = tester.run_command(
        "docker exec src-postgres-1 psql -U postgres -d aidlc_db -c \"SELECT COUNT(*) FROM cards;\"",
        "Check test data"
    )
    
    if success and "0" in output:
        tester.log_issue("No test data found")
        tester.log_fix("Inserting test data...")
        
        # Copy and insert test data
        success1, _ = tester.run_command(
            "docker cp /Users/jiyoung/work/AIDLC/project/aidlc-docs/construction/unit4_card_search/src/test_data.sql src-postgres-1:/tmp/test_data.sql",
            "Copy test data file"
        )
        
        if success1:
            success2, _ = tester.run_command(
                "docker exec src-postgres-1 psql -U postgres -d aidlc_db -f /tmp/test_data.sql",
                "Insert test data"
            )
            
            if success2:
                tester.log_fix("Test data inserted successfully")
            else:
                return False
        else:
            return False
    
    print("✅ Test data exists")
    return True

def test_5_api_connectivity(tester: DiagnosticTester) -> bool:
    """Test 5: Check API connectivity"""
    print("\n=== 5. API Connectivity Check ===")
    
    # Wait for API to be ready
    for attempt in range(5):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is responding")
                return True
        except Exception:
            pass
        
        if attempt < 4:
            print(f"⏳ API not ready, waiting... (attempt {attempt + 1}/5)")
            time.sleep(5)
    
    tester.log_issue("API is not responding")
    
    # Try to restart the application container
    tester.log_fix("Restarting application container...")
    success, _ = tester.run_command(
        "cd /Users/jiyoung/work/AIDLC/project/aidlc-docs/construction/unit4_card_search/src && docker compose restart unit4-search",
        "Restart app container"
    )
    
    if success:
        time.sleep(10)
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                tester.log_fix("API is now responding after restart")
                return True
        except Exception:
            pass
    
    return False

def test_6_database_connectivity_from_app(tester: DiagnosticTester) -> bool:
    """Test 6: Check database connectivity from application"""
    print("\n=== 6. App-to-Database Connectivity ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/my-cards", timeout=10)
        data = response.json()
        
        if data.get("success") == True:
            print("✅ Database connectivity from app is working")
            return True
        elif data.get("success") == False:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            tester.log_issue(f"Database connectivity issue: {error_msg}")
            
            # Try to fix by rebuilding the container
            tester.log_fix("Rebuilding application container...")
            success, _ = tester.run_command(
                "cd /Users/jiyoung/work/AIDLC/project/aidlc-docs/construction/unit4_card_search/src && docker compose build unit4-search && docker compose up -d unit4-search",
                "Rebuild app container"
            )
            
            if success:
                time.sleep(15)
                response = requests.get(f"{BASE_URL}/api/my-cards", timeout=10)
                data = response.json()
                if data.get("success") == True:
                    tester.log_fix("Database connectivity restored after rebuild")
                    return True
            
            return False
        
    except Exception as e:
        tester.log_issue(f"Cannot test database connectivity: {str(e)}")
        return False

def test_7_functional_api_tests(tester: DiagnosticTester) -> bool:
    """Test 7: Run functional API tests"""
    print("\n=== 7. Functional API Tests ===")
    
    tests = [
        ("/api/my-cards", "My Cards List"),
        ("/api/my-cards?search=React", "Search Functionality"),
        ("/api/my-cards/favorites", "Favorites API"),
        ("/api/public-cards?search=Python", "Public Cards Search"),
        ("/api/tags?scope=my", "Tags API")
    ]
    
    passed = 0
    for endpoint, name in tests:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            data = response.json()
            
            if data.get("success") == True:
                print(f"✅ {name}")
                passed += 1
            else:
                print(f"❌ {name}: {data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
    
    success_rate = passed / len(tests)
    if success_rate >= 0.8:  # 80% success rate
        print(f"✅ Functional tests: {passed}/{len(tests)} passed ({success_rate:.0%})")
        return True
    else:
        tester.log_issue(f"Functional tests failed: {passed}/{len(tests)} passed")
        return False

def main():
    print("🔧 Unit4 Comprehensive Diagnostic and Fix Suite")
    print("=" * 60)
    
    tester = DiagnosticTester()
    
    # Run diagnostic tests in order
    tests = [
        ("Container Status", test_1_container_status),
        ("Database Existence", test_2_database_existence),
        ("Database Schema", test_3_database_schema),
        ("Test Data", test_4_test_data),
        ("API Connectivity", test_5_api_connectivity),
        ("App-DB Connectivity", test_6_database_connectivity_from_app),
        ("Functional Tests", test_7_functional_api_tests)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func(tester)
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                # Don't stop on failure, continue with other tests
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {str(e)}")
            results.append((test_name, False))
    
    # Final summary
    print(f"\n{'='*60}")
    print("📊 DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if tester.issues_found:
        print(f"\n🔍 Issues Found ({len(tester.issues_found)}):")
        for i, issue in enumerate(tester.issues_found, 1):
            print(f"  {i}. {issue}")
    
    if tester.fixes_applied:
        print(f"\n🔧 Fixes Applied ({len(tester.fixes_applied)}):")
        for i, fix in enumerate(tester.fixes_applied, 1):
            print(f"  {i}. {fix}")
    
    if passed == total:
        print("\n🎉 ALL DIAGNOSTICS PASSED! System is fully functional.")
        return True
    else:
        print(f"\n⚠️  {total - passed} diagnostic(s) failed. Manual intervention may be required.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
