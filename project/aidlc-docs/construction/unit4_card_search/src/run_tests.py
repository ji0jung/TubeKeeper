#!/usr/bin/env python3
"""Unit4 Unified Test Runner"""

import subprocess
import sys
import time

def run_test_suite(test_file: str, description: str) -> bool:
    """Run a test suite and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run {test_file}: {e}")
        return False

def main():
    print("🚀 Unit4 Card Search & Display - Complete Test Suite")
    print("=" * 60)
    
    # Check if API is running
    import requests
    try:
        response = requests.get("http://localhost:8004/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not running. Please start the service first.")
            print("   Run: docker compose up -d")
            return False
    except Exception:
        print("❌ Cannot connect to API at http://localhost:8004")
        print("   Run: docker compose up -d")
        return False
    
    print("✅ API is running and accessible")
    
    # Test suites to run
    test_suites = [
        ("test_api_fixed.py", "Functional API Tests"),
        ("test_performance.py", "Performance & Load Tests")
    ]
    
    results = []
    start_time = time.time()
    
    for test_file, description in test_suites:
        success = run_test_suite(test_file, description)
        results.append((description, success))
        
        if not success:
            print(f"\n❌ {description} failed!")
        else:
            print(f"\n✅ {description} passed!")
    
    # Summary
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n{'='*60}")
    print("📊 FINAL TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} test suites passed")
    print(f"⏱️  Total execution time: {total_time:.1f} seconds")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Unit4 is ready for production.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed. Please review and fix.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
