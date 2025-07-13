#!/usr/bin/env python3
"""
Test runner for AI Coach application.
Runs all unit tests and provides a summary.
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests and return results."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

def main():
    """Main test runner function."""
    print("🧪 Running AI Coach Unit Tests...")
    print("=" * 50)
    
    # Run tests
    result = run_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        
        # Print failure details
        if result.failures:
            print("\n🔍 Failures:")
            for test, traceback in result.failures:
                print(f"   {test}: {traceback}")
        
        if result.errors:
            print("\n🚨 Errors:")
            for test, traceback in result.errors:
                print(f"   {test}: {traceback}")
        
        return 1

if __name__ == '__main__':
    sys.exit(main()) 