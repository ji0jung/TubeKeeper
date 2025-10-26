#!/usr/bin/env python3
"""
Unit4 Performance Test Suite with Data Management
Tests API performance under various load conditions with automatic data setup/cleanup.
"""

import requests
import time
import statistics
import concurrent.futures
import subprocess
import sys
from typing import List

BASE_URL = "http://localhost:8004"

class PerformanceTester:
    """Performance test suite with automatic data management."""
    
    def __init__(self):
        self.results = []
        
    def setup_performance_test_data(self) -> bool:
        """
        Set up test data optimized for performance testing.
        Creates larger dataset for realistic performance testing.
        """
        print("🔧 Setting up performance test data...")
        
        try:
            # Clear existing data
            self._run_db_command("DELETE FROM cards; DELETE FROM categories; DELETE FROM users;")
            
            # Insert test users
            self._run_db_command("""
                INSERT INTO users (id, email, name) VALUES 
                ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'Test User'),
                ('550e8400-e29b-41d4-a716-446655440010', 'user2@example.com', 'User Two'),
                ('550e8400-e29b-41d4-a716-446655440020', 'user3@example.com', 'User Three');
            """)
            
            # Insert categories
            self._run_db_command("""
                INSERT INTO categories (id, user_id, name) VALUES 
                ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', '개발'),
                ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', '디자인'),
                ('550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440010', '마케팅');
            """)
            
            # Insert multiple cards for performance testing
            cards_sql = """
                INSERT INTO cards (id, user_id, category_id, title, content_url, summary, tags, is_favorite, is_public, favorited_at) VALUES 
            """
            
            card_values = []
            for i in range(20):  # Create 20 test cards
                user_id = '550e8400-e29b-41d4-a716-446655440000' if i < 15 else '550e8400-e29b-41d4-a716-446655440010'
                category_id = '550e8400-e29b-41d4-a716-446655440001' if i % 2 == 0 else '550e8400-e29b-41d4-a716-446655440002'
                is_favorite = 'true' if i < 3 else 'false'
                is_public = 'true' if i % 3 == 0 else 'false'
                favorited_at = 'NOW()' if is_favorite == 'true' else 'NULL'
                
                card_values.append(f"""
                    ('550e8400-e29b-41d4-a716-44665544{i:04d}', '{user_id}', '{category_id}', 
                     'Test Card {i}', 'https://youtube.com/watch?v=test{i}', 
                     'Test summary for card {i}', ARRAY['tag{i}', 'test', 'performance'], 
                     {is_favorite}, {is_public}, {favorited_at})
                """)
            
            full_sql = cards_sql + ','.join(card_values) + ";"
            self._run_db_command(full_sql)
            
            print("✅ Performance test data setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Performance test data setup failed: {str(e)}")
            return False
    
    def cleanup_test_data(self) -> bool:
        """Clean up performance test data."""
        print("🧹 Cleaning up performance test data...")
        
        try:
            self._run_db_command("DELETE FROM cards; DELETE FROM categories; DELETE FROM users;")
            print("✅ Performance test data cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Performance test data cleanup failed: {str(e)}")
            return False
    
    def _run_db_command(self, sql: str) -> bool:
        """Execute SQL command on test database."""
        try:
            result = subprocess.run([
                'docker', 'exec', 'src-postgres-1', 'psql', 
                '-U', 'postgres', '-d', 'aidlc_db', '-c', sql
            ], capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False
        
    def measure_response_time(self, url: str, iterations: int = 10) -> List[float]:
        """
        Measure response times for multiple requests.
        
        Args:
            url: API endpoint to test
            iterations: Number of requests to make
            
        Returns:
            List of response times in milliseconds
        """
        times = []
        for _ in range(iterations):
            start_time = time.time()
            try:
                response = requests.get(f"{BASE_URL}{url}", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append((end_time - start_time) * 1000)  # Convert to ms
            except Exception:
                pass  # Skip failed requests
        
        return times
    
    def concurrent_requests(self, url: str, concurrent_users: int = 10) -> List[float]:
        """
        Test concurrent requests performance.
        
        Args:
            url: API endpoint to test
            concurrent_users: Number of concurrent requests
            
        Returns:
            List of response times in milliseconds
        """
        def make_request():
            start_time = time.time()
            try:
                response = requests.get(f"{BASE_URL}{url}", timeout=10)
                end_time = time.time()
                return (end_time - start_time) * 1000 if response.status_code == 200 else None
            except Exception:
                return None
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_users)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return [r for r in results if r is not None]
    
    def analyze_performance(self, name: str, times: List[float]) -> bool:
        """
        Analyze and report performance metrics.
        
        Args:
            name: Test name
            times: List of response times
            
        Returns:
            True if performance meets criteria
        """
        if not times:
            print(f"❌ {name}: No successful requests")
            return False
        
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
    """Main performance test execution function."""
    print("⚡ Unit4 Performance Test Suite with Data Management")
    print("=" * 60)
    
    tester = PerformanceTester()
    
    # Setup performance test data
    if not tester.setup_performance_test_data():
        print("❌ Failed to setup performance test data. Exiting.")
        return False
    
    try:
        # Wait for data to be ready
        time.sleep(3)
        
        passed_tests = 0
        total_tests = 0
        
        # 1. Basic Endpoint Performance
        print("\n=== 1. Basic Endpoint Performance ===")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/api/my-cards", "My Cards List"),
            ("/api/my-cards?search=Test", "Search Query"),
            ("/api/my-cards?tag=test", "Tag Filter"),
            ("/api/my-cards/favorites", "Favorites"),
            ("/api/public-cards?search=Test", "Public Cards Search"),
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
            ("/api/my-cards?search=Test", "Search - 10 concurrent")
        ]
        
        for endpoint, name in load_tests:
            times = tester.concurrent_requests(endpoint, concurrent_users=10)
            if tester.analyze_performance(name, times):
                passed_tests += 1
            total_tests += 1
        
        # 3. Database Query Performance
        print(f"\n=== 3. Database Query Performance ===")
        
        db_tests = [
            ("/api/my-cards?limit=20", "Large Result Set"),
            ("/api/public-cards?search=test&page=1", "Public Search with Pagination"),
            ("/api/tags?scope=public", "Tag Aggregation Query")
        ]
        
        for endpoint, name in db_tests:
            times = tester.measure_response_time(endpoint, iterations=3)
            if tester.analyze_performance(name, times):
                passed_tests += 1
            total_tests += 1
        
        # Summary
        print(f"\n📊 Performance Test Summary: {passed_tests}/{total_tests} passed")
        
        success = passed_tests == total_tests
        if success:
            print("🎉 All performance tests passed! API is ready for production.")
        else:
            print("⚠️  Some performance issues detected. Consider optimization.")
        
        return success
        
    finally:
        # Always cleanup test data
        tester.cleanup_test_data()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
