"""
NewsLens Test Runner

Comprehensive test suite runner for all modules.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Run all tests with coverage."""
    print("=" * 70)
    print("NEWSLENS COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Run pytest with coverage
    args = [
        'tests/',
        '-v',
        '--tb=short',
        '--color=yes',
        '--cov=src',
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
    ]
    
    exit_code = pytest.main(args)
    
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("ALL TESTS PASSED")
        print("Coverage report generated in: htmlcov/index.html")
    else:
        print("SOME TESTS FAILED")
    print("=" * 70)
    
    return exit_code


def run_module_tests(module):
    """Run tests for a specific module."""
    test_file = Path('tests') / f'test_{module}.py'
    
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return 1
    
    print(f"Running tests for: {module}")
    args = [str(test_file), '-v', '--tb=short']
    return pytest.main(args)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific module tests
        module = sys.argv[1]
        exit_code = run_module_tests(module)
    else:
        # Run all tests
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
