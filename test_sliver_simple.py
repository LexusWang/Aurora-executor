#!/usr/bin/env python3
import asyncio
from attack_executor.post_exploit.Sliver import SliverExecutor

async def main():
    sliver_exe = SliverExecutor("/home/lexuswang/Aurora-executor-demo/zer0cool.cfg")

    print("Testing Sliver CLI connection...")
    print("=" * 60)

    # Test raw command output
    result = await sliver_exe._run_sliver_command(['sessions'], timeout=30)

    print(f"Success: {result['success']}")
    print(f"Return Code: {result['returncode']}")
    print(f"\nOutput:\n{result['output']}")
    print(f"\nError:\n{result['error']}")
    print("=" * 60)

    # Test session parsing
    sessions = sliver_exe._parse_sessions(result['output'])
    print(f"\nParsed Sessions: {sessions}")

if __name__ == "__main__":
    asyncio.run(main())
