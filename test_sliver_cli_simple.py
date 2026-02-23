#!/usr/bin/env python3
"""
简单测试脚本 - 测试新的 CLI 版本的 Sliver.py
"""

import asyncio
from attack_executor.config import load_config
from attack_executor.post_exploit.Sliver import SliverExecutor

async def main():
    print("=" * 60)
    print("测试 Sliver CLI Executor")
    print("=" * 60)

    # 加载配置
    config = load_config(config_file_path="/home/lexuswang/Aurora-executor-demo/config.ini")

    # 创建 executor
    print("\n[1/4] 初始化 Sliver Executor...")
    sliver_executor = SliverExecutor(config=config)
    print("✓ 初始化成功")

    try:
        # 列出会话
        print("\n[2/4] 获取会话列表...")
        session_id = await sliver_executor.select_sessions()

        if not session_id:
            print("⚠ 没有可用的会话")
            print("\n提示：请确保有 Sliver implant 连接到服务器")
            return

        print(f"✓ 已选择会话: {session_id}")

        # 测试基本命令
        print("\n[3/4] 测试基本命令...")

        print("\n  执行: pwd")
        await sliver_executor.pwd(session_id)

        print("\n  执行: whoami")
        await sliver_executor.whoami(session_id)

        # 截图测试
        print("\n[4/4] 测试截图功能...")
        await sliver_executor.screenshot(session_id)

        print("\n" + "=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理
        if sliver_executor.console and sliver_executor.console.isalive():
            print("\n清理连接...")
            sliver_executor.console.sendline('exit')

if __name__ == "__main__":
    asyncio.run(main())
