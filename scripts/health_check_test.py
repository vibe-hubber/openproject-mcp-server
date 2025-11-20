#!/usr/bin/env python3
"""
Health check script for OpenProject MCP Server.

This script tests the connection to the OpenProject API and is used by Docker's
HEALTHCHECK command to monitor container health status.

Exit codes:
    0: Health check passed - OpenProject connection successful
    1: Health check failed - Unable to connect to OpenProject
    2: Health check error - Unexpected error during check
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src directory to path for imports
# Support both Docker (/app/src) and local development paths
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path.resolve()))

try:
    from openproject_client import OpenProjectClient
except ImportError as e:
    print(f"ERROR: Failed to import OpenProjectClient: {e}", file=sys.stderr)
    sys.exit(2)


async def check_health() -> dict:
    """
    Perform health check by testing OpenProject API connection.
    
    Returns:
        dict: Health check result containing success status and details
    """
    client = OpenProjectClient()
    try:
        result = await client.test_connection()
        return result
    except Exception as e:
        return {
            'success': False,
            'message': f'Health check failed: {str(e)}',
            'error': str(e)
        }
    finally:
        await client.close()


def main() -> int:
    """
    Main entry point for health check.
    
    Returns:
        int: Exit code (0 for success, 1 for failure, 2 for error)
    """
    try:
        result = asyncio.run(check_health())
        
        # Print result for logging/debugging
        if result.get('success'):
            print(f"✓ Health check passed - OpenProject v{result.get('openproject_version', 'unknown')}")
        else:
            print(f"✗ Health check failed - {result.get('message', 'Unknown error')}", file=sys.stderr)
        
        return 0 if result.get('success') else 1
        
    except KeyboardInterrupt:
        print("\nHealth check interrupted by user", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: Unexpected error during health check: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
