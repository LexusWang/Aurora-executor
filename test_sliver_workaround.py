#!/usr/bin/env python3
"""
Test workaround for Sliver gRPC/OpenSSL compatibility issue.
This script attempts to bypass the ECC certificate signature algorithm incompatibility.
"""

import asyncio
import os
import sys

# Try to patch SSL before importing grpc
try:
    import ssl
    # Create a less strict SSL context
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

# Set environment variables before importing sliver
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH:!aNULL:!eNULL:@STRENGTH'
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''

from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from typing import Dict

console = Console()

def print_welcome_message():
    console.print(
        Panel(
            "[bold blink yellow]🎯 Welcome to Attack Execution Wizard[/]",
            title="[bold green]Hello[/]",
            subtitle="[bold blue]Let's Begin[/]",
            expand=False,
        )
    )

async def main():
    print_welcome_message()

    try:
        # Import after environment setup
        from attack_executor.config import load_config
        from attack_executor.post_exploit.Sliver import SliverExecutor

        config = load_config(config_file_path="/home/lexuswang/Aurora-executor-demo/config.ini")

        console.print("[bold cyan]Initializing Sliver executor with workarounds...[/]")
        sliver_executor = SliverExecutor(config=config)

        console.print("[bold cyan]Attempting to connect and list sessions...[/]")
        selected_session = await sliver_executor.select_sessions()

        if selected_session:
            console.print(f"[bold green]✓ Successfully connected! Session ID: {selected_session}[/]")

            # Test screenshot
            console.print(f"[bold cyan]Taking screenshot...[/]")
            await sliver_executor.screenshot(selected_session)
            console.print("[bold green]✓ Screenshot completed![/]")
        else:
            console.print("[bold yellow]No sessions available[/]")

    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/]")
        console.print(f"[yellow]Error type: {type(e).__name__}[/]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
