#!/usr/bin/env python3
"""
Test runner script for CI/CD pipelines and local development
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description="Running command"):
    """Run a command and return the result"""
    print(f"\n{description}...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Run tests for weather MCP server")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--fail-fast", "-x", 
        action="store_true", 
        help="Stop on first failure"
    )
    parser.add_argument(
        "--parallel", "-n", 
        type=int, 
        help="Number of parallel workers for pytest-xdist"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("weather_mcp").exists():
        print("Error: Must run from project root directory")
        sys.exit(1)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test type marker
    if args.type == "unit":
        cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        cmd.extend(["-m", "integration"])
    # "all" runs everything (no marker filter)
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=weather_mcp",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=80"
        ])
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add fail-fast
    if args.fail_fast:
        cmd.append("-x")
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add test directory
    cmd.append("tests/")
    
    # Run the tests
    result = run_command(cmd, f"Running {args.type} tests")
    
    if result.returncode == 0:
        print(f"\n✅ {args.type.capitalize()} tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ {args.type.capitalize()} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 