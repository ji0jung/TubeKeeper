#!/usr/bin/env python3
"""
Unit4 Complete Test Suite with Data Management
Handles test data setup, execution, and cleanup automatically.
"""

import requests
import subprocess
import sys
import time
from typing import Dict, Any, List

BASE_URL = "http://localhost:8004"

class CompleteAPITester:
    """Complete API test suite with automatic data management."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        
    def setup_test_data(self) -> bool:
        """
        Set up clean test data for testing.
        Clears existing data and inserts fresh test data.
        """
        print("🔧 Setting up test data...")
        
        try:
            # Clear existing data
            self._run_db_command("DELETE FROM cards; DELETE FROM categories; DELETE FROM users;")
            
            # Insert test users
            self._run_db_command("""
                INSERT INTO users (id, email, name) VALUES 
                ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'Test User'),
                ('550e8400-e29b-41d4-a716-446655440010', 'user2@example.com', 'User Two');
            """)
            
            # Insert test categories
            self._run_db_command("""
                INSERT INTO categories (id, user_id, name) VALUES 
                ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', '개발'),
                ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', '디자인');
            """)
            
            # Insert test cards
            self._run_db_command("""
                INSERT INTO cards (id, user_id, category_id, title, content_url, summary, tags, is_favorite, is_public, favorited_at) VALUES 
                ('550e8400-e29b-41d4-a716-446655440100', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440001', 'React 완벽 가이드', 'https://youtube.com/watch?v=react', 'React 기초부터 고급까지', ARRAY['react', 'javascript', 'frontend'], true, true, NOW()),
                ('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440001', 'Node.js 백엔드', 'https://youtube.com/watch?v=nodejs', 'Express 백엔드 개발', ARRAY['nodejs', 'backend'], false, true, NULL),
                ('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440002', 'UI/UX 디자인', 'https://youtube.com/watch?v=uiux', '사용자 경험 디자인', ARRAY['design', 'ui', 'ux'], true, false, NOW()),
                ('550e8400-e29b-41d4-a716-446655440200', '550e8400-e29b-41d4-a716-446655440010', NULL, 'Python 머신러닝', 'https://youtube.com/watch?v=python', 'ML 기초 가이드', ARRAY['python', 'ml'], false, true, NULL);
            """)
            
            print("✅ Test data setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Test data setup failed: {str(e)}")
            return False
    
    def cleanup_test_data(self) -> bool:
        """
        Clean up test data after testing.
        Removes all test data from database.
        """
        print("🧹 Cleaning up test data...")
        
        try:
            self._run_db_command("DELETE FROM cards; DELETE FROM categories; DELETE FROM users;")
            print("✅ Test data cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Test data cleanup failed: {str(e)}")
            return False
    
    def _run_db_command(self, sql: str) -> bool:
        """Execute SQL command on test database."""
        try:
            result = subprocess.run([
                'docker', 'exec', 'src-postgres-1', 'psql', 
                '-U', 'postgres', '-d', 'aidlc_db', '-c', sql
            ], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def test_api(self, name: str, url: str, validator_func, method: str = "GET", data: Dict = None):
        """
        Execute API test with custom validator function.
        
        Args:
            name: Test case name
            url: API endpoint URL
            validator_func: Function to validate response
            method: HTTP method (GET/POST)
            data: Request data for POST requests
        """
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{url}", timeout=10)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{url}", json=data, timeout=10)
            
            json_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            
            if validator_func(response, json_data):
                print(f"✅ {name}")
                self.passed += 1
                return json_data
            else:
                print(f"❌ {name}")
                self.failed += 1
                return None
                
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            self.failed += 1
            return None
    
    def run_basic_functionality_tests(self):
        """Test basic API functionality including health checks and core endpoints."""
        print("\n=== 1. Basic API Functionality ===")
        
        self.test_api(
            "Health Check",
            "/health",
            lambda resp, data: resp.status_code == 200 and data.get("status") == "healthy"
        )
        
        self.test_api(
            "My Cards - Standard Response",
            "/api/my-cards",
            lambda resp, data: (
                resp.status_code == 200 and
                data.get("success") == True and
                "data" in data and
                "cards" in data["data"] and
                isinstance(data["data"]["cards"], list)
            )
        )
    
    def run_search_functionality_tests(self):
        """Test search functionality including keyword and tag searches."""
        print("\n=== 2. Search Functionality ===")
        
        self.test_api(
            "React Search - Returns Results",
            "/api/my-cards?search=React",
            lambda resp, data: (
                data.get("success") == True and
                len(data.get("data", {}).get("cards", [])) > 0 and
                any("React" in card.get("title", "") for card in data["data"]["cards"])
            )
        )
        
        self.test_api(
            "JavaScript Tag Search",
            "/api/my-cards?tag=javascript", 
            lambda resp, data: (
                data.get("success") == True and
                any("javascript" in card.get("tags", []) for card in data.get("data", {}).get("cards", []))
            )
        )
        
        self.test_api(
            "Nonexistent Tag - Empty Results",
            "/api/my-cards?tag=nonexistent",
            lambda resp, data: (
                data.get("success") == True and
                len(data.get("data", {}).get("cards", [])) == 0
            )
        )
    
    def run_favorites_tests(self):
        """Test favorites functionality."""
        print("\n=== 3. Favorites API ===")
        
        self.test_api(
            "Favorites - Only Favorite Cards",
            "/api/my-cards/favorites",
            lambda resp, data: (
                data.get("success") == True and
                all(card.get("isFavorite", False) for card in data.get("data", {}).get("cards", []))
            )
        )
    
    def run_public_cards_tests(self):
        """Test public cards search functionality."""
        print("\n=== 4. Public Cards API ===")
        
        self.test_api(
            "Public Cards - Keyword Search",
            "/api/public-cards?search=Python",
            lambda resp, data: (
                data.get("success") == True and
                "totalCount" in data.get("data", {}) and
                "currentPage" in data.get("data", {}) and
                isinstance(data["data"]["cards"], list)
            )
        )
        
        self.test_api(
            "Public Cards - Tag Search", 
            "/api/public-cards?tag=ml",
            lambda resp, data: (
                data.get("success") == True and
                isinstance(data.get("data", {}).get("cards", []), list)
            )
        )
    
    def run_error_handling_tests(self):
        """Test error handling and validation."""
        print("\n=== 5. Error Handling ===")
        
        self.test_api(
            "Public Cards - Keyword+Tag Forbidden",
            "/api/public-cards?search=Python&tag=ml",
            lambda resp, data: (
                data.get("success") == False and
                data.get("error", {}).get("code") == "SEARCH_001"
            )
        )
        
        self.test_api(
            "Public Cards - No Parameters Forbidden",
            "/api/public-cards",
            lambda resp, data: (
                data.get("success") == False and
                data.get("error", {}).get("code") == "SEARCH_001"
            )
        )
        
        self.test_api(
            "404 Not Found",
            "/api/invalid-endpoint",
            lambda resp, data: resp.status_code == 404
        )
    
    def run_parameter_validation_tests(self):
        """Test parameter validation."""
        print("\n=== 6. Parameter Validation ===")
        
        self.test_api(
            "Invalid Limit (Negative)",
            "/api/my-cards?limit=-1",
            lambda resp, data: resp.status_code == 422
        )
        
        self.test_api(
            "Invalid Limit (Too Large)",
            "/api/my-cards?limit=1000", 
            lambda resp, data: resp.status_code == 422
        )
    
    def run_tags_api_tests(self):
        """Test tags API functionality."""
        print("\n=== 7. Tags API ===")
        
        self.test_api(
            "My Tags - Valid Structure",
            "/api/tags?scope=my",
            lambda resp, data: (
                data.get("success") == True and
                isinstance(data.get("data", {}).get("tags", []), list)
            )
        )
    
    def run_pagination_tests(self):
        """Test pagination functionality."""
        print("\n=== 8. Pagination ===")
        
        self.test_api(
            "Limit Parameter Works",
            "/api/my-cards?limit=2",
            lambda resp, data: (
                data.get("success") == True and
                len(data.get("data", {}).get("cards", [])) <= 2
            )
        )
        
        self.test_api(
            "Cursor Pagination Structure",
            "/api/my-cards",
            lambda resp, data: (
                data.get("success") == True and
                "nextCursor" in data.get("data", {}) and
                "hasMore" in data.get("data", {})
            )
        )
    
    def run_post_api_tests(self):
        """Test POST API endpoints."""
        print("\n=== 9. POST API ===")
        
        self.test_api(
            "Save Public Card",
            "/api/public-cards/550e8400-e29b-41d4-a716-446655440200/save",
            lambda resp, data: (
                resp.status_code == 200 and
                data.get("success") == True
            ),
            method="POST",
            data={}
        )
    
    def summary(self):
        """Print test summary and return success status."""
        total = self.passed + self.failed
        print(f"\n📊 Test Summary: {self.passed}/{total} passed ({self.failed} failed)")
        return self.failed == 0

def main():
    """Main test execution function."""
    print("🧪 Unit4 Complete Test Suite with Data Management")
    print("=" * 60)
    
    tester = CompleteAPITester()
    
    # Setup test data
    if not tester.setup_test_data():
        print("❌ Failed to setup test data. Exiting.")
        return False
    
    try:
        # Wait for API to be ready
        time.sleep(2)
        
        # Run all test suites
        tester.run_basic_functionality_tests()
        tester.run_search_functionality_tests()
        tester.run_favorites_tests()
        tester.run_public_cards_tests()
        tester.run_error_handling_tests()
        tester.run_parameter_validation_tests()
        tester.run_tags_api_tests()
        tester.run_pagination_tests()
        tester.run_post_api_tests()
        
        # Print summary
        success = tester.summary()
        
        if success:
            print("\n🎉 ALL TESTS PASSED! API is fully functional.")
        else:
            print("\n⚠️  Some tests failed. Please review and fix.")
        
        return success
        
    finally:
        # Always cleanup test data
        tester.cleanup_test_data()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
