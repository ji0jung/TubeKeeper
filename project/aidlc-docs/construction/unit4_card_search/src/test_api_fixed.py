#!/usr/bin/env python3
"""Unit4 Fixed Advanced API Test Suite"""

import requests
import json
import sys
from typing import Dict, Any, List

BASE_URL = "http://localhost:8004"

class FixedAPITester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        
    def test_api(self, name: str, url: str, validator_func, method: str = "GET", data: Dict = None):
        """Generic API test with custom validator"""
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{url}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{url}", json=data)
            
            json_data = response.json()
            
            if validator_func(response, json_data):
                print(f"✅ {name}")
                self.passed += 1
                return json_data
            else:
                print(f"❌ {name}")
                self.failed += 1
                return None
                
        except Exception as e:
            print(f"❌ {name}: Exception - {str(e)}")
            self.failed += 1
            return None
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n📊 Test Summary: {self.passed}/{total} passed ({self.failed} failed)")
        return self.failed == 0

def main():
    tester = FixedAPITester()
    
    print("🔧 Unit4 Fixed API Test Suite Starting...\n")
    
    # 1. Basic API Tests
    print("=== 1. Basic API Functionality ===")
    
    tester.test_api(
        "Health Check",
        "/health",
        lambda resp, data: resp.status_code == 200 and data.get("status") == "healthy"
    )
    
    tester.test_api(
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
    
    # 2. Search Functionality Tests
    print("\n=== 2. Search Functionality ===")
    
    tester.test_api(
        "React Search - Returns Results",
        "/api/my-cards?search=React",
        lambda resp, data: (
            data.get("success") == True and
            len(data.get("data", {}).get("cards", [])) > 0 and
            any("React" in card.get("title", "") for card in data["data"]["cards"])
        )
    )
    
    tester.test_api(
        "JavaScript Tag Search",
        "/api/my-cards?tag=javascript", 
        lambda resp, data: (
            data.get("success") == True and
            any("javascript" in card.get("tags", []) for card in data.get("data", {}).get("cards", []))
        )
    )
    
    tester.test_api(
        "Nonexistent Tag - Empty Results",
        "/api/my-cards?tag=nonexistent",
        lambda resp, data: (
            data.get("success") == True and
            len(data.get("data", {}).get("cards", [])) == 0
        )
    )
    
    # 3. Favorites API
    print("\n=== 3. Favorites API ===")
    
    tester.test_api(
        "Favorites - Only Favorite Cards",
        "/api/my-cards/favorites",
        lambda resp, data: (
            data.get("success") == True and
            all(card.get("isFavorite", False) for card in data.get("data", {}).get("cards", []))
        )
    )
    
    # 4. Public Cards API
    print("\n=== 4. Public Cards API ===")
    
    tester.test_api(
        "Public Cards - Keyword Search",
        "/api/public-cards?search=Python",
        lambda resp, data: (
            data.get("success") == True and
            "totalCount" in data.get("data", {}) and
            "currentPage" in data.get("data", {}) and
            isinstance(data["data"]["cards"], list)
        )
    )
    
    tester.test_api(
        "Public Cards - Tag Search", 
        "/api/public-cards?tag=ml",
        lambda resp, data: (
            data.get("success") == True and
            isinstance(data.get("data", {}).get("cards", []), list)
        )
    )
    
    # 5. Error Handling Tests
    print("\n=== 5. Error Handling ===")
    
    tester.test_api(
        "Public Cards - Keyword+Tag Forbidden",
        "/api/public-cards?search=Python&tag=ml",
        lambda resp, data: (
            data.get("success") == False and
            data.get("error", {}).get("code") == "SEARCH_001"
        )
    )
    
    tester.test_api(
        "Public Cards - No Parameters Forbidden",
        "/api/public-cards",
        lambda resp, data: (
            data.get("success") == False and
            data.get("error", {}).get("code") == "SEARCH_001"
        )
    )
    
    tester.test_api(
        "Invalid UUID Format",
        "/api/my-cards?category_id=invalid-uuid",
        lambda resp, data: (
            data.get("success") == False and
            data.get("error", {}).get("code") == "SEARCH_009"
        )
    )
    
    tester.test_api(
        "404 Not Found",
        "/api/invalid-endpoint",
        lambda resp, data: resp.status_code == 404
    )
    
    # 6. Parameter Validation
    print("\n=== 6. Parameter Validation ===")
    
    tester.test_api(
        "Invalid Limit (Negative)",
        "/api/my-cards?limit=-1",
        lambda resp, data: resp.status_code == 422
    )
    
    tester.test_api(
        "Invalid Limit (Too Large)",
        "/api/my-cards?limit=1000", 
        lambda resp, data: resp.status_code == 422
    )
    
    tester.test_api(
        "Invalid Page (Zero)",
        "/api/public-cards?search=test&page=0",
        lambda resp, data: resp.status_code == 422
    )
    
    # 7. Tags API
    print("\n=== 7. Tags API ===")
    
    tester.test_api(
        "My Tags - Valid Structure",
        "/api/tags?scope=my",
        lambda resp, data: (
            data.get("success") == True and
            isinstance(data.get("data", {}).get("tags", []), list) and
            all(isinstance(tag.get("name"), str) and isinstance(tag.get("count"), int) 
                for tag in data["data"]["tags"])
        )
    )
    
    tester.test_api(
        "Public Tags - Valid Structure", 
        "/api/tags?scope=public",
        lambda resp, data: (
            data.get("success") == True and
            isinstance(data.get("data", {}).get("tags", []), list)
        )
    )
    
    # 8. Pagination Tests
    print("\n=== 8. Pagination ===")
    
    tester.test_api(
        "Limit Parameter Works",
        "/api/my-cards?limit=2",
        lambda resp, data: (
            data.get("success") == True and
            len(data.get("data", {}).get("cards", [])) <= 2
        )
    )
    
    tester.test_api(
        "Cursor Pagination Structure",
        "/api/my-cards",
        lambda resp, data: (
            data.get("success") == True and
            "nextCursor" in data.get("data", {}) and
            "hasMore" in data.get("data", {}) and
            isinstance(data["data"]["hasMore"], bool)
        )
    )
    
    # 9. POST API Tests
    print("\n=== 9. POST API ===")
    
    tester.test_api(
        "Save Public Card",
        "/api/public-cards/550e8400-e29b-41d4-a716-446655440200/save",
        lambda resp, data: (
            resp.status_code == 200 and
            data.get("success") == True and
            "newCard" in data.get("data", {}) and
            "alreadyExists" in data.get("data", {})
        ),
        method="POST",
        data={}
    )
    
    return tester.summary()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
