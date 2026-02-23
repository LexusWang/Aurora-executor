import asyncio
import os
import grpc

# Set environment variables before importing sliver
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384'
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''

from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from typing import Dict

console = Console()
user_params: Dict[str, str] = {}
pddl_parameters = {}
executor_dict = {}

def print_welcome_message():
    console.print(
        Panel(
            "[bold blink yellow]🎯 Welcome to Attack Execution Wizard[/]",
            title="[bold green]Hello[/]",
            subtitle="[bold blue]Let's Begin[/]",
            expand=False,
        )
    )

def confirm_action(prompt: str = "Keep going with the next attack step?") -> bool:
    styled_prompt = f"[bold bright_cyan]{prompt}[/]"
    return Confirm.ask(
        styled_prompt,
        default="y",
        choices=["y", "n"],
        show_default=False,
    )

async def main():
    print_welcome_message()
    from attack_executor.config import load_config
    config = load_config(config_file_path="/home/lexuswang/Aurora-executor-demo/config.ini")

    # Initialize Sliver executor
    from attack_executor.post_exploit.Sliver import SliverExecutor
    sliver_executor = SliverExecutor(config=config)

    console.print("[bold cyan]Attempting to connect to Sliver server...[/]")
    try:
        selected_session = await sliver_executor.select_sessions()
        user_params["SessionID"] = selected_session
        pddl_parameters["executor4"] = selected_session
        executor_dict["executor4"] = {
            "type": "Sliver Executor",
            "isDerivedExecutor": False,
            "RealSessionID": selected_session,
            "parentExecutor": None
        }

        console.print(f"[bold green]✓ Connected! Session ID: {selected_session}[/]")

        # Test screenshot functionality
        console.print(f"[bold cyan]\n📌[Sliver Executor] Taking screenshot[/]")
        confirm_action()
        try:
            await sliver_executor.screenshot(selected_session)
            console.print("[bold green]✓ Screenshot taken successfully![/]")
        except Exception as e:
            console.print(f"[bold red]✗ Screenshot failed: {str(e)}[/]")
            raise

    except Exception as e:
        console.print(f"[bold red]✗ Connection failed: {str(e)}[/]")
        console.print(f"[yellow]Error type: {type(e).__name__}[/]")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())
