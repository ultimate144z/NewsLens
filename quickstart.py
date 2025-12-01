"""
NewsLens Quick Start Script

Simple command-line runner for common tasks.
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent


def run_dashboard():
    """Launch the Streamlit dashboard."""
    print("Launching NewsLens Dashboard...")
    print("Dashboard will open at: http://localhost:8501")
    print("Press Ctrl+C to stop.")
    
    subprocess.run([
        sys.executable, '-m', 'streamlit', 'run',
        str(project_root / 'app' / 'dashboard.py')
    ])


def run_tests():
    """Run all tests."""
    print("Running NewsLens Test Suite...")
    subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/', '-v'
    ])


def show_help():
    """Show help message."""
    print("""
NewsLens Quick Start

Commands:
    python quickstart.py dashboard    # Launch dashboard
    python quickstart.py tests        # Run tests
    python quickstart.py help         # Show this help

Examples:
    # Launch dashboard
    python quickstart.py dashboard
    
    # Run tests
    python quickstart.py tests

For full pipeline execution, see run.py
    """)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_help()
    elif sys.argv[1] == 'dashboard':
        run_dashboard()
    elif sys.argv[1] == 'tests':
        run_tests()
    elif sys.argv[1] == 'help':
        show_help()
    else:
        print(f"Unknown command: {sys.argv[1]}")
        show_help()
