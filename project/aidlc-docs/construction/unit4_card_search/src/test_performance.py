#!/usr/bin/env python3
"""Unit4 Performance and Load Test Suite"""

import requests
import time
import statistics
import concurrent.futures
import sys
from typing import List

BASE_URL = "http://localhost:8004"

class PerformanceTester:
    def __init__(self):
        self.results = []
        
    def measure_response_time(self, url: str, iterations: int = 10) -> List[float]:
        """Measure response times for multiple requests"""
        times = []
        for _ in range(iterations):
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{url}")
            end_time = time.time()
            
            if response.status_code == 200:
                times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return times
    
    def concurrent_requests(self, url: str, concurrent_users: int = 10) -> List[float]:
        """Test concurrent requests"""
        def make_request():
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{url}")
            end_time = time.time()
            return (end_time - start_time) * 1000 if response.status_code == 200 else None
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_users)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return [r for r in results if r is not None]
    
    def analyze_performance(self, name: str, times: List[float]):
        """Analyze and report performance metrics"""
        if not times:
            print(f"❌ {name}: No successful requests")
            return
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        
        # Performance thresholds
        if avg_time < 100:
            status = "🟢 Excellent"
        elif avg_time < 500:
            status = "🟡 Good"
        elif avg_time < 1000:
            status = "🟠 Acceptable"
        else:
            status = "🔴 Slow"
        
        print(f"{status} {name}:")
        print(f"   📊 Avg: {avg_time:.1f}ms | Min: {min_time:.1f}ms | Max: {max_time:.1f}ms | Median: {median_time:.1f}ms")
        
        return avg_time < 1000  # Pass if under 1 second

def main():
    tester = PerformanceTester()
    passed_tests = 0
    total_tests = 0
    
    print("⚡ Unit4 Performance Test Suite Starting...\n")
    
    # 1. Basic Endpoint Performance
    print("=== 1. Basic Endpoint Performance ===")
    
    endpoints = [
        ("/health", "Health Check"),
        ("/api/my-cards", "My Cards List"),
        ("/api/my-cards?search=React", "Search Query"),
        ("/api/my-cards?tag=javascript", "Tag Filter"),
        ("/api/my-cards/favorites", "Favorites"),
        ("/api/public-cards?search=Python", "Public Cards Search"),
        ("/api/tags?scope=my", "Tags API")
    ]
    
    for endpoint, name in endpoints:
        times = tester.measure_response_time(endpoint, iterations=5)
        if tester.analyze_performance(name, times):
            passed_tests += 1
        total_tests += 1
    
    # 2. Load Testing
    print(f"\n=== 2. Concurrent Load Testing ===")
    
    load_tests = [
        ("/health", "Health Check - 10 concurrent"),
        ("/api/my-cards", "My Cards - 10 concurrent"),
        ("/api/my-cards?search=React", "Search - 10 concurrent")
    ]
    
    for endpoint, name in load_tests:
        times = tester.concurrent_requests(endpoint, concurrent_users=10)
        if tester.analyze_performance(name, times):
            passed_tests += 1
        total_tests += 1
    
    # 3. Database Query Performance
    print(f"\n=== 3. Database Query Performance ===")
    
    db_tests = [
        ("/api/my-cards?limit=50", "Large Result Set"),
        ("/api/public-cards?search=test&page=1", "Public Search with Pagination"),
        ("/api/tags?scope=public", "Tag Aggregation Query")
    ]
    
    for endpoint, name in db_tests:
        times = tester.measure_response_time(endpoint, iterations=3)
        if tester.analyze_performance(name, times):
            passed_tests += 1
        total_tests += 1
    
    # 4. Edge Case Performance
    print(f"\n=== 4. Edge Case Performance ===")
    
    edge_tests = [
        ("/api/my-cards?search=" + "a" * 100, "Long Search Query"),
        ("/api/public-cards?search=nonexistent", "No Results Query"),
        ("/api/my-cards?tag=nonexistent", "Empty Tag Search")
    ]
    
    for endpoint, name in edge_tests:
        times = tester.measure_response_time(endpoint, iterations=3)
        if tester.analyze_performance(name, times):
            passed_tests += 1
        total_tests += 1
    
    # 5. Error Response Performance
    print(f"\n=== 5. Error Response Performance ===")
    
    # Test error responses are fast
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/api/public-cards")  # Should return error
    end_time = time.time()
    error_time = (end_time - start_time) * 1000
    
    if error_time < 100:
        print(f"🟢 Error Response: {error_time:.1f}ms")
        passed_tests += 1
    else:
        print(f"🔴 Error Response: {error_time:.1f}ms (too slow)")
    total_tests += 1
    
    # Summary
    print(f"\n📊 Performance Test Summary: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All performance tests passed! API is ready for production.")
        return True
    else:
        print("⚠️  Some performance issues detected. Consider optimization.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
