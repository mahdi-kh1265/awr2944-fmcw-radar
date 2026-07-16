"""CLI for AWR2944 + DCA1000 radar research toolkit.

Root command: ``awr``

Existing commands:
    awr doctor                         ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Check setup / environment
    awr inspect-config <yaml>          ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Validate and display config + derived params
    awr parse <bin> --config <yaml>    ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Parse adc_data.bin into radar cube
    awr process <bin> --config <yaml>  ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Full DSP pipeline ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ range profile + range-Doppler
    awr compare-layouts <target>       ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Compare candidate binary layouts

Config management:
    awr config new --preset <name>     ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Generate capture.yaml from preset
    awr config validate <yaml>         ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Deep validation of capture config
    awr config summarize <yaml>        ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Human-readable config summary

Experiment management:
    awr experiment init <name>         ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Scaffold experiment directory

TI bridge:
    awr ti inspect <file>              ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Inspect TI Lua/JSON config file
    awr ti import <file>               ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Import TI config to capture.yaml
    awr ti compare <yaml> <ti_file>    ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Compare our config vs TI config
    awr ti export-lua-template <yaml>  ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Generate Lua template
    awr ti export-dca-config <yaml>    ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Generate DCA1000 JSON config
    awr ti inspect <file>              ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â  Inspect TI Lua/JSON config file
    awr ti import <file>               ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â  Import TI config to capture.yaml
    awr ti compare <yaml> <ti_file>    ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â  Compare our config vs TI config
    awr ti export-lua-template <yaml>  ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â  Generate Lua template
    awr ti export-dca-config <yaml>    ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â  Generate DCA1000 JSON config
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    help="AWR2944 + DCA1000 radar research toolkit.",
    no_args_is_help=True,
)
ports_app = typer.Typer(help="Hardware COM port discovery and management")
app.add_typer(ports_app, name="ports")
hardware_app = typer.Typer(help="Hardware discovery and diagnostics")
app.add_typer(hardware_app, name="hardware")
mmws_app = typer.Typer(help="mmWave Studio backend controller")
# app.add_typer(mmws_app, name="mmws")
mmws_conn_app = typer.Typer(help="Connection-tab control (Lua-based, DIAGNOSTIC ONLY)")
mmws_app.add_typer(mmws_conn_app, name="connection")
mmws_guiconn_app = typer.Typer(help="GUI-button automation for Connection tab (pywinauto) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â OFFICIAL")
mmws_app.add_typer(mmws_guiconn_app, name="gui-connect")
mmws_studio_app = typer.Typer(help="mmWave Studio process management")
mmws_app.add_typer(mmws_studio_app, name="studio")
mmws_bridge_app = typer.Typer(help="C# RSTD bridge management")
mmws_app.add_typer(mmws_bridge_app, name="csharp-bridge")
mmws_matlab_bridge_app = typer.Typer(help="MATLAB-to-Studio bridge diagnostics")
mmws_app.add_typer(mmws_matlab_bridge_app, name="matlab-bridge")

mmws_win32_conn_app = typer.Typer(help="Win32 API backend for Connection tab (pywin32)")
mmws_app.add_typer(mmws_win32_conn_app, name="win32-connect")

mmws_post_app = typer.Typer(help="Post-connection automation (Firmware, RF, Static, Data)")
mmws_app.add_typer(mmws_post_app, name="post")

mmws_internals_app = typer.Typer(help="Internal reflection and diagnostics (Lua/.NET)")
mmws_app.add_typer(mmws_internals_app, name="internals")

dca_app = typer.Typer(help="DCA1000 integration commands")
app.add_typer(dca_app, name="dca")

adc_app = typer.Typer(help="ADC data commands")
app.add_typer(adc_app, name="adc")

capture_smoke_app = typer.Typer(help="DCA capture smoke workflow")
# dca_app.add_typer(capture_smoke_app, name="capture-smoke")

manual_app = typer.Typer(help="Manual Lua scripts for the mmWave Studio Lua Shell")
mmws_app.add_typer(manual_app, name="manual")

project_app = typer.Typer(help="Project management commands", no_args_is_help=True)
app.add_typer(project_app, name="project")

capture_mgmt_app = typer.Typer(help="Capture management commands", no_args_is_help=True)
app.add_typer(capture_mgmt_app, name="capture")

# ---------------------------------------------------------------------------
# Hardware Doctor Commands
# ---------------------------------------------------------------------------

@app.command("doctor")
def doctor_cmd(
    project_root: Optional[Path] = typer.Option(None, help="Project root (auto-detected if omitted)"),
    offline: bool = typer.Option(False, "--offline", help="Run only offline checks"),
) -> None:
    """Run project health and hardware diagnostics (alias for 'hardware verify')."""
    from awr2944_dca.lab import RadarProject
    
    if project_root:
        project = RadarProject.open(project_root)
    else:
        project = RadarProject.open_here()
        
    report = project.doctor(include_hardware=not offline)
    report.print()
    report.raise_for_errors(strict=False)

@hardware_app.command("discover")
def hardware_discover_cmd(
    project_root: Optional[Path] = typer.Option(None, help="Project root (auto-detected if omitted)"),
) -> None:
    """Discover connected hardware without comparing to configuration."""
    from awr2944_dca.lab import RadarProject
    
    if project_root:
        project = RadarProject.open(project_root)
    else:
        project = RadarProject.open_here()
        
    report = project.hardware.discover()
    
    from rich.console import Console
    console = Console()
    
    console.print(f"[bold cyan]Hardware Discovery[/bold cyan] (Timestamp: {report.timestamp})")
    
    console.print("\n[bold]Serial Ports (pyserial)[/bold]")
    for p in report.serial_ports:
        console.print(f"  {p.port:8s} {p.name}")
        
    console.print("\n[bold]COM Port Roles (heuristics)[/bold]")
    for p in report.com_ports:
        console.print(f"  {p.com:8s} -> {p.likely_role} (conf={p.confidence})")
        
    console.print("\n[bold]Network Adapters[/bold]")
    for a in report.network_adapters:
        alias = a.get("InterfaceAlias", "")
        ip = a.get("IPAddress", "")
        console.print(f"  {alias}: {ip}")

@hardware_app.command("verify")
def hardware_verify_cmd(
    project_root: Optional[Path] = typer.Option(None, help="Project root (auto-detected if omitted)"),
    offline: bool = typer.Option(False, "--offline", help="Run only offline checks"),
    strict: bool = typer.Option(False, "--strict", help="Raise error on any FAIL, WARN, or SKIP"),
) -> None:
    """Run project health and hardware diagnostics."""
    from awr2944_dca.lab import RadarProject
    
    if project_root:
        project = RadarProject.open(project_root)
    else:
        project = RadarProject.open_here()
        
    report = project.hardware.verify(include_hardware=not offline)
    report.print()
    report.raise_for_errors(strict=strict)


# ---------------------------------------------------------------------------
# mmWave Studio Commands
# ---------------------------------------------------------------------------

@mmws_internals_app.command("lua-dotnet-probe")
def mmws_internals_lua_dotnet_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Generate a Lua script to test luanet reflection in mmWave Studio."""
    from .legacy_mmws.internals import build_lua_dotnet_probe_script
    import uuid

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    script_path = probe_dir / f"lua_dotnet_probe_{run_id}.lua"
    result_path = probe_dir / f"lua_dotnet_probe_result_{run_id}.json"

    script = build_lua_dotnet_probe_script(run_id, str(result_path.resolve()))
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]Generated lua-dotnet-probe script:[/cyan] {script_path}")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{script_path.resolve()}]])[/green]")
    console.print(f"\nResult will be written to: {result_path}")
    console.print(f"\nAfter running, check ti/probe_logs/lua_dotnet_probe_result_*.json to see if luanet exists.")
    
    if verbose:
        console.print("\n[dim]Preview of generated script (first 15 lines):[/dim]")
        preview = "\n".join(script.splitlines()[:15])
        console.print(f"[dim]{preview}[/dim]")

@mmws_internals_app.command("lua-dotnet-connect-probe")
def mmws_internals_lua_dotnet_connect_probe(
    com: str = typer.Option("COM6", "--com", help="COM port"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Generate a Lua script that connects via WinForms controls using luanet."""
    from .legacy_mmws.internals import build_lua_dotnet_connect_script
    import uuid

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    script_path = probe_dir / f"lua_dotnet_connect_{run_id}.lua"
    result_path = probe_dir / f"lua_dotnet_connect_result_{run_id}.json"

    script = build_lua_dotnet_connect_script(run_id, str(result_path.resolve()), com, baud)
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]Generated lua-dotnet-connect script:[/cyan] {script_path}")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{script_path.resolve()}]])[/green]")
    console.print(f"\nResult will be written to: {result_path}")

    if verbose:
        console.print("\n[dim]Preview of generated script (first 15 lines):[/dim]")
        preview = "\n".join(script.splitlines()[:15])
        console.print(f"[dim]{preview}[/dim]")


@mmws_win32_conn_app.command("inspect")
def mmws_win32_conn_inspect(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Dump the Win32 HWND tree of mmWave Studio."""
    from .legacy_mmws.win32_connect import inspect_win32
    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")
            
    probe_dir = _lua_launch_probe_dir()
    
    try:
        inspect_win32(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)
        
    console.print(f"[green]Win32 inspection complete. Tree dumped to: {probe_dir / 'win32_inspect_tree.txt'}[/green]")


@mmws_win32_conn_app.command("click-flow")
def mmws_win32_conn_click_flow(
    com: str = typer.Option("COM6", "--com", help="COM port (e.g. COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Execute the Connection tab flow using Win32 API messages."""
    from .legacy_mmws.win32_connect import click_flow_win32
    
    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")
            
    probe_dir = _lua_launch_probe_dir()
    
    try:
        result = click_flow_win32(
            pid=pid, title_regex=title_regex,
            com_port=com, baud=baud,
            probe_dir=probe_dir, verbose_log=vlog
        )
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)
        
    console.print(f"\n[bold]Status: {result.status}[/bold]")
    if result.device_status_text:
        console.print(f"  Device Status: {result.device_status_text}")
    if result.error:
        console.print(f"  [red]Error: {result.error}[/red]")
        
    if result.status == "CONNECTION_WIN32_SUCCESS":
        console.print("\n[green][OK] Valid AWR2944/GP/SOP:2 connection confirmed via Win32 messages.[/green]")
    else:
        console.print("\n[red][FAIL] Win32 connection state not valid.[/red]")
        raise typer.Exit(1)

@manual_app.command("connect-script")
def mmws_manual_connect_script(
    com: str = typer.Option("COM6", "--com", help="COM port"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Generate a connect script for manual copy/paste into an initialized mmWave Studio."""
    from .legacy_mmws.lua_builder import build_lua_manual_connect_script
    import uuid
    from pathlib import Path

    com_upper = com.upper()
    try:
        com_num = int(com_upper[3:])
    except Exception:
        com_num = 6

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    script_path = probe_dir / f"manual_connect_{run_id}.lua"
    result_path = probe_dir / f"manual_connect_{run_id}_result.json"

    script = build_lua_manual_connect_script(run_id, str(result_path.resolve()), com_num, baud)
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]Generated manual script:[/cyan] {script_path}")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{script_path.resolve()}]])[/green]")
    console.print(f"\nResult will be written to: {result_path}")


mmws_lua_launch_app = typer.Typer(help="Official Studio Lua Launch diagnostics")
mmws_app.add_typer(mmws_lua_launch_app, name="lua-launch")

console = Console()


# ---------------------------------------------------------------------------
# awr doctor
# ---------------------------------------------------------------------------


@app.command()
def doctor(deep: bool = typer.Option(False, help="Run extended checks")) -> None:
    """Check environment, dependencies, and hardware connectivity."""
    table = Table(
        title="[bold]AWR Doctor - Environment Check[/bold]",
        show_lines=True,
    )
    table.add_column("Check", style="cyan", min_width=20)
    table.add_column("Status", min_width=8)
    table.add_column("Details", min_width=40)

    # Python version
    py_ver = platform.python_version()
    py_ok = sys.version_info >= (3, 12)
    table.add_row(
        "Python version",
        "[green]OK[/green]" if py_ok else "[red]FAIL[/red]",
        f"{py_ver} {'(>=3.12 OK)' if py_ok else '(need >=3.12)'}",
    )

    # Core dependencies
    deps = {
        "numpy": "numpy",
        "scipy": "scipy",
        "pydantic": "pydantic",
        "typer": "typer",
        "rich": "rich",
        "pyyaml": "yaml",
        "matplotlib": "matplotlib",
    }
    for name, module in deps.items():
        try:
            mod = __import__(module)
            ver = getattr(mod, "__version__", "?")
            table.add_row(name, "[green]OK[/green]", f"v{ver}")
        except ImportError:
            table.add_row(name, "[red]MISSING[/red]", "pip install needed")

    # Package itself
    try:
        from awr2944_dca import __version__

        table.add_row("awr2944-dca-lab", "[green]OK[/green]", f"v{__version__}")
    except ImportError:
        table.add_row("awr2944-dca-lab", "[red]MISSING[/red]", "pip install -e .")

    # DCA1000 IP placeholder
    table.add_row(
        "DCA1000 IP",
        "[yellow]TODO[/yellow]",
        "Need 192.168.33.30/24 on Ethernet adapter",
    )

    # COM ports placeholder
    table.add_row(
        "COM ports",
        "[yellow]TODO[/yellow]",
        "Detect AWR/DCA FTDI & XDS110 ports",
    )

    # mmWave Studio placeholder
    table.add_row(
        "mmWave Studio",
        "[yellow]TODO[/yellow]",
        r"Search C:\ti\mmwave_studio*",
    )

    console.print(table)

    if deep:
        console.print(
            Panel(
                "[yellow]Deep checks not yet implemented (M2+).[/yellow]\n"
                "Will add: Ethernet ping, COM port enumeration, firmware version check.",
                title="Deep Check",
            )
        )


# ---------------------------------------------------------------------------
# awr inspect-config
# ---------------------------------------------------------------------------


@app.command("inspect-config")
def inspect_config(
    config_path: Path = typer.Argument(..., help="Path to YAML config file"),
) -> None:
    """Validate and display a radar experiment config with derived parameters."""
    from awr2944_dca.config.derived import compute_derived
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.formats.layouts import get_layout

    # Load and validate
    try:
        cfg = RadarConfig.from_yaml(config_path)
    except Exception as e:
        console.print(f"[red]Config validation failed:[/red] {e}")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            f"[bold]{cfg.experiment.name}[/bold]\n{cfg.experiment.description}",
            title="Experiment",
            subtitle=f"Operator: {cfg.experiment.operator}",
        )
    )

    # Config table
    config_table = Table(title="[bold]Configuration[/bold]", show_lines=True)
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value")

    config_table.add_row("Rig", f"{cfg.rig.radar} + {cfg.rig.capture_card}")
    config_table.add_row("TX channels", str(cfg.hardware.tx_enabled))
    config_table.add_row("RX channels", str(cfg.hardware.rx_enabled))
    config_table.add_row("Antenna mode", cfg.hardware.antenna_mode.value)
    config_table.add_row("Samples/chirp", str(cfg.adc.samples_per_chirp))
    config_table.add_row("ADC bits", str(cfg.adc.bits))
    config_table.add_row("ADC mode", "complex" if cfg.adc.is_complex else "real")
    config_table.add_row("LVDS lanes", str(cfg.adc.num_lvds_lanes))
    config_table.add_row("Layout", cfg.adc.layout)
    config_table.add_row("Start freq", f"{cfg.profile.start_freq_ghz} GHz")
    config_table.add_row("Slope", f"{cfg.profile.slope_mhz_per_us} MHz/us")
    config_table.add_row("Sample rate", f"{cfg.profile.sample_rate_ksps} ksps")
    config_table.add_row("Idle time", f"{cfg.profile.idle_time_us} us")
    config_table.add_row("Ramp end time", f"{cfg.profile.ramp_end_time_us} us")
    config_table.add_row("Chirps/frame", str(cfg.frame.chirps_per_frame))
    config_table.add_row("Num frames", str(cfg.frame.num_frames))
    config_table.add_row("Frame period", f"{cfg.frame.frame_period_ms} ms")

    console.print(config_table)

    # Derived parameters
    derived = compute_derived(cfg)

    derived_table = Table(title="[bold]Derived Parameters[/bold]", show_lines=True)
    derived_table.add_column("Parameter", style="cyan")
    derived_table.add_column("Value")
    derived_table.add_column("Note", style="dim")

    derived_table.add_row(
        "Bandwidth", f"{derived.bandwidth_mhz:.1f} MHz", "B = slope * ramp_time"
    )
    derived_table.add_row(
        "Wavelength", f"{derived.wavelength_m * 1000:.2f} mm", "lambda = c / f0"
    )
    derived_table.add_row(
        "Range resolution",
        f"{derived.range_resolution_m * 100:.2f} cm",
        "d_res = c/(2B) -- TI FMCW deck",
    )
    derived_table.add_row(
        "Max range",
        f"{derived.max_range_m:.2f} m",
        "d_max = Fs*c/(2S) -- TI FMCW deck",
    )
    derived_table.add_row(
        "Max velocity",
        f"{derived.max_velocity_mps:.2f} m/s",
        "[yellow]estimate[/yellow] -- v_max = lambda/(4Tc)",
    )
    derived_table.add_row(
        "Velocity resolution",
        f"{derived.velocity_resolution_mps:.4f} m/s",
        "[yellow]estimate[/yellow] -- v_res = lambda/(2Tf)",
    )
    derived_table.add_row(
        "Virtual antennas",
        str(derived.num_virtual_antennas),
        "[yellow]estimate[/yellow] -- requires validated array",
    )
    derived_table.add_row(
        "Expected file size",
        f"{derived.expected_file_size_bytes:,} bytes ({derived.expected_disk_mb:.2f} MB)",
        "",
    )
    derived_table.add_row(
        "Capture duration",
        f"{derived.capture_duration_s:.3f} s",
        "",
    )

    console.print(derived_table)

    # Layout status
    try:
        layout = get_layout(cfg.adc.layout)
        status = "[green]lab validated[/green]" if layout.lab_validated else "[yellow]NOT validated[/yellow]"
        ref = "SWRA581B ref" if layout.swra581b_reference else "custom/unvalidated"
        console.print(
            Panel(
                f"Layout: [bold]{layout.name}[/bold]\n"
                f"Status: {status}\n"
                f"Source: {ref}\n"
                f"[dim]{layout.description}[/dim]",
                title="Layout Status",
            )
        )
    except KeyError:
        console.print(f"[red]Unknown layout: {cfg.adc.layout}[/red]")


# ---------------------------------------------------------------------------
# awr parse
# ---------------------------------------------------------------------------


@app.command()
def parse(
    bin_file: Path = typer.Argument(..., help="Path to adc_data.bin"),
    config: Path = typer.Option(..., "--config", "-c", help="Path to YAML config"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Save cube as .npy"),
    strict: bool = typer.Option(True, help="Fail on file-size mismatch"),
) -> None:
    """Parse a headerless adc_data.bin into a radar cube."""
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.formats.adc_parser import parse_adc_bin, validate_file_size

    try:
        cfg = RadarConfig.from_yaml(config)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    # Validate file size first
    size_result = validate_file_size(bin_file, cfg)
    if size_result.ok:
        console.print(f"[green]OK[/green] {size_result.message}")
    else:
        console.print(f"[red]FAIL[/red] {size_result.message}")
        if strict:
            raise typer.Exit(code=1)

    # Parse
    try:
        import warnings

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            cube = parse_adc_bin(bin_file, cfg, strict_size=strict)

        for w in caught:
            console.print(f"[yellow]WARNING: {w.message}[/yellow]")

    except Exception as e:
        console.print(f"[red]Parse error:[/red] {e}")
        raise typer.Exit(code=1)

    # Report
    report_table = Table(title="[bold]Parse Result[/bold]", show_lines=True)
    report_table.add_column("Property", style="cyan")
    report_table.add_column("Value")

    report_table.add_row("Shape", str(cube.shape))
    report_table.add_row("Dtype", str(cube.dtype))
    report_table.add_row(
        "Dimensions",
        f"[{cube.shape[0]} frames, {cube.shape[1]} chirps, "
        f"{cube.shape[2]} rx, {cube.shape[3]} samples]",
    )
    report_table.add_row("Min value", f"{np.min(np.abs(cube)):.4f}")
    report_table.add_row("Max value", f"{np.max(np.abs(cube)):.4f}")
    report_table.add_row("Mean |value|", f"{np.mean(np.abs(cube)):.4f}")

    console.print(report_table)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        np.save(output, cube)
        console.print(f"[green]Cube saved to {output}[/green]")


# ---------------------------------------------------------------------------
# Context-Aware Aliases (awr init, awr check, awr summary, awr set)
# ---------------------------------------------------------------------------

@app.command("init")
def init_project(
    name: Optional[str] = typer.Argument(None, help="Project name"),
    parent: Optional[Path] = typer.Option(None, "--parent", help="Parent directory (defaults to CWD)"),
    at: Optional[Path] = typer.Option(None, "--at", help="Exact path to create project at"),
) -> None:
    """Scaffold a new AWR2944 hardware project."""
    from awr2944_dca.lab import RadarProject
    import os
    
    if at:
        if name or parent:
            console.print("[red]Error: Cannot provide name/parent when using --at.[/red]")
            raise typer.Exit(code=1)
        project = RadarProject.create_at(at, git_init=True)
    else:
        if not name:
            console.print("[red]Error: Must provide a project name or use --at.[/red]")
            raise typer.Exit(code=1)
        if parent is None:
            parent = Path(os.getcwd())
        project = RadarProject.create(name=name, parent=parent, git_init=True)
        
    console.print(f"[green]Successfully initialized project '{project.name}'[/green]")
    console.print(f"Location: {project.root}")
    console.print("You can now enter the directory and run 'awr doctor' to verify hardware.")


@app.command("check")
def check_alias(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Explicit config path"),
) -> None:
    """Validate experiment config. Auto-detects local capture.yaml."""
    from awr2944_dca.context import discover_context

    if config_path is None:
        ctx = discover_context()
        if not ctx:
            console.print("[red]No .awr-experiment found. Must run inside an experiment folder or provide --config.[/red]")
            raise typer.Exit(code=1)
        config_path = ctx.config_path

    config_validate(config_path)


@app.command("summary")
def summary_alias(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Explicit config path"),
) -> None:
    """Summarize experiment config. Auto-detects local capture.yaml."""
    from awr2944_dca.context import discover_context

    if config_path is None:
        ctx = discover_context()
        if not ctx:
            console.print("[red]No .awr-experiment found. Must run inside an experiment folder or provide --config.[/red]")
            raise typer.Exit(code=1)
        config_path = ctx.config_path

    config_summarize(config_path)


set_app = typer.Typer(help="Modify local config values.", no_args_is_help=True)
app.add_typer(set_app, name="set")

@set_app.command("device")
def set_device(
    device: str = typer.Argument(..., help="Radar device name (e.g. AWR2944EVM)"),
) -> None:
    """Set the radar device in the local capture.yaml."""
    from awr2944_dca.context import discover_context
    import yaml

    ctx = discover_context()
    if not ctx:
        console.print("[red]Must be run inside an experiment directory.[/red]")
        raise typer.Exit(code=1)

    data = yaml.safe_load(ctx.config_path.read_text(encoding="utf-8"))
    if "rig" not in data:
        data["rig"] = {}
    data["rig"]["radar"] = device

    # keep header comments? yaml.dump destroys them, so we just write it back.
    # A real implementation might use ruamel.yaml to preserve comments.
    # For now we'll accept the comment loss on update.
    ctx.config_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8")
    console.print(f"[green]OK[/green] Updated device to {device} in {ctx.config_path}")


@set_app.command("capture")
def set_capture(
    backend: str = typer.Argument(..., help="Capture backend (e.g. DCA1000EVM)"),
) -> None:
    """Set the capture backend in the local capture.yaml."""
    from awr2944_dca.context import discover_context
    import yaml

    ctx = discover_context()
    if not ctx:
        console.print("[red]Must be run inside an experiment directory.[/red]")
        raise typer.Exit(code=1)

    data = yaml.safe_load(ctx.config_path.read_text(encoding="utf-8"))
    if "rig" not in data:
        data["rig"] = {}
    data["rig"]["capture_card"] = backend

    ctx.config_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8")
    console.print(f"[green]OK[/green] Updated capture card to {backend} in {ctx.config_path}")


# ---------------------------------------------------------------------------
# awr process
# ---------------------------------------------------------------------------


@app.command()
def process(
    bin_file: Path = typer.Argument(..., help="Path to adc_data.bin"),
    config: Path = typer.Option(..., "--config", "-c", help="Path to YAML config"),
    output_dir: Path = typer.Option(
        Path("output"), "--output-dir", "-o", help="Directory for output plots"
    ),
    frame: int = typer.Option(0, "--frame", "-f", help="Frame index to plot"),
    rx: int = typer.Option(0, "--rx", help="RX channel index to plot"),
    no_clutter: bool = typer.Option(False, help="Skip static clutter removal"),
) -> None:
    """Parse and process: DC removal -> range FFT -> clutter removal -> Doppler FFT -> plots."""
    import warnings

    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use("Agg")  # Non-interactive backend for CLI

    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.dsp.dsp import process_cube
    from awr2944_dca.dsp.plotting import plot_range_doppler, plot_range_profile
    from awr2944_dca.formats.adc_parser import parse_adc_bin

    try:
        cfg = RadarConfig.from_yaml(config)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold]Processing {bin_file}[/bold]")
    console.print(f"  Config: {cfg.experiment.name}")
    console.print(f"  Frame: {frame}, RX: {rx}")

    # Parse
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        cube = parse_adc_bin(bin_file, cfg, strict_size=False)
    for w in caught:
        console.print(f"[yellow]WARNING: {w.message}[/yellow]")

    console.print(f"  Cube shape: {cube.shape}, dtype: {cube.dtype}")

    # Process
    results = process_cube(cube, remove_clutter=not no_clutter)

    # Output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Range profile plot
    range_path = output_dir / "range_profile"
    plot_range_profile(
        results["range_fft"],
        cfg,
        frame=frame,
        rx=rx,
        save_path=range_path,
    )
    console.print(f"[green]OK[/green] Range profile saved: {range_path}.png / .svg")

    # Range-Doppler plot
    rd_path = output_dir / "range_doppler"
    plot_range_doppler(
        results["range_doppler"],
        cfg,
        frame=frame,
        rx=rx,
        save_path=rd_path,
    )
    console.print(f"[green]OK[/green] Range-Doppler saved: {rd_path}.png / .svg")

    plt.close("all")

    console.print(
        Panel(
            f"[bold green]Processing complete![/bold green]\n"
            f"Outputs in: {output_dir.absolute()}",
            title="Done",
        )
    )


# ---------------------------------------------------------------------------
# awr compare-layouts
# ---------------------------------------------------------------------------


@app.command("compare-layouts")
def compare_layouts(
    target: Path = typer.Argument(..., help="Path to adc_data.bin or experiment folder"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Path to YAML config (required if target is a bin file)"),
) -> None:
    """Compare the two AWR2944 candidate layouts against a raw capture."""
    import warnings

    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.formats.adc_parser import parse_adc_bin, validate_file_size

    if target.is_dir():
        bin_file = target / "raw" / "adc_data.bin"
        config_file = target / "capture.yaml"
        if not bin_file.exists():
            console.print(f"[red]Could not find bin file:[/red] {bin_file}")
            raise typer.Exit(code=1)
        if not config_file.exists():
            console.print(f"[red]Could not find config file:[/red] {config_file}")
            raise typer.Exit(code=1)
    else:
        bin_file = target
        if not config:
            console.print("[red]--config is required when target is a file[/red]")
            raise typer.Exit(code=1)
        config_file = config

    try:
        cfg = RadarConfig.from_yaml(config_file)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold]Comparing layouts for {bin_file}[/bold]")
    console.print(
        "[yellow]IMPORTANT: Input file MUST be the headerless `adc_data.bin`. "
        "`adc_data_Raw_*.bin` requires packet reorder and zero-fill first.[/yellow]\n"
    )
    
    layouts = [
        ("awr2944_real_2lane_interleaved_candidate", 0),
        ("awr2944_real_2lane_noninterleaved_candidate", 1),
    ]

    for layout_name, ch_interleave in layouts:
        cfg.adc.layout = layout_name
        cfg.adc.channel_interleave = ch_interleave
        
        console.print(f"\n[cyan]=== {layout_name} ===[/cyan]")
        console.print(f"channel_interleave: {ch_interleave}")

        # Validate file size
        size_result = validate_file_size(bin_file, cfg)
        if size_result.ok:
            console.print(f"Size validation: [green]OK[/green] ({size_result.message})")
        else:
            console.print(f"Size validation: [red]FAIL[/red] ({size_result.message})")

        # Parse
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                cube = parse_adc_bin(bin_file, cfg, strict_size=False)

            for w in caught:
                console.print(f"[yellow]WARNING: {w.message}[/yellow]")

            console.print(f"Cube shape: {cube.shape}")
            console.print(f"Dtype: {cube.dtype}")

            # Per-RX stats
            stats_table = Table(title="[bold]Per-RX Stats[/bold]", show_lines=True)
            stats_table.add_column("RX", justify="right")
            stats_table.add_column("Mean")
            stats_table.add_column("StdDev")
            stats_table.add_column("Min")
            stats_table.add_column("Max")
            
            for rx in range(cube.shape[2]):
                rx_data = cube[:, :, rx, :]
                stats_table.add_row(
                    str(rx),
                    f"{np.mean(rx_data):.2f}",
                    f"{np.std(rx_data):.2f}",
                    f"{np.min(rx_data):.2f}",
                    f"{np.max(rx_data):.2f}",
                )
            console.print(stats_table)

            # First 16 samples for frame 0, chirp 0
            samples_table = Table(title="[bold]First 16 Samples (Frame 0, Chirp 0)[/bold]", show_lines=True)
            samples_table.add_column("RX", justify="right", style="cyan")
            samples_table.add_column("Values")
            
            for rx in range(cube.shape[2]):
                vals = cube[0, 0, rx, :16]
                vals_str = ", ".join(f"{v:g}" for v in vals)
                samples_table.add_row(str(rx), vals_str)
            console.print(samples_table)

        except Exception as e:
            console.print(f"[red]Parse error:[/red] {e}")


# ---------------------------------------------------------------------------
# Context-Aware Aliases (awr init, awr check, awr summary, awr set)
# ---------------------------------------------------------------------------



@app.command("check")
def check_alias(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Explicit config path"),
) -> None:
    """Validate experiment config."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.config.validation import Severity
    
    try:
        exp = Experiment.open(config_path.parent if config_path else ".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    results = exp.check()

    table = Table(title="[bold]Deep Validation[/bold]", show_lines=True)
    table.add_column("Field", style="cyan", min_width=30)
    table.add_column("Status", min_width=8)
    table.add_column("Message", min_width=40)

    has_errors = False
    warnings_count = 0
    for r in results:
        if r.severity == Severity.OK:
            status = "[green]OK[/green]"
        elif r.severity == Severity.WARNING:
            status = "[yellow]WARN[/yellow]"
            warnings_count += 1
        else:
            status = "[red]ERROR[/red]"
            has_errors = True

        table.add_row(r.field, status, r.message)

    console.print(table)
    
    if has_errors:
        console.print("[red]Validation failed with errors.[/red]")
        raise typer.Exit(code=1)
    elif warnings_count > 0:
        console.print(f"[yellow]No errors; {warnings_count} warning(s).[/yellow]")
    else:
        console.print("[green]All checks passed.[/green]")


@app.command("summary")
def summary_alias(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Explicit config path"),
) -> None:
    """Summarize experiment config."""
    from awr2944_dca.api.experiment import Experiment
    
    try:
        exp = Experiment.open(config_path.parent if config_path else ".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    summary = exp.summary()
    cfg = summary["config"]
    derived = summary["derived"]
    expected_bytes = summary["expected_bytes"]
    expected_mib = expected_bytes / (1024 * 1024)

    table = Table(title="[bold]Experiment Summary[/bold]", show_lines=True)
    table.add_column("Parameter", style="cyan")
    table.add_column("Value")

    table.add_row("Device", cfg.rig.radar)
    table.add_row("Capture card", cfg.rig.capture_card)
    table.add_row("ADC mode", "complex" if cfg.adc.is_complex else "real")
    table.add_row("ADC bits", str(cfg.adc.bits))
    table.add_row("RX enabled", str(cfg.hardware.rx_enabled))
    table.add_row("TX enabled", str(cfg.hardware.tx_enabled))
    table.add_row("Antenna mode", cfg.hardware.antenna_mode.value)
    table.add_row("channel_interleave", str(cfg.adc.channel_interleave))
    
    table.add_row("Samples/chirp", str(cfg.adc.samples_per_chirp))
    table.add_row("Chirps/frame", str(cfg.frame.chirps_per_frame))
    table.add_row("Frames", str(cfg.frame.num_frames))
    table.add_row("Expected adc_data.bin size", f"{expected_bytes:,} bytes ({expected_mib:.2f} MiB)")
    
    table.add_row("Bandwidth", f"{derived.bandwidth_mhz:.1f} MHz")
    table.add_row("Range resolution", f"{derived.range_resolution_m * 100:.2f} cm")
    table.add_row("Max range", f"{derived.max_range_m:.2f} m")
    table.add_row("Max velocity (estimate)", f"{derived.max_velocity_mps:.2f} m/s")
    table.add_row("Velocity resolution (estimate)", f"{derived.velocity_resolution_mps:.4f} m/s")
    table.add_row("Virtual antennas (estimate)", str(derived.num_virtual_antennas))
    table.add_row("Capture duration", f"{derived.capture_duration_s:.3f} s")

    console.print(table)
    
    # Print layout below table to prevent truncation
    console.print(f"[cyan]Parser layout:[/cyan] {cfg.adc.layout}")

    if "candidate" in cfg.adc.layout or "unvalidated" in cfg.adc.layout:
        console.print(
            "\n[yellow]WARNING: Layout is a candidate/unvalidated. "
            "Run 'awr compare-layouts' with real data to confirm.[/yellow]"
        )


set_app = typer.Typer(help="Modify local config values.", no_args_is_help=True)
app.add_typer(set_app, name="set")

@set_app.command("device")
def set_device(
    device: str = typer.Argument(..., help="Radar device name (e.g. AWR2944EVM)"),
) -> None:
    """Set the radar device in the local capture.yaml."""
    from awr2944_dca.api.experiment import Experiment
    try:
        exp = Experiment.open(".")
        exp.set_device(device)
        console.print(f"[green]OK[/green] Updated device to {device}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@set_app.command("capture")
def set_capture(
    backend: str = typer.Argument(..., help="Capture backend (e.g. DCA1000EVM)"),
) -> None:
    """Set the capture backend in the local capture.yaml."""
    from awr2944_dca.api.experiment import Experiment
    try:
        exp = Experiment.open(".")
        exp.set_capture(backend)
        console.print(f"[green]OK[/green] Updated capture card to {backend}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


# ===========================================================================
# awr config ...
# ===========================================================================

config_app = typer.Typer(help="Config management commands.", no_args_is_help=True)
app.add_typer(config_app, name="config")


@config_app.command("new")
def config_new(
    preset: str = typer.Option(..., "--preset", "-p", help="Preset name"),
    out: Path = typer.Option(Path("capture.yaml"), "--out", "-o", help="Output YAML path"),
) -> None:
    """Generate a capture.yaml from a preset."""
    from awr2944_dca.config.presets import get_preset, list_presets

    try:
        preset_dict = get_preset(preset)
    except KeyError:
        console.print(
            f"[red]Unknown preset '{preset}'.[/red] "
            f"Available: {list_presets()}"
        )
        raise typer.Exit(code=1)

    import yaml
    out.parent.mkdir(parents=True, exist_ok=True)

    # Add header comment
    header = (
        f"# Generated by awr2944_dca from preset: {preset}\n"
        f"# Review and customize before use.\n\n"
    )
    yaml_str = yaml.dump(preset_dict, default_flow_style=False, sort_keys=False)
    out.write_text(header + yaml_str, encoding="utf-8")

    console.print(f"[green]OK[/green] Config written to {out}")

    # Validate the generated config
    from awr2944_dca.config.schema import RadarConfig
    RadarConfig.model_validate(preset_dict)
    console.print("[green]OK[/green] Generated config passes schema validation.")

    if "EXPERIMENTAL" in preset_dict.get("experiment", {}).get("description", ""):
        console.print(
            "[yellow]WARNING: This preset uses TDM-MIMO which is NOT validated.[/yellow]"
        )


@config_app.command("edit")
def config_edit(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Explicit config path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't actually open editor (for tests)"),
) -> None:
    """Open capture.yaml in the system editor, then validate."""
    from awr2944_dca.api.experiment import Experiment
    
    try:
        exp = Experiment.open(config_path.parent if config_path else ".")
        exp.config_edit(dry_run=dry_run)
        console.print("[dim]Editor closed. Running validation...[/dim]")
        check_alias(exp.config_path)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("wizard")
def config_wizard(
    out: Path | None = typer.Option(None, "--out", "-o", help="Output YAML path"),
) -> None:
    """Interactive config generator."""
    from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.context import discover_context

    if out is None:
        ctx = discover_context()
        if ctx:
            out = ctx.config_path
        else:
            out = Path("capture.yaml")

    console.print("[bold cyan]AWR2944 Config Wizard[/bold cyan]")
    
    name = Prompt.ask("Experiment name", default="wizard_capture")
    device = Prompt.ask("Radar device", default="AWR2944EVM")
    capture = Prompt.ask("Capture backend", default="DCA1000EVM")
    
    is_complex = Confirm.ask("Complex ADC?", default=False)
    bits = IntPrompt.ask("ADC bits", default=16, choices=["12", "14", "16"])
    
    samples = IntPrompt.ask("Samples per chirp", default=256)
    chirps = IntPrompt.ask("Chirps per frame", default=128)
    frames = IntPrompt.ask("Number of frames", default=10)

    cfg = {
        "experiment": {"name": name},
        "rig": {"radar": device, "capture_card": capture},
        "adc": {
            "is_complex": is_complex,
            "bits": bits,
            "samples_per_chirp": samples,
            "layout": f"{device.lower().replace('evm', '')}_{'complex' if is_complex else 'real'}_2lane_noninterleaved_candidate"
        },
        "frame": {
            "chirps_per_frame": chirps,
            "num_frames": frames
        }
    }

    import yaml
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.dump(cfg, default_flow_style=False, sort_keys=False), encoding="utf-8")
    
    console.print(f"[green]OK[/green] Wrote config to {out}")
    config_validate(out)


@config_app.command("validate")
def config_validate(
    config_path: Path = typer.Argument(..., help="Path to capture.yaml"),
) -> None:
    """Deep validation of a capture config."""
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.config.validation import Severity, validate_config

    try:
        cfg = RadarConfig.from_yaml(config_path)
    except Exception as e:
        console.print(f"[red]Schema validation FAILED:[/red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[green]OK[/green] Schema validation passed for {config_path}")

    results = validate_config(cfg)

    table = Table(title="[bold]Deep Validation[/bold]", show_lines=True)
    table.add_column("Field", style="cyan", min_width=30)
    table.add_column("Status", min_width=8)
    table.add_column("Message", min_width=40)

    has_errors = False
    for r in results:
        if r.severity == Severity.OK:
            status = "[green]OK[/green]"
        elif r.severity == Severity.WARNING:
            status = "[yellow]WARN[/yellow]"
        else:
            status = "[red]ERROR[/red]"
            has_errors = True
        table.add_row(r.field, status, r.message)

    console.print(table)

    if has_errors:
        console.print("[red]Validation has errors. Fix before capture.[/red]")
        raise typer.Exit(code=1)
    else:
        console.print("[green]All checks passed.[/green]")


@config_app.command("summarize")
def config_summarize(
    config_path: Path = typer.Argument(..., help="Path to capture.yaml"),
) -> None:
    """Print a clean human-readable config summary."""
    from awr2944_dca.config.derived import compute_derived
    from awr2944_dca.config.schema import RadarConfig

    try:
        cfg = RadarConfig.from_yaml(config_path)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    derived = compute_derived(cfg)

    console.print(Panel(
        f"[bold]{cfg.experiment.name}[/bold]\n{cfg.experiment.description}",
        title="Experiment Summary",
    ))

    table = Table(show_lines=True)
    table.add_column("Parameter", style="cyan", min_width=25)
    table.add_column("Value", min_width=35)

    table.add_row("Device", cfg.rig.radar)
    table.add_row("Capture card", cfg.rig.capture_card)
    table.add_row("ADC mode", "complex" if cfg.adc.is_complex else "real")
    table.add_row("ADC bits", str(cfg.adc.bits))
    table.add_row("RX enabled", str(cfg.hardware.rx_enabled))
    table.add_row("TX enabled", str(cfg.hardware.tx_enabled))
    table.add_row("Antenna mode", cfg.hardware.antenna_mode.value)
    table.add_row("channel_interleave", str(cfg.adc.channel_interleave))
    table.add_row("Parser layout", cfg.adc.layout)
    table.add_row("Samples/chirp", str(cfg.adc.samples_per_chirp))
    table.add_row("Chirps/frame", str(cfg.frame.chirps_per_frame))
    table.add_row("Frames", str(cfg.frame.num_frames))
    table.add_row(
        "Expected adc_data.bin size",
        f"{derived.expected_file_size_bytes:,} bytes ({derived.expected_disk_mb:.2f} MB)",
    )
    table.add_row("", "")
    table.add_row("Bandwidth", f"{derived.bandwidth_mhz:.1f} MHz")
    table.add_row("Range resolution", f"{derived.range_resolution_m * 100:.2f} cm")
    table.add_row("Max range", f"{derived.max_range_m:.2f} m")
    table.add_row(
        "Max velocity [italic](estimate)[/italic]",
        f"{derived.max_velocity_mps:.2f} m/s",
    )
    table.add_row(
        "Velocity resolution [italic](estimate)[/italic]",
        f"{derived.velocity_resolution_mps:.4f} m/s",
    )
    table.add_row(
        "Virtual antennas [italic](estimate)[/italic]",
        str(derived.num_virtual_antennas),
    )
    table.add_row("Capture duration", f"{derived.capture_duration_s:.3f} s")

    console.print(table)

    # Layout warning
    if "candidate" in cfg.adc.layout or "unvalidated" in cfg.adc.layout:
        console.print(
            "[yellow]WARNING: Layout is a candidate/unvalidated. "
            "Run 'awr compare-layouts' with real data to confirm.[/yellow]"
        )


# ===========================================================================
# awr experiment ...
# ===========================================================================

experiment_app = typer.Typer(help="Experiment management commands.", no_args_is_help=True)
app.add_typer(experiment_app, name="experiment")


@experiment_app.command("init")
def experiment_init(
    name: str = typer.Argument(..., help="Experiment name"),
    preset: str = typer.Option("first-capture", "--preset", "-p", help="Config preset"),
    root: Path = typer.Option(Path("experiments"), "--root", "-r", help="Experiments root dir"),
) -> None:
    from awr2944_dca.api.experiment import Experiment
    try:
        exp = Experiment.init(name, preset, root)
        console.print(f"[green]OK[/green] Scaffolded experiment at {exp.root_dir}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

# ===========================================================================
# awr capture run  (acquisition)
# ===========================================================================

@capture_mgmt_app.command("run")
def capture_run_cmd(
    profile: str = typer.Option("smoke_v1", help="Profile name"),
    frames: Optional[int] = typer.Option(None, help="Number of frames (overrides profile)"),
    guard_frames: Optional[int] = typer.Option(None, help="Guard frames (default from project)"),
    name: str = typer.Option("dca_capture", help="Capture name"),
    project_root: Optional[Path] = typer.Option(None, help="Project root (auto-detected if omitted)"),
) -> None:
    """Execute a full production capture."""
    from awr2944_dca.lab import RadarProject
    console = Console()
    try:
        if project_root:
            proj = RadarProject.open(project_root)
        else:
            proj = RadarProject.open_here()
        result = proj.capture.run(
            profile=profile,
            frames=frames,
            guard_frames=guard_frames,
            name=name,
        )
        if result.success:
            console.print(f"[green]✓ Capture successful: {result.capture.capture_id}[/green]")
        else:
            console.print(f"[red]✗ Capture failed: {result.session_result.manifest.get('failure_reason', 'unknown')}[/red]")
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# ===========================================================================
# awr captures ...  (persisted artifact management)
# ===========================================================================

captures_app = typer.Typer(help="Capture artifact management.", no_args_is_help=True)
app.add_typer(captures_app, name="captures")


@captures_app.command("list")
def captures_list_cmd(
    project_root: Optional[Path] = typer.Option(None, help="Project root (auto-detected if omitted)"),
) -> None:
    """List all managed captures."""
    from awr2944_dca.lab import RadarProject
    console = Console()
    try:
        if project_root:
            proj = RadarProject.open(project_root)
        else:
            proj = RadarProject.open_here()
        caps = proj.captures.list()
        if not caps:
            console.print("[dim]No captures found.[/dim]")
            return
        table = Table(title="Captures")
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Status")
        for cap in caps:
            s = cap.status()
            table.add_row(s.get('capture_id', ''), s.get('capture_name', ''), s.get('status', ''))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@captures_app.command("show")
def captures_show_cmd(
    query: str = typer.Argument(..., help="Capture ID or name substring"),
    project_root: Optional[Path] = typer.Option(None, help="Project root (auto-detected if omitted)"),
) -> None:
    """Show details of a specific capture."""
    from awr2944_dca.lab import RadarProject
    console = Console()
    try:
        if project_root:
            proj = RadarProject.open(project_root)
        else:
            proj = RadarProject.open_here()
        cap = proj.captures.get(query)
        console.print(f"[bold]Capture:[/bold] {cap.capture_id}")
        s = cap.status()
        for k, v in s.items():
            console.print(f"  {k}: {v}")
        prod = cap.manifest
        if prod:
            console.print(f"\n  [bold]Production Manifest:[/bold]")
            for key in ('native_byte_count', 'canonical_native_byte_count',
                        'packet_count', 'sequence_gaps', 'native_sha256',
                        'canonical_sha256', 'logical_cube_shape', 'success'):
                if key in prod:
                    console.print(f"    {key}: {prod[key]}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@captures_app.command("verify")
def captures_verify_cmd(
    query: str = typer.Argument(..., help="Capture ID or name substring"),
    strict: bool = typer.Option(False, "--strict", help="Raise on failure"),
    project_root: Optional[Path] = typer.Option(None, help="Project root (auto-detected if omitted)"),
) -> None:
    """Verify a capture's integrity."""
    from awr2944_dca.lab import RadarProject
    console = Console()
    try:
        if project_root:
            proj = RadarProject.open(project_root)
        else:
            proj = RadarProject.open_here()
        cap = proj.captures.get(query)
        report = cap.verify(strict=strict)
        console.print(report.summary())
        if not report.success:
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


# ===========================================================================
# awr profiles ...
# ===========================================================================

profiles_app = typer.Typer(help="Structured profile management (Offline).", no_args_is_help=True)
app.add_typer(profiles_app, name="profiles")

@profiles_app.command("list")
def profiles_list() -> None:
    """List all available profiles."""
    from awr2944_dca.lab import RadarProject
    proj = RadarProject.open_here()
    entries = proj.profiles.list()
    
    table = Table(title="Structured Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Origin")
    table.add_column("Path")
    
    for e in sorted(entries, key=lambda x: x.name):
        origin_str = "[blue]built-in[/blue]" if e.origin == "built_in" else "[green]project[/green]"
        if e.shadows_built_in:
            origin_str += " (shadows built-in)"
        table.add_row(e.name, origin_str, str(e.path) if e.path else "-")
        
    console.print(table)


@profiles_app.command("show")
def profiles_show(name: str = typer.Argument(..., help="Profile name")) -> None:
    """Show details of a structured profile."""
    from awr2944_dca.lab import RadarProject
    proj = RadarProject.open_here()
    try:
        prof = proj.profiles.get(name)
        console.print(prof.to_toml())
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@profiles_app.command("validate")
def profiles_validate(name: str = typer.Argument(..., help="Profile name")) -> None:
    """Validate a structured profile and display its derived parameters."""
    from awr2944_dca.lab import RadarProject
    proj = RadarProject.open_here()
    try:
        prof = proj.profiles.get(name)
        report = prof.validate()
        
        console.print(f"[bold]Validation for {name}[/bold]")
        console.print(report.summary())
        
        if report.derived:
            console.print("\n[bold]Derived Parameters:[/bold]")
            for k, v in report.derived.items():
                console.print(f"  {k}: {v}")
                
        if not report.success:
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


@profiles_app.command("export")
def profiles_export(
    name: str = typer.Argument(..., help="Profile name"),
    format: str = typer.Option("sdk-cli", "--format", help="Export format")
) -> None:
    """Export profile to SDK CLI commands (offline)."""
    from awr2944_dca.lab import RadarProject
    proj = RadarProject.open_here()
    try:
        prof = proj.profiles.get(name)
        if format != "sdk-cli":
            console.print("[red]Error: Only --format sdk-cli is currently supported.[/red]")
            raise typer.Exit(code=1)
            
        cmds = prof.to_sdk_cli()
        for c in cmds:
            console.print(c)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

# ===========================================================================
# awr ti ...
# ===========================================================================

ti_app = typer.Typer(help="TI mmWave Studio bridge commands.", no_args_is_help=True)
app.add_typer(ti_app, name="ti")


@ti_app.command("inspect")
def ti_inspect(
    file_path: Path = typer.Argument(..., help="Path to TI config file (Lua/JSON)"),
) -> None:
    """Inspect a TI config file and extract parsing-relevant fields."""
    from awr2944_dca.ti.inspect import UNKNOWN, inspect_ti_file

    try:
        result = inspect_ti_file(file_path)
    except FileNotFoundError:
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(code=1)

    console.print(Panel(
        f"Source: {result.source_file}\nFormat: {result.source_format}",
        title="TI Config Inspection",
    ))

    table = Table(title="[bold]Extracted Fields[/bold]", show_lines=True)
    table.add_column("Field", style="cyan", min_width=25)
    table.add_column("Value", min_width=20)

    fields = [
        ("adcFmt / adcOutFormat", result.adc_fmt),
        ("adcBits", result.adc_bits),
        ("chInterleave", result.ch_interleave),
        ("iqSwapSel", result.iq_swap_sel),
        ("rxChannelEn", result.rx_channel_en),
        ("txChannelEn", result.tx_channel_en),
        ("numAdcSamples", result.num_adc_samples),
        ("startFreqGHz", result.start_freq_ghz),
        ("slopeMHzPerUs", result.slope_mhz_per_us),
        ("sampleRateKsps", result.sample_rate_ksps),
        ("idleTimeUs", result.idle_time_us),
        ("rampEndTimeUs", result.ramp_end_time_us),
        ("chirpsPerFrame", result.chirps_per_frame),
        ("numFrames", result.num_frames),
        ("framePeriodMs", result.frame_period_ms),
        ("dataPathIntf", result.data_path_intf),
        ("lvdsLaneEn", result.lvds_lane_en),
    ]

    for name, value in fields:
        if value == UNKNOWN:
            table.add_row(name, "[yellow]UNKNOWN[/yellow]")
        else:
            table.add_row(name, str(value))

    console.print(table)

    if result.raw_api_calls:
        console.print("\n[bold]Raw API Calls:[/bold]")
        for call in result.raw_api_calls:
            console.print(f"  {call}")


@ti_app.command("import")
def ti_import(
    ti_file: Path = typer.Argument(..., help="Path to TI config file"),
    out: Path = typer.Option(Path("capture.yaml"), "--out", "-o", help="Output YAML path"),
) -> None:
    """Import a TI config file into capture.yaml format."""
    from awr2944_dca.ti.import_config import import_ti_config

    try:
        config_dict, assumptions, unknown_fields = import_ti_config(
            ti_file, output_path=out
        )
    except FileNotFoundError:
        console.print(f"[red]File not found: {ti_file}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Import error: {e}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]OK[/green] Config imported to {out}")

    if assumptions:
        console.print("\n[yellow]Assumptions (fields defaulted):[/yellow]")
        for a in assumptions:
            console.print(f"  [yellow]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {a}[/yellow]")

    if unknown_fields:
        console.print("\n[red]Unknown fields (could not extract):[/red]")
        for f in unknown_fields:
            console.print(f"  [red]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {f}[/red]")

    console.print(
        "\n[yellow]Run 'awr config validate' on the output to check for issues.[/yellow]"
    )


@ti_app.command("compare")
def ti_compare(
    config_path: Path = typer.Argument(..., help="Path to our capture.yaml"),
    ti_file: Path = typer.Argument(..., help="Path to TI config file"),
) -> None:
    """Compare our capture.yaml against a TI config file."""
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.ti.compare import CompSeverity, compare_configs

    try:
        cfg = RadarConfig.from_yaml(config_path)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    try:
        results = compare_configs(cfg, ti_file)
    except FileNotFoundError:
        console.print(f"[red]TI file not found: {ti_file}[/red]")
        raise typer.Exit(code=1)

    table = Table(title="[bold]Config Comparison[/bold]", show_lines=True)
    table.add_column("Field", style="cyan", min_width=20)
    table.add_column("Our Value", min_width=12)
    table.add_column("TI Value", min_width=12)
    table.add_column("Status", min_width=8)
    table.add_column("Message", min_width=30)

    has_errors = False
    for r in results:
        if r.severity == CompSeverity.MATCH:
            status = "[green]MATCH[/green]"
        elif r.severity == CompSeverity.WARNING:
            status = "[yellow]WARN[/yellow]"
        elif r.severity == CompSeverity.ERROR:
            status = "[red]ERROR[/red]"
            has_errors = True
        else:
            status = "[dim]SKIP[/dim]"

        table.add_row(r.field, r.our_value, r.ti_value, status, r.message)

    console.print(table)

    if has_errors:
        console.print(
            "[red]CRITICAL MISMATCHES DETECTED. "
            "Fix before capture or data will be unparseable.[/red]"
        )
    else:
        console.print("[green]No critical mismatches.[/green]")


# @ti_app.command("export-lua-template")
def ti_export_lua_template(
    config_path: Path = typer.Argument(..., help="Path to capture.yaml"),
    out: Path = typer.Option(Path("capture.lua"), "--out", "-o", help="Output Lua path"),
) -> None:
    """Generate a Lua template from capture.yaml (NOT hardware-validated)."""
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.ti.export_lua import export_lua_template

    try:
        cfg = RadarConfig.from_yaml(config_path)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    result_path = export_lua_template(cfg, out, source_name=str(config_path))
    console.print(f"[green]OK[/green] Lua template written to {result_path}")
    console.print(
        "[yellow]WARNING: This is a TEMPLATE. Not hardware validated. "
        "Review every parameter before running on hardware.[/yellow]"
    )


@ti_app.command("export-dca-config")
def ti_export_dca_config(
    config_path: Path = typer.Argument(..., help="Path to capture.yaml"),
    out: Path = typer.Option(
        Path("dca1000_config.json"), "--out", "-o", help="Output JSON path"
    ),
) -> None:
    """Generate a DCA1000 JSON config from capture.yaml."""
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.ti.export_dca import DcaConfigError, export_dca_config

    try:
        cfg = RadarConfig.from_yaml(config_path)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    try:
        result_path = export_dca_config(cfg, out)
    except DcaConfigError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]OK[/green] DCA1000 config written to {result_path}")
    console.print(
        "[yellow]NOTE: Verify firmware/schema version matches your DCA1000.[/yellow]"
    )


# @ti_app.command("find-studio")
def ti_find_studio() -> None:
    """Search for mmWave Studio installations."""
    from awr2944_dca.ti.probe import find_studio

    installs = find_studio()
    if not installs:
        console.print("[yellow]No mmWave Studio installations found in common paths.[/yellow]")
        return

    console.print(f"[green]Found {len(installs)} installation(s):[/green]")
    for install in installs:
        console.print(f"  - {install.path}")
        console.print(f"    Exe: {install.exe_path}")


@ti_app.command("probe")
def ti_probe(
    offline: bool = typer.Option(False, "--offline", help="Required. Probe without connecting to hardware"),
) -> None:
    """Probe mmWave Studio for offline execution capabilities."""
    if not offline:
        console.print("[red]Must pass --offline flag. Hardware probe is not implemented.[/red]")
        raise typer.Exit(1)

    from awr2944_dca.api.experiment import Experiment

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    probe_lua = exp.generate_ti_probe()

    console.print("\n[yellow]PARTIAL: probe.lua generated.[/yellow]")
    console.print(f"Run this helper to get the command for mmWave Studio:")
    console.print(f"  awr ti lua-command {probe_lua.relative_to(exp.root_dir)} --copy")
    console.print("Then run `awr ti probe-status`")


@ti_app.command("probe-status")
def ti_probe_status() -> None:
    """Read the results of the offline Lua probe."""
    import json
    from awr2944_dca.api.experiment import Experiment

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    result_file = exp.root_dir / "ti" / "probe_logs" / "probe_result.json"
    manifest_file = exp.root_dir / "ti" / "probe_logs" / "probe_manifest.json"

    if not result_file.exists():
        console.print("[yellow]NOT RUN[/yellow] - probe_result.json not found.")
        return

    try:
        data = json.loads(result_file.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]ERROR[/red] parsing probe_result.json: {e}")
        raise typer.Exit(1)
        
    if manifest_file.exists():
        try:
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            if data.get("probe_id") != manifest_data.get("probe_id"):
                console.print(f"[yellow]STALE RESULT[/yellow] - probe_id mismatch. Re-run the script in mmWave Studio.")
                return
        except Exception as e:
            console.print(f"[red]ERROR[/red] parsing probe_manifest.json: {e}")
            raise typer.Exit(1)

    if data.get("error"):
        console.print(f"[red]ERROR[/red] in Lua script: {data['error']}")
        return

    if not data.get("probe_executed"):
        console.print("[yellow]PARTIAL[/yellow] - JSON exists but probe_executed is false?")
        return

    if data.get("ar1_available"):
        console.print("[green]SUCCESS[/green] - Lua ran and ar1 API is available.")
    else:
        console.print("[yellow]PARTIAL[/yellow] - Lua ran but ar1 API is MISSING.")
        
    table = Table(show_lines=True)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    for k, v in data.items():
        table.add_row(str(k), str(v))
    console.print(table)


@ti_app.command("inventory")
def ti_inventory(
    offline: bool = typer.Option(False, "--offline", help="Required. Run without connecting to hardware"),
) -> None:
    """Generate the offline API inventory extraction script."""
    if not offline:
        console.print("[red]Must pass --offline flag. Hardware inventory is not implemented.[/red]")
        raise typer.Exit(1)

    from awr2944_dca.api.experiment import Experiment

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    inventory_lua = exp.generate_ti_inventory()

    console.print("\n[yellow]PARTIAL: inventory.lua generated.[/yellow]")
    console.print(f"Run this helper to get the command for mmWave Studio:")
    console.print(f"  awr ti lua-command {inventory_lua.relative_to(exp.root_dir)} --copy")
    console.print("Then run `awr ti inventory-status`")


@ti_app.command("inventory-status")
def ti_inventory_status() -> None:
    """Read the results of the offline Lua API inventory."""
    import json
    from awr2944_dca.api.experiment import Experiment

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    result_file = exp.root_dir / "ti" / "probe_logs" / "inventory_result.json"
    manifest_file = exp.root_dir / "ti" / "probe_logs" / "inventory_manifest.json"

    if not result_file.exists():
        console.print("[yellow]NOT RUN[/yellow] - inventory_result.json not found.")
        return

    try:
        data = json.loads(result_file.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]ERROR[/red] parsing inventory_result.json: {e}")
        raise typer.Exit(1)
        
    if manifest_file.exists():
        try:
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            if data.get("probe_id") != manifest_data.get("probe_id"):
                console.print(f"[yellow]STALE RESULT[/yellow] - probe_id mismatch. Re-run the script in mmWave Studio.")
                return
        except Exception as e:
            console.print(f"[red]ERROR[/red] parsing inventory_manifest.json: {e}")
            raise typer.Exit(1)

    if data.get("inventory_executed"):
        console.print("[green]SUCCESS[/green] - Inventory script executed.")
    else:
        console.print("[red]ERROR[/red] - Script failed to execute properly.")
        return

    console.print(f"ar1 exists: {data.get('ar1_exists')}")
    console.print(f"ar1 type: {data.get('ar1_type')}")
    console.print(f"ar1 iterable: {data.get('ar1_iterable')}")
    
    if data.get("ar1_error"):
        console.print(f"[red]ar1 iteration error:[/red] {data.get('ar1_error')}")

    ar1_keys = data.get("ar1_keys", {})
    console.print(f"Extracted {len(ar1_keys)} keys from ar1.")
    g_keys = data.get("_G_keys", {})
    console.print(f"Extracted {len(g_keys)} keys from _G.")
    

@ti_app.command("inventory-list")
def ti_inventory_list(
    filter: str = typer.Option(None, "--filter", help="Case-insensitive filter for API names"),
) -> None:
    """List extracted API inventory keys."""
    import json
    from awr2944_dca.api.experiment import Experiment

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    result_file = exp.root_dir / "ti" / "probe_logs" / "inventory_result.json"
    if not result_file.exists():
        console.print("[yellow]NOT RUN[/yellow] - inventory_result.json not found.")
        return

    try:
        data = json.loads(result_file.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]ERROR[/red] parsing inventory_result.json: {e}")
        raise typer.Exit(1)
        
    ar1_keys = data.get("ar1_keys", {})
    
    table = Table(title="ar1 API Keys", show_lines=True)
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Value Summary", max_width=60)
    
    count = 0
    for k, v in ar1_keys.items():
        if filter and filter.lower() not in k.lower():
            continue
            
        type_str = v.get("type", "unknown")
        val_str = v.get("value", "")
        table.add_row(k, type_str, val_str)
        count += 1
        
    console.print(table)
    console.print(f"Showing {count} / {len(ar1_keys)} keys.")

@ti_app.command("inventory-classify")
def ti_inventory_classify() -> None:
    """Classify extracted API inventory keys using static analysis."""
    import json
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.ti.classify import generate_classification, write_outputs, scan_ti_scripts

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    log_dir = exp.root_dir / "ti" / "probe_logs"
    result_file = log_dir / "inventory_result.json"
    
    if not result_file.exists():
        console.print("[yellow]NOT RUN[/yellow] - inventory_result.json not found.")
        return

    try:
        data = json.loads(result_file.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]ERROR[/red] parsing inventory_result.json: {e}")
        raise typer.Exit(1)
        
    ti_dir = Path("C:/ti")
    usage_map = {}
    if ti_dir.exists():
        console.print(f"Scanning TI installation for Lua scripts in {ti_dir}...")
        usage_map = scan_ti_scripts(ti_dir)
        console.print(f"Found usages for {len(usage_map)} ar1 APIs.")
        
    console.print("Classifying APIs heuristically...")
    keys = generate_classification(data, ti_dir)
    write_outputs(keys, usage_map, log_dir)
    
    console.print(f"[green]SUCCESS[/green] - Classification written to {log_dir}")


@ti_app.command("workflow-map")
def ti_workflow_map(
    source: str = typer.Option("DataCaptureDemo_xWR.lua", "--source", help="Source Lua file to extract from"),
) -> None:
    """Extract and map the first-capture workflow from a TI script."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.ti.workflow_map import extract_workflow, write_workflow_map

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    ti_dir = Path("C:/ti")
    log_dir = exp.root_dir / "ti" / "probe_logs"
    
    if not ti_dir.exists():
        console.print(f"[red]TI installation directory {ti_dir} not found.[/red]")
        raise typer.Exit(1)
        
    console.print(f"Extracting first-capture workflow from {source}...")
    steps = extract_workflow(ti_dir, source)
    
    if not steps:
        console.print(f"[red]Could not find or extract from {source}[/red]")
        raise typer.Exit(1)
        
    log_dir.mkdir(parents=True, exist_ok=True)
    write_workflow_map(steps, log_dir)
    console.print(f"[green]SUCCESS[/green] - Workflow map written to {log_dir}")


# @ti_app.command("lua-command")
def ti_lua_command(
    script_path: Path = typer.Argument(..., help="Path to Lua script"),
    copy: bool = typer.Option(False, "--copy", help="Copy command to clipboard (Windows only)"),
) -> None:
    """Print the dofile command to execute a script in mmWave Studio."""
    import subprocess
    import sys
    
    cmd = f'dofile([[{script_path.resolve()}]])'
    console.print(f"\n{cmd}\n")
    
    if copy:
        if sys.platform == "win32":
            try:
                subprocess.run(['clip.exe'], input=cmd.encode('utf-16le'), check=True)
                console.print("[green]Command copied to clipboard![/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not copy to clipboard: {e}[/yellow]")
        else:
            console.print("[yellow]Clipboard copy is only supported on Windows with clip.exe.[/yellow]")


# @ti_app.command("run-lua")
def ti_run_lua(
    script_path: Path = typer.Argument(..., help="Path to Lua script"),
    offline: bool = typer.Option(False, "--offline", help="Required. Run without connecting to hardware"),
    force_hardware_risk: bool = typer.Option(False, "--force-hardware-risk", help="Bypass static scan for hardware actions"),
) -> None:
    """Run a Lua script via mmWave Studio."""
    if not offline:
        console.print("[red]Must pass --offline flag. Hardware execution is not implemented.[/red]")
        raise typer.Exit(1)

    from awr2944_dca.ti.probe import static_scan_for_hardware_actions

    if not script_path.exists():
        console.print(f"[red]Script not found: {script_path}[/red]")
        raise typer.Exit(1)

    if not force_hardware_risk:
        findings = static_scan_for_hardware_actions(script_path)
        if findings:
            console.print("[red]ERROR: Script contains dangerous hardware actions![/red]")
            for line in findings:
                console.print(f"  [yellow]{line}[/yellow]")
            console.print("Refusing to run. Pass --force-hardware-risk to bypass.")
            raise typer.Exit(1)

    console.print("[green]Scan passed. No hardware actions found.[/green]")
    console.print("Headless execution of Lua is partially supported. (See probe command).")


@ports_app.command("scan")
def ports_scan(
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed port heuristics reasoning"),
) -> None:
    """Enumerate Windows COM ports and classify likely TI radar roles."""
    from awr2944_dca.hardware.ports import scan_ports
    
    try:
        ports = scan_ports()
    except Exception as e:
        console.print(f"[red]Error scanning ports: {e}[/red]")
        raise typer.Exit(1)
        
    if not ports:
        console.print("[yellow]No COM ports found.[/yellow]")
        return
        
    table = Table(title="Discovered COM Ports", show_lines=True)
    table.add_column("COM")
    table.add_column("Friendly Name")
    if verbose:
        table.add_column("Manufacturer")
        table.add_column("HWID (VID/PID)")
    table.add_column("Role", style="cyan")
    table.add_column("Confidence")
    if verbose:
        table.add_column("Reason")
    
    for p in ports:
        if verbose:
            table.add_row(p.com, p.friendly_name, p.manufacturer, p.hwid, p.likely_role, p.confidence, p.reason)
        else:
            table.add_row(p.com, p.friendly_name, p.likely_role, p.confidence)
        
    console.print(table)


@ports_app.command("resolve")
def ports_resolve(
    role: str = typer.Option(..., "--role", help="Role to resolve (e.g., awr-rs232)"),
) -> None:
    """Recommend a COM port for a specific hardware role."""
    from awr2944_dca.hardware.ports import resolve_port
    
    candidates = resolve_port(role)
    if not candidates:
        console.print("[red]No COM ports available to resolve.[/red]")
        raise typer.Exit(1)
        
    console.print(f"Candidates for role [cyan]{role}[/cyan]:")
    
    table = Table(show_lines=True)
    table.add_column("Rank")
    table.add_column("COM")
    table.add_column("Name")
    table.add_column("Confidence")
    
    for i, c in enumerate(candidates, start=1):
        table.add_row(str(i), c.com, c.friendly_name, c.confidence)
        
    console.print(table)
    console.print("\n[yellow]To save your choice to the local experiment config, run:[/yellow]")
    console.print(f"  awr ports save --role {role} --com {candidates[0].com}")


@ports_app.command("save")
def ports_save(
    role: str = typer.Option(..., "--role", help="Role to save (e.g., awr-rs232)"),
    com: str = typer.Option(..., "--com", help="COM port name (e.g., COM8)"),
) -> None:
    """Save a COM port mapping to local_hardware.yaml in the experiment root."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.hardware.ports import save_local_hardware
    
    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)
        
    cfg = save_local_hardware(exp.root_dir, role, com)
    console.print(f"[green]Saved {role} -> {com}[/green] in {cfg.name}")
    console.print("This file is gitignored as COM ports are machine-specific.")


# @ti_app.command("connection-probe", deprecated=True)
def ti_connection_probe(
    com: str = typer.Option(None, "--com", help="[DEPRECATED] Use 'awr mmws connection script'"),
    baud: int = typer.Option(921600, "--baud", help="Baud rate"),
    timeout_ms: int = typer.Option(1000, "--timeout-ms", help="Connect timeout in ms"),
) -> None:
    """[DEPRECATED] Use 'awr mmws connection script' instead."""
    console.print("[yellow]DEPRECATED: Use 'awr mmws connection script' instead.[/yellow]")
    mmws_connection_script_cmd(com=com, baud=baud, timeout_ms=timeout_ms)


# @ti_app.command("connection-status", deprecated=True)
def ti_connection_status() -> None:
    """[DEPRECATED] Use 'awr mmws connection status' instead."""
    console.print("[yellow]DEPRECATED: Use 'awr mmws connection status' instead.[/yellow]")
    mmws_connection_status()


# ---------------------------------------------------------------------------
# awr mmws scan-scripts
# ---------------------------------------------------------------------------


@mmws_app.command("scan-scripts")
def mmws_scan_scripts() -> None:
    """Scan TI mmWave Studio scripts for ar1 API calls and build a catalog."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.legacy_mmws.catalog import discover_mmws_installations, scan_scripts, write_catalog

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    installs = discover_mmws_installations()
    if not installs:
        console.print("[red]No mmWave Studio installations found under C:\\ti[/red]")
        raise typer.Exit(1)

    console.print(f"Found {len(installs)} mmWave Studio installation(s):")
    for d in installs:
        console.print(f"  {d}")

    catalog = scan_scripts(installs)
    log_dir = exp.root_dir / "ti" / "probe_logs"
    json_path, md_path = write_catalog(catalog, log_dir)

    console.print(f"\n[green]Catalog written:[/green]")
    console.print(f"  {json_path.name} ({len(catalog)} functions)")
    console.print(f"  {md_path.name}")

    known = sum(1 for e in catalog.values() if e.known_stage)
    unknown = len(catalog) - known
    console.print(f"\n  Known stage functions: {known}")
    console.print(f"  Unknown (needs manual inspection): {unknown}")


# ---------------------------------------------------------------------------
# awr mmws connection plan / script / status
# ---------------------------------------------------------------------------


def _resolve_com(com: str | None) -> str:
    """Resolve COM port from argument or local_hardware.yaml."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.hardware.ports import get_local_hardware_config

    if com:
        return com

    try:
        exp = Experiment.open(".")
    except FileNotFoundError:
        pass
    else:
        cfg = get_local_hardware_config(exp.root_dir)
        saved = cfg.get("hardware", {}).get("awr_rs232_com")
        if saved:
            return saved

    return ""


@mmws_conn_app.command("plan")
def mmws_connection_plan() -> None:
    """Show the dry-run plan for connection-only stage (no script generated)."""
    from awr2944_dca.legacy_mmws.stages import get_stage, StageName

    stage = get_stage(StageName.CONNECTION_ONLY)

    console.print(Panel(
        f"[bold]Stage: {stage.display_name}[/bold]\n"
        f"Risk: {stage.risk}\n"
        f"Enabled: {stage.allowed_yet}",
        title="Connection Plan",
    ))

    table = Table(title="Planned ar1 Calls", show_lines=True)
    table.add_column("ar1 Call")
    table.add_column("Purpose")
    table.add_column("Allowed")

    purposes = {
        "SOPControl": "Set SOP mode for RS232 connection",
        "Connect": "Open RS232 connection to AWR device",
        "IsConnected": "Check connection status (optional)",
        "Disconnect": "Close RS232 connection (optional)",
    }
    for call in sorted(stage.allowed_ar1_calls):
        table.add_row(
            f"ar1.{call}",
            purposes.get(call, ""),
            "[green]Yes[/green]" if stage.allowed_yet else "[red]No[/red]",
        )
    console.print(table)
    console.print("\nTo generate the Lua script: [cyan]awr mmws connection script[/cyan]")


@mmws_conn_app.command("script")
def mmws_connection_script_cmd(
    com: str = typer.Option(None, "--com", help="COM port (e.g., COM6)"),
    baud: int = typer.Option(921600, "--baud", help="Baud rate"),
    timeout_ms: int = typer.Option(1000, "--timeout-ms", help="Connect timeout in ms"),
    execute: bool = typer.Option(False, "--execute", help="Auto-execute in mmWave Studio"),
    mode: str = typer.Option("auto", "--mode", help="Execution mode (auto, csharp-rstd, rstd, pywinauto, manual)"),
    manual: bool = typer.Option(False, "--manual", help="Print dofile command (debug fallback)"),
    timeout: float = typer.Option(30.0, "--timeout", help="Seconds to wait for result JSON"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Generate a connection-only Lua script for mmWave Studio.

    With --execute: auto-run via RSTD/.NET Remoting or pywinauto.
    With --manual: print the dofile command only (debug/fallback).
    Without either: generate script and print next-step instructions.
    """
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.legacy_mmws.bridge import StudioBridge, StageStatus
    import re

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    resolved = _resolve_com(com)
    if not resolved:
        console.print("[red]No COM port specified and awr_rs232_com not found in local_hardware.yaml.[/red]")
        console.print("Run:")
        console.print("  [cyan]awr ports scan[/cyan]")
        console.print("  [cyan]awr ports resolve --role awr-rs232[/cyan]")
        console.print("  [cyan]awr ports save --role awr-rs232 --com COM<number>[/cyan]")
        raise typer.Exit(1)

    m = re.search(r"\d+", resolved)
    if not m:
        console.print(f"[red]Could not parse numeric port from '{resolved}'.[/red]")
        raise typer.Exit(1)

    com_num = int(m.group(0))
    log_dir = exp.root_dir / "ti" / "probe_logs"
    bridge = StudioBridge(log_dir)
    script = bridge.generate_connection_script(com_num, baud, timeout_ms)

    console.print(f"[green]Generated {script.name}[/green] (COM{com_num}, baud={baud})")

    if manual:
        from awr2944_dca.legacy_mmws.executor import build_dofile_command
        console.print(f"\n[cyan]{build_dofile_command(script)}[/cyan]")
        return

    if execute:
        console.print("Executing in mmWave Studio...")
        try:
            result = bridge.execute(script, mode=mode, timeout=timeout, verbose=verbose)
        except RuntimeError as e:
            console.print(f"[red]ERROR: {e}[/red]")
            raise typer.Exit(1)

        status = result["status"]
        exec_result = result["exec_result"]
        stage_result = result["stage_result"]

        console.print(f"Transport: {exec_result.mode.value} ({exec_result.elapsed_seconds:.1f}s)")

        if status == StageStatus.TIMEOUT:
            console.print(f"[red]STATUS: TIMEOUT[/red] (no result JSON after {timeout}s)")
            raise typer.Exit(1)
        elif status == StageStatus.SUCCESS:
            com_display = stage_result.get("com_display", "?")
            console.print(f"[green]STATUS: SUCCESS[/green] (Connected on {com_display})")
        else:
            console.print("[red]STATUS: ERROR[/red]")
            err = stage_result.get("error")
            if err:
                console.print(f"  Error: {err}")
            ret = stage_result.get("connect_return")
            if ret is not None:
                console.print(f"  Connect returned: {ret}")
            raise typer.Exit(1)
        return

    # Default: print instructions
    console.print("Next steps:")
    console.print(f"  [cyan]awr mmws connection script --com {resolved} --execute[/cyan]  (auto-run)")
    console.print(f"  [cyan]awr mmws connection script --com {resolved} --manual[/cyan]  (print dofile)")
    console.print("  [cyan]awr mmws connection status[/cyan]  (check result)")



@mmws_conn_app.command("status")
def mmws_connection_status() -> None:
    """Check the result of the connection-only stage."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.legacy_mmws.bridge import StudioBridge, StageStatus
    from awr2944_dca.legacy_mmws.stages import StageName

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    log_dir = exp.root_dir / "ti" / "probe_logs"
    bridge = StudioBridge(log_dir)
    status, result = bridge.check_status(StageName.CONNECTION_ONLY)

    if status == StageStatus.NOT_RUN:
        console.print("[yellow]STATUS: NOT RUN[/yellow]")
    elif status == StageStatus.STALE_RESULT:
        console.print("[yellow]STATUS: STALE RESULT[/yellow] (run_id mismatch)")
    elif status == StageStatus.SUCCESS:
        com = result.get("com_display", "?")
        console.print(f"[green]STATUS: SUCCESS[/green] (Connected on {com})")
    else:
        console.print("[red]STATUS: ERROR[/red]")
        err = result.get("error")
        if err:
            console.print(f"  Error: {err}")
        ret = result.get("connect_return")
        if ret is not None:
            console.print(f"  Connect returned: {ret}")


# ---------------------------------------------------------------------------
# awr mmws static plan
# ---------------------------------------------------------------------------



# (Assume this gets injected inside cli.py where mmws_conn_app commands are defined)

@mmws_conn_app.command("preflight")
def mmws_connection_preflight() -> None:
    """Run pre-flight checks before attempting connection."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.legacy_mmws.executor import _is_mmws_running, _find_csharp_bridge
    from awr2944_dca.hardware.ports import get_local_hardware_config, scan_ports
    
    try:
        exp = Experiment.open(".")
        console.print(f"[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green] Inside experiment: {exp.root_dir.name}")
    except FileNotFoundError:
        console.print("[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â[/red] Not inside an experiment directory.")
        raise typer.Exit(1)
        
    if _is_mmws_running():
        console.print("[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green] mmWave Studio is running.")
    else:
        console.print("[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â[/red] mmWave Studio is NOT running.")
        
    if _find_csharp_bridge():
        console.print("[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green] C# Bridge is built.")
    else:
        console.print("[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â[/red] C# Bridge not found. Run: awr mmws csharp-bridge build")
        
    hw = get_local_hardware_config(exp.root_dir)
    com = hw.get("hardware", {}).get("awr_rs232_com")
    if com:
        console.print(f"[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green] Local hardware config has awr_rs232_com: {com}")
        
        # Check heuristics
        ports = scan_ports()
        p_info = next((p for p in ports if p.com.upper() == com.upper()), None)
        if p_info:
            if p_info.likely_role == "dca_ftdi_candidate":
                console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â[/red] WARNING: {com} is identified as the DCA1000 FTDI port. This is usually wrong for AWR RS232.")
            elif p_info.likely_role == "awr_xds_uart_candidate":
                console.print(f"[yellow]![/yellow] WARNING: {com} is an XDS110 port. AWR2944 usually uses the FTDI port for mmWave Studio RS232.")
            else:
                console.print(f"[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green] Port role seems acceptable: {p_info.likely_role}")
        else:
            console.print(f"[yellow]![/yellow] Port {com} is not currently visible in Windows Device Manager.")
            
    else:
        console.print("[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â[/red] Local hardware config missing awr_rs232_com. Run: awr ports scan")


def _run_diag_step(com_num: int, baud: int, mode: str, timeout: float, verbose: bool, steps: list[str], script_name: str) -> None:
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.legacy_mmws.lua_builder import write_connection_diag_script
    from awr2944_dca.legacy_mmws.executor import execute_script
    import uuid
    
    exp = Experiment.open(".")
    log_dir = exp.root_dir / "ti" / "probe_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = str(uuid.uuid4())
    script_path = log_dir / script_name
    
    write_connection_diag_script(
        out_path=script_path,
        run_id=run_id,
        com_num=com_num,
        baud=baud,
        steps=steps,
    )
    console.print(f"[cyan]Generated diagnostic script: {script_path.name}[/cyan]")
    
    # Execute
    result = execute_script(script_path, mode=mode, timeout=timeout, verbose=verbose, allow_fallback=False)
    
    if not result.success:
        if result.error and "HARDWARE_SCRIPT_TIMEOUT" in result.error:
            console.print(f"[red]STATUS: HARDWARE_SCRIPT_TIMEOUT[/red]")
            # Parse jsonl
            jsonl = log_dir / "connection_progress.jsonl"
            last_step = "unknown"
            if jsonl.exists():
                try:
                    for line in jsonl.read_text().splitlines():
                        data = json.loads(line)
                        last_step = data.get("step", last_step)
                except Exception:
                    pass
            console.print(f"[red]HUNG_AT_STEP: {last_step}[/red]")
            console.print("Please restart mmWave Studio and reset the board before retrying.")
        else:
            console.print(f"[red]ERROR: {result.error}[/red]")
        raise typer.Exit(1)
        
    # Check result json
    res_json = log_dir / "connection_result.json"
    if res_json.exists():
        data = json.loads(res_json.read_text())
        err = data.get("error")
        if err:
            console.print(f"[red]STATUS: ERROR[/red]")
            console.print(f"  {err}")
            raise typer.Exit(1)
        else:
            console.print(f"[green]STATUS: SUCCESS[/green] (completed without error)")
    else:
        console.print("[red]STATUS: ERROR (Result JSON not found)[/red]")
        raise typer.Exit(1)


@mmws_conn_app.command("diag")
def mmws_connection_diag(
    com: str = typer.Option(..., "--com", help="COM port (e.g., COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    execute: bool = typer.Option(False, "--execute", help="Auto-execute in mmWave Studio"),
    mode: str = typer.Option("csharp-rstd", "--mode", help="Execution mode (csharp-rstd, manual)"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Run full diagnostic connection with step logging."""
    if not execute:
        console.print("Use --execute to run the diagnostics.")
        return
    m = re.search(r"\d+", com)
    if not m:
        console.print(f"[red]Could not parse numeric port from '{com}'.[/red]")
        raise typer.Exit(1)
    com_num = int(m.group(0))
    _run_diag_step(com_num, baud, mode, 30.0, verbose, ["is_connected_initial", "sop", "connect", "is_connected_final"], "connection_diag.lua")


@mmws_conn_app.command("diag-status")
def mmws_connection_diag_status() -> None:
    """Check the status of the last connection diagnostic run."""
    from awr2944_dca.api.experiment import Experiment
    try:
        exp = Experiment.open(".")
    except Exception:
        raise typer.Exit(1)
        
    log_dir = exp.root_dir / "ti" / "probe_logs"
    res_json = log_dir / "connection_result.json"
    prog_jsonl = log_dir / "connection_progress.jsonl"
    
    if not res_json.exists() and not prog_jsonl.exists():
        console.print("[yellow]STATUS: NOT RUN[/yellow]")
        return
        
    # Check if hung
    if prog_jsonl.exists() and not res_json.exists():
        last_step = "unknown"
        try:
            for line in prog_jsonl.read_text().splitlines():
                last_step = json.loads(line).get("step", last_step)
        except Exception:
            pass
        console.print(f"[red]STATUS: HUNG_AT_STEP={last_step}[/red]")
        return
        
    if res_json.exists():
        data = json.loads(res_json.read_text())
        if data.get("error"):
            console.print(f"[red]STATUS: ERROR[/red] - {data['error']}")
        else:
            console.print("[green]STATUS: SUCCESS[/green]")


@mmws_conn_app.command("is-connected")
def mmws_connection_is_connected(
    execute: bool = typer.Option(False, "--execute", help="Auto-execute in mmWave Studio"),
    mode: str = typer.Option("csharp-rstd", "--mode", help="Execution mode (csharp-rstd, manual)"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Run ONLY the IsConnected check."""
    if not execute:
        console.print("Use --execute to run the script.")
        return
    _run_diag_step(0, 115200, mode, 10.0, verbose, ["is_connected_initial"], "is_connected_only.lua")


@mmws_conn_app.command("sop")
def mmws_connection_sop(
    execute: bool = typer.Option(False, "--execute", help="Auto-execute in mmWave Studio"),
    mode: str = typer.Option("csharp-rstd", "--mode", help="Execution mode (csharp-rstd, manual)"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Run ONLY the SOPControl(2) check."""
    if not execute:
        console.print("Use --execute to run the script.")
        return
    _run_diag_step(0, 115200, mode, 10.0, verbose, ["sop"], "sop_only.lua")


@mmws_conn_app.command("disconnect")
def mmws_connection_disconnect(
    execute: bool = typer.Option(False, "--execute", help="Auto-execute in mmWave Studio"),
    mode: str = typer.Option("csharp-rstd", "--mode", help="Execution mode (csharp-rstd, manual)"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Run ONLY the Disconnect check."""
    if not execute:
        console.print("Use --execute to run the script.")
        return
    _run_diag_step(0, 115200, mode, 10.0, verbose, ["disconnect"], "disconnect_only.lua")


@mmws_conn_app.command("connect-only")
def mmws_connection_connect_only(
    com: str = typer.Option(..., "--com", help="COM port (e.g., COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    execute: bool = typer.Option(False, "--execute", help="Auto-execute in mmWave Studio"),
    mode: str = typer.Option("csharp-rstd", "--mode", help="Execution mode (csharp-rstd, manual)"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Run ONLY the ar1.Connect check."""
    if not execute:
        console.print("Use --execute to run the script.")
        return
    m = re.search(r"\d+", com)
    if not m:
        console.print(f"[red]Could not parse numeric port from '{com}'.[/red]")
        raise typer.Exit(1)
    com_num = int(m.group(0))
    _run_diag_step(com_num, baud, mode, 15.0, verbose, ["connect"], "connect_only_diag.lua")



@mmws_app.command("static-plan")
def mmws_static_plan(
    config: Path = typer.Argument(..., help="Path to capture.yaml"),
) -> None:
    """Dry-run plan: show what static-config ar1 calls would be needed.

    Does NOT generate an executable Lua script.
    """
    from awr2944_dca.config.schema import RadarConfig
    from awr2944_dca.legacy_mmws.stages import STATIC_CONFIG_FIELD_MAP, get_stage, StageName

    if not config.exists():
        console.print(f"[red]Config file not found: {config}[/red]")
        raise typer.Exit(1)

    cfg = RadarConfig.from_yaml(config)
    stage = get_stage(StageName.STATIC_CONFIG)

    console.print(Panel(
        f"[bold]Stage: {stage.display_name}[/bold]\n"
        f"Risk: {stage.risk}\n"
        f"Enabled: [red]{stage.allowed_yet}[/red] (dry-run only)",
        title="Static Config Plan",
    ))

    # Safety checks
    warnings = []
    if len(cfg.hardware.tx_enabled) > 1:
        warnings.append("WARNING: Multiple TX channels enabled. Consider single TX for first bring-up.")
    if cfg.adc.bits not in (12, 14, 16):
        warnings.append(f"WARNING: Unusual ADC bits ({cfg.adc.bits}). Standard values: 12, 14, 16.")

    for w in warnings:
        console.print(f"[yellow]{w}[/yellow]")

    # Build the plan table
    tx_mask = 0
    for tx in cfg.hardware.tx_enabled:
        tx_mask |= 1 << tx
    rx_mask = 0
    for rx in cfg.hardware.rx_enabled:
        rx_mask |= 1 << rx

    adc_fmt = 2 if cfg.adc.is_complex else 1  # 1=real, 2=complex1x

    table = Table(title="Intended ar1 Calls (NOT executed)", show_lines=True)
    table.add_column("ar1 Call")
    table.add_column("Source Fields")
    table.add_column("Example Args")
    table.add_column("Allowed Yet")

    plans = [
        ("ChanNAdcConfig", f"rx_mask={rx_mask}, tx_mask={tx_mask}, bits={cfg.adc.bits}, fmt={adc_fmt}"),
        ("LPModConfig", f"low_power={0}"),
        ("DataPathConfig", f"intf_sel={1}, fmt={adc_fmt}"),
        ("LvdsClkConfig", f"lanes={cfg.adc.num_lvds_lanes}"),
        ("LVDSLaneConfig", f"lanes={cfg.adc.num_lvds_lanes}"),
    ]
    for call, example in plans:
        fields = ", ".join(STATIC_CONFIG_FIELD_MAP.get(call, []))
        table.add_row(
            f"ar1.{call}",
            fields,
            example,
            "[red]No[/red]",
        )
    console.print(table)
    console.print("\n[yellow]This is a dry-run plan. No Lua script is generated.[/yellow]")
    console.print("Static config execution is not yet enabled.")


# ---------------------------------------------------------------------------
# awr mmws inspect-execution (no experiment needed)
# ---------------------------------------------------------------------------


@mmws_app.command("inspect-execution")
def mmws_inspect_execution() -> None:
    """Discover available mmWave Studio execution transports.

    Does NOT require an experiment context (.awr-experiment).
    """
    from awr2944_dca.legacy_mmws.executor import detect_available_modes

    modes = detect_available_modes()

    table = Table(title="Execution Transports", show_lines=True)
    table.add_column("Mode")
    table.add_column("Available")
    table.add_column("Confidence")
    table.add_column("Detail")

    for m in modes:
        avail_str = "[green]Yes[/green]" if m.available else "[red]No[/red]"
        table.add_row(m.mode.value, avail_str, m.confidence, m.detail)

    console.print(table)

    available = [m for m in modes if m.available and m.mode.value != "manual_one_shot"]
    if available:
        console.print(f"\n[green]{len(available)} automatic transport(s) available.[/green]")
    else:
        console.print("\n[yellow]No automatic transports available.[/yellow]")
        console.print("Install: [cyan]python -m pip install -e \".[automation]\"[/cyan]")
        console.print("Then start mmWave Studio and try again.")


# ---------------------------------------------------------------------------
# awr mmws run-script
# ---------------------------------------------------------------------------


@mmws_app.command("run-script")
def mmws_run_script(
    script: Path = typer.Argument(..., help="Path to Lua script"),
    mode: str = typer.Option("auto", "--mode", help="Transport: auto, rstd, pywinauto, manual"),
    timeout: float = typer.Option(30.0, "--timeout", help="Seconds to wait for result JSON"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Execute a Lua script in mmWave Studio.

    With --mode auto (default): tries RSTD, then pywinauto. Errors if none available.
    With --mode manual: prints dofile command only.
    """
    from awr2944_dca.legacy_mmws.executor import execute_script, build_dofile_command, wait_for_result_json

    if not script.exists():
        console.print(f"[red]Script not found: {script}[/red]")
        raise typer.Exit(1)

    if mode == "manual":
        console.print(f"\n[cyan]{build_dofile_command(script)}[/cyan]")
        return

    console.print(f"Executing {script.name} in mmWave Studio (mode={mode})...")
    try:
        exec_result = execute_script(script, mode=mode, verbose=verbose)
    except RuntimeError as e:
        console.print(f"[red]ERROR: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"Transport: {exec_result.mode.value}")
    if exec_result.return_code is not None:
        console.print(f"SendCommand return code: {exec_result.return_code}")
    if exec_result.lua_command_sent:
        console.print(f"Command sent: {exec_result.lua_command_sent}")

    if verbose and exec_result.verbose_log:
        console.print("[dim]Verbose log:[/dim]")
        for line in exec_result.verbose_log:
            console.print(f"  [dim]{line}[/dim]")

    if exec_result.success:
        console.print(f"[green]Command submitted[/green] (return code: {exec_result.return_code})")
        console.print("[dim]Waiting for result JSON is the caller's responsibility.[/dim]")
    else:
        console.print(f"[red]FAILED: {exec_result.error}[/red]")
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# awr mmws smoke
# ---------------------------------------------------------------------------


@mmws_app.command("smoke")
def mmws_smoke(
    execute: bool = typer.Option(False, "--execute", help="Auto-execute in mmWave Studio"),
    manual: bool = typer.Option(False, "--manual", help="Print dofile command only"),
    timeout: float = typer.Option(30.0, "--timeout", help="Seconds to wait for result"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
    mode: str = typer.Option("auto", "--mode", help="Execution mode: auto, csharp-rstd, matlab-rstd, rstd, pywinauto, manual"),
    apartment: str = typer.Option("mta", "--apartment", help="ApartmentState for C# RSTD bridge (mta or sta)"),
) -> None:
    """Generate and optionally execute a harmless smoke test.

    Proves: Python -> mmWave Studio -> Lua -> JSON -> Python works.
    Contains NO ar1 hardware calls.
    """
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.legacy_mmws.bridge import StudioBridge, StageStatus

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    log_dir = exp.root_dir / "ti" / "probe_logs"
    bridge = StudioBridge(log_dir)
    script = bridge.generate_smoke_script()

    console.print(f"[green]Generated {script.name}[/green] (no ar1 hardware calls)")

    if manual:
        from awr2944_dca.legacy_mmws.executor import build_dofile_command
        console.print(f"\n[cyan]{build_dofile_command(script)}[/cyan]")
        return

    if execute:
        console.print("Executing smoke test in mmWave Studio...")
        try:
            result = bridge.execute(script, mode=mode, timeout=timeout, verbose=verbose, apartment=apartment)
        except RuntimeError as e:
            console.print(f"[red]ERROR: {e}[/red]")
            raise typer.Exit(1)

        status = result["status"]
        exec_result = result["exec_result"]
        stage_result = result["stage_result"]
        execution_status = result.get("execution_status")

        console.print(f"Transport: {exec_result.mode.value} ({exec_result.elapsed_seconds:.1f}s)")
        if exec_result.return_code is not None:
            console.print(f"SendCommand return code: {exec_result.return_code}")
        if execution_status:
            console.print(f"Execution status: {execution_status.value}")
        if exec_result.lua_command_sent:
            console.print(f"Command sent: {exec_result.lua_command_sent}")

        if verbose and exec_result.verbose_log:
            console.print("[dim]Verbose log:[/dim]")
            for line in exec_result.verbose_log:
                console.print(f"  [dim]{line}[/dim]")

        expected_result = log_dir / "smoke_result.json"
        console.print(f"Expected result: {expected_result}")
        console.print(f"Result file exists: {expected_result.exists()}")

        if status == StageStatus.TIMEOUT:
            console.print(f"[red]STATUS: SUBMITTED_BUT_NO_RESULT[/red] (no result JSON after {timeout}s)")
            console.print("The Lua script probably did not execute in Studio.")
            console.print("Run [cyan]awr mmws rstd-ping --execute[/cyan] to diagnose.")
            raise typer.Exit(1)
        elif status == StageStatus.SUCCESS:
            log_ok = stage_result.get("log_available", False)
            console.print(f"[green]STATUS: SUCCESS[/green]")
            console.print(f"  WriteToLog available: {log_ok}")
            console.print("  Python -> mmWave Studio -> Lua -> JSON -> Python: [green]WORKING[/green]")
        else:
            console.print("[red]STATUS: LUA_REPORTED_ERROR[/red]")
            err = stage_result.get("error")
            if err:
                console.print(f"  Error: {err}")
            raise typer.Exit(1)
        return

    # Default: instructions
    console.print("Next steps:")
    console.print("  [cyan]awr mmws smoke --execute[/cyan]           (auto-run)")
    console.print("  [cyan]awr mmws smoke --execute --verbose[/cyan] (auto-run with diagnostics)")
    console.print("  [cyan]awr mmws smoke --manual[/cyan]            (print dofile)")


# ---------------------------------------------------------------------------
# awr mmws rstd-ping (diagnostic, no experiment needed)
# ---------------------------------------------------------------------------


@mmws_app.command("rstd-ping")
def mmws_rstd_ping(
    execute: bool = typer.Option(False, "--execute", help="Actually send commands through RSTD"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
    per_variant_timeout: float = typer.Option(5.0, "--per-variant-timeout", help="Max seconds to wait per variant"),
) -> None:
    """Diagnostic: test RSTD .NET Remoting with inline Lua.

    Sends minimal inline Lua through RSTD SendCommand (no dofile).
    Tries multiple command formats and reports which ones work.

    Does NOT require an experiment context.
    """
    import json
    from awr2944_dca.legacy_mmws.executor import (
        _is_rstd_port_open, _find_rtttnet_dll, _RSTD_PORT,
        _HAVE_PYTHONNET, rstd_ping_diagnostic,
    )

    console.print("[bold]RSTD Ping Diagnostic[/bold]")
    console.print()

    # Pre-checks
    dll = _find_rtttnet_dll()
    port_open = _is_rstd_port_open()

    console.print(f"pythonnet installed: {'[green]Yes[/green]' if _HAVE_PYTHONNET else '[red]No[/red]'}")
    console.print(f"RtttNetClientAPI.dll: {'[green]' + str(dll) + '[/green]' if dll else '[red]Not found[/red]'}")
    console.print(f"TCP {_RSTD_PORT}: {'[green]Open[/green]' if port_open else '[red]Closed[/red]'}")

    if not _HAVE_PYTHONNET:
        console.print("\n[red]Cannot proceed: pythonnet not installed[/red]")
        console.print("Install: [cyan]python -m pip install -e \".[automation]\"[/cyan]")
        raise typer.Exit(1)

    if not port_open:
        console.print(f"\n[red]Cannot proceed: RSTD port {_RSTD_PORT} not open[/red]")
        console.print("Is mmWave Studio running with RSTD.NetStart()?")
        raise typer.Exit(1)

    if not execute:
        console.print("\nAdd [cyan]--execute[/cyan] to actually send commands through RSTD.")
        return

    # Find a writable directory (use experiment if available, else temp)
    from awr2944_dca.api.experiment import Experiment
    try:
        exp = Experiment.open(".")
        result_dir = exp.root_dir / "ti" / "probe_logs"
    except FileNotFoundError:
        result_dir = Path.cwd() / "ti" / "probe_logs"

    result_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\nResult directory: {result_dir}")
    console.print("Running diagnostic variants...")

    results = rstd_ping_diagnostic(
        result_dir, 
        verbose=verbose, 
        per_variant_timeout=per_variant_timeout,
        print_fn=console.print
    )

    # Display results
    console.print("\n[bold]Summary[/bold]")
    table = Table(title="RSTD Ping Variants", show_lines=True)
    table.add_column("Variant")
    table.add_column("Send Return")
    table.add_column("Result Exists")
    table.add_column("Status")
    table.add_column("Elapsed")

    for v in results["variants_tried"]:
        file_str = "N/A"
        if v.get("file_appeared") is True:
            file_str = "[green]Yes[/green]"
        elif v.get("file_appeared") is False:
            file_str = "[red]No[/red]"
            
        status_str = "[red]FAILED[/red]"
        if v.get("success_submit") and (v.get("file_appeared") or v.get("file_appeared") is None):
            status_str = "[green]SUCCESS[/green]"
        if v.get("error"):
            status_str += f"\n{v['error']}"
            
        elapsed_str = f"{v.get('elapsed', 0.0):.2f}s"

        table.add_row(
            v["name"],
            str(v.get("return_code", "?")),
            file_str,
            status_str,
            elapsed_str,
        )

    console.print(table)

    if verbose:
        for v in results["variants_tried"]:
            if v.get("verbose_log"):
                console.print(f"\n[dim]Verbose log for {v['name']}:[/dim]")
                for line in v["verbose_log"]:
                    console.print(f"  [dim]{line}[/dim]")
            console.print(f"  [dim]Lua: {v.get('lua', '')!r}[/dim]")

    if results["working_variant"]:
        console.print(f"\n[green]Working variant: {results['working_variant']}[/green]")
        console.print("RSTD execution channel is functional.")

        # Check if it was a file-writing variant
        for v in results["variants_tried"]:
            if v.get("result_json"):
                console.print(f"Result JSON: {json.dumps(v['result_json'])}")
                break
    else:
        console.print("\n[red]All variants failed.[/red]")
        console.print("Run step-level diagnostics to identify the exact hang point:")
        console.print("  [cyan]awr mmws rstd-env[/cyan]")
        console.print("  [cyan]awr mmws rstd-methods --verbose[/cyan]")
        console.print("  [cyan]awr mmws rstd-worker-test --step import-clr --verbose[/cyan]")
        console.print("  [cyan]awr mmws rstd-worker-test --step init --verbose[/cyan]")
        console.print("  [cyan]awr mmws rstd-worker-test --step connect --verbose[/cyan]")
        console.print("  [cyan]awr mmws rstd-worker-test --step send-log --verbose[/cyan]")

    # Write diagnostic report
    report_path = result_dir / "rstd_execution_notes.md"
    _write_rstd_report(report_path, results, dll, port_open)
    console.print(f"\nDiagnostic report: {report_path}")


def _write_rstd_report(path: Path, results: dict, dll: Path | None, port_open: bool) -> None:
    """Write RSTD execution diagnostic report."""
    lines = [
        "# RSTD Execution Diagnostic Report",
        "",
        "## Environment",
        f"- RtttNetClientAPI.dll: {dll}",
        f"- TCP 2777 open: {port_open}",
        f"- pythonnet available: True",
        "",
        "## Known-Good API Sequence (from TI MATLAB example)",
        "",
        "Source: `C:\\ti\\mmwave_studio_03_00_00_14\\mmWaveStudio\\MatlabExamples\\",
        "4chip_cascade_TxBF_example\\RSTD\\Init_RSTD_Connection.m`",
        "",
        "```matlab",
        "% 1. Load DLL",
        "RSTD_Assembly = NET.addAssembly(RSTD_DLL_Path);",
        "",
        "% 2. Init client",
        "ErrStatus = RtttNetClientAPI.RtttNetClient.Init();",
        "",
        "% 3. Connect to localhost:2777",
        "ErrStatus = RtttNetClientAPI.RtttNetClient.Connect('127.0.0.1', 2777);",
        "",
        "% 4. Send Lua command string",
        "Lua_String = 'WriteToLog(\"Running script from MATLAB\\n\", \"green\")';",
        "ErrStatus = RtttNetClientAPI.RtttNetClient.SendCommand(Lua_String);",
        "% Returns 30000 if no error",
        "```",
        "",
        "## Key Notes",
        "",
        "- `SendCommand` takes raw Lua strings, not file paths",
        "- TI MATLAB examples send `ar1.ProfileConfig(...)` directly as strings",
        "- For scripts, use `dofile([[C:/path/to/script.lua]])`",
        "- Return code 30000 = command submitted, NOT proof of Lua success",
        "- `Init()` alone is NOT enough ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â `Connect('127.0.0.1', 2777)` is required",
        "",
        "## Variant Results",
        "",
    ]
    for v in results["variants_tried"]:
        lines.append(f"### {v['name']}")
        lines.append(f"- Submit OK: {v.get('success_submit')}")
        lines.append(f"- Return code: {v.get('return_code')}")
        lines.append(f"- File appeared: {v.get('file_appeared')}")
        lines.append(f"- Error: {v.get('error')}")
        lines.append(f"- Lua: `{v.get('lua', '')}`")
        lines.append("")

    if results["working_variant"]:
        lines.append(f"## Conclusion: **{results['working_variant']}** worked")
    else:
        lines.append("## Conclusion: **All variants failed**")

    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# awr mmws rstd-env (environment diagnostics, no experiment needed)
# ---------------------------------------------------------------------------


@mmws_app.command("rstd-env")
def mmws_rstd_env() -> None:
    """Print RSTD environment diagnostics: bitness, runtime, paths.

    Does NOT require an experiment context.
    """
    import platform
    import struct
    from awr2944_dca.legacy_mmws.executor import (
        _is_rstd_port_open, _find_rtttnet_dll, _find_mmws_dir,
        _RSTD_PORT, _HAVE_PYTHONNET,
    )

    console.print("[bold]RSTD Environment Diagnostics[/bold]\n")

    # Python info
    console.print(f"Python executable: {sys.executable}")
    console.print(f"Python version:    {platform.python_version()}")
    bits = struct.calcsize("P") * 8
    console.print(f"Python architecture: [{'green' if bits == 64 else 'yellow'}]{bits}-bit[/{'green' if bits == 64 else 'yellow'}]")

    # pythonnet
    if _HAVE_PYTHONNET:
        try:
            import clr  # type: ignore
            pn_ver = getattr(clr, "__version__", "unknown")
            console.print(f"pythonnet version: [green]{pn_ver}[/green]")
        except Exception:
            console.print("pythonnet version: [green]installed (version unknown)[/green]")

        # .NET runtime
        try:
            import clr  # type: ignore
            from System import Environment  # type: ignore
            console.print(f".NET CLR version:  {Environment.Version}")
        except Exception:
            console.print(".NET CLR version:  [yellow]could not determine[/yellow]")
    else:
        console.print("pythonnet: [red]not installed[/red]")

    # DLL
    dll = _find_rtttnet_dll()
    console.print(f"\nRtttNetClientAPI.dll: {'[green]' + str(dll) + '[/green]' if dll else '[red]Not found[/red]'}")

    # mmWave Studio dir
    mmws_dir = _find_mmws_dir()
    console.print(f"mmWave Studio dir:   {'[green]' + str(mmws_dir) + '[/green]' if mmws_dir else '[red]Not found[/red]'}")

    # CWD
    console.print(f"Current directory:   {Path.cwd()}")

    # TCP 2777
    port_open = _is_rstd_port_open()
    console.print(f"\nTCP {_RSTD_PORT}: {'[green]Open[/green]' if port_open else '[red]Closed[/red]'}")

    if bits == 32:
        console.print("\n[yellow]Warning: 32-bit Python detected. TI DLLs may require 64-bit.[/yellow]")


# ---------------------------------------------------------------------------
# awr mmws rstd-methods (DLL method introspection via isolated subprocess)
# ---------------------------------------------------------------------------


@mmws_app.command("rstd-methods")
def mmws_rstd_methods(
    timeout: float = typer.Option(10.0, "--timeout", help="Max seconds for introspection subprocess"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
) -> None:
    """Introspect RtttNetClientAPI.dll public methods via isolated subprocess.

    Does NOT require an experiment context.
    Runs introspection in a separate process so hangs are safely killed.
    """
    from awr2944_dca.legacy_mmws.executor import run_rstd_introspect, _find_rtttnet_dll

    dll = _find_rtttnet_dll()
    if not dll:
        console.print("[red]RtttNetClientAPI.dll not found[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]RSTD DLL Method Introspection[/bold]")
    console.print(f"DLL: {dll}")
    console.print(f"Timeout: {timeout}s\n")

    result = run_rstd_introspect(timeout=timeout, verbose=verbose)

    if not result["success"]:
        error = result.get("error", "Unknown error")
        last_step = result.get("last_worker_step")
        console.print(f"[red]Introspection failed: {error}[/red]")
        if last_step:
            console.print(f"[yellow]Last worker step: {last_step}[/yellow]")
        raise typer.Exit(1)

    methods = result.get("methods", [])
    properties = result.get("properties", [])

    console.print(f"[green]Found {len(methods)} methods, {len(properties)} properties[/green]\n")

    if methods:
        console.print("[bold]Methods:[/bold]")
        for m in methods:
            console.print(f"  - {m}")

    if properties:
        console.print("\n[bold]Properties:[/bold]")
        for p in properties:
            console.print(f"  - {p}")

    # Highlight key methods
    console.print("\n[bold]Key methods available:[/bold]")
    for key in ["Init", "Connect", "IsConnected", "SendCommand", "RunScript", "Disconnect"]:
        present = key in methods
        console.print(f"  {key}: {'[green]Yes[/green]' if present else '[red]No[/red]'}")


# ---------------------------------------------------------------------------
# awr mmws rstd-worker-test (step-level diagnostic, no experiment needed)
# ---------------------------------------------------------------------------


@mmws_app.command("rstd-worker-test")
def mmws_rstd_worker_test(
    step: str = typer.Option(..., "--step", help="Step to stop at: import-clr, add-reference, import-api, init, connect, send-log"),
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
    timeout: float = typer.Option(10.0, "--timeout", help="Max seconds for worker subprocess"),
    cwd_mode: str = typer.Option("default", "--cwd-mode", help="Worker CWD: default or mmwave-studio"),
    method: str = typer.Option("SendCommand", "--method", help="RtttNetClient method: SendCommand or RunScript"),
) -> None:
    """Test RSTD worker subprocess up to a specific step.

    Isolates exactly which .NET API call hangs.
    Does NOT require an experiment context.

    Steps (in order):
      import-clr        - import pythonnet/clr
      add-reference     - clr.AddReference(dll)
      import-api        - from RtttNetClientAPI import RtttNetClient
      init              - RtttNetClient.Init()
      connect           - RtttNetClient.Connect(host, port)
      send-log          - RtttNetClient.SendCommand(WriteToLog)
      runscript-file    - RtttNetClient.RunScript(lua_file_path)
      sendcommand-dofile - RtttNetClient.SendCommand('dofile([[path]])')
    """
    from awr2944_dca.legacy_mmws.executor import run_rstd_worker_test as _run_test

    valid_steps = [
        "import-clr", "add-reference", "import-api", "init", "connect",
        "send-log", "runscript-file", "sendcommand-dofile",
    ]
    if step not in valid_steps:
        console.print(f"[red]Invalid step '{step}'. Valid: {', '.join(valid_steps)}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]RSTD Worker Test[/bold]")
    console.print(f"Step:     {step}")
    console.print(f"Timeout:  {timeout}s")
    console.print(f"CWD mode: {cwd_mode}")
    console.print(f"Method:   {method}\n")

    result = _run_test(
        step=step,
        timeout=timeout,
        verbose=verbose,
        cwd_mode=cwd_mode,
        method=method,
    )

    if result["success"]:
        console.print(f"[green]Step '{step}' completed successfully.[/green]")
        worker_data = result.get("worker_result", {})
        if worker_data.get("init_return") is not None:
            console.print(f"  Init return:    {worker_data['init_return']}")
        if worker_data.get("connect_return") is not None:
            console.print(f"  Connect return: {worker_data['connect_return']}")
        if worker_data.get("send_return") is not None:
            console.print(f"  Send return:    {worker_data['send_return']}")
        if worker_data.get("elapsed_seconds") is not None:
            console.print(f"  Elapsed:        {worker_data['elapsed_seconds']:.2f}s")
        # Check Lua-side result
        lua_result = result.get("lua_result")
        if lua_result:
            import json
            console.print(f"  [green]Lua result JSON: {json.dumps(lua_result)}[/green]")
        elif step in ("runscript-file", "sendcommand-dofile"):
            console.print(f"  [yellow]No Lua result file appeared (script may not have executed)[/yellow]")
    else:
        error = result.get("error", "Unknown error")
        last_step = result.get("last_worker_step")
        console.print(f"[red]Step '{step}' FAILED: {error}[/red]")
        if last_step:
            console.print(f"[yellow]Last completed worker step: {last_step}[/yellow]")

    # Print progress log
    progress_text = result.get("progress", "")
    if progress_text and verbose:
        console.print(f"\n[dim]Progress log:[/dim]")
        for line in progress_text.strip().splitlines():
            console.print(f"  [dim]{line}[/dim]")

    # Print stderr
    stderr = result.get("stderr", "")
    if stderr and verbose:
        console.print(f"\n[dim]Worker stderr:[/dim]")
        for line in stderr.strip().splitlines():
            console.print(f"  [dim]{line}[/dim]")

    if not result["success"]:
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# awr mmws rstd-last-error (diagnostic, no experiment needed)
# ---------------------------------------------------------------------------


@mmws_app.command("rstd-last-error")
def mmws_rstd_last_error(
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed diagnostic info"),
    timeout: float = typer.Option(10.0, "--timeout", help="Max seconds for subprocess"),
) -> None:
    """Query RSTD GetLastError() and GetErrMsg() via isolated subprocess.

    Runs Init + Connect (no Send), then calls GetLastError/GetErrMsg.
    Does NOT require an experiment context.
    """
    from awr2944_dca.legacy_mmws.executor import run_rstd_get_last_error, _find_rtttnet_dll

    dll = _find_rtttnet_dll()
    if not dll:
        console.print("[red]RtttNetClientAPI.dll not found[/red]")
        raise typer.Exit(1)

    console.print("[bold]RSTD Last Error Diagnostic[/bold]")
    console.print(f"DLL: {dll}")
    console.print(f"Timeout: {timeout}s\n")

    result = run_rstd_get_last_error(timeout=timeout, verbose=verbose)

    if not result["success"]:
        error = result.get("error", "Unknown error")
        last_step = result.get("last_worker_step")
        console.print(f"[red]Failed: {error}[/red]")
        if last_step:
            console.print(f"[yellow]Last worker step: {last_step}[/yellow]")
        raise typer.Exit(1)

    console.print(f"GetLastError(): {result.get('last_error', 'N/A')}")
    console.print(f"GetErrMsg():    {result.get('error_msg', 'N/A')}")
    console.print(f"Elapsed:        {result.get('elapsed_seconds', 0):.2f}s")


# ---------------------------------------------------------------------------
# awr mmws studio launch / attach / status (no experiment needed)
# ---------------------------------------------------------------------------


@mmws_studio_app.command("launch")
def mmws_studio_launch() -> None:
    """Launch mmWave Studio from the discovered installation."""
    from awr2944_dca.legacy_mmws.executor import _find_mmws_exe
    import subprocess

    exe = _find_mmws_exe()
    if not exe:
        console.print("[red]mmWaveStudio.exe not found under C:\\ti[/red]")
        raise typer.Exit(1)

    console.print(f"Launching {exe}...")
    subprocess.Popen([str(exe)], cwd=str(exe.parent))
    console.print("[green]mmWave Studio launch initiated.[/green]")
    console.print("Wait for it to fully load before running commands.")


@mmws_studio_app.command("attach")
def mmws_studio_attach() -> None:
    """Check if Python can reach a running mmWave Studio instance."""
    from awr2944_dca.legacy_mmws.executor import (
        _is_mmws_running, _is_rstd_port_open, _RSTD_PORT,
        _HAVE_PYTHONNET, _HAVE_PYWINAUTO,
    )

    running = _is_mmws_running()
    port_open = _is_rstd_port_open()

    if running:
        console.print("[green]mmWave Studio is running.[/green]")
    else:
        console.print("[red]mmWave Studio is NOT running.[/red]")
        console.print("Launch it: [cyan]awr mmws studio launch[/cyan]")

    if port_open:
        console.print(f"[green]RSTD port {_RSTD_PORT} is open.[/green]")
    else:
        console.print(f"[yellow]RSTD port {_RSTD_PORT} is closed.[/yellow]")
        if running:
            console.print("Check if RSTD.NetStart() was called (it should be in Startup.lua).")

    if _HAVE_PYTHONNET:
        console.print("[green]pythonnet is installed.[/green]")
    else:
        console.print("[yellow]pythonnet not installed.[/yellow]")
    if _HAVE_PYWINAUTO:
        console.print("[green]pywinauto is installed.[/green]")
    else:
        console.print("[yellow]pywinauto not installed.[/yellow]")

    if not _HAVE_PYTHONNET and not _HAVE_PYWINAUTO:
        console.print("\nInstall automation deps:")
        console.print("  [cyan]python -m pip install -e \".[automation]\"[/cyan]")


@mmws_studio_app.command("status")
def mmws_studio_status(
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed path/version info"),
) -> None:
    """Report mmWave Studio process and RSTD remoting status.

    With --verbose, checks if the running process and selected DLL
    come from the same mmwave_studio_* installation.
    Does NOT require an experiment context (.awr-experiment).
    """
    from awr2944_dca.legacy_mmws.executor import (
        _is_mmws_running, _is_rstd_port_open, _find_mmws_exe,
        _find_rtttnet_dll, _find_mmws_dir, _get_mmws_process_path,
        _extract_version_from_path, _RSTD_PORT,
        _HAVE_PYTHONNET, _HAVE_PYWINAUTO,
    )

    table = Table(title="mmWave Studio Status", show_lines=True)
    table.add_column("Check")
    table.add_column("Result")

    exe = _find_mmws_exe()
    running = _is_mmws_running()
    port_open = _is_rstd_port_open()
    dll = _find_rtttnet_dll()
    mmws_dir = _find_mmws_dir()

    table.add_row("mmWaveStudio.exe found", "[green]Yes[/green]" if exe else "[red]No[/red]")
    table.add_row("Process running", "[green]Yes[/green]" if running else "[red]No[/red]")
    table.add_row(f"RSTD port {_RSTD_PORT}", "[green]Open[/green]" if port_open else "[red]Closed[/red]")
    table.add_row("RtttNetClientAPI.dll", "[green]Found[/green]" if dll else "[red]Not found[/red]")
    table.add_row("pythonnet installed", "[green]Yes[/green]" if _HAVE_PYTHONNET else "[yellow]No[/yellow]")
    table.add_row("pywinauto installed", "[green]Yes[/green]" if _HAVE_PYWINAUTO else "[yellow]No[/yellow]")

    console.print(table)

    if verbose:
        console.print()
        # Process path
        process_path = _get_mmws_process_path()
        if process_path:
            console.print(f"Running process path: [green]{process_path}[/green]")
        elif running:
            console.print("[yellow]Process running but path could not be determined.[/yellow]")
            console.print("  mmWave Studio likely runs elevated (Run as administrator).")
            console.print("  From an [bold]elevated[/bold] PowerShell, run:")
            console.print("    [cyan]Get-Process mmWaveStudio | Select-Object Id, Path[/cyan]")
        else:
            console.print("[yellow]mmWave Studio is not running.[/yellow]")

        # DLL path
        if dll:
            console.print(f"RtttNetClientAPI.dll: [green]{dll}[/green]")
        if mmws_dir:
            console.print(f"mmWave Studio dir:   [green]{mmws_dir}[/green]")

        # Version matching
        if process_path and dll:
            proc_ver = _extract_version_from_path(process_path)
            dll_ver = _extract_version_from_path(dll)
            console.print(f"\nProcess version: {proc_ver or 'unknown'}")
            console.print(f"DLL version:     {dll_ver or 'unknown'}")

            if proc_ver and dll_ver:
                if proc_ver == dll_ver:
                    console.print(f"[green]Version match: both from mmwave_studio_{proc_ver}[/green]")
                else:
                    console.print(f"\n[red]VERSION MISMATCH![/red]")
                    console.print(f"  Running process: mmwave_studio_{proc_ver}")
                    console.print(f"  Selected DLL:    mmwave_studio_{dll_ver}")
                    console.print(f"\n[red]RSTD auto-execution may fail when process and DLL are from different versions.[/red]")
                    console.print(f"[yellow]Close the mismatched mmWave Studio and launch the correct one.[/yellow]")
        elif running:
            console.print("\n[yellow]Could not determine process path for version comparison.[/yellow]")
            console.print("Run manually: [cyan]Get-Process mmWaveStudio | Select-Object Id, Path[/cyan]")


# ---------------------------------------------------------------------------
# awr mmws lua-command (manual dofile helper)
# ---------------------------------------------------------------------------


@mmws_app.command("lua-command")
def mmws_lua_command(
    script: Path = typer.Argument(..., help="Path to Lua script"),
    copy: bool = typer.Option(False, "--copy", help="Copy dofile command to clipboard (Windows)"),
) -> None:
    """Print or copy the dofile([[...]]) command for manual use."""
    from awr2944_dca.legacy_mmws.executor import build_dofile_command

    if not script.exists():
        console.print(f"[red]Script not found: {script}[/red]")
        raise typer.Exit(1)

    cmd = build_dofile_command(script)
    console.print(f"\n[cyan]{cmd}[/cyan]")

    if copy:
        try:
            import subprocess
            proc = subprocess.run(
                ["clip.exe"],
                input=cmd.encode("utf-8"),
                capture_output=True,
                timeout=5,
            )
            if proc.returncode == 0:
                console.print("[green]Copied to clipboard.[/green]")
            else:
                console.print("[yellow]clip.exe failed. Copy the command manually.[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Could not copy to clipboard: {e}[/yellow]")


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# awr mmws matlab-bridge *
# ---------------------------------------------------------------------------

@mmws_matlab_bridge_app.command("locate")
def mmws_matlab_bridge_locate(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Locate MATLAB installations and runtimes."""
    from .legacy_mmws.matlab_bridge import locate_matlab
    
    console.print("[cyan]Locating MATLAB...[/cyan]")
    info = locate_matlab()
    
    if info["where_matlab"]:
        console.print("[green]Found via `where matlab`:[/green]")
        for p in info["where_matlab"]:
            console.print(f"  {p}")
    else:
        console.print("[yellow]Not found via `where matlab`.[/yellow]")
        
    if info["full_matlab"]:
        console.print("[green]Found Full MATLAB:[/green]")
        for p in info["full_matlab"]:
            console.print(f"  {p}")
    else:
        console.print("[red]Full MATLAB not found in Program Files.[/red]")
        
    if info["matlab_runtime"]:
        console.print("[yellow]Found MATLAB Runtime:[/yellow]")
        for p in info["matlab_runtime"]:
            console.print(f"  {p}")
        console.print("[yellow]Note: MATLAB Runtime is not enough for `matlab -batch`.[/yellow]")
    else:
        console.print("[dim]No MATLAB Runtime found.[/dim]")

@mmws_matlab_bridge_app.command("ping")
def mmws_matlab_bridge_ping(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test MATLAB-to-Studio connection (Init + Connect)."""
    from .legacy_mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (ping)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dummy.lua"
        p.touch()
        res = _execute_matlab_bridge(p, verbose=verbose, timeout=30.0, bridge_mode="ping")
        
    if res.success:
        console.print("[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ MATLAB bridge ping successful![/green]")
    else:
        console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â MATLAB bridge ping failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)

@mmws_matlab_bridge_app.command("send-inline")
def mmws_matlab_bridge_send_inline(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test MATLAB-to-Studio send-inline command."""
    from .legacy_mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (send-inline)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dummy.lua"
        p.touch()
        res = _execute_matlab_bridge(p, verbose=verbose, timeout=30.0, bridge_mode="send-inline")
        
    if res.success:
        console.print("[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ MATLAB bridge send-inline successful![/green]")
    else:
        console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â MATLAB bridge send-inline failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)

@mmws_matlab_bridge_app.command("smoke")
def mmws_matlab_bridge_smoke(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test MATLAB-to-Studio RunScript via smoke script."""
    from .legacy_mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (smoke)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "smoke.lua"
        p.write_text("WriteToLog(\"SMOKE\\n\")", encoding="utf-8")
        res = _execute_matlab_bridge(p, verbose=verbose, timeout=30.0, bridge_mode="send-command")
        
    if res.success:
        console.print("[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ MATLAB bridge smoke successful![/green]")
    else:
        console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â MATLAB bridge smoke failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)


@mmws_matlab_bridge_app.command("dofile-test")
def mmws_matlab_bridge_dofile_test(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test MATLAB-to-Studio dofile command."""
    from .legacy_mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (dofile-test)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dofile_test.lua"
        res_file = Path(d) / "matlab_dofile_test_result.json"
        p.write_text(f"WriteToLog(\"DOFILE_TEST\\\\n\")\nres_file=io.open([[{str(res_file).replace('\\\\', '/')}ÃƒÆ’Ã‚Â§Ãƒâ€šÃ‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‹Å“]], 'w')\nres_file:write('{{\"success\":true}}')\nres_file:close()", encoding="utf-8")
        # Wait, just write the result file properly
        lua_code = f"""
WriteToLog("DOFILE_TEST\\n")
local f = io.open([[{str(res_file).replace("\\", "/")}ÃƒÆ’Ã‚Â§Ãƒâ€šÃ‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‹Å“]], "w")
f:write('{{"success":true}}')
f:close()
""".replace("ÃƒÆ’Ã‚Â§Ãƒâ€šÃ‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‹Å“", "")
        p.write_text(lua_code, encoding="utf-8")
        if res_file.exists():
            res_file.unlink()
        res = _execute_matlab_bridge(p, verbose=verbose, timeout=30.0, bridge_mode="dofile-test")
        
    if res.success:
        import json
        if res_file.exists():
            try:
                data = json.loads(res_file.read_text())
                if data.get("success"):
                    console.print("[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ MATLAB bridge dofile-test successful![/green]")
                    return
                else:
                    console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â MATLAB bridge dofile-test Lua result failed: {data}[/red]")
            except Exception as e:
                console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â MATLAB bridge dofile-test JSON error: {e}[/red]")
        else:
            console.print("[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â MATLAB bridge dofile-test failed: lua result json not found[/red]")
    else:
        console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â MATLAB bridge dofile-test failed: {res.error}[/red]")
    
    if res.verbose_log:
        for line in res.verbose_log:
            console.print(line)
    raise typer.Exit(1)

# awr mmws lua-launch *
# ---------------------------------------------------------------------------

def _lua_launch_probe_dir(probe_dir_override: Optional[str] = None) -> "Path":
    """Return (and create) the lua-launch probe_logs directory."""
    from pathlib import Path
    if probe_dir_override:
        d = Path(probe_dir_override)
    else:
        d = Path("ti") / "probe_logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


@mmws_lua_launch_app.command("smoke")
def mmws_lua_launch_smoke(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Self-contained smoke test via mmWaveStudio.exe /lua.

    No WriteToLog, no ar1, no Startup.lua dependency.
    Verifies io.open writes a result JSON.  Process exit is NOT required.
    Generated script and result JSON are saved to ti/probe_logs/.
    """
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_smoke
    import uuid
    from pathlib import Path
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_smoke_result.json"
    script_path = probe_dir / "lua_launch_smoke.lua"
    
    # Clean previous result
    if result_path.exists():
        result_path.unlink()
    
    script = build_lua_launch_smoke(run_id, str(result_path.resolve()))
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch smoke (run_id={run_id})...[/cyan]")
    console.print(f"  Script:  {script_path.resolve()}")
    console.print(f"  Result:  {result_path.resolve()}")
    
    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")
    
    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose, timeout=30.0, result_path=result_path.resolve(),
    )
    
    if res.success:
        console.print("[green][OK] lua-launch smoke successful![/green]")
        console.print(f"  Result saved: {result_path.resolve()}")
    else:
        console.print(f"[red][FAIL] lua-launch smoke failed: {res.error}[/red]")
    
    if res.verbose_log:
        for line in res.verbose_log:
            console.print(line)
    
    if not res.success:
        raise typer.Exit(1)


@mmws_lua_launch_app.command("env-probe")
def mmws_lua_launch_env_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Probe the mmWaveStudio /lua environment.

    Reports: _VERSION, type(ar1), type(WriteToLog), type(writeToLog),
    package.path, whether io.open works.

    The Startup.lua warning is expected and harmless for standalone scripts.
    Generated script and result are saved to ti/probe_logs/.
    """
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_env_probe
    import uuid
    import json
    from pathlib import Path
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_env_probe_result.json"
    script_path = probe_dir / "lua_launch_env_probe.lua"
    
    # Clean previous result
    if result_path.exists():
        result_path.unlink()
    
    script = build_lua_launch_env_probe(run_id, str(result_path.resolve()))
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch env-probe (run_id={run_id})...[/cyan]")
    console.print(f"  Script:  {script_path.resolve()}")
    console.print(f"  Result:  {result_path.resolve()}")
    
    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")
    
    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose, timeout=30.0, result_path=result_path.resolve(),
    )
    
    if not res.success:
        console.print(f"[red][FAIL] env-probe failed: {res.error}[/red]")
        # Dump raw result if it exists but couldn't be parsed
        if result_path.exists():
            raw = result_path.read_text(encoding="utf-8")
            raw_path = probe_dir / "env_probe_result_raw.txt"
            raw_path.write_text(raw, encoding="utf-8")
            console.print(f"[yellow]Raw result saved: {raw_path.resolve()}[/yellow]")
            console.print(f"[dim]Raw contents:\n{raw}[/dim]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)
    
    # Parse and display the probe results
    data: dict = {}
    if result_path.exists():
        raw = result_path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            console.print(f"[red]Result JSON parse error: {e}[/red]")
            raw_path = probe_dir / "env_probe_result_raw.txt"
            raw_path.write_text(raw, encoding="utf-8")
            console.print(f"[yellow]Raw result saved: {raw_path.resolve()}[/yellow]")
            console.print(f"[dim]Raw contents:\n{raw}[/dim]")
            raise typer.Exit(1)
    
    console.print("[green][OK] env-probe completed[/green]")
    console.print(f"  _VERSION:         {data.get('_VERSION', '?')}")
    console.print(f"  type(ar1):        {data.get('type_ar1', '?')}")
    ar1_connect = data.get("ar1_connect_exists", False)
    console.print(f"  ar1.Connect:      {'exists' if ar1_connect else '[red]missing[/red]'}")
    console.print(f"  type(WriteToLog): {data.get('type_WriteToLog', '?')}")
    console.print(f"  type(writeToLog): {data.get('type_writeToLog', '?')}")
    console.print(f"  io.open works:    {data.get('io_open_works', '?')}")
    console.print(f"  package.path:     {data.get('package_path', '?')}")
    console.print(f"  Result saved:     {result_path.resolve()}")
    
    if data.get("type_ar1") == "nil":
        console.print(
            "\n[yellow]ar1 is nil ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â /lua runs before Startup.lua initializes RadarAPI.\n"
            "lua-launch is useful only for standalone scripts unless we learn\n"
            "how to initialize RadarAPI/Startup safely.[/yellow]"
        )
    
    if not ar1_connect:
        console.print(
            "[yellow]Do NOT run hardware connection under lua-launch until\n"
            "env-probe proves type(ar1)==\"table\" and ar1.Connect exists.[/yellow]"
        )


# awr mmws csharp-bridge *
# ---------------------------------------------------------------------------


@mmws_bridge_app.command("build")
def mmws_bridge_build(
    verbose: bool = typer.Option(False, "--verbose", help="Print detailed build info"),
) -> None:
    """Build the C# RSTD bridge (MmwsRstdBridge.exe).

    Compiles the C# source using .NET Framework csc.exe (x86).
    Requires RtttNetClientAPI.dll from mmWave Studio installation.
    """
    from awr2944_dca.legacy_mmws.executor import build_csharp_bridge

    console.print("[cyan]Building C# RSTD bridge...[/cyan]")
    success, message = build_csharp_bridge(verbose=verbose)

    for line in message.splitlines():
        if "SUCCESS" in line:
            console.print(f"[green]{line}[/green]")
        elif "FAILED" in line or "WARNING" in line or "ERROR" in line:
            console.print(f"[red]{line}[/red]")
        else:
            console.print(f"  {line}")

    if not success:
        raise typer.Exit(1)



@mmws_bridge_app.command("send-inline")
def mmws_csharp_bridge_send_inline(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose bridge output"),
    apartment: str = typer.Option("mta", "--apartment", help="ApartmentState (mta or sta)"),
) -> None:
    """Test C# bridge send-inline command."""
    from .legacy_mmws.executor import _execute_via_csharp_bridge
    import tempfile
    from pathlib import Path
    
    console.print(f"[cyan]Testing C# bridge (send-inline, apartment={apartment})...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dummy.lua"
        p.touch()
        res = _execute_via_csharp_bridge(
            script_path=p,
            verbose=verbose,
            timeout=10.0,
            bridge_mode="send-inline",
            apartment=apartment,
        )
        
    if res.success:
        console.print("[green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ C# bridge send-inline successful![/green]")
    else:
        console.print(f"[red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â C# bridge send-inline failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)

@mmws_bridge_app.command("ping")
def mmws_bridge_ping(
    verbose: bool = typer.Option(False, "--verbose", help="Print verbose bridge output"),
    timeout: float = typer.Option(10.0, "--timeout", help="Seconds to wait"),
) -> None:
    """Ping mmWave Studio via the C# RSTD bridge.

    Tests: Init + Connect + IsConnected + GetLastError.
    Does NOT send any Lua commands.
    """
    import json
    import subprocess
    import tempfile
    from awr2944_dca.legacy_mmws.executor import _find_csharp_bridge, _find_rtttnet_dll, _RSTD_HOST, _RSTD_PORT

    bridge = _find_csharp_bridge()
    if bridge is None:
        console.print("[red]MmwsRstdBridge.exe not found.[/red]")
        console.print("Run: [cyan]awr mmws csharp-bridge build[/cyan]")
        raise typer.Exit(1)

    console.print(f"[cyan]Bridge:[/cyan] {bridge}")

    # Find DLL directory for AssemblyResolve
    dll_path = _find_rtttnet_dll()
    dll_dir = str(Path(dll_path).parent) if dll_path else None

    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = Path(tmpdir) / "ping_result.json"
        cmd = [
            str(bridge), "--mode", "ping",
            "--host", _RSTD_HOST, "--port", str(_RSTD_PORT),
            "--result", str(result_path),
        ]
        if dll_dir:
            cmd.extend(["--dll-dir", dll_dir])
        if verbose:
            cmd.append("--verbose")

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                cwd=dll_dir if dll_dir else None,
            )
            if verbose and proc.stderr:
                for line in proc.stderr.strip().splitlines():
                    console.print(f"[dim]  {line}[/dim]")

            if result_path.exists():
                data = json.loads(result_path.read_text())
                console.print(f"  Init return:    {data.get('init_return')}")
                console.print(f"  Connect return: {data.get('connect_return')}")
                console.print(f"  IsConnected:    {data.get('is_connected')}")
                console.print(f"  GetLastError:   {data.get('last_error')}")
                console.print(f"  Elapsed:        {data.get('elapsed_ms')}ms")
                exc = data.get("exception")
                if exc is not None:
                    console.print(f"  [red]Exception: {exc}[/red]")
                elif data.get("is_connected"):
                    console.print("[green]PING SUCCESS[/green]")
                else:
                    console.print("[yellow]Connected but IsConnected=false[/yellow]")
            else:
                console.print("[red]Bridge did not write result file[/red]")
                if proc.stdout:
                    console.print(proc.stdout)
                raise typer.Exit(1)

        except subprocess.TimeoutExpired:
            console.print(f"[red]Bridge timed out after {timeout}s[/red]")
            raise typer.Exit(1)


@mmws_bridge_app.command("introspect")
def mmws_bridge_introspect(
    verbose: bool = typer.Option(False, "--verbose", help="Print verbose output"),
    timeout: float = typer.Option(10.0, "--timeout", help="Seconds to wait"),
) -> None:
    """List public methods on RtttNetClient via the C# bridge."""
    import json
    import subprocess
    import tempfile
    from awr2944_dca.legacy_mmws.executor import _find_csharp_bridge, _find_rtttnet_dll

    bridge = _find_csharp_bridge()
    if bridge is None:
        console.print("[red]MmwsRstdBridge.exe not found. Run: awr mmws csharp-bridge build[/red]")
        raise typer.Exit(1)

    # Find DLL directory for AssemblyResolve
    dll_path = _find_rtttnet_dll()
    dll_dir = str(Path(dll_path).parent) if dll_path else None

    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = Path(tmpdir) / "introspect_result.json"
        cmd = [
            str(bridge), "--mode", "introspect",
            "--result", str(result_path),
        ]
        if dll_dir:
            cmd.extend(["--dll-dir", dll_dir])
        if verbose:
            cmd.append("--verbose")

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                cwd=dll_dir if dll_dir else None,
            )
            if verbose and proc.stderr:
                for line in proc.stderr.strip().splitlines():
                    console.print(f"[dim]  {line}[/dim]")

            if result_path.exists():
                data = json.loads(result_path.read_text())
                methods = data.get("methods")
                if methods:
                    methods_list = json.loads(methods) if isinstance(methods, str) else methods
                    console.print(f"[green]RtttNetClient public static methods ({len(methods_list)}):[/green]")
                    for m in methods_list:
                        console.print(f"  {m.get('signature', m)}")
                exc = data.get("exception")
                if exc:
                    console.print(f"[red]Exception: {exc}[/red]")
            else:
                console.print("[red]No result file[/red]")
                raise typer.Exit(1)

        except subprocess.TimeoutExpired:
            console.print(f"[red]Introspection timed out after {timeout}s[/red]")
            raise typer.Exit(1)



@mmws_lua_launch_app.command("startup-probe")
def mmws_lua_launch_startup_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Explicitly invoke Startup.lua and probe the environment to see if it loads ar1."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_startup_probe
    import uuid
    import json
    from pathlib import Path
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_startup_probe_result.json"
    script_path = probe_dir / "lua_launch_startup_probe.lua"
    
    # Clean previous result
    if result_path.exists():
        result_path.unlink()
    
    # Path to standard mmWave Studio Startup.lua
    startup_lua_path = "C:/ti/mmwave_studio_03_01_04_04/mmWaveStudio/Scripts/Startup.lua"
    
    script = build_lua_launch_startup_probe(run_id, str(result_path.resolve()), startup_lua_path)
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch startup-probe (run_id={run_id})...[/cyan]")
    console.print(f"  Script:  {script_path.resolve()}")
    console.print(f"  Result:  {result_path.resolve()}")
    
    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")
            
    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose, timeout=120.0, result_path=result_path.resolve(),
    )
    
    if not res.success:
        console.print(f"[red][FAIL] startup-probe failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)
        
    data: dict = {}
    if result_path.exists():
        raw = result_path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            console.print(f"[red]Result JSON parse error: {e}[/red]")
            console.print(f"[dim]Raw contents:\n{raw}[/dim]")
            raise typer.Exit(1)
            
    console.print("[green][OK] startup-probe completed[/green]")
    console.print("[cyan]Before Startup.lua:[/cyan]")
    console.print(f"  type(ar1):        {data.get('before_type_ar1', '?')}")
    console.print(f"  type(WriteToLog): {data.get('before_type_WriteToLog', '?')}")
    console.print(f"  type(RSTD):       {data.get('before_type_RSTD', '?')}")
    console.print(f"  startup_ok:       {data.get('startup_ok', '?')}")
    if not data.get('startup_ok'):
        console.print(f"[red]  startup_err:      {data.get('startup_err', '?')}[/red]")
    console.print("[cyan]After Startup.lua:[/cyan]")
    console.print(f"  type(ar1):        {data.get('after_type_ar1', '?')}")
    console.print(f"  ar1.Connect:      {'exists' if data.get('after_ar1_connect_exists') else '[red]missing[/red]'}")
    console.print(f"  type(WriteToLog): {data.get('after_type_WriteToLog', '?')}")
    console.print(f"  type(RSTD):       {data.get('after_type_RSTD', '?')}")


            
    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose, timeout=30.0, result_path=result_path.resolve(),
    )
    
    if not res.success:
        console.print(f"[red][FAIL] wait-env-probe failed: {res.error}[/red]")
        raise typer.Exit(1)
        
    data: dict = {}
    if result_path.exists():
        raw = result_path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            console.print(f"[red]Result JSON parse error: {e}[/red]")
            raise typer.Exit(1)
            
    console.print("[green][OK] wait-env-probe completed[/green]")
    console.print(f"  timeout hit:      {data.get('timeout', '?')}")
    console.print(f"  final type(ar1):  {data.get('final_ar1_type', '?')}")
    
    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            try:
                row = json.loads(line)
                console.print(f"  [dim]{row['elapsed']:.2f}s | ar1: {row['type_ar1']} | connect: {row['ar1_connect_exists']} | log: {row['type_WriteToLog']}[/dim]")
            except:
                pass


mmws_startup_app = typer.Typer(
    help="Inspect mmWave Studio initialization scripts", no_args_is_help=True
)
mmws_app.add_typer(mmws_startup_app, name="startup")

@mmws_startup_app.command("inspect")
def mmws_startup_inspect() -> None:
    """Inspect Startup.lua directly."""
    from pathlib import Path
    
    startup_path = Path("C:/ti/mmwave_studio_03_01_04_04/mmWaveStudio/Scripts/Startup.lua")
    if not startup_path.exists():
        console.print("[red]Startup.lua not found![/red]")
        raise typer.Exit(1)
        
    content = startup_path.read_text()
    console.print(f"[cyan]Inspecting {startup_path.resolve()}[/cyan]")
    
    ar1_creations = [line.strip() for line in content.splitlines() if "ar1" in line.lower() and "=" in line]
    console.print(f"\n[yellow]ar1 assignments:[/yellow]")
    if not ar1_creations:
        console.print("  (None found)")
    else:
        for c in ar1_creations: console.print(f"  {c}")
        
    log_creations = [line.strip() for line in content.splitlines() if "WriteToLog" in line and "=" in line]
    console.print(f"\n[yellow]WriteToLog assignments:[/yellow]")
    if not log_creations:
        console.print("  (None found)")
    else:
        for c in log_creations: console.print(f"  {c}")
        
    netstarts = [line.strip() for line in content.splitlines() if "NetStart" in line]
    console.print(f"\n[yellow]RSTD.NetStart calls:[/yellow]")
    for n in netstarts: console.print(f"  {n}")
    
    registerdlls = [line.strip() for line in content.splitlines() if "RegisterDll" in line]
    console.print(f"\n[yellow]DLL registrations:[/yellow]")
    for r in registerdlls: console.print(f"  {r}")


@mmws_lua_launch_app.command("rstd-env-probe")
def mmws_lua_launch_rstd_env_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Probe the initial /lua environment for RSTD availability without running Startup.lua."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_rstd_env_probe
    import uuid, json
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_rstd_env_probe_result.json"
    script_path = probe_dir / "lua_launch_rstd_env_probe.lua"
    
    if result_path.exists(): result_path.unlink()
        
    script = build_lua_launch_rstd_env_probe(run_id, str(result_path.resolve()))
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch rstd-env-probe (run_id={run_id})...[/cyan]")
    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=30.0, result_path=result_path.resolve())
    
    if not res.success:
        console.print(f"[red][FAIL] rstd-env-probe failed: {res.error}[/red]")
        raise typer.Exit(1)
        
    data = json.loads(result_path.read_text(encoding="utf-8"))
    console.print("[green][OK] rstd-env-probe completed[/green]")
    for k, v in data.items():
        if k not in ["run_id", "executed", "error"]:
            console.print(f"  {k}: {v}")

@mmws_lua_launch_app.command("registerdll-probe")
def mmws_lua_launch_registerdll_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Probe environment after calling RSTD.RegisterDllEx."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_registerdll_probe
    import uuid, json
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_registerdll_probe_result.json"
    script_path = probe_dir / "lua_launch_registerdll_probe.lua"
    jsonl_path = probe_dir / "lua_launch_registerdll_probe_result.jsonl"
    
    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()
        
    script = build_lua_launch_registerdll_probe(run_id, str(result_path.resolve()))
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch registerdll-probe (run_id={run_id})...[/cyan]")
    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=30.0, result_path=result_path.resolve())
    
    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            console.print(f"  [dim]{line}[/dim]")
            
    if not res.success:
        console.print(f"[red][FAIL] registerdll-probe failed: {res.error}[/red]")
        raise typer.Exit(1)
        
    data = json.loads(result_path.read_text(encoding="utf-8"))
    console.print("[green][OK] registerdll-probe completed[/green]")
    for k, v in data.items():
        if k not in ["run_id", "executed", "error"]:
            console.print(f"  {k}: {v}")


@mmws_lua_launch_app.command("startup-lite-probe")
def mmws_lua_launch_startup_lite_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Run non-blocking subset of Startup.lua."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_startup_lite_probe
    import uuid, json
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_startup_lite_probe_result.json"
    script_path = probe_dir / "lua_launch_startup_lite_probe.lua"
    
    if result_path.exists(): result_path.unlink()
        
    script = build_lua_launch_startup_lite_probe(run_id, str(result_path.resolve()))
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch startup-lite-probe (run_id={run_id})...[/cyan]")
    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=60.0, result_path=result_path.resolve())
            
    if not res.success:
        console.print(f"[red][FAIL] startup-lite-probe failed: {res.error}[/red]")
        raise typer.Exit(1)
        
    data = json.loads(result_path.read_text(encoding="utf-8"))
    console.print("[green][OK] startup-lite-probe completed[/green]")
    for k, v in data.items():
        if k not in ["run_id", "executed", "error"]:
            console.print(f"  {k}: {v}")


# ---------------------------------------------------------------------------
# lua-launch: cleanup
# ---------------------------------------------------------------------------

@mmws_lua_launch_app.command("cleanup")
def mmws_lua_launch_cleanup(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Kill existing mmWaveStudio.exe instances and wait until gone."""
    import subprocess
    import time

    def _is_running() -> bool:
        try:
            r = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq mmWaveStudio.exe", "/NH"],
                capture_output=True, text=True, timeout=5,
            )
            return "mmWaveStudio.exe" in r.stdout
        except Exception:
            return False

    if not _is_running():
        console.print("[green][OK] No mmWaveStudio.exe instances running.[/green]")
        return

    console.print("[yellow]Found running mmWaveStudio.exe -- attempting to kill...[/yellow]")

    # Try taskkill first (may need admin on some installs)
    r = subprocess.run(
        ["taskkill", "/F", "/IM", "mmWaveStudio.exe"],
        capture_output=True, text=True, timeout=10,
    )
    if verbose:
        console.print(f"  [dim]taskkill stdout: {r.stdout.strip()}[/dim]")
        console.print(f"  [dim]taskkill stderr: {r.stderr.strip()}[/dim]")

    # Wait up to 10 seconds for the process to disappear
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if not _is_running():
            console.print("[green][OK] mmWaveStudio.exe terminated.[/green]")
            return
        time.sleep(0.5)

    if _is_running():
        console.print("[red][FAIL] Could not kill mmWaveStudio.exe. Try running as admin or close manually.[/red]")
        raise typer.Exit(1)
    else:
        console.print("[green][OK] mmWaveStudio.exe terminated.[/green]")


# ---------------------------------------------------------------------------
# lua-launch: ar1-readonly-probe
# ---------------------------------------------------------------------------

@mmws_lua_launch_app.command("ar1-readonly-probe")
def mmws_lua_launch_ar1_readonly_probe(
    mode: str = typer.Option("method-only", "--mode", help="Probe mode: method-only or isconnected-call"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
    force: bool = typer.Option(False, "--force", help="Kill existing mmWaveStudio.exe before running"),
) -> None:
    """Run startup-lite + read-only ar1 checks."""
    from .legacy_mmws.executor import _execute_lua_launch, _is_mmws_running
    from .legacy_mmws.lua_builder import build_lua_launch_ar1_readonly_probe
    import uuid
    import json

    if mode not in ("method-only", "isconnected-call"):
        console.print(f"[red][FAIL] Invalid mode: {mode}[/red]")
        raise typer.Exit(1)

    if _is_mmws_running():
        if force:
            console.print("[yellow]--force: killing existing mmWaveStudio.exe...[/yellow]")
            import subprocess, time
            subprocess.run(["taskkill", "/F", "/IM", "mmWaveStudio.exe"],
                           capture_output=True, text=True, timeout=10)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if not _is_mmws_running():
                    break
                time.sleep(0.5)
            if _is_mmws_running():
                console.print("[red][FAIL] Could not kill mmWaveStudio.exe.[/red]")
                raise typer.Exit(1)
            console.print("[green]Existing instance terminated.[/green]")
        else:
            console.print("[red][FAIL] mmWaveStudio.exe is already running.[/red]")
            console.print("  Use --force to kill it, or run 'awr mmws lua-launch cleanup' first.")
            raise typer.Exit(1)

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_ar1_readonly_probe_result.json"
    jsonl_path = probe_dir / "lua_launch_ar1_readonly_probe_progress.jsonl"
    script_path = probe_dir / "lua_launch_ar1_readonly_probe.lua"

    if result_path.exists():
        result_path.unlink()
    if jsonl_path.exists():
        jsonl_path.unlink()

    script = build_lua_launch_ar1_readonly_probe(run_id, str(result_path.resolve()), str(jsonl_path.resolve()), mode)
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]lua-launch ar1-readonly-probe (mode={mode}, run_id={run_id})...[/cyan]")

    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")

    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose, timeout=60.0, result_path=result_path.resolve(),
    )

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] ar1-readonly-probe failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")

    if status == "AR1_READONLY_OK":
        console.print(f"[green][OK] ar1-readonly-probe passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] ar1-readonly-probe status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if status != "AR1_READONLY_OK":
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# lua-launch: connect-only
# ---------------------------------------------------------------------------

def _check_ar1_readonly_gate() -> bool:
    import json
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_ar1_readonly_probe_result.json"
    if not result_path.exists():
        return False
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
        return data.get("status") == "AR1_READONLY_OK" and data.get("executed") is True
    except Exception:
        return False


@mmws_lua_launch_app.command("connect-only")
def mmws_lua_launch_connect_only(
    com: str = typer.Option("COM6", "--com", help="COM port (e.g. COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
    force: bool = typer.Option(False, "--force", help="Kill existing mmWaveStudio.exe before running"),
    skip_gate: bool = typer.Option(False, "--skip-gate", help="Skip ar1-readonly-probe safety gate"),
) -> None:
    """Connect to radar via ar1.Connect only (no SOPControl, no firmware, no DCA)."""
    from .legacy_mmws.executor import _execute_lua_launch, _is_mmws_running
    from .legacy_mmws.lua_builder import build_lua_launch_connect_only
    import uuid
    import json

    if not skip_gate and not _check_ar1_readonly_gate():
        console.print("[red][FAIL] Safety gate: ar1-readonly-probe has not passed.[/red]")
        console.print("  Run 'awr mmws lua-launch ar1-readonly-probe --verbose' first.")
        console.print("  Or use --skip-gate to bypass (expert only).")
        raise typer.Exit(1)

    if _is_mmws_running():
        if force:
            console.print("[yellow]--force: killing existing mmWaveStudio.exe...[/yellow]")
            import subprocess, time
            subprocess.run(["taskkill", "/F", "/IM", "mmWaveStudio.exe"],
                           capture_output=True, text=True, timeout=10)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if not _is_mmws_running():
                    break
                time.sleep(0.5)
            if _is_mmws_running():
                console.print("[red][FAIL] Could not kill mmWaveStudio.exe.[/red]")
                raise typer.Exit(1)
            console.print("[green]Existing instance terminated.[/green]")
        else:
            console.print("[red][FAIL] mmWaveStudio.exe is already running.[/red]")
            console.print("  Use --force to kill it, or run 'awr mmws lua-launch cleanup' first.")
            raise typer.Exit(1)

    com_upper = com.upper()
    if not com_upper.startswith("COM"):
        console.print(f"[red][FAIL] Invalid COM port: {com}. Expected format: COM6[/red]")
        raise typer.Exit(1)
    try:
        com_num = int(com_upper[3:])
    except ValueError:
        console.print(f"[red][FAIL] Invalid COM port number: {com}[/red]")
        raise typer.Exit(1)

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_connect_only_result.json"
    jsonl_path = probe_dir / "lua_launch_connect_only_progress.jsonl"
    script_path = probe_dir / "lua_launch_connect_only.lua"

    if result_path.exists():
        result_path.unlink()
    if jsonl_path.exists():
        jsonl_path.unlink()

    script = build_lua_launch_connect_only(
        run_id, str(result_path.resolve()), str(jsonl_path.resolve()),
        com_num=com_num, baud=baud, timeout_ms=1000,
    )
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]lua-launch connect-only (run_id={run_id})...[/cyan]")
    console.print(f"  COM: {com_upper}  Baud: {baud}")

    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")

    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose, timeout=60.0, result_path=result_path.resolve(),
    )

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] connect-only failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")

    if status == "CONNECT_SUCCESS":
        console.print(f"[green][OK] connect-only passed (status={status})[/green]")
    elif status == "CONNECT_RETURNED_ERROR":
        console.print(f"[yellow][WARN] ar1.Connect returned non-zero (status={status})[/yellow]")
    else:
        console.print(f"[red][FAIL] connect-only status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if status not in ("CONNECT_SUCCESS",):
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# lua-launch: dll-diagnostics
# ---------------------------------------------------------------------------

@mmws_lua_launch_app.command("dll-diagnostics")
def mmws_lua_launch_dll_diagnostics(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Analyze mmWave Studio DLL paths and export hashes."""
    from pathlib import Path
    import os
    import hashlib
    from datetime import datetime
    from rich.table import Table

    def file_info(path: Path) -> dict:
        try:
            stat = path.stat()
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            return {"size": size, "mtime": mtime, "sha256": sha256, "ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def check_export(path: Path, func_name: str) -> bool:
        try:
            # Simple binary scan for the export name. This works for most uncompressed PE files.
            content = path.read_bytes()
            return func_name.encode("ascii") in content
        except Exception:
            return False

    console.print("[cyan]Scanning for mmWave Studio DLLs in C:\\ti...[/cyan]")
    base_dir = Path("C:/ti")

    radar_dlls = list(base_dir.rglob("RadarLinkDLL.dll")) if base_dir.exists() else []
    ar1_dlls = list(base_dir.rglob("AR1xController.dll")) if base_dir.exists() else []

    table = Table(title="RadarLinkDLL.dll")
    table.add_column("Path", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified")
    table.add_column("SHA256 (short)")
    table.add_column("Export: IsConnected?")

    for dll in radar_dlls:
        info = file_info(dll)
        if info["ok"]:
            has_export = check_export(dll, "RadarLinkImpl_IsConnected")
            table.add_row(str(dll), f"{info['size']:,}", info["mtime"], info["sha256"][:12], "[green]YES[/green]" if has_export else "[red]NO[/red]")
        else:
            table.add_row(str(dll), "ERROR", "-", "-", "-")

    console.print(table)

    table2 = Table(title="AR1xController.dll")
    table2.add_column("Path", style="cyan")
    table2.add_column("Size", justify="right")
    table2.add_column("Modified")
    table2.add_column("SHA256 (short)")

    for dll in ar1_dlls:
        info = file_info(dll)
        if info["ok"]:
            table2.add_row(str(dll), f"{info['size']:,}", info["mtime"], info["sha256"][:12])
        else:
            table2.add_row(str(dll), "ERROR", "-", "-")

    console.print(table2)

    console.print("\n[yellow]Pre-launch PATH injections for _execute_lua_launch:[/yellow]")
    console.print("  C:\\ti\\mmwave_studio_03_01_04_04\\mmWaveStudio\\Clients\\AR1xController")
    console.print("  C:\\ti\\mmwave_studio_03_01_04_04\\mmWaveStudio\\RunTime")


@mmws_lua_launch_app.command("ar1-methods")
def mmws_lua_launch_ar1_methods(
    filter: str = typer.Option("", "--filter", help="Filter string for methods (e.g. Connect)"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """List methods available in the ar1 table."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_ar1_methods
    import uuid, json
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_ar1_methods_result.json"
    script_path = probe_dir / "lua_launch_ar1_methods.lua"
    
    script = build_lua_launch_ar1_methods(run_id, str(result_path.resolve()), filter)
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch ar1-methods...[/cyan]")
    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=60.0, result_path=result_path.resolve())
    
    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)
        
    data = json.loads(result_path.read_text(encoding="utf-8"))
    if not data.get("executed"):
        console.print(f"[red][FAIL] Script failed: {data.get('error')}[/red]")
        raise typer.Exit(1)
        
    console.print(f"[green]Methods matching '{filter}':[/green]")
    for m in data.get("methods", []):
        console.print(f"  {m}")

@mmws_lua_launch_app.command("startup-lite-v2-probe")
def mmws_lua_launch_startup_lite_v2_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Run startup-lite-v2 (includes RTTT alias + NetStart). Use radarapi-init-probe --mode full instead."""
    console.print("[yellow]Redirecting to radarapi-init-probe --mode full (startup-lite-v2 is now radarapi-init-probe).[/yellow]")
    console.print("Run: awr mmws lua-launch radarapi-init-probe --mode full --verbose")

@mmws_lua_launch_app.command("radarapi-init-probe")
def mmws_lua_launch_radarapi_init_probe(
    mode: str = typer.Option("full", "--mode", help="Mode: no-showgui, rttt-no-showgui, showgui-only, showgui-plus-getversion, showgui-plus-loadsettings, full"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Run startup-lite and the normal GUI initialization sequence."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_radarapi_init_probe
    import uuid, json

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_radarapi_init_probe_result.json"
    jsonl_path = probe_dir / "lua_launch_radarapi_init_probe_progress.jsonl"
    script_path = probe_dir / "lua_launch_radarapi_init_probe.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    script = build_lua_launch_radarapi_init_probe(run_id, str(result_path.resolve()), str(jsonl_path.resolve()), mode)
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch radarapi-init-probe (mode={mode}, run_id={run_id})...[/cyan]")
    
    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")
            
    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=80.0, result_path=result_path.resolve())
    
    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")
            
    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)
        
    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")
    
    if status == "INIT_PROBE_SUCCESS":
        console.print(f"[green][OK] Init passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] Init status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if status != "INIT_PROBE_SUCCESS":
        raise typer.Exit(1)


@mmws_lua_launch_app.command("radarapi-connect-probe")
def mmws_lua_launch_radarapi_connect_probe(
    mode: str = typer.Option("full", "--mode", help="Mode: no-showgui, rttt-no-showgui, showgui-only, showgui-plus-getversion, showgui-plus-loadsettings, full"),
    com: str = typer.Option("COM6", "--com", help="COM port (e.g. COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Run radarapi init sequence and then connect."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_radarapi_connect_probe
    import uuid, json
    
    com_upper = com.upper()
    try:
        com_num = int(com_upper[3:])
    except ValueError:
        console.print(f"[red][FAIL] Invalid COM port number: {com}[/red]")
        raise typer.Exit(1)
        
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_radarapi_connect_probe_result.json"
    jsonl_path = probe_dir / "lua_launch_radarapi_connect_probe_progress.jsonl"
    script_path = probe_dir / "lua_launch_radarapi_connect_probe.lua"
    
    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()
    
    script = build_lua_launch_radarapi_connect_probe(run_id, str(result_path.resolve()), str(jsonl_path.resolve()), mode, com_num, baud)
    script_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]lua-launch radarapi-connect-probe (mode={mode}, run_id={run_id})...[/cyan]")
    console.print(f"  COM: {com_upper}  Baud: {baud}")
    
    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")
            
    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=80.0, result_path=result_path.resolve())
    
    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")
            
    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)
        
    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")
    
    if status == "CONNECT_SUCCESS":
        console.print(f"[green][OK] Connect passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] Connect status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if status != "CONNECT_SUCCESS":
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# lua-launch: startup-lite-v3-probe
# ---------------------------------------------------------------------------

@mmws_lua_launch_app.command("startup-lite-v3-probe")
def mmws_lua_launch_startup_lite_v3_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Run startup-lite-v3 (exact Startup.lua reproduction with RTTT, AR1_GUI, GuiVersion)."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_startup_lite_v3_probe
    import uuid, json

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_startup_lite_v3_probe_result.json"
    jsonl_path = probe_dir / "lua_launch_startup_lite_v3_probe_progress.jsonl"
    script_path = probe_dir / "lua_launch_startup_lite_v3_probe.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    script = build_lua_launch_startup_lite_v3_probe(run_id, str(result_path.resolve()), str(jsonl_path.resolve()))
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]lua-launch startup-lite-v3-probe (run_id={run_id})...[/cyan]")

    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")

    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=60.0, result_path=result_path.resolve())

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")

    if status == "STARTUP_LITE_V3_OK":
        console.print(f"[green][OK] startup-lite-v3 passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] startup-lite-v3 status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if status != "STARTUP_LITE_V3_OK":
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# lua-launch: path-env-probe
# ---------------------------------------------------------------------------

@mmws_lua_launch_app.command("path-env-probe")
def mmws_lua_launch_path_env_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Dump RSTD paths, package.path, and type info before/after startup-lite-v3."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_path_env_probe
    import uuid, json

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_path_env_probe_result.json"
    jsonl_path = probe_dir / "lua_launch_path_env_probe_progress.jsonl"
    script_path = probe_dir / "lua_launch_path_env_probe.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    script = build_lua_launch_path_env_probe(run_id, str(result_path.resolve()), str(jsonl_path.resolve()))
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]lua-launch path-env-probe (run_id={run_id})...[/cyan]")

    res = _execute_lua_launch(script_path.resolve(), verbose=verbose, timeout=60.0, result_path=result_path.resolve())

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    for k, v in data.items():
        if k not in ["run_id"]:
            console.print(f"  {k}: {v}")


# ---------------------------------------------------------------------------
# lua-launch: radarapi-v3-connect-probe
# ---------------------------------------------------------------------------

@mmws_lua_launch_app.command("radarapi-v3-connect-probe")
def mmws_lua_launch_radarapi_v3_connect_probe(
    mode: str = typer.Option("v3-no-showgui", "--mode", help="Mode: v3-no-showgui or v3-showgui"),
    com: str = typer.Option("COM6", "--com", help="COM port (e.g. COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Startup-lite-v3 + optional ShowGui + ar1.Connect."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_radarapi_v3_connect_probe
    import uuid, json

    com_upper = com.upper()
    try:
        com_num = int(com_upper[3:])
    except ValueError:
        console.print(f"[red][FAIL] Invalid COM port number: {com}[/red]")
        raise typer.Exit(1)

    show_gui = (mode == "v3-showgui")

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "lua_launch_radarapi_v3_connect_probe_result.json"
    jsonl_path = probe_dir / "lua_launch_radarapi_v3_connect_probe_progress.jsonl"
    script_path = probe_dir / "lua_launch_radarapi_v3_connect_probe.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    script = build_lua_launch_radarapi_v3_connect_probe(
        run_id, str(result_path.resolve()), str(jsonl_path.resolve()),
        com_num=com_num, baud=baud, show_gui=show_gui,
    )
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]lua-launch radarapi-v3-connect-probe (mode={mode}, run_id={run_id})...[/cyan]")
    console.print(f"  COM: {com_upper}  Baud: {baud}  ShowGui: {show_gui}")

    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")

    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose,
        timeout=90.0 if show_gui else 60.0,
        result_path=result_path.resolve(),
    )

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")

    if status == "CONNECT_SUCCESS":
        console.print(f"[green][OK] Connect passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] Connect status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if status != "CONNECT_SUCCESS":
        raise typer.Exit(1)

# ---------------------------------------------------------------------------
# connection commands (official backend)
# ---------------------------------------------------------------------------

_RETURN3_DIAGNOSTICS = """
[yellow]ConnectTarget returned 3.[/yellow]
This may indicate the radar/FTDI/RS232 target is in the wrong state or needs
a physical NRST/power-cycle. Do not proceed to firmware.

[bold]Recovery steps:[/bold]
  1. Verify you are using the default sequence (gui-set1-fullreset-connect).
  2. If using default and still failing: Manual GUI also returned 3 after Set(1); power-cycle AWR using power-before-USB order.
  3. Close/kill mmWave Studio.
  4. Power-cycle or press NRST/SW1 on the AWR2944 board.
  5. Confirm J10 FTDI USB is connected and COM port is correct.
  6. Re-run connect-gui.
"""


@mmws_conn_app.command("connect-gui")
def mmws_connection_connect_gui(
    com: str = typer.Option("COM6", "--com", help="COM port (e.g. COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    sequence: str = typer.Option(
        "gui-set1-fullreset-connect", "--sequence",
        help="Sequence: showgui-connect, showgui-sleep-connect, "
             "showgui-sop-sleep-connect, showgui-select-sop-connect, "
             "showgui-sop-reset-longwait-connect, select-set-connect, gui-set1-fullreset-connect, gui-set1-fullreset-aw2944-connect",
    ),
    force: bool = typer.Option(False, "--force", help="Kill existing mmWaveStudio instances first"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """[DIAGNOSTIC ONLY] Lua ar1.Connect connection backend.

    WARNING: Lua ar1.Connect is unreliable for AWR2944 RS232 connection.
    It can return 0 with invalid device identity or return 3 after valid
    GUI Set. Use 'awr mmws gui-connect click-flow' instead.
    """
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_connection_sequenced, CONNECT_SEQUENCES
    import uuid, json

    console.print(
        "[yellow][DIAGNOSTIC ONLY] Lua ar1.Connect is unreliable for AWR2944 "
        "RS232 connection. It can return 0 with invalid device identity or "
        "return 3 after valid GUI Set. Use 'awr mmws gui-connect click-flow' "
        "instead.[/yellow]"
    )

    com_upper = com.upper()
    try:
        com_num = int(com_upper[3:])
    except ValueError:
        console.print(f"[red][FAIL] Invalid COM port number: {com}[/red]")
        raise typer.Exit(1)

    if sequence not in CONNECT_SEQUENCES:
        console.print(f"[red][FAIL] Unknown sequence: {sequence}[/red]")
        console.print(f"  Valid sequences: {', '.join(CONNECT_SEQUENCES)}")
        raise typer.Exit(1)

    if force:
        console.print("[yellow]Killing existing mmWave Studio instances...[/yellow]")
        mmws_lua_launch_cleanup(verbose=verbose)

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "connection_connect_gui_result.json"
    jsonl_path = probe_dir / "connection_connect_gui_progress.jsonl"
    script_path = probe_dir / "connection_connect_gui.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    # Compute timeout based on sequence sleep durations
    timeout = 90.0
    if "longwait" in sequence:
        timeout = 120.0

    script = build_lua_launch_connection_sequenced(
        run_id, str(result_path.resolve()), str(jsonl_path.resolve()),
        com_num=com_num, baud=baud, sequence=sequence, retry_on_3=True,
    )
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]connection connect-gui (run_id={run_id})...[/cyan]")
    console.print(f"  COM: {com_upper}  Baud: {baud}  Sequence: {sequence}")

    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")

    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose,
        timeout=timeout,
        result_path=result_path.resolve(),
    )

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")
    connect_return = data.get("connect_return")

    if status == "CONNECTION_GUI_SUCCESS":
        console.print(f"[green][OK] Connect passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] Connect status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    # Return-3 specific diagnostics
    if connect_return == "3" or connect_return == 3 or status == "CONNECT_RETURNED_3":
        console.print(_RETURN3_DIAGNOSTICS)

    if status != "CONNECTION_GUI_SUCCESS":
        raise typer.Exit(1)


@mmws_conn_app.command("connect-return3-diag")
def mmws_connection_connect_return3_diag(
    com: str = typer.Option("COM6", "--com", help="COM port (e.g. COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    sequence: str = typer.Option(
        "gui-set1-fullreset-connect", "--sequence",
        help="Sequence: showgui-connect, showgui-sleep-connect, "
             "showgui-sop-sleep-connect, showgui-select-sop-connect, "
             "showgui-sop-reset-longwait-connect, select-set-connect, gui-set1-fullreset-connect, gui-set1-fullreset-aw2944-connect",
    ),
    force: bool = typer.Option(False, "--force", help="Kill existing mmWaveStudio instances first"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """[DIAGNOSTIC ONLY] Diagnostic tool for ConnectTarget return code 3.

    WARNING: Lua ar1.Connect is unreliable for AWR2944 RS232 connection.
    It can return 0 with invalid device identity or return 3 after valid
    GUI Set. Use 'awr mmws gui-connect click-flow' instead.
    """
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_connection_sequenced, CONNECT_SEQUENCES
    import uuid, json

    com_upper = com.upper()
    try:
        com_num = int(com_upper[3:])
    except ValueError:
        console.print(f"[red][FAIL] Invalid COM port number: {com}[/red]")
        raise typer.Exit(1)

    if sequence not in CONNECT_SEQUENCES:
        console.print(f"[red][FAIL] Unknown sequence: {sequence}[/red]")
        console.print(f"  Valid sequences: {', '.join(CONNECT_SEQUENCES)}")
        raise typer.Exit(1)

    if force:
        console.print("[yellow]Killing existing mmWave Studio instances...[/yellow]")
        mmws_lua_launch_cleanup(verbose=verbose)

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "connection_return3_diag_result.json"
    jsonl_path = probe_dir / "connection_return3_diag_progress.jsonl"
    script_path = probe_dir / "connection_return3_diag.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    timeout = 90.0
    if "longwait" in sequence:
        timeout = 120.0

    # No retry for diagnostic mode
    script = build_lua_launch_connection_sequenced(
        run_id, str(result_path.resolve()), str(jsonl_path.resolve()),
        com_num=com_num, baud=baud, sequence=sequence, retry_on_3=False,
    )
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]connection return3-diag (run_id={run_id})...[/cyan]")
    console.print(f"  COM: {com_upper}  Baud: {baud}  Sequence: {sequence}")
    console.print(f"  Retry: disabled (diagnostic mode)")

    if verbose:
        console.print("[dim]Generated Lua:[/dim]")
        for line in script.splitlines():
            console.print(f"  [dim]{line}[/dim]")

    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose,
        timeout=timeout,
        result_path=result_path.resolve(),
    )

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")
    connect_return = data.get("connect_return")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if connect_return == "3" or connect_return == 3 or status == "CONNECT_RETURNED_3":
        console.print(_RETURN3_DIAGNOSTICS)
    elif status == "CONNECTION_GUI_SUCCESS":
        console.print(f"[green][OK] Sequence '{sequence}' produced CONNECT_SUCCESS.[/green]")
        console.print(f"  Use: awr mmws connection connect-gui --sequence {sequence} --force")
    else:
        console.print(f"[red][FAIL] Connect status: {status}[/red]")


@mmws_conn_app.command("sop-set-only")
def mmws_connection_sop_set_only(
    mode: int = typer.Option(2, "--mode", help="SOP mode (e.g. 2)"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """[DIAGNOSTIC ONLY] Run SOPControl only (NOT full Set(1)) via /lua.

    WARNING: Lua ar1.Connect is unreliable for AWR2944 RS232 connection.
    Use 'awr mmws gui-connect click-flow' for the official connection path.
    SOPControl(2) alone does NOT reproduce the GUI Set(1) button behavior.
    """
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_connection_sop_set_only
    import uuid, json

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "connection_sop_set_only_result.json"
    jsonl_path = probe_dir / "connection_sop_set_only_progress.jsonl"
    script_path = probe_dir / "connection_sop_set_only.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    script = build_lua_launch_connection_sop_set_only(
        run_id, str(result_path.resolve()), str(jsonl_path.resolve()),
        mode=mode
    )
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]connection sop-set-only (run_id={run_id})...[/cyan]")
    console.print(f"  Mode: {mode}")

    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose,
        timeout=30.0,
        result_path=result_path.resolve(),
    )

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")

    if status == "SOPCONTROL_SUCCESS":
        console.print(f"[green][OK] SOP Set passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] SOP Set status: {status}[/red]")

    for k, v in data.items():
        if k not in ["run_id", "executed"]:
            console.print(f"  {k}: {v}")

    if status != "SOPCONTROL_SUCCESS":
        raise typer.Exit(1)


@mmws_conn_app.command("set1-discovery")
def mmws_connection_set1_discovery(
    force: bool = typer.Option(False, "--force", help="Kill existing mmWaveStudio instances first"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Dump ar1 methods matching Set(1) keywords to discover the true API."""
    from .legacy_mmws.executor import _execute_lua_launch
    from .legacy_mmws.lua_builder import build_lua_launch_connection_set1_discovery
    import uuid, json

    if force:
        console.print("[yellow]Killing existing mmWave Studio instances...[/yellow]")
        mmws_lua_launch_cleanup(verbose=verbose)

    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "connection_set1_discovery_result.json"
    jsonl_path = probe_dir / "connection_set1_discovery_progress.jsonl"
    script_path = probe_dir / "connection_set1_discovery.lua"

    if result_path.exists(): result_path.unlink()
    if jsonl_path.exists(): jsonl_path.unlink()

    script = build_lua_launch_connection_set1_discovery(
        run_id, str(result_path.resolve()), str(jsonl_path.resolve())
    )
    script_path.write_text(script, encoding="utf-8")

    console.print(f"[cyan]connection set1-discovery (run_id={run_id})...[/cyan]")

    res = _execute_lua_launch(
        script_path.resolve(), verbose=verbose,
        timeout=60.0,
        result_path=result_path.resolve(),
    )

    if jsonl_path.exists():
        console.print("[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            console.print(f"  [dim]{line}[/dim]")

    if not res.success:
        console.print(f"[red][FAIL] Failed: {res.error}[/red]")
        raise typer.Exit(1)

    data = json.loads(result_path.read_text(encoding="utf-8"))
    status = data.get("status", "UNKNOWN")

    if status == "DISCOVERY_SUCCESS":
        console.print(f"[green][OK] Discovery passed (status={status})[/green]")
    else:
        console.print(f"[red][FAIL] Discovery status: {status}[/red]")

    methods = data.get("methods", {})
    console.print(f"[bold]Found {len(methods)} matching methods:[/bold]")
    for k, v in methods.items():
        console.print(f"  {k} : {v}")

    if status != "DISCOVERY_SUCCESS":
        raise typer.Exit(1)


@mmws_conn_app.command("parse-manual-log")
def mmws_connection_parse_manual_log(
    log_path: str = typer.Argument(..., help="Path to manual GUI set1 log text file"),
) -> None:
    """Extract [RadarAPI] ar1.* calls in order from a manual GUI log paste."""
    from pathlib import Path
    
    p = Path(log_path)
    if not p.exists():
        console.print(f"[red][FAIL] Log file not found: {log_path}[/red]")
        raise typer.Exit(1)
        
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    console.print(f"[cyan]Parsing {p.name}...[/cyan]")
    
    found = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "[RadarAPI]" in line and "ar1." in line:
            console.print(f"[green]{line}[/green]")
            found += 1
            
    if found == 0:
        console.print("[yellow]No [RadarAPI] ar1. calls found in log.[/yellow]")
    else:
        console.print(f"[bold]Extracted {found} RadarAPI calls.[/bold]")


# ---------------------------------------------------------------------------
# gui-connect commands ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â pywinauto GUI-button automation (OFFICIAL)
# ---------------------------------------------------------------------------

_GUI_CONNECT_PRECONDITION = (
    "[cyan]Expected precondition: mmWave Studio is open as admin, "
    "Startup.lua completed, and AWR was power-cycled using "
    "power-before-USB order.[/cyan]"
)


@mmws_guiconn_app.command("inspect")
def mmws_gui_connect_inspect(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Attach to mmWave Studio and dump the Connection tab control tree.

    Does NOT click anything. Identifies candidate controls for:
    frequency, device, Set(1), COM, baud, RS232 Connect, Device Status.
    """
    from .legacy_mmws.gui_connect import (
        attach_mmwave_studio, dump_control_tree, inspect_connection_tab,
    )

    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")

    probe_dir = _lua_launch_probe_dir()

    try:
        app, window = attach_mmwave_studio(
            pid=pid, title_regex=title_regex,
            probe_dir=probe_dir, verbose_log=vlog,
        )
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)

    controls_path = probe_dir / "gui_connect_controls.txt"

    count = dump_control_tree(window, controls_path, verbose_log=vlog)
    console.print(f"[green]Dumped {count} controls to {controls_path}[/green]")

    controls = inspect_connection_tab(window, verbose_log=vlog)

    console.print("\n[bold]Connection Tab Controls:[/bold]")
    _print_control_status("RadarAPI window", controls.radarapi_window)
    _print_control_status("77 GHz radio (m_RadioBtn77GHzRadarDev)", controls.frequency_radio)
    _print_control_status("Device Variant group (m_grpDeviceVariantTypes)", controls.device_variant_group)
    _print_control_status("Device Variant AWR29xx/XWR2944", controls.device_variant_radio)
    _print_control_status("Set(1) button (m_btnSetSop)", controls.set_button)
    _print_control_status("Refresh Ports (m_btnRefreshPorts)", controls.refresh_ports_button)
    _print_control_status("COM port (m_cboComPort)", controls.com_combo)
    _print_control_status("Baud rate (m_cboBaudRate)", controls.baud_combo)
    _print_control_status("RS232 Connect (m_btnConnect)", controls.rs232_connect_button)
    _print_control_status("RS232 status (m_lblRS232UARTConnectivityStatus)", controls.rs232_status_label)
    _print_control_status("SPI status (m_lblSPIConnectivityStatus)", controls.spi_status_label)
    _print_control_status("Device Status label", controls.device_status_label)
    _print_control_status("Output document (m_ConsoleText)", controls.output_document)

    # Show Device Variant candidates (always, for debugging)
    if controls.device_variant_candidates:
        console.print(f"\n[bold]Device Variant candidates ({len(controls.device_variant_candidates)}):[/bold]")
        for aid, txt in controls.device_variant_candidates:
            matched = controls.device_variant_radio is not None and (
                aid == (controls.device_variant_radio.automation_id()
                        if hasattr(controls.device_variant_radio, 'automation_id') else "")
            )
            marker = " [green]<<< MATCHED[/green]" if matched else ""
            console.print(f"  auto_id={aid!r} text={txt!r}{marker}")
    elif controls.device_variant_group is not None:
        console.print("\n[yellow]Device Variant group found but no children enumerated.[/yellow]")

    if controls.missing:
        console.print(f"\n[yellow]Missing/not found: {', '.join(controls.missing)}[/yellow]")

    if controls.all_required_found:
        console.print("\n[green][OK] All required controls (Set(1), RS232 Connect) found.[/green]")
    else:
        console.print("\n[red][FAIL] Required controls missing. Check control tree dump.[/red]")
        raise typer.Exit(1)


def _print_control_status(label: str, ctrl) -> None:
    """Print a control status line."""
    if ctrl is not None:
        try:
            text = ctrl.window_text()[:60]
            auto_id = ctrl.automation_id() if hasattr(ctrl, "automation_id") else ""
            console.print(f"  [green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green] {label}: text={text!r} auto_id={auto_id!r}")
        except Exception:
            console.print(f"  [green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green] {label}: [dim]present[/dim]")
    else:
        console.print(f"  [red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â[/red] {label}: [red]not found[/red]")


@mmws_guiconn_app.command("click-flow")
def mmws_gui_connect_click_flow(
    com: str = typer.Option("COM6", "--com", help="COM port (e.g. COM6)"),
    baud: int = typer.Option(115200, "--baud", help="Baud rate"),
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Identify controls and print planned actions without clicking"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
    slow: bool = typer.Option(False, "--slow", help="Wait longer after clicks for slow GUI"),
    allow_keyboard_fallback: bool = typer.Option(False, "--allow-keyboard-fallback", help="Allow typing COM/Baud blindly if selection fails"),
) -> None:
    """Execute the full GUI click sequence: Set(1) + RS232 Connect.

    Attaches to an already-open mmWave Studio instance and clicks the actual
    GUI buttons to reproduce the manual connection flow:

    1. Select 77 GHz frequency band
    2. Select xWR2944/AWR29xx device variant
    3. Click Set(1) button
    4. Wait for SOP
    5. Set COM port and baud rate
    6. Click RS232 Connect button
    7. Verify Device Status shows AWR2944/GP/SOP:2

    Use --dry-run to preview what would be clicked without actually clicking.
    """
    from .legacy_mmws.gui_connect import (
        attach_mmwave_studio, click_flow,
    )
    import json

    console.print(_GUI_CONNECT_PRECONDITION)

    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")

    probe_dir = _lua_launch_probe_dir()

    try:
        app, window = attach_mmwave_studio(
            pid=pid, title_regex=title_regex,
            probe_dir=probe_dir, verbose_log=vlog,
        )
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print("[yellow]DRY RUN ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â identifying controls, no clicks.[/yellow]")

    result = click_flow(
        window,
        com_port=com,
        baud=baud,
        probe_dir=probe_dir,
        dry_run=dry_run,
        verbose_log=vlog,
        slow=slow,
        allow_keyboard_fallback=allow_keyboard_fallback,
    )

    # Write result JSON
    result_path = probe_dir / "gui_connect_click_flow_result.json"
    result_data = {
        "status": result.status,
        "device_status_text": result.device_status_text,
        "details": result.details,
        "error": result.error,
    }
    result_path.write_text(json.dumps(result_data, indent=2), encoding="utf-8")

    # Print progress log
    jsonl_path = probe_dir / "gui_connect_click_flow_progress.jsonl"
    if jsonl_path.exists():
        console.print("\n[cyan]Progress Log:[/cyan]")
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            console.print(f"  [dim]{line}[/dim]")

    # Print result
    console.print(f"\n[bold]Status: {result.status}[/bold]")
    if result.device_status_text:
        console.print(f"  Device Status: {result.device_status_text}")
    if result.error:
        console.print(f"  [red]Error: {result.error}[/red]")

    if result.status == "CONNECTION_GUI_BUTTON_SUCCESS":
        console.print("[green][OK] Connection established via GUI buttons.[/green]")
        console.print("[green]Ready for firmware loading stage.[/green]")
    elif result.status == "DRY_RUN_COMPLETE":
        console.print("[yellow]Dry run complete. No clicks were performed.[/yellow]")
        if "planned_actions" in result.details:
            console.print("\n[bold]Planned actions:[/bold]")
            for action in result.details["planned_actions"]:
                console.print(f"  ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ {action}")
    elif result.status == "NEED_POWER_CYCLE":
        console.print(
            "[yellow]Power-cycle AWR using power-before-USB order, "
            "restart mmWave Studio, and retry.[/yellow]"
        )
    elif result.status == "CONTROL_NOT_FOUND":
        console.print(
            "[red]Check ti/probe_logs/gui_connect_controls.txt for the "
            "full control tree dump.[/red]"
        )

    if result.status not in ("CONNECTION_GUI_BUTTON_SUCCESS", "DRY_RUN_COMPLETE"):
        raise typer.Exit(1)


@mmws_guiconn_app.command("status")
def mmws_gui_connect_status(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Read Device Status from mmWave Studio and verify valid AWR2944 connection.

    Success requires Device Status containing AWR2944, GP, and SOP:2.
    Does NOT use Connect_return == 0 as the success criterion.
    """
    from .legacy_mmws.gui_connect import (
        attach_mmwave_studio, inspect_connection_tab, read_device_status,
    )
    import json

    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")

    probe_dir = _lua_launch_probe_dir()

    try:
        app, window = attach_mmwave_studio(
            pid=pid, title_regex=title_regex,
            probe_dir=probe_dir, verbose_log=vlog,
        )
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)

    controls = inspect_connection_tab(window, verbose_log=vlog)
    status = read_device_status(window, controls, verbose_log=vlog)

    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / "gui_connect_status_result.json"
    result_path.write_text(json.dumps(status, indent=2), encoding="utf-8")

    console.print(f"\n[bold]Device Status:[/bold]")
    console.print(f"  Raw text: {status['raw_text']!r}")
    console.print(f"  Device:   {status['device']}")
    console.print(f"  Type:     {status['type']}")
    console.print(f"  SOP:      {status['sop']}")
    console.print(f"  ES:       {status['es']}")

    if status["valid"]:
        console.print(
            "\n[green][OK] Valid AWR2944/GP/SOP:2 connection confirmed.[/green]"
        )
        console.print("[green]Ready for firmware loading stage.[/green]")
    else:
        console.print(
            "\n[red][FAIL] Device Status does not show valid "
            "AWR2944/GP/SOP:2.[/red]"
        )
        if not status["raw_text"]:
            console.print(
                "[yellow]Device Status label may not have been found. "
                "Run 'awr mmws gui-connect inspect' to check the control tree.[/yellow]"
            )
        raise typer.Exit(1)


@mmws_guiconn_app.command("manual-check")
def mmws_gui_connect_manual_check(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Verify mmWave Studio Device Status after manual Connection tab usage.
    
    This reads the Output document and RS232 status label to verify a
    valid AWR2944 connection (AWR2944/GP/SOP:2) established by human clicking.
    """
    from .legacy_mmws.gui_connect import (
        attach_mmwave_studio, manual_check
    )

    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")

    probe_dir = _lua_launch_probe_dir()

    try:
        app, window = attach_mmwave_studio(
            pid=pid, title_regex=title_regex,
            probe_dir=probe_dir, verbose_log=vlog,
        )
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)

    console.print("[cyan]Reading mmWave Studio state...[/cyan]")
    result = manual_check(window, probe_dir=probe_dir, verbose_log=vlog)

    console.print(f"\n[bold]Status: {result.status}[/bold]")
    if result.device_status_text:
        console.print(f"  Device Status: {result.device_status_text}")
    if result.error:
        console.print(f"  [red]Error: {result.error}[/red]")

    if result.status == "MANUAL_CONNECTION_VALID":
        console.print("\n[green][OK] Valid AWR2944/GP/SOP:2 connection confirmed.[/green]")
        console.print("[green]Ready for firmware loading stage.[/green]")
    else:
        console.print("\n[red][FAIL] Manual connection state not valid.[/red]")
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# awr mmws post *
# ---------------------------------------------------------------------------

@mmws_post_app.command("status")
def mmws_post_status(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(r"^mmWave Studio", "--title-regex", help="Regex for mmWave Studio window title"),
    fallback_latest_snapshot: bool = typer.Option(False, "--fallback-latest-snapshot", help="Use previous snapshot if live dump fails"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Print mmWave Studio's post-connection state using live snapshot dump."""
    from .legacy_mmws.post_connect import get_post_status, parse_post_status_text
    from .legacy_mmws.gui_connect import attach_mmwave_studio
    import json
    import uuid
    import dataclasses
    
    probe_dir = _lua_launch_probe_dir()
    vlog = console.print if verbose else lambda _: None
    run_id = str(uuid.uuid4())[:8]

    try:
        app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
        device_status, status, source_info = get_post_status(window, vlog, run_id, probe_dir)
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)
        
    if source_info.get("status_source") == "live_snapshot_failed" and fallback_latest_snapshot:
        # try to find the latest snapshot
        snapshots = list(probe_dir.glob("*_status_output_snapshot.txt"))
        if snapshots:
            latest = max(snapshots, key=lambda p: p.stat().st_mtime)
            console.print(f"[yellow]Falling back to snapshot: {latest.name}[/yellow]")
            doc_text = latest.read_text(encoding="utf-8")
            status, source_info = parse_post_status_text(
                doc_text,
                rs232_valid=device_status.get("gate_passed", False),
                spi_connected=status.spi_connected,
                source_name="fallback_snapshot",
                snapshot_path=str(latest)
            )

    status_dict = dataclasses.asdict(status)
    status_dict.update(source_info)
    
    result_path = probe_dir / f"{run_id}_post_status_result.json"
    result_path.write_text(json.dumps(status_dict, indent=2), encoding="utf-8")
    
    console.print(f"\n[bold]Post-Connection Status (run_id: {run_id}):[/bold]")
    
    chars = source_info.get("source_text_chars", 0)
    if chars < 1000:
        console.print(f"\n[red][WARNING] Output text is suspiciously short ({chars} chars). Parsing may be invalid![/red]")
    
    console.print(f"\n[bold]Post-Connection Status:[/bold]")
    for k, v in status_dict.items():
        color = "green" if v else ("red" if k in ("rs232_valid", "bss_downloaded", "mss_downloaded", "mss_powered", "bss_powered", "rf_enabled") and not v else "yellow")
        console.print(f"  {k}: [{color}]{v}[/{color}]")
        
    console.print(f"\n[dim]Wrote full status to {result_path}[/dim]")
    
    if not status.rs232_valid:
        console.print("\n[red][WARNING] Connection gate failed. Device identity or RS232 status is invalid.[/red]")


@mmws_post_app.command("parser-test")
def mmws_post_parser_test(
    snapshot: str = typer.Option(..., "--snapshot", help="Path to mmws_output_snapshot.txt to test parse"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test the post-status parser offline using a saved snapshot."""
    from .legacy_mmws.post_connect import parse_post_status_text
    import json
    
    snap_path = Path(snapshot)
    if not snap_path.exists():
        console.print(f"[red]Snapshot file not found: {snap_path}[/red]")
        raise typer.Exit(1)
        
    doc_text = snap_path.read_text(encoding="utf-8")
    status, source_info = parse_post_status_text(
        doc_text, 
        rs232_valid=True, 
        spi_connected=True, 
        source_name="parser_test_snapshot",
        snapshot_path=str(snap_path)
    )
    
    import dataclasses
    import uuid
    status_dict = dataclasses.asdict(status)
    status_dict.update(source_info)
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / f"{run_id}_parser_test_result.json"
    result_path.write_text(json.dumps(status_dict, indent=2), encoding="utf-8")
    
    console.print(f"\n[bold]Offline Parse Result for {snap_path}:[/bold]")
    console.print(json.dumps(status_dict, indent=2))
    console.print(f"\n[green]Wrote parser result to: {result_path}[/green]")


@mmws_post_app.command("output-snapshot")
def mmws_post_output_snapshot(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Dump the full mmWave Studio Output document."""
    from .legacy_mmws.gui_connect import attach_mmwave_studio
    from .legacy_mmws.post_connect import dump_output_snapshot
    
    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")

    probe_dir = _lua_launch_probe_dir()
    out_path = probe_dir / "mmws_output_snapshot.txt"

    try:
        app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
        dump_output_snapshot(window, vlog, out_path)
        console.print(f"[green]Successfully dumped output snapshot to {out_path}[/green]")
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)


@mmws_post_app.command("extract-ar1")
def mmws_post_extract_ar1(
    after_device_status: bool = typer.Option(True, "--after-device-status/--all", help="Only extract after the last valid Device Status"),
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Extract and classify ar1.* commands from the live Output document."""
    from .legacy_mmws.gui_connect import attach_mmwave_studio
    from .legacy_mmws.post_connect import connection_gate, dump_output_snapshot, extract_ar1_commands, generate_replay_lua
    import uuid
    import json
    
    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")

    probe_dir = _lua_launch_probe_dir()
    run_id = str(uuid.uuid4())[:8]

    try:
        app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
        device_status = connection_gate(window, vlog)
        if not device_status.get("gate_passed"):
            console.print("[red][FAIL] POST_CONNECTION_NOT_VALID: Cannot reliably extract commands without valid RS232 connection state.[/red]")
            raise typer.Exit(1)
            
        snap_path = probe_dir / f"{run_id}_output_snapshot.txt"
        dump_output_snapshot(window, vlog, snap_path)
        doc_text = snap_path.read_text(encoding="utf-8")
        
        commands = extract_ar1_commands(doc_text, after_device_status)
        
        import dataclasses
        cmd_dicts = [dataclasses.asdict(c) for c in commands]
        json_path = probe_dir / f"{run_id}_extracted_ar1_commands.json"
        json_path.write_text(json.dumps(cmd_dicts, indent=2), encoding="utf-8")
        
        lua_path = probe_dir / f"{run_id}_extracted_replay.lua"
        lua_script = generate_replay_lua(commands, run_id, lua_path)
        lua_path.write_text(lua_script, encoding="utf-8")
        
        console.print(f"[green]Extracted {len(commands)} commands.[/green]")
        console.print(f"JSON: {json_path}")
        console.print(f"Replay Lua: {lua_path}")
        console.print(f"To replay: [cyan]dofile([[{lua_path.resolve()}]])[/cyan]")
        
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)


@mmws_post_app.command("session-audit")
def mmws_post_session_audit(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Audit the session state: detect dirty events and determine stage readiness."""
    from .legacy_mmws.gui_connect import attach_mmwave_studio
    from .legacy_mmws.post_connect import connection_gate, dump_output_snapshot, audit_session
    import json
    import uuid
    import dataclasses
    
    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")
    
    probe_dir = _lua_launch_probe_dir()
    run_id = str(uuid.uuid4())[:8]
    
    try:
        app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
        device_status = connection_gate(window, vlog)
        rs232_valid = device_status.get("gate_passed", False)
        
        snap_path = probe_dir / f"{run_id}_session_audit_snapshot.txt"
        dump_output_snapshot(window, vlog, snap_path)
        
        doc_text = ""
        if snap_path.exists():
            doc_text = snap_path.read_text(encoding="utf-8")
        
        audit = audit_session(doc_text, rs232_valid=rs232_valid)
        
        audit_dict = dataclasses.asdict(audit)
        audit_path = probe_dir / f"{run_id}_session_audit.json"
        audit_path.write_text(json.dumps(audit_dict, indent=2), encoding="utf-8")
        
        console.print(f"\n[bold]Session Audit (run_id: {run_id}):[/bold]")
        for k, v in audit_dict.items():
            if k == "reason":
                continue
            if isinstance(v, bool):
                color = "green" if v else "red"
                if k in ("requires_power_cycle", "rf_enable_failed", "poweroff_seen",
                         "disconnect_seen", "protocol_error_seen", "static_config_failed"):
                    color = "red" if v else "green"
                elif k in ("clean_for_firmware_power", "firmware_power_success", "rs232_valid"):
                    color = "green" if v else "red"
                else:
                    color = "yellow" if v else "dim"
                console.print(f"  {k}: [{color}]{v}[/{color}]")
            else:
                console.print(f"  {k}: {v}")
        
        if audit.reason:
            console.print(f"\n[bold]Reasons:[/bold]")
            for r in audit.reason:
                console.print(f"  [red]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {r}[/red]")
        
        if audit.requires_power_cycle:
            console.print(f"\n[red][!] SESSION IS DIRTY. Power-cycle and reconnect required.[/red]")
        elif audit.clean_for_firmware_power:
            console.print(f"\n[green][OK] Session is clean for firmware-power-script.[/green]")
        elif audit.firmware_power_success:
            console.print(f"\n[green][OK] Firmware/power succeeded. Session is clean for config.[/green]")
        
        console.print(f"\n[dim]Wrote audit to {audit_path}[/dim]")
        
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)


@mmws_post_app.command("preflight-firmware")
def mmws_post_preflight_firmware(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    snapshot: str = typer.Option(None, "--snapshot", help="Use saved output snapshot text instead of dumping live UI"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Check if the session is clean enough for firmware-power-script."""
    from .legacy_mmws.gui_connect import attach_mmwave_studio
    from .legacy_mmws.post_connect import connection_gate, dump_output_snapshot, audit_session, preflight_firmware
    import uuid
    
    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")
    
    probe_dir = _lua_launch_probe_dir()
    run_id = str(uuid.uuid4())[:8]
    
    try:
        doc_text = ""
        source_type = "live_uia"
        source_path = ""
        rs232_valid = False
        
        if snapshot:
            snap_path = Path(snapshot)
            if snap_path.exists():
                doc_text = snap_path.read_text(encoding="utf-8")
            source_type = "snapshot"
            source_path = str(snap_path.resolve())
            # Without UI, assume RS232 is valid for offline check, or leave False.
            # Usually users rely on preflight-firmware online.
            rs232_valid = True 
        else:
            app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
            device_status = connection_gate(window, vlog)
            rs232_valid = device_status.get("gate_passed", False)
            
            snap_path = probe_dir / f"{run_id}_preflight_fw_snapshot.txt"
            dump_output_snapshot(window, vlog, snap_path)
            
            if snap_path.exists():
                doc_text = snap_path.read_text(encoding="utf-8")
                source_path = str(snap_path)
        
        audit = audit_session(doc_text, rs232_valid=rs232_valid, source_type=source_type, source_path=source_path)
        passed, reasons = preflight_firmware(audit)
        
        if passed:
            console.print(f"\n[green]FIRMWARE_PREFLIGHT_PASSED[/green]")
            console.print("[green]Session is clean for firmware-power-script.[/green]")
        else:
            console.print(f"\n[red]FIRMWARE_PREFLIGHT_FAILED_REQUIRES_CLEAN_SESSION[/red]")
            for r in reasons:
                console.print(f"  [red]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {r}[/red]")
            raise typer.Exit(1)
            
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)


@mmws_post_app.command("preflight-config")
def mmws_post_preflight_config(
    pid: int = typer.Option(None, "--pid", help="Attach directly by PID"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    snapshot: str = typer.Option(None, "--snapshot", help="Use saved output snapshot text instead of dumping live UI"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Check if the session is clean enough for config scripts."""
    from .legacy_mmws.gui_connect import attach_mmwave_studio
    from .legacy_mmws.post_connect import connection_gate, dump_output_snapshot, audit_session, preflight_config
    import uuid
    
    vlog_lines: list[str] = []
    def vlog(msg: str):
        vlog_lines.append(msg)
        if verbose:
            console.print(f"  [dim]{msg}[/dim]")
    
    probe_dir = _lua_launch_probe_dir()
    run_id = str(uuid.uuid4())[:8]
    
    try:
        doc_text = ""
        source_type = "live_uia"
        source_path = ""
        rs232_valid = False
        
        if snapshot:
            snap_path = Path(snapshot)
            if snap_path.exists():
                doc_text = snap_path.read_text(encoding="utf-8")
            source_type = "snapshot"
            source_path = str(snap_path.resolve())
            rs232_valid = True 
        else:
            app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
            device_status = connection_gate(window, vlog)
            rs232_valid = device_status.get("gate_passed", False)
            
            snap_path = probe_dir / f"{run_id}_preflight_cfg_snapshot.txt"
            dump_output_snapshot(window, vlog, snap_path)
            
            if snap_path.exists():
                doc_text = snap_path.read_text(encoding="utf-8")
                source_path = str(snap_path)
        
        audit = audit_session(doc_text, rs232_valid=rs232_valid, source_type=source_type, source_path=source_path)
        passed, reasons = preflight_config(audit)
        
        if passed:
            console.print(f"\n[green]CONFIG_PREFLIGHT_PASSED[/green]")
            console.print("[green]Session is ready for config scripts.[/green]")
        else:
            console.print(f"\n[red]CONFIG_PREFLIGHT_FAILED_REQUIRES_CLEAN_SESSION[/red]")
            for r in reasons:
                console.print(f"  [red]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {r}[/red]")
            raise typer.Exit(1)
            
    except RuntimeError as e:
        console.print(f"[red][FAIL] {e}[/red]")
        raise typer.Exit(1)


@mmws_post_app.command("firmware-power-script")
def mmws_post_firmware_power_script(
    pid: int = typer.Option(None, "--pid", help="Attach to mmWave Studio by PID for preflight check"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    snapshot: str = typer.Option(None, "--snapshot", help="Use saved output snapshot text for preflight"),
    audit: str = typer.Option(None, "--audit", help="Use saved audit JSON for preflight"),
    force: bool = typer.Option(False, "--force", help="Generate even if preflight fails"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Generate a deterministic AWR2944 firmware and power-on Lua script.
    
    If --pid or --snapshot or --audit is provided, runs preflight-firmware before generating.
    If preflight fails, refuses to generate unless --force is set.
    """
    from .legacy_mmws.post_connect import generate_firmware_power_script
    import uuid
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    
    # Preflight gate
    if pid is not None or snapshot or audit:
        from .legacy_mmws.gui_connect import attach_mmwave_studio
        from .legacy_mmws.post_connect import connection_gate, dump_output_snapshot, audit_session, preflight_firmware, SessionAudit
        import json
        
        vlog_lines: list[str] = []
        def vlog(msg: str):
            vlog_lines.append(msg)
            if verbose:
                console.print(f"  [dim]{msg}[/dim]")
        
        try:
            if audit:
                audit_path = Path(audit)
                audit_dict = json.loads(audit_path.read_text(encoding="utf-8"))
                audit_obj = SessionAudit(**audit_dict)
                passed, reasons = preflight_firmware(audit_obj)
            else:
                doc_text = ""
                source_type = "live_uia"
                source_path = ""
                rs232_valid = False
                
                if snapshot:
                    snap_path = Path(snapshot)
                    if snap_path.exists():
                        doc_text = snap_path.read_text(encoding="utf-8")
                    source_type = "snapshot"
                    source_path = str(snap_path.resolve())
                    rs232_valid = True
                elif pid is not None:
                    app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
                    device_status = connection_gate(window, vlog)
                    rs232_valid = device_status.get("gate_passed", False)
                    
                    snap_path = probe_dir / f"{run_id}_preflight_fw_snapshot.txt"
                    dump_output_snapshot(window, vlog, snap_path)
                    
                    if snap_path.exists():
                        doc_text = snap_path.read_text(encoding="utf-8")
                        source_path = str(snap_path)
                
                audit_obj = audit_session(doc_text, rs232_valid=rs232_valid, source_type=source_type, source_path=source_path)
                passed, reasons = preflight_firmware(audit_obj)
            
            if not passed:
                console.print(f"\n[red]FIRMWARE_PREFLIGHT_FAILED_REQUIRES_CLEAN_SESSION[/red]")
                for r in reasons:
                    console.print(f"  [red]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {r}[/red]")
                if not force:
                    console.print("[red]Refusing to generate script. Use --force to override.[/red]")
                    raise typer.Exit(1)
                else:
                    console.print("[yellow]--force specified. Generating script despite failed preflight.[/yellow]")
            else:
                console.print(f"[green]FIRMWARE_PREFLIGHT_PASSED[/green]")
                
        except RuntimeError as e:
            console.print(f"[red][FAIL] {e}[/red]")
            if not force:
                raise typer.Exit(1)
    else:
        console.print("[yellow]" + "=" * 70 + "[/yellow]")
        console.print("[yellow]WARNING: NO PREFLIGHT WAS RUN.[/yellow]")
        console.print("[yellow]Only use this immediately after a clean manual RS232 connection.[/yellow]")
        console.print("[yellow]Use --pid <PID> for automatic session safety checks.[/yellow]")
        console.print("[yellow]" + "=" * 70 + "[/yellow]\n")
    
    lua_path = probe_dir / f"{run_id}_firmware_power.lua"
    
    generated = generate_firmware_power_script(run_id, lua_path)
    lua_path.write_text(generated.script, encoding="utf-8")
    
    console.print(f"[cyan]Generated firmware-power script:[/cyan] {lua_path}")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{lua_path.resolve()}]])[/green]")
    
    if verbose:
        console.print("\n[dim]Preview of generated script (first 15 lines):[/dim]")
        preview = "\n".join(script.splitlines()[:15])
        console.print(f"[dim]{preview}[/dim]")


@mmws_post_app.command("ar1-help-probe")
def mmws_post_ar1_help_probe(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Generate a Lua script to probe types and help strings for ar1 commands."""
    from .legacy_mmws.post_connect import generate_ar1_help_probe
    import uuid
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    result_path = probe_dir / f"{run_id}_ar1_help_result.txt"
    lua_path = probe_dir / f"{run_id}_ar1_help_probe.lua"
    
    script = generate_ar1_help_probe(run_id, result_path)
    lua_path.write_text(script, encoding="utf-8")
    
    console.print(f"[cyan]Generated ar1-help-probe script:[/cyan] {lua_path}")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{lua_path.resolve()}]])[/green]")


@mmws_post_app.command("replay-lua")
def mmws_post_replay_lua(
    script: str = typer.Option(..., "--script", help="Path to a generated replay Lua script"),
    only_firmware: bool = typer.Option(False, "--only-firmware", help="Replay only firmware commands"),
    only_power_rf: bool = typer.Option(False, "--only-power-rf", help="Replay only power/rf commands"),
    only_static_config: bool = typer.Option(False, "--only-static-config", help="Replay only static config commands"),
    only_data_config: bool = typer.Option(False, "--only-data-config", help="Replay only data config commands"),
    only_profile_frame: bool = typer.Option(False, "--only-profile-frame", help="Replay only profile/chirp/frame commands"),
    only_capture: bool = typer.Option(False, "--only-capture", help="Replay only capture commands"),
    all_cmds: bool = typer.Option(False, "--all", help="Replay all non-connection commands"),
) -> None:
    """Print the dofile command for a replay script (filtering options coming soon)."""
    # TODO: regenerate the script if filter flags are set, or just tell user what to paste
    script_path = Path(script)
    if not script_path.exists():
        console.print(f"[red]Script not found: {script_path}[/red]")
        raise typer.Exit(1)
        
    console.print(f"To replay this script, paste this into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{script_path.resolve()}]])[/green]")


@mmws_post_app.command("check-lua-result")
def mmws_post_check_lua_result(
    result: str = typer.Option(..., "--result", help="Path to the JSON result file"),
    progress: str = typer.Option(..., "--progress", help="Path to the JSONL progress file"),
) -> None:
    """Summarize the result of a generated Lua script execution."""
    import json
    
    res_path = Path(result)
    prog_path = Path(progress)
    
    if not res_path.exists():
        console.print(f"[yellow]Result file not found: {res_path}[/yellow]")
    else:
        try:
            res_data = json.loads(res_path.read_text(encoding="utf-8"))
            if res_data.get("success"):
                console.print(f"[green]Lua script execution SUCCESS (run_id: {res_data.get('run_id')})[/green]")
            else:
                console.print(f"[red]Lua script execution FAILED: {res_data.get('error')}[/red]")
        except Exception as e:
            console.print(f"[red]Failed to parse result JSON: {e}[/red]")

    if not prog_path.exists():
        console.print(f"[yellow]Progress file not found: {prog_path}[/yellow]")
    else:
        console.print("\n[bold]Progress Log:[/bold]")
        lines = prog_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if not line.strip(): continue
            try:
                p = json.loads(line)
                ok_str = "[green]OK[/green]" if p.get("ok") else "[red]FAIL[/red]"
                ret_str = f"ret={p.get('ret')}"
                err_str = f" err={p.get('err')}" if p.get("err") else ""
                console.print(f"  {p.get('ts')} | {p.get('cmd')} | {ok_str} | {ret_str}{err_str}")
            except Exception:
                console.print(f"  [dim]{line}[/dim]")


@mmws_post_app.command("inspect-extracted")
def mmws_post_inspect_extracted(
    commands: str = typer.Option(..., "--commands", help="Path to the extracted ar1 commands JSON"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Inspect extracted ar1 commands: counts, signatures, failures, missing commands."""
    from .legacy_mmws.post_connect import AR1Command, inspect_extracted_commands
    import json
    import dataclasses
    
    cmd_path = Path(commands)
    if not cmd_path.exists():
        console.print(f"[red]Commands file not found: {cmd_path}[/red]")
        raise typer.Exit(1)
    
    cmd_dicts = json.loads(cmd_path.read_text(encoding="utf-8"))
    cmd_list = [AR1Command(**d) for d in cmd_dicts]
    
    report = inspect_extracted_commands(cmd_list)
    
    console.print(f"\n[bold]Extracted Command Inspection ({len(cmd_list)} commands):[/bold]")
    
    console.print("\n[bold]Ordered Commands:[/bold]")
    for i, f in enumerate(report["ordered_functions"]):
        cmd = cmd_list[i]
        status_tag = ""
        if cmd.observed_status == "passed":
            status_tag = " [green]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ[/green]"
        elif cmd.observed_status == "failed":
            err = f" ({cmd.observed_error_type})" if cmd.observed_error_type else ""
            status_tag = f" [red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â{err}[/red]"
        console.print(f"  {i+1}. [{cmd.normalized_category}] {f}{status_tag}")
    
    console.print(f"\n[bold]Category Counts:[/bold]")
    for cat, cnt in sorted(report["category_counts"].items()):
        console.print(f"  {cat}: {cnt}")
        
    if report.get("reclassified_commands"):
        console.print(f"\n[yellow]Reclassified {len(report['reclassified_commands'])} old commands to current taxonomy:[/yellow]")
        for rc in report["reclassified_commands"]:
            console.print(f"  {rc['function']}: {rc['original_category']} -> {rc['normalized_category']}")

    
    if report["unknown_functions"]:
        console.print(f"\n[yellow]Unknown functions: {', '.join(report['unknown_functions'])}[/yellow]")
    
    if report["missing_required"]:
        console.print(f"\n[red]Missing required commands: {', '.join(report['missing_required'])}[/red]")
    
    if report["failed_commands"]:
        console.print(f"\n[red]Failed commands in source log:[/red]")
        for fc in report["failed_commands"]:
            console.print(f"  {fc['function']} (line {fc['line']}): {fc['observed_error_type']}")
    
    if report["signature_warnings"]:
        console.print(f"\n[yellow]Signature warnings:[/yellow]")
        for w in report["signature_warnings"]:
            console.print(f"  {w}")
    
    if report["warnings"]:
        for w in report["warnings"]:
            console.print(f"[yellow]WARNING: {w}[/yellow]")
    
    # Write report JSON
    probe_dir = _lua_launch_probe_dir()
    import uuid
    run_id = str(uuid.uuid4())[:8]
    report_path = probe_dir / f"{run_id}_inspect_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    console.print(f"\n[green]Wrote inspection report to: {report_path}[/green]")


@mmws_post_app.command("generate-smoke-from-extracted")
def mmws_post_generate_smoke_from_extracted(
    commands: str = typer.Option(..., "--commands", help="Path to the extracted ar1 commands JSON"),
    include_failed: bool = typer.Option(False, "--include-failed-source-commands", help="Include commands that failed in the source log"),
    include_unknown: bool = typer.Option(False, "--include-unknown", help="Include commands with unknown category"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Generate Lua smoke config from exact extracted commands."""
    from .legacy_mmws.post_connect import AR1Command, generate_smoke_from_extracted
    import json
    import uuid
    
    cmd_path = Path(commands)
    if not cmd_path.exists():
        console.print(f"[red]Commands file not found: {cmd_path}[/red]")
        raise typer.Exit(1)
    
    cmd_dicts = json.loads(cmd_path.read_text(encoding="utf-8"))
    cmd_list = [AR1Command(**d) for d in cmd_dicts]
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    lua_path = probe_dir / f"{run_id}_smoke_from_extracted.lua"
    
    generated = generate_smoke_from_extracted(
        cmd_list, run_id, lua_path,
        commands_json_path=str(cmd_path),
        include_failed=include_failed,
        include_unknown=include_unknown,
    )
    
    lua_path.write_text(generated.script, encoding="utf-8")
    
    result_path = probe_dir / f"{run_id}_smoke_from_extracted_result.json"
    result_path.write_text(json.dumps(generated.metadata, indent=2), encoding="utf-8")
    
    if generated.metadata.get("signature_warnings"):
        for w in generated.metadata["signature_warnings"]:
            console.print(f"[yellow]SIGNATURE WARNING: {w}[/yellow]")
    
    console.print(f"\n[cyan]Generated smoke-from-extracted script:[/cyan] {lua_path}")
    console.print(f"Included: {len(result['included_commands'])} commands")
    console.print(f"Skipped: {len(result['skipped_commands'])} commands")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{lua_path.resolve()}]])[/green]")


@mmws_post_app.command("smoke-from-known-awr2944")
def mmws_post_smoke_from_known_awr2944(
    pid: int = typer.Option(None, "--pid", help="Attach to mmWave Studio by PID for preflight check"),
    title_regex: str = typer.Option(None, "--title-regex", help="Match window title by regex"),
    snapshot: str = typer.Option(None, "--snapshot", help="Use saved output snapshot text for preflight"),
    audit: str = typer.Option(None, "--audit", help="Use saved audit JSON for preflight"),
    force: bool = typer.Option(False, "--force", help="Generate even if preflight fails"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Generate Lua smoke config using GUI-derived AWR2944 commands.
    
    If --pid or --snapshot or --audit is provided, runs preflight-config before generating.
    If preflight fails, refuses to generate unless --force is set.
    """
    from .legacy_mmws.post_connect import generate_smoke_known_awr2944
    import json
    import uuid
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    
    # Preflight gate
    if pid is not None or snapshot or audit:
        from .legacy_mmws.gui_connect import attach_mmwave_studio
        from .legacy_mmws.post_connect import connection_gate, dump_output_snapshot, audit_session, preflight_config, SessionAudit
        
        vlog_lines: list[str] = []
        def vlog(msg: str):
            vlog_lines.append(msg)
            if verbose:
                console.print(f"  [dim]{msg}[/dim]")
        
        try:
            if audit:
                audit_path = Path(audit)
                audit_dict = json.loads(audit_path.read_text(encoding="utf-8"))
                audit_obj = SessionAudit(**audit_dict)
                passed, reasons = preflight_config(audit_obj)
            else:
                doc_text = ""
                source_type = "live_uia"
                source_path = ""
                rs232_valid = False
                
                if snapshot:
                    snap_path = Path(snapshot)
                    if snap_path.exists():
                        doc_text = snap_path.read_text(encoding="utf-8")
                    source_type = "snapshot"
                    source_path = str(snap_path.resolve())
                    rs232_valid = True
                elif pid is not None:
                    app, window = attach_mmwave_studio(pid=pid, title_regex=title_regex, probe_dir=probe_dir, verbose_log=vlog)
                    device_status = connection_gate(window, vlog)
                    rs232_valid = device_status.get("gate_passed", False)
                    
                    snap_path = probe_dir / f"{run_id}_preflight_cfg_snapshot.txt"
                    dump_output_snapshot(window, vlog, snap_path)
                    
                    if snap_path.exists():
                        doc_text = snap_path.read_text(encoding="utf-8")
                        source_path = str(snap_path)
                
                audit_obj = audit_session(doc_text, rs232_valid=rs232_valid, source_type=source_type, source_path=source_path)
                passed, reasons = preflight_config(audit_obj)
            
            if not passed:
                console.print(f"\n[red]CONFIG_PREFLIGHT_FAILED_REQUIRES_CLEAN_SESSION[/red]")
                for r in reasons:
                    console.print(f"  [red]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {r}[/red]")
                if not force:
                    console.print("[red]Refusing to generate script. Use --force to override.[/red]")
                    raise typer.Exit(1)
                else:
                    console.print("[yellow]--force specified. Generating script despite failed preflight.[/yellow]")
            else:
                console.print(f"[green]CONFIG_PREFLIGHT_PASSED[/green]")
                
        except RuntimeError as e:
            console.print(f"[red][FAIL] {e}[/red]")
            if not force:
                raise typer.Exit(1)
    else:
        console.print("[yellow]" + "=" * 70 + "[/yellow]")
        console.print("[yellow]WARNING: NO PREFLIGHT WAS RUN.[/yellow]")
        console.print("[yellow]Only use this after a successful firmware-power-script.[/yellow]")
        console.print("[yellow]Use --pid <PID> for automatic session safety checks.[/yellow]")
        console.print("[yellow]" + "=" * 70 + "[/yellow]\n")
    
    lua_path = probe_dir / f"{run_id}_smoke_known_awr2944.lua"
    
    generated = generate_smoke_known_awr2944(run_id, lua_path)
    lua_path.write_text(generated.script, encoding="utf-8")
    
    result_path = probe_dir / f"{run_id}_smoke_known_awr2944_result.json"
    result_path.write_text(json.dumps(generated.metadata, indent=2), encoding="utf-8")
    
    for w in generated.metadata.get("warnings", []):
        console.print(f"[yellow]WARNING: {w}[/yellow]")
    
    console.print(f"\n[bold]NOTE:[/bold] GUI-derived AWR2944 frozen smoke config. Replay-validated on this local setup; keep frozen unless revalidated.")
    console.print(f"[cyan]Generated script:[/cyan] {lua_path}")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{lua_path.resolve()}]])[/green]")


@mmws_post_app.command("print-known-awr2944-commands")
def mmws_post_print_known_awr2944_commands() -> None:
    """Print the exact frozen GUI-derived AWR2944 command list."""
    from .legacy_mmws.post_connect import VALIDATED_AWR2944_SMOKE_V0
    
    console.print("[bold]Frozen GUI-Derived AWR2944 Commands:[/bold]")
    console.print("[dim]These are the EXACT strings that smoke-from-known-awr2944 emits.[/dim]\n")
    for i, cmd in enumerate(VALIDATED_AWR2944_SMOKE_V0.commands, 1):
        console.print(f"  {i:2d}. ar1.{cmd}")


@mmws_post_app.command("verify-known-script")
def mmws_post_verify_known_script(
    script: str = typer.Option(..., "--script", help="Path to the generated Lua script to verify"),
) -> None:
    """Verify a generated Lua script against the frozen AWR2944 command list.
    
    Checks that every frozen command appears in an executable (non-comment)
    line, and that no known bad patterns appear.
    """
    from .legacy_mmws.post_connect import VALIDATED_AWR2944_SMOKE_V0, _KNOWN_BAD_PATTERNS
    
    script_path = Path(script)
    if not script_path.exists():
        console.print(f"[red]Script not found: {script_path}[/red]")
        raise typer.Exit(1)
    
    text = script_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    
    # Filter to executable lines (non-comment, non-empty)
    exec_lines = [l for l in lines if l.strip() and not l.strip().startswith("--")]
    exec_text = "\n".join(exec_lines)
    
    errors: list[str] = []
    
    # Check frozen commands present in executable lines
    for cmd_line in VALIDATED_AWR2944_SMOKE_V0.commands:
        expected = f"ar1.{cmd_line}"
        if expected not in exec_text:
            errors.append(f"MISSING frozen command: ar1.{cmd_line}")
    
    # Check bad patterns absent from executable lines
    for bad in _KNOWN_BAD_PATTERNS:
        if bad in exec_text:
            errors.append(f"BAD PATTERN found: {bad}")
    
    if errors:
        console.print(f"\n[red]VERIFY FAILED ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â {len(errors)} error(s):[/red]")
        for e in errors:
            console.print(f"  [red]ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â {e}[/red]")
        raise typer.Exit(1)
    else:
        console.print(f"[green]VERIFY PASSED ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â all {len(_AWR2944_GUI_DERIVED_COMMAND_LINES)} frozen commands present, no bad patterns.[/green]")


_CRITICAL_CMDS = {
    "firmware_power": {"DownloadBSSFw", "DownloadMSSFw", "PowerOn", "RfEnable"},
    "smoke_known_awr2944": {"ChanNAdcConfig", "LPModConfig", "RfLdoBypassConfig", "SetCalMonFreqLimitConfig", "SetRFDeviceConfig", "RfSetCalMonFreqTxPowLimitConfig", "SetApllSynthBWCtlConfig", "RfInit", "DataPathConfig", "LVDSLaneConfig", "ProfileConfig", "ChirpConfig", "FrameConfig"},
}
_CRITICAL_CMDS["smoke_from_extracted"] = _CRITICAL_CMDS["smoke_known_awr2944"]
_CRITICAL_CMDS["smoke_config"] = _CRITICAL_CMDS["smoke_known_awr2944"]

def _is_cmd_successful(cmd: str, stage: str, ret: Any, ok: bool) -> bool:
    if not ok:
        return False
    if ret in (0, None, "null", ""):
        return True
    try:
        ret_val = float(ret)
        if ret_val != 0.0:
            crits = _CRITICAL_CMDS.get(stage, set())
            if cmd in crits:
                return False
    except (ValueError, TypeError):
        pass # String returns like version with ok=True are successful
    return True


@mmws_post_app.command("check-run")
def mmws_post_check_run(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to look up"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    """Look up result and progress files for a run ID and summarize them."""
    check_run_impl(run_id, probe_dir)

def check_run_impl(run_id: str, probe_dir: str = None) -> None:

    import json
    
    probe_dir = _lua_launch_probe_dir(probe_dir)
    
    # Check for manifest first
    manifest_path = probe_dir / f"{run_id}_manifest.json"
    result_files = []
    progress_files = []
    stage = "unknown"
    
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stage = manifest.get("stage", "unknown")
        if "result_path" in manifest:
            rp = Path(manifest["result_path"])
            if rp.exists():
                result_files.append(rp)
        if "progress_path" in manifest:
            pp = Path(manifest["progress_path"])
            if pp.exists():
                progress_files.append(pp)
    else:
        # Fallback to globbing
        result_files = sorted(probe_dir.glob(f"{run_id}_*_result.json")) + sorted(probe_dir.glob(f"{run_id}_*result.json"))
        progress_files = sorted(probe_dir.glob(f"{run_id}_*_progress.jsonl")) + sorted(probe_dir.glob(f"{run_id}_*progress.jsonl"))
        
        result_files = sorted(set(result_files))
        progress_files = sorted(set(progress_files))
        
        ref_file = result_files[0] if result_files else (progress_files[0] if progress_files else None)
        if ref_file:
            fname = ref_file.stem
            if "firmware_power" in fname:
                stage = "firmware_power"
            elif "smoke_known_awr2944" in fname:
                stage = "smoke_known_awr2944"
            elif "smoke_from_extracted" in fname:
                stage = "smoke_from_extracted"
            elif "smoke_config" in fname:
                stage = "smoke_config"
            elif "session_audit" in fname:
                stage = "session_audit"
            elif "ar1_help" in fname:
                stage = "ar1_help_probe"
    
    console.print(f"\n[bold]Run Summary (run_id: {run_id}):[/bold]")
    console.print(f"  Stage: {stage}")
    
    # Parse result JSON
    if result_files:
        rpath = result_files[0]
        console.print(f"  Result file: {rpath.name}")
        try:
            res = json.loads(rpath.read_text(encoding="utf-8"))
            success = res.get("success", "?")
            error = res.get("error", "")
            warnings = res.get("warnings", [])
            
            color = "green" if success else "red"
            console.print(f"  Success: [{color}]{success}[/{color}]")
            if error:
                console.print(f"  Error: [red]{error}[/red]")
            if warnings:
                console.print(f"  Warnings ({len(warnings)}):")
                for w in warnings:
                    console.print(f"    [yellow]ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {w}[/yellow]")
        except Exception as e:
            console.print(f"  [red]Failed to parse result: {e}[/red]")
    else:
        console.print(f"  Result file: [yellow]not found[/yellow]")
    
    # Parse progress JSONL
    if progress_files:
        ppath = progress_files[0]
        console.print(f"  Progress file: {ppath.name}")
        try:
            plines = ppath.read_text(encoding="utf-8").strip().splitlines()
            first_fail = None
            console.print(f"\n  [bold]Command Returns ({len(plines)} entries):[/bold]")
            for pl in plines:
                try:
                    entry = json.loads(pl)
                    cmd = entry.get("cmd", "?")
                    ret = entry.get("ret")
                    ok = entry.get("ok", True)
                    err = entry.get("err")
                    
                    if _is_cmd_successful(cmd, stage, ret, ok):
                        console.print(f"    {cmd}: ret={ret} [green]ok[/green]")
                    else:
                        console.print(f"    {cmd}: ret={ret} [red]FAIL[/red]" + (f" err={err}" if err else ""))
                        if first_fail is None:
                            first_fail = cmd
                except json.JSONDecodeError:
                    console.print(f"    [dim]{pl[:80]}[/dim]")
            
            if first_fail:
                console.print(f"\n  [red]First failed command: {first_fail}[/red]")
        except Exception as e:
            console.print(f"  [red]Failed to parse progress: {e}[/red]")
    else:
        console.print(f"  Progress file: [yellow]not found[/yellow]")


@mmws_post_app.command("watch-run")
def mmws_post_watch_run(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to watch"),
    timeout: int = typer.Option(180, "--timeout", help="Timeout in seconds to wait for result"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    """Watch a Lua run's progress and wait for its completion."""
    watch_run_impl(run_id, timeout, probe_dir)

def watch_run_impl(run_id: str, timeout: int, probe_dir: str = None) -> None:

    import json
    import time
    import sys
    from .legacy_mmws.post_connect import load_run_result
    
    probe_dir_path = _lua_launch_probe_dir(probe_dir)
    manifest_path = probe_dir_path / f"{run_id}_manifest.json"
    
    stage = "unknown"
    result_path = None
    progress_path = None
    
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stage = manifest.get("stage", "unknown")
        result_path = Path(manifest["result_path"]) if "result_path" in manifest else None
        progress_path = Path(manifest["progress_path"]) if "progress_path" in manifest else None
        
        # If the script hasn't started writing yet, print the dofile
        if (not result_path or not result_path.exists()) and (not progress_path or not progress_path.exists()):
            dofile_cmd = manifest.get("dofile", f"dofile([[{manifest.get('lua_path', '')}]])")
            console.print("[yellow]Script execution has not started yet.[/yellow]")
            console.print("Paste this into mmWave Studio Lua Shell:")
            console.print(f"[green]{dofile_cmd}[/green]\n")
    else:
        # Fallback globs
        result_files = sorted(probe_dir_path.glob(f"{run_id}_*result.json"))
        progress_files = sorted(probe_dir_path.glob(f"{run_id}_*progress.jsonl"))
        if result_files:
            result_path = result_files[0]
        if progress_files:
            progress_path = progress_files[0]
            stage = progress_path.stem.replace(f"{run_id}_", "").replace("_progress", "")
    
    if not result_path and not progress_path:
        console.print(f"[red]No manifest, result, or progress files found for run_id: {run_id}[/red]")
        raise typer.Exit(1)
        
    console.print(f"[bold]Watching run: {run_id}[/bold] (stage: {stage})")
    console.print(f"Waiting up to {timeout}s for completion...\n")
    
    start_time = time.time()
    last_pos = 0
    
    while time.time() - start_time < timeout:
        # Read new progress lines
        if progress_path and progress_path.exists():
            with open(progress_path, "r", encoding="utf-8") as f:
                f.seek(last_pos)
                new_lines = f.readlines()
                last_pos = f.tell()
                
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        cmd = entry.get("cmd", "?")
                        ret = entry.get("ret")
                        ok = entry.get("ok", True)
                        
                        if _is_cmd_successful(cmd, stage, ret, ok):
                            console.print(f"  {cmd}: [green]ok[/green]")
                        else:
                            console.print(f"  {cmd}: [red]FAIL (ret={ret})[/red]")
                    except json.JSONDecodeError:
                        pass
        
        # Check result
        if result_path and result_path.exists():
            try:
                res = json.loads(result_path.read_text(encoding="utf-8"))
                # If success field exists, the script finished
                if "success" in res:
                    success = res["success"]
                    error = res.get("error", "")
                    console.print(f"\n[bold]Run Completed:[/bold] {'[green]Success[/green]' if success else '[red]Failed[/red]'}")
                    if error:
                        console.print(f"[red]Error: {error}[/red]")
                    sys.exit(0 if success else 1)
            except (json.JSONDecodeError, IOError):
                pass # Wait for atomic write or retry
                
        time.sleep(1.0)
        
    # Final reconciliation before timeout
    res = load_run_result(run_id, probe_dir_path)
    if res.exists:
        console.print(f"\n[bold]Run Completed (Reconciled after timeout):[/bold] {'[green]Success[/green]' if res.success else '[red]Failed[/red]'}")
        if res.error:
            console.print(f"[red]Error: {res.error}[/red]")
        sys.exit(0 if res.success else 1)
        
    console.print("\n[red]Timeout reached waiting for result.[/red]")
    raise typer.Exit(1)


@mmws_post_app.command("summarize-session")
def mmws_post_summarize_session(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    """Summarize a post-connection session (firmware + config runs)."""
    summarize_session_impl(firmware_run_id, config_run_id, probe_dir)

def summarize_session_impl(firmware_run_id: str, config_run_id: str, probe_dir: str = None) -> None:

    import json
    
    probe_dir_path = _lua_launch_probe_dir(probe_dir)
    
    def _read_result(rid: str) -> dict[str, Any]:
        manifest_path = probe_dir_path / f"{rid}_manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                rp = Path(manifest.get("result_path", ""))
                if rp.exists():
                    return json.loads(rp.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        # Fallback to glob
        result_files = sorted(probe_dir_path.glob(f"{rid}_*result.json"))
        if result_files:
            return json.loads(result_files[0].read_text(encoding="utf-8"))
        return {}

    fw_res = _read_result(firmware_run_id)
    cfg_res = _read_result(config_run_id)
    
    fw_ok = fw_res.get("success") is True
    cfg_ok = cfg_res.get("success") is True
    
    console.print("\n[bold]Session Summary[/bold]")
    console.print("=" * 40)
    console.print(f"Firmware Run  ({firmware_run_id}): {'[green]VALIDATED[/green]' if fw_ok else '[red]FAILED/UNKNOWN[/red]'}")
    console.print(f"Config Run    ({config_run_id}): {'[green]VALIDATED[/green]' if cfg_ok else '[red]FAILED/UNKNOWN[/red]'}")
    console.print("=" * 40)
    
    post_conn_ok = fw_ok and cfg_ok
    console.print(f"\npost_connection_config_validated: {'[green]true[/green]' if post_conn_ok else '[red]false[/red]'}")
    
    warnings = fw_res.get("warnings", []) + cfg_res.get("warnings", [])
    if warnings:
        console.print(f"\n[yellow]Warnings ({len(warnings)}):[/yellow]")
        for w in warnings:
            console.print(f"  ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢ {w}")
            
    console.print("\n[bold]recommended_next_stage:[/bold] configuration hardening / Python wrapper")


@mmws_post_app.command("smoke-config-script")
def mmws_post_smoke_config_script(
    config: str = typer.Option(None, "--config", help="Path to capture.yaml to override TI baselines"),
    write_template: str = typer.Option(None, "--write-template", help="Dump the resolved YAML to this path instead of generating Lua"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """[DEPRECATED] Generate smoke config using guessed TI baselines.
    
    WARNING: The guessed TI-baseline arguments have incorrect signatures for
    AWR2944 (e.g. ChanNAdcConfig takes 11 args, not 10).
    Use 'smoke-from-known-awr2944' or 'generate-smoke-from-extracted' instead.
    """
    from .legacy_mmws.post_connect import generate_smoke_config_script
    import uuid
    import yaml
    
    console.print("[red][DEPRECATED] This command uses experimental guessed baselines.[/red]")
    console.print("[red]Not recommended for AWR2944 until validated.[/red]")
    console.print("[yellow]Use 'smoke-from-known-awr2944' or 'generate-smoke-from-extracted' instead.[/yellow]\n")
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir = _lua_launch_probe_dir()
    
    lua_path = probe_dir / f"{run_id}_smoke_config.lua"
    
    script, result = generate_smoke_config_script(run_id, config, lua_path)
    
    if write_template:
        out_path = Path(write_template)
        dump_data = {
            "radar_device": "awr2944",
            "profile": {
                "freq_slope_const": 29.982,
                "num_adc_samples": 256,
                "adc_sample_rate": 10000
            },
            "_resolved_args": result["args"]
        }
        out_path.write_text(yaml.dump(dump_data, sort_keys=False), encoding="utf-8")
        console.print(f"[green]Wrote resolved template to {out_path}[/green]")
        return
        
    lua_path.write_text(script, encoding="utf-8")
    
    for w in result.get("warnings", []):
        console.print(f"[yellow]WARNING: {w}[/yellow]")
        
    console.print(f"[cyan]Generated smoke config script:[/cyan] {lua_path}")
    console.print(f"Source: {result['source']}")
    console.print(f"Paste this command into the mmWave Studio Lua Shell:")
    console.print(f"[green]dofile([[{lua_path.resolve()}]])[/green]")


@mmws_post_app.command("dca-preflight")
def mmws_post_dca_preflight() -> None:
    """[STUB] Check DCA1000 network connectivity and configuration."""
    console.print("[yellow]STUB: dca-preflight not yet implemented.[/yellow]")
    
@mmws_post_app.command("capture-smoke-script")
def mmws_post_capture_smoke_script() -> None:
    """[STUB] Generate Lua script for a minimal capture smoke test."""
    console.print("[yellow]STUB: capture-smoke-script not yet implemented.[/yellow]")

@mmws_post_app.command("parse-smoke-bin")
def mmws_post_parse_smoke_bin() -> None:
    """[STUB] Parse the raw .bin file from the smoke test capture."""
    console.print("[yellow]STUB: parse-smoke-bin not yet implemented.[/yellow]")


@mmws_post_app.command("record-validation")
def mmws_post_record_validation(
    firmware_run_id: str = typer.Option(..., "--firmware-run-id", help="Run ID of the firmware sequence"),
    config_run_id: str = typer.Option(..., "--config-run-id", help="Run ID of the config sequence"),
    label: str = typer.Option(..., "--label", help="Notes or label for this validation record"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    """Record a successful full post-connection validation."""
    record_validation_impl(firmware_run_id, config_run_id, label, probe_dir)

def record_validation_impl(firmware_run_id: str, config_run_id: str, label: str, probe_dir: str = None) -> None:
    import json
    import time
    import datetime
    
    probe_dir = _lua_launch_probe_dir(probe_dir)
    
    def _read_result(rid: str) -> dict[str, Any]:
        manifest_path = probe_dir / f"{rid}_manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            rp = Path(manifest.get("result_path", ""))
            if rp.exists():
                return json.loads(rp.read_text(encoding="utf-8"))
        # Fallback to glob
        result_files = sorted(probe_dir.glob(f"{rid}_*result.json"))
        if result_files:
            return json.loads(result_files[0].read_text(encoding="utf-8"))
        return {}

    fw_res = _read_result(firmware_run_id)
    cfg_res = _read_result(config_run_id)
    
    fw_ok = fw_res.get("success") is True
    cfg_ok = cfg_res.get("success") is True
    
    record = {
        "timestamp_iso": datetime.datetime.now().isoformat(),
        "timestamp_epoch": time.time(),
        "label": label,
        "firmware_run_id": firmware_run_id,
        "config_run_id": config_run_id,
        "post_connection_config_validated": fw_ok and cfg_ok,
        "firmware_result": fw_res,
        "config_result": cfg_res,
    }
    
    # Try to get git commit
    try:
        import subprocess
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        record["git_commit"] = git_commit
    except Exception:
        pass
        
    ts_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    record_path = probe_dir / f"validation_{ts_str}.json"
    
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    
    console.print(f"[green]Validation record written to: {record_path}[/green]")


@mmws_post_app.command("list-validations")
def mmws_post_list_validations() -> None:
    """List all recorded validation runs."""
    import json
    
    probe_dir = _lua_launch_probe_dir()
    records = sorted(probe_dir.glob("validation_*.json"))
    
    if not records:
        console.print("[yellow]No validation records found.[/yellow]")
        return
        
    console.print("[bold]Recorded Validations:[/bold]")
    for rec_path in records:
        try:
            rec = json.loads(rec_path.read_text(encoding="utf-8"))
            label = rec.get("label", "none")
            fw_id = rec.get("firmware_run_id", "?")
            cfg_id = rec.get("config_run_id", "?")
            valid = rec.get("post_connection_config_validated", False)
            color = "green" if valid else "red"
            ts = rec.get("timestamp_iso", rec_path.stem.replace("validation_", ""))
            commit = rec.get("git_commit", "")
            commit_str = f" [dim]({commit[:7]})[/dim]" if commit else ""
            
            console.print(f"  [{color}]{ts}[/{color}] - {label}{commit_str}")
            console.print(f"    Firmware: {fw_id} | Config: {cfg_id} | Valid: [{color}]{valid}[/{color}]")
        except Exception:
            console.print(f"  [dim]{rec_path.name} (failed to parse)[/dim]")


@mmws_post_app.command("frozen-config-inspect")
def mmws_post_frozen_config_inspect(
    format: str = typer.Option("text", "--format", help="Output format: text or json")
) -> None:
    """Print the frozen AWR2944 config in grouped, human-readable form."""
    from .legacy_mmws.post_connect import VALIDATED_AWR2944_SMOKE_V0
    from .legacy_mmws.config_parser import parse_ar1_call
    import json
    
    parsed_cmds = {parse_ar1_call(cmd)["name"]: parse_ar1_call(cmd) for cmd in VALIDATED_AWR2944_SMOKE_V0.commands}
    
    inspect_data = {
        "metadata": {
            "validation_status": "replay-validated locally",
            "firmware_run_id": VALIDATED_AWR2944_SMOKE_V0.firmware_run_id,
            "config_run_id": VALIDATED_AWR2944_SMOKE_V0.config_run_id,
            "git_commit": VALIDATED_AWR2944_SMOKE_V0.git_commit,
        },
        "groups": {
            "channel_adc": {
                "raw": parsed_cmds.get("ChanNAdcConfig", {}).get("raw", ""),
                "tx_enables": {"tx0": 1, "tx1": 1, "tx2": 0, "tx3": 0},
                "rx_enables": {"rx0": 1, "rx1": 1, "rx2": 0, "rx3": 0},
                "adc_bits_val": 2,
                "adc_fmt_val": 0,
                "iq_swap": 0
            },
            "low_power": {
                "raw": parsed_cmds.get("LPModConfig", {}).get("raw", ""),
                "lp_adc_mode": "0, 0 (needs confirmation)"
            },
            "rf_static": {
                "RfLdoBypassConfig": parsed_cmds.get("RfLdoBypassConfig", {}).get("raw", ""),
                "SetCalMonFreqLimitConfig": parsed_cmds.get("SetCalMonFreqLimitConfig", {}).get("raw", ""),
                "SetRFDeviceConfig": parsed_cmds.get("SetRFDeviceConfig", {}).get("raw", ""),
                "RfSetCalMonFreqTxPowLimitConfig": parsed_cmds.get("RfSetCalMonFreqTxPowLimitConfig", {}).get("raw", ""),
                "SetApllSynthBWCtlConfig": parsed_cmds.get("SetApllSynthBWCtlConfig", {}).get("raw", "")
            },
            "rf_init": {
                "raw": parsed_cmds.get("RfInit", {}).get("raw", "")
            },
            "data_path": {
                "DataPathConfig": parsed_cmds.get("DataPathConfig", {}).get("raw", ""),
                "LVDSLaneConfig": parsed_cmds.get("LVDSLaneConfig", {}).get("raw", "")
            },
            "sensor_profile": {
                "raw": parsed_cmds.get("ProfileConfig", {}).get("raw", ""),
                "profile_id": 0,
                "start_freq_ghz": 77,
                "idle_time_us": 100,
                "adc_start_time_us": 6,
                "ramp_end_time_us": 60,
                "freq_slope_mhz_per_us": 29.982,
                "num_adc_samples": 256,
                "sample_rate_ksps": 10000,
                "rx_gain": 30
            },
            "chirp_frame": {
                "ChirpConfig": parsed_cmds.get("ChirpConfig", {}).get("raw", ""),
                "FrameConfig": parsed_cmds.get("FrameConfig", {}).get("raw", ""),
                "chirp_start_end": "0, 0",
                "enabled_tx_in_chirp": {"tx0": 1, "tx1": 1, "tx2": 0, "tx3": 0},
                "frame_count": 8,
                "loop_count": 128,
                "periodicity_ms": 40,
                "trigger_select": 1
            }
        }
    }
    
    if format == "json":
        print(json.dumps(inspect_data, indent=2))
        return
        
    console.print("[bold]Frozen Config Inspection[/bold]\n")
    console.print(f"Validation status: {inspect_data['metadata']['validation_status']}")
    console.print(f"Firmware run ID: {inspect_data['metadata']['firmware_run_id']}")
    console.print(f"Config run ID: {inspect_data['metadata']['config_run_id']}")
    console.print(f"Git commit: {inspect_data['metadata']['git_commit']}\n")
    
    for group_name, group_data in inspect_data["groups"].items():
        console.print(f"[cyan]--- {group_name.upper()} ---[/cyan]")
        for k, v in group_data.items():
            if isinstance(v, dict):
                v_str = ", ".join(f"{sk}={sv}" for sk, sv in v.items())
                console.print(f"  {k}: {v_str}")
            else:
                console.print(f"  {k}: {v}")
        console.print("")


@mmws_post_app.command("frozen-config-explain")
def mmws_post_frozen_config_explain(
    format: str = typer.Option("text", "--format", help="Output format: text or json")
) -> None:
    """Explain each frozen ar1 command."""
    from .legacy_mmws.post_connect import VALIDATED_AWR2944_SMOKE_V0, AWR2944_ARG_COUNTS
    from .legacy_mmws.config_parser import parse_ar1_call
    import json
    
    explanations = []
    
    # Simple hardcoded argument names for explain based on standard signatures
    arg_names = {
        "ChanNAdcConfig": ["Tx0En", "Tx1En", "Tx2En", "Tx3En", "Rx0En", "Rx1En", "Rx2En", "Rx3En", "BitsVal", "FmtVal", "IQSwap"],
        "ChirpConfig": ["ChirpStartIdx", "ChirpEndIdx", "ProfileId", "StartFreqVar", "FreqSlopeVar", "IdleTimeVar", "AdcStartVar", "Tx0En", "Tx1En", "Tx2En", "Tx3En"],
        "FrameConfig": ["ChirpStartIdx", "ChirpEndIdx", "FrameCount", "LoopCount", "Periodicity", "TriggerDelay", "TriggerSelect"],
        "ProfileConfig": ["ProfileId", "StartFreq", "IdleTime", "AdcStartTime", "RampEndTime", "TxOutPower", "TxPhaseShifter", "FreqSlopeConst", "TxStartTime", "NumAdcSamples", "DigOutSampleRate", "HpfCornerFreq1", "HpfCornerFreq2", "RxGain"]
    }
    
    for cmd_str in VALIDATED_AWR2944_SMOKE_V0.commands:
        parsed = parse_ar1_call(cmd_str)
        name = parsed["name"]
        expected = AWR2944_ARG_COUNTS.get(name, -1)
        
        args_decoded = {}
        names = arg_names.get(name, [])
        for i, val in enumerate(parsed["args"]):
            arg_n = names[i] if i < len(names) else f"arg{i+1} (unknown/needs confirmation)"
            args_decoded[arg_n] = val
            
        explanations.append({
            "command": name,
            "raw": cmd_str,
            "arg_count": parsed["arg_count"],
            "expected_arg_count": expected,
            "args_decoded": args_decoded
        })
        
    if format == "json":
        print(json.dumps(explanations, indent=2))
        return
        
    for exp in explanations:
        console.print(f"[bold]{exp['command']}:[/bold]")
        console.print(f"  expected args: {exp['expected_arg_count']}")
        console.print(f"  actual args: {exp['arg_count']}")
        if exp["args_decoded"]:
            for k, v in exp["args_decoded"].items():
                console.print(f"  {k} = {v}")
        else:
            console.print("  (no args)")
        console.print("")


@mmws_post_app.command("validate-frozen-config")
def mmws_post_validate_frozen_config() -> None:
    """Validate that the frozen baseline is exactly correct and ordered."""
    from .legacy_mmws.post_connect import VALIDATED_AWR2944_SMOKE_V0, AWR2944_ARG_COUNTS
    from .legacy_mmws.config_parser import parse_ar1_call
    
    expected_order = [
        "ChanNAdcConfig", "LPModConfig", "RfLdoBypassConfig", "SetCalMonFreqLimitConfig",
        "SetRFDeviceConfig", "RfSetCalMonFreqTxPowLimitConfig", "SetApllSynthBWCtlConfig",
        "RfInit", "DataPathConfig", "LVDSLaneConfig", "ProfileConfig", "ChirpConfig", "FrameConfig"
    ]
    
    if len(VALIDATED_AWR2944_SMOKE_V0.commands) != len(expected_order):
        console.print(f"[red]FAIL: Baseline has {len(VALIDATED_AWR2944_SMOKE_V0.commands)} commands, expected {len(expected_order)}[/red]")
        raise typer.Exit(1)
        
    for i, (cmd_str, expected_name) in enumerate(zip(VALIDATED_AWR2944_SMOKE_V0.commands, expected_order)):
        parsed = parse_ar1_call(cmd_str)
        name = parsed["name"]
        
        if name != expected_name:
            console.print(f"[red]FAIL: Command {i+1} is {name}, expected {expected_name}[/red]")
            raise typer.Exit(1)
            
        expected_count = AWR2944_ARG_COUNTS.get(name)
        if expected_count is not None and parsed["arg_count"] != expected_count:
            console.print(f"[red]FAIL: {name} has {parsed['arg_count']} args, expected {expected_count}[/red]")
            raise typer.Exit(1)
            
    console.print("[green]Frozen config validation PASSED.[/green]")


@mmws_post_app.command("generate-config-variant")
def mmws_post_generate_config_variant(
    variant: str = typer.Option(..., "--variant", help="Variant to generate (e.g. tx0-only)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="MUST be provided. Dry run only."),
    format: str = typer.Option("text", "--format", help="Output format: text or json")
) -> None:
    """Generate a modified dry-run config variant."""
    from .legacy_mmws.post_connect import VALIDATED_AWR2944_SMOKE_V0, AWR2944_ARG_COUNTS
    from .legacy_mmws.config_parser import parse_ar1_call
    import json
    
    if not dry_run:
        console.print("[red]FAIL: --dry-run MUST be provided in Configuration Hardening v1.[/red]")
        raise typer.Exit(1)
        
    allowed_variants = ["tx0-only", "tx1-only", "tx0-tx1", "rx0-rx1-only", "all-rx", "samples-128", "samples-256"]
    if variant not in allowed_variants:
        console.print(f"[red]FAIL: Unknown variant '{variant}'. Allowed: {allowed_variants}[/red]")
        raise typer.Exit(1)
        
    # Copy baseline parsed cmds
    parsed_cmds = [parse_ar1_call(cmd) for cmd in VALIDATED_AWR2944_SMOKE_V0.commands]
    
    warnings = []
    
    def _find_cmd(name: str):
        for c in parsed_cmds:
            if c["name"] == name:
                return c
        return None
        
    chan = _find_cmd("ChanNAdcConfig")
    chirp = _find_cmd("ChirpConfig")
    prof = _find_cmd("ProfileConfig")
    frame = _find_cmd("FrameConfig")
    
    if not (chan and chirp and prof and frame):
        console.print("[red]FAIL: Missing critical commands in baseline.[/red]")
        raise typer.Exit(1)
        
    if variant == "tx0-only":
        chan["args"][0:4] = [1, 0, 0, 0]
        chirp["args"][7:11] = [1, 0, 0, 0]
    elif variant == "tx1-only":
        chan["args"][0:4] = [0, 1, 0, 0]
        chirp["args"][7:11] = [0, 1, 0, 0]
    elif variant == "tx0-tx1":
        chan["args"][0:4] = [1, 1, 0, 0]
        chirp["args"][7:11] = [1, 1, 0, 0]
        warnings.append("Multiple TX are enabled. TX power backoff is still 0 dB in the frozen config. This variant is dry-run only.")
    elif variant == "rx0-rx1-only":
        chan["args"][4:8] = [1, 1, 0, 0]
        warnings.append("RX enable count changed but DataPathConfig/LVDSLaneConfig are still frozen; hardware execution is not allowed until data-path implications are validated.")
    elif variant == "all-rx":
        chan["args"][4:8] = [1, 1, 1, 1]
        warnings.append("RX enable count changed but DataPathConfig/LVDSLaneConfig are still frozen; hardware execution is not allowed until data-path implications are validated.")
    elif variant == "samples-128":
        prof["args"][15] = 128
        warnings.append("numAdcSamples changed to 128. Downstream parser and capture scripts will need to expect smaller chunks.")
    elif variant == "samples-256":
        prof["args"][15] = 256
        
    # Rebuild strings
    modified_strings = []
    diffs = []
    
    for i, (orig_str, mod_cmd) in enumerate(zip(VALIDATED_AWR2944_SMOKE_V0.commands, parsed_cmds)):
        mod_str = f"{mod_cmd['name']}({', '.join(str(x) for x in mod_cmd['args'])})" if mod_cmd["args"] else f"{mod_cmd['name']}()"
        modified_strings.append(mod_str)
        
        if mod_str != orig_str:
            orig_parsed = parse_ar1_call(orig_str)
            arg_diffs = []
            for j, (o_a, m_a) in enumerate(zip(orig_parsed["args"], mod_cmd["args"])):
                if o_a != m_a:
                    arg_diffs.append(f"arg{j+1}: {o_a} -> {m_a}")
            diffs.append({"command": mod_cmd["name"], "original": orig_str, "modified": mod_str, "arg_diffs": arg_diffs})
            
    # Guardrails
    if sum(chan["args"][0:4]) == 0:
        console.print("[red]FAIL: No TX enabled.[/red]")
        raise typer.Exit(1)
    if sum(chan["args"][4:8]) == 0:
        console.print("[red]FAIL: No RX enabled.[/red]")
        raise typer.Exit(1)
        
    for cmd in parsed_cmds:
        expected = AWR2944_ARG_COUNTS.get(cmd["name"])
        if expected is not None and len(cmd["args"]) != expected:
            console.print(f"[red]FAIL: {cmd['name']} arg count mismatch: {len(cmd['args'])} != {expected}[/red]")
            raise typer.Exit(1)
            
    output = {
        "variant": variant,
        "warnings": warnings,
        "diffs": diffs,
        "modified_commands": modified_strings
    }
    
    if format == "json":
        print(json.dumps(output, indent=2))
        return
        
    console.print("\n[bold yellow]" + "="*60)
    console.print("HARDWARE EMISSION DISABLED.")
    console.print("This is a dry-run software-only variant.")
    console.print("Do not paste these commands into mmWave Studio unless a future")
    console.print("validation step explicitly enables hardware emission.")
    console.print("="*60 + "[/bold yellow]\n")
    
    if warnings:
        for w in warnings:
            console.print(f"[yellow]WARNING: {w}[/yellow]")
        console.print("")
        
    if not diffs:
        console.print("No changes from baseline.")
    else:
        for d in diffs:
            console.print(f"[bold]{d['command']}:[/bold]")
            for ad in d["arg_diffs"]:
                console.print(f"  {ad}")
        
    console.print("\n[green]Signature validation passed.[/green]")


@mmws_post_app.command("list-windows")
def mmws_post_list_windows() -> None:
    """List candidate mmWave Studio processes and their window states."""
    from .legacy_mmws.gui_connect import _get_powershell_candidates, _is_strong_candidate
    from rich.table import Table
    
    candidates = _get_powershell_candidates()
    
    table = Table(title="Candidate mmWave Studio Processes")
    table.add_column("PID", justify="right", style="cyan")
    table.add_column("Process Name", style="magenta")
    table.add_column("Window Handle", justify="right", style="green")
    table.add_column("Window Title", style="yellow")
    table.add_column("Responding", style="blue")
    table.add_column("Strong", style="red")
    
    if not candidates:
        console.print("[yellow]No candidate mmWave Studio processes found.[/yellow]")
        return
        
    for c in candidates:
        pid = str(c.get("Id", ""))
        name = str(c.get("ProcessName", ""))
        handle = str(c.get("MainWindowHandle", ""))
        title = str(c.get("MainWindowTitle", ""))
        resp = str(c.get("Responding", ""))
        strong = str(_is_strong_candidate(c))
        table.add_row(pid, name, handle, title, resp, strong)
        
    console.print(table)


@mmws_post_app.command("uia-probe")
def mmws_post_uia_probe(
    pid: int = typer.Option(..., "--pid", help="PID to probe"),
) -> None:
    """Diagnostic probe: test UIA attach strategies for a specific PID.

    Read-only: no UIA control interaction, no Lua, no ar1 calls.
    Calls the same internal attach functions used by guided-validate
    but in diagnostic mode, printing strategy results.
    """
    import json as _json
    from .legacy_mmws.gui_connect import uia_probe

    vlog = lambda m: console.print(f"  [dim]{m}[/dim]")
    console.print(f"[cyan]UIA Probe for PID={pid}[/cyan]\n")

    results = uia_probe(pid, verbose_log=vlog)

    # Print PowerShell candidate
    cand = results.get("ps_candidate")
    if cand:
        console.print(f"[green]PowerShell candidate found:[/green]")
        console.print(f"  PID={cand.get('Id')}  Name={cand.get('ProcessName')}")
        console.print(f"  MainWindowHandle={cand.get('MainWindowHandle')}")
        console.print(f"  MainWindowTitle={cand.get('MainWindowTitle')!r}")
        console.print(f"  Responding={cand.get('Responding')}")
    else:
        console.print(f"[red]PID={pid} not found in PowerShell candidates[/red]")

    console.print(f"\n[cyan]Resolved hwnd={results.get('hwnd')}[/cyan]\n")

    # Print strategy results
    for key, strat in results.get("strategies", {}).items():
        method = strat.get("method", key)
        console.print(f"[bold]{method}[/bold]")
        if strat.get("skipped"):
            console.print(f"  [yellow]Skipped: {strat['skipped']}[/yellow]")
        elif strat.get("connected") is True:
            console.print(f"  [green]Connected: True[/green]")
            console.print(f"  Window count: {strat.get('window_count', 0)}")
            for w in strat.get("windows", []):
                console.print(f"    text={w['text']!r}  handle={w['handle']}")
        elif "exists" in strat:
            console.print(f"  exists={strat['exists']}")
            if strat.get("text"):
                console.print(f"  text={strat['text']!r}")
        elif strat.get("connected") is False:
            console.print(f"  [red]Connected: False[/red]")
            console.print(f"  Error: {strat.get('error', 'unknown')}")
        console.print()

    if results.get("error"):
        console.print(f"[red]Error: {results['error']}[/red]")


@mmws_post_app.command("manual-status-probe")
def mmws_post_manual_status_probe(
    pid: int = typer.Option(..., "--pid", help="PID of mmWave Studio"),
    title_regex: str = typer.Option(None, "--title-regex", help="Regex for window title"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override probe directory"),
) -> None:
    """Diagnostic probe: test Device Status extraction from mmWave Studio.

    Read-only: no clicks, no Lua, no ar1, no firmware.
    Calls the same status extraction path used by manual-check in guided-validate.
    """
    from pathlib import Path as _Path
    from .legacy_mmws.gui_connect import attach_mmwave_studio, manual_status_probe

    pd = _Path(probe_dir) if probe_dir else _Path("ti") / "probe_logs"
    vlog = lambda m: console.print(f"  [dim]{m}[/dim]")

    console.print(f"[cyan]Manual Status Probe for PID={pid}[/cyan]\n")

    try:
        app, window = attach_mmwave_studio(
            pid=pid, title_regex=title_regex, probe_dir=pd, verbose_log=vlog
        )
    except RuntimeError as e:
        console.print(f"[red]Attach failed: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]Attached to: {window.window_text()!r}  handle={window.handle}[/green]\n")

    results = manual_status_probe(window, probe_dir=pd, verbose_log=vlog)

    # Print summary
    console.print(f"[bold]RadarAPI (frmAR1Main) found:[/bold] {results.get('radarapi_found')}")
    console.print(f"[bold]m_ConsoleText found:[/bold] {results.get('console_text_found')}")
    console.print(f"[bold]Console text length:[/bold] {results.get('console_text_length')}")

    ds = results.get("device_status", {})
    console.print(f"\n[bold]Device Status raw:[/bold] {ds.get('raw_text')!r}")
    console.print(f"[bold]Device Status valid:[/bold] {ds.get('valid')}")

    console.print(f"\n[bold]RS232 status:[/bold] {results.get('rs232_status_raw')!r}")
    console.print(f"[bold]SPI status:[/bold] {results.get('spi_status_raw')!r}")
    console.print(f"[bold]Device Status label:[/bold] {results.get('device_status_label_raw')!r}")

    ext = results.get("extraction", {})
    console.print(f"\n[bold]Extraction source:[/bold] {ext.get('extraction_source', 'none')}")
    console.print(f"[bold]Descendants searched:[/bold] {ext.get('descendants_searched')}")

    # Last 30 lines of console text
    last_lines = results.get("console_text_last_30_lines", [])
    if last_lines:
        console.print(f"\n[bold]Last {len(last_lines)} lines of m_ConsoleText:[/bold]")
        for line in last_lines:
            console.print(f"  {line}")

    # Matching descendants
    matching = results.get("matching_descendants", [])
    if matching:
        console.print(f"\n[bold]Matching descendants ({len(matching)}):[/bold]")
        for md in matching[:30]:
            if "error" in md:
                console.print(f"  [red]<error: {md['error']}>[/red]")
            else:
                console.print(f"  auto_id={md['automation_id']!r}  name={md['name']!r}  text={md['text']!r}")
        if len(matching) > 30:
            console.print(f"  ... and {len(matching) - 30} more")

    console.print(f"\n[bold]Diagnostic file:[/bold] {results.get('diagnostic_file')}")

    if missing:
        console.print(f"\n[yellow]Missing controls:[/yellow]")
        for m in missing:
            console.print(f"  {m}")


@mmws_post_app.command("guided-validate")
def mmws_post_guided_validate(
    label: str = typer.Option(..., "--label", help="Label for this validation run"),
    pid: int = typer.Option(None, "--pid", help="PID of mmWave Studio if running"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate the workflow without writing Lua or manifests"),
    timeout_firmware: int = typer.Option(180, "--timeout-firmware", help="Timeout for firmware run"),
    timeout_config: int = typer.Option(120, "--timeout-config", help="Timeout for config run"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
    assume_manual_connected: bool = typer.Option(False, "--assume-manual-connected",
        help="Bypass Device Status scrape; assume user has visually confirmed connection"),
) -> None:
    """Run the guided, ordered, strictly validated post-connection workflow."""
    from pathlib import Path
    
    if probe_dir is None:
        cwd = Path.cwd()
        if (cwd / "pyproject.toml").exists() or (cwd / ".git").exists():
            console.print(f"[red]ERROR: guided-validate was launched from the repository root.[/red]")
            console.print(f"\nThis command writes hardware-run artifacts and must be run from an experiment directory, or with an explicit --probe-dir.")
            console.print(f"\nCurrent directory appears to be:")
            console.print(f"{cwd.resolve()}")
            console.print(f"\nRefusing to continue to avoid writing run artifacts into the wrong ti/probe_logs folder.")
            console.print(f"\nUse one of:")
            console.print(f"  cd <project_dir>")
            console.print(f"  awr mmws post guided-validate --pid <PID> --label \"<label>\"")
            console.print(f"\nor:")
            console.print(f"  awr mmws post guided-validate --pid <PID> --label \"<label>\" --probe-dir C:\\...\\ti\\probe_logs\n")
            raise typer.Exit(1)
            
    from .legacy_mmws.guided_runner import run_guided_workflow
    run_guided_workflow(
        label=label,
        pid=pid,
        dry_run=dry_run,
        timeout_firmware=timeout_firmware,
        timeout_config=timeout_config,
        probe_dir=probe_dir,
        assume_manual_connected=assume_manual_connected,
    )


@mmws_post_app.command("guided-resume")
def mmws_post_guided_resume(
    state: str = typer.Option(..., "--state", help="Path to state JSON file to resume"),
    timeout_firmware: int = typer.Option(180, "--timeout-firmware", help="Timeout for firmware run"),
    timeout_config: int = typer.Option(120, "--timeout-config", help="Timeout for config run"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    """Resume an interrupted guided validation workflow."""
    from .legacy_mmws.guided_runner import resume_guided_workflow
    # probe_dir here is mainly for consistency if the user provides it, but resume gets it from state path.
    resume_guided_workflow(
        state_path=state,
        timeout_firmware=timeout_firmware,
        timeout_config=timeout_config,
    )

@mmws_post_app.command("failure-report")
def mmws_post_failure_report(
    latest: bool = typer.Option(False, "--latest", help="Scan for the most recent failure"),
    state: str = typer.Option(None, "--state", help="Path to specific guided state JSON"),
    run_id: str = typer.Option(None, "--run-id", help="Analyze specific run ID"),
    workflow_id: str = typer.Option(None, "--workflow-id", help="Analyze specific workflow ID"),
    since_minutes: int = typer.Option(30, "--since-minutes", help="Lookback window for latest failures"),
    format_type: str = typer.Option("text", "--format", help="Output format: text or json"),
    probe_dir: str = typer.Option(None, "--probe-dir", help="Override the directory where probe logs are written"),
) -> None:
    """Read-only diagnostic tool to detect and report workflow failures."""
    import json
    from .legacy_mmws.failure_report import generate_failure_report
    
    # "with no arguments, treat it as --latest"
    if not latest and not state and not run_id and not workflow_id:
        latest = True

    report = generate_failure_report(
        latest=latest,
        state_path=state,
        run_id=run_id,
        workflow_id=workflow_id,
        since_minutes=since_minutes,
        probe_dir_override=probe_dir,
    )
    
    if format_type.lower() == "json":
        print(json.dumps(report.to_dict()))
        return
        
    console.print("\n[bold]Failure Report[/bold]")
    console.print("=" * 14)
    console.print(f"type:                    {report.detected_failure_type}")
    console.print(f"primary_artifact:        {report.primary_artifact}")
    console.print(f"workflow_id:             {report.workflow_id}")
    console.print(f"run_id:                  {report.run_id}")
    console.print(f"stage:                   {report.current_stage}")
    
    if report.errors:
        console.print("errors:")
        for e in report.errors:
            console.print(f"  - {e}")
    else:
        console.print("errors:                  []")
        
    console.print(f"related_artifacts:       {report.related_artifacts}")
    console.print(f"orphan_artifacts:        {report.orphan_artifacts}")
    console.print(f"resume_safe:             {report.resume_safe}")
    console.print(f"hardware_likely_touched: {report.hardware_likely_touched}")
    console.print(f"power_cycle_required:    {str(report.power_cycle_required).lower()}")
    console.print(f"likely_root_cause:       {report.likely_root_cause}")
    console.print(f"recommended_next_action: {report.recommended_next_action}")
    console.print("")


# ===========================================================================
# DCA1000 Commands
# ===========================================================================

@dca_app.command("preflight")
def dca_preflight(
    host_ip: str = typer.Option("192.168.33.30", "--host-ip", help="PC static IP for DCA"),
    dca_ip: str = typer.Option("192.168.33.180", "--dca-ip", help="DCA1000 FPGA IP"),
    ping_only: bool = typer.Option(False, "--ping-only", help="Only run ping test"),
    format_type: str = typer.Option("text", "--format", help="Output format: text or json"),
) -> None:
    """Run read-only DCA1000 network preflight checks."""
    import json
    from .dca.preflight import run_dca_preflight
    
    report = run_dca_preflight(host_ip=host_ip, dca_ip=dca_ip, ping_only=ping_only)
    
    if format_type == "json":
        import dataclasses
        print(json.dumps(dataclasses.asdict(report), indent=2, default=str))
        if report.overall == "NOT_READY":
            sys.exit(1)
        return
        
    console.print(f"[bold]DCA1000 Preflight Report[/bold]")
    console.print("=" * 30)
    for check in report.checks:
        color = "green" if check.status == "PASS" else "yellow" if check.status == "WARN" else "red" if check.status == "FAIL" else "magenta"
        status_str = f"[{color}]{check.status:8}[/{color}]"
        console.print(f"{check.name:30} {status_str} ({check.detail})")
    
    overall_color = "green" if report.overall == "READY" else "yellow" if "WARN" in report.overall else "red"
    console.print(f"\nOverall: [{overall_color}]{report.overall}[/{overall_color}]")
    
    missing_ip = any(c.name.startswith(f"Adapter IP {host_ip}") and c.status == "FAIL" for c in report.checks)
    if missing_ip:
        try:
            from .dca.adapters import suggest_dca_adapter
            suggestion = suggest_dca_adapter()
            if suggestion:
                console.print(f"\n[cyan]Suggested DCA adapter: {suggestion.interface_alias}[/cyan]")
                console.print("[cyan]To configure:[/cyan]")
                console.print(f"[cyan]awr dca configure-adapter --interface \"{suggestion.interface_alias}\" --dry-run[/cyan]")
                console.print(f"[cyan]awr dca configure-adapter --interface \"{suggestion.interface_alias}\" --yes[/cyan]")
        except ImportError:
            pass
            
    if report.overall == "NOT_READY":
        sys.exit(1)


# @dca_app.command("generate-setup")
def dca_generate_setup(
    probe_dir: Path = typer.Option(..., "--probe-dir", help="Directory for output files"),
    host_ip: str = typer.Option("192.168.33.30", "--host-ip", help="PC static IP for DCA"),
    dca_ip: str = typer.Option("192.168.33.180", "--dca-ip", help="DCA1000 FPGA IP"),
    dca_mac: str = typer.Option("12:34:56:78:90:12", "--dca-mac", help="DCA1000 MAC address"),
    config_port: int = typer.Option(4096, "--config-port", help="UDP config port"),
    data_port: int = typer.Option(4098, "--data-port", help="UDP data port"),
    packet_delay: int = typer.Option(25, "--packet-delay", help="UDP packet delay in us"),
) -> None:
    """Generate DCA1000 setup Lua script (non-RF)."""
    import uuid
    from .dca.scripts import generate_dca_setup_script
    
    run_id = str(uuid.uuid4())[:8]
    probe_dir.mkdir(parents=True, exist_ok=True)
    out_path = probe_dir / f"{run_id}_dca_setup.lua"
    
    script = generate_dca_setup_script(
        run_id=run_id,
        out_path=out_path,
        host_ip=host_ip,
        dca_ip=dca_ip,
        dca_mac=dca_mac,
        config_port=config_port,
        data_port=data_port,
        packet_delay=packet_delay,
    )
    
    script.lua_path.write_text(script.script, encoding="utf-8")
    
    console.print(f"[green]DCA setup script generated (run_id={run_id}):[/green]")
    console.print(script.dofile)


def get_default_postproc_dir() -> Path:
    base = Path("C:/ti")
    if base.exists():
        candidates = list(base.glob("mmwave_studio_*/mmWaveStudio/PostProc"))
        if candidates:
            return sorted(candidates)[-1]
    return Path(r"C:\ti\mmwave_studio\PostProc")


# @dca_app.command("generate-capture")
def dca_generate_capture(
    probe_dir: Path = typer.Option(..., "--probe-dir", help="Directory for output files"),
    output_dir: Path = typer.Option(get_default_postproc_dir(), "--output-dir", help="Capture directory"),
    confirm_startframe: bool = typer.Option(False, "--confirm-startframe", help="Confirm generation of StartFrame"),
) -> None:
    """Generate DCA1000 capture trigger Lua script (RF transmission!)."""
    import uuid
    from .dca.scripts import generate_capture_trigger_script
    
    try:
        run_id = str(uuid.uuid4())[:8]
        probe_dir.mkdir(parents=True, exist_ok=True)
        out_path = probe_dir / f"{run_id}_capture_trigger.lua"
        
        script = generate_capture_trigger_script(
            run_id=run_id,
            out_path=out_path,
            output_dir=output_dir,
            confirm_startframe=confirm_startframe,
        )
        script.lua_path.write_text(script.script, encoding="utf-8")
        
        console.print(f"[red bold]WARNING: This script triggers RF transmission.[/red bold]")
        console.print(f"[green]Capture trigger script generated (run_id={run_id}):[/green]")
        console.print(script.dofile)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


# @dca_app.command("generate-postproc")
def dca_generate_postproc(
    probe_dir: Path = typer.Option(..., "--probe-dir", help="Directory for output files"),
    output_dir: Path = typer.Option(get_default_postproc_dir(), "--output-dir", help="Capture directory"),
) -> None:
    """Generate Matlab post-processing Lua script."""
    import uuid
    from .dca.scripts import generate_postproc_script
    
    try:
        run_id = str(uuid.uuid4())[:8]
        probe_dir.mkdir(parents=True, exist_ok=True)
        out_path = probe_dir / f"{run_id}_postproc.lua"
        
        script = generate_postproc_script(
            run_id=run_id,
            out_path=out_path,
            output_dir=output_dir,
        )
        script.lua_path.write_text(script.script, encoding="utf-8")
        
        console.print(f"[green]Post-processing script generated (run_id={run_id}):[/green]")
        console.print(script.dofile)
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@dca_app.command("check-capture")
def dca_check_capture(
    capture_dir: Path = typer.Option(get_default_postproc_dir(), "--capture-dir", help="Capture directory"),
    expected_bytes: int = typer.Option(
        4194304,
        "--expected-bytes",
        help=(
            "Expected size of adc_data.bin in bytes. "
            "Validated default: 4194304 (256 samples * 4 bytes/sample * 4 RX * 128 chirps * 8 frames). "
            "Old smoke config was 524288 (1 frame). Ratio = 8.0x."
        ),
    ),
    run_id: str = typer.Option(None, "--run-id", help="Optional run_id for context"),
    format_type: str = typer.Option("text", "--format", help="Output format: text or json"),
) -> None:
    """Validate DCA1000 capture output files."""
    import json
    from .dca.validate import check_capture_files
    
    validation = check_capture_files(capture_dir=capture_dir, expected_bytes=expected_bytes)
    
    if format_type == "json":
        import dataclasses
        print(json.dumps(dataclasses.asdict(validation), indent=2, default=str))
        if validation.overall == "FAIL":
            sys.exit(1)
        return
        
    console.print(f"[bold]DCA Capture Validation[/bold]")
    console.print("=" * 30)
    console.print(f"Capture dir:      {validation.capture_dir}")
    console.print(f"Expected bytes:   {validation.expected_bytes:,}")
    console.print(f"Size model:       256 samples × 4 bytes × 4 RX × 128 chirps × 8 frames = 4,194,304 (validated)")
    if run_id:
        console.print(f"Run ID:           {run_id}")
    console.print("")
    
    for f in [validation.postproc_file, validation.raw_file]:
        status_color = "green" if f.status == "PASS" else "yellow" if f.status == "WARN" else "red"
        exists_str = "FOUND" if f.exists else "NOT FOUND"
        console.print(f"{f.filename:20} {exists_str:10} size={f.size_bytes:<10} [{status_color}]{f.status}[/{status_color}] ({f.detail})")
    
    console.print("")
    console.print(f"Post-processing:  {validation.post_processing_status}")
    overall_color = "green" if validation.overall == "PASS" else "yellow" if validation.overall == "WARN" else "red"
    console.print(f"Overall:          [{overall_color}]{validation.overall}[/{overall_color}]")
    
    if validation.dca_log:
        console.print("")
        console.print(f"[yellow]Latest DCA Log:[/yellow]")
        console.print(f"[dim]{validation.dca_log}[/dim]")
        
    if validation.overall == "FAIL":
        sys.exit(1)


@dca_app.command("record-validation")
def dca_record_validation(
    capture_dir: Path = typer.Option(get_default_postproc_dir(), "--capture-dir", help="Capture directory"),
    expected_bytes: int = typer.Option(4194304, "--expected-bytes", help="Expected size of adc_data.bin"),
    capture_run_id: str = typer.Option(None, "--capture-run-id", help="Run ID of capture trigger script"),
    postproc_run_id: str = typer.Option(None, "--postproc-run-id", help="Run ID of post-processing script"),
    dca_setup_run_id: str = typer.Option(None, "--dca-setup-run-id", help="Run ID of DCA setup script"),
    firmware_run_id: str = typer.Option(None, "--firmware-run-id", help="Run ID of firmware script"),
    config_run_id: str = typer.Option(None, "--config-run-id", help="Run ID of config script"),
    probe_dir: Path = typer.Option(None, "--probe-dir", help="Probe dir for run results"),
    out: Path = typer.Option(None, "--out", help="Output validation JSON path (default: capture_dir/dca_validation_<ts>.json)"),
) -> None:
    """Record a DCA1000 capture validation entry."""
    import datetime
    import json
    from .dca.validate import check_capture_files
    
    validation = check_capture_files(capture_dir=capture_dir, expected_bytes=expected_bytes)
    
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    record: dict = {
        "schema_version": 1,
        "timestamp": datetime.datetime.now().isoformat(),
        "overall": validation.overall,
        "capture_dir": str(capture_dir.resolve()),
        "expected_bytes": expected_bytes,
        "size_model": "256 samples × 4 bytes × 4 RX × 128 chirps × 8 frames",
        "adc_data_bin": {
            "exists": validation.postproc_file.exists,
            "size_bytes": validation.postproc_file.size_bytes,
            "status": validation.postproc_file.status,
            "detail": validation.postproc_file.detail,
        },
        "run_ids": {
            "firmware": firmware_run_id,
            "config": config_run_id,
            "dca_setup": dca_setup_run_id,
            "capture_trigger": capture_run_id,
            "postproc": postproc_run_id,
        },
        "post_processing_status": validation.post_processing_status,
    }
    
    if out is None:
        out = capture_dir / f"dca_validation_{ts}.json"
        
    out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    
    overall_color = "green" if validation.overall == "PASS" else "yellow" if validation.overall == "WARN" else "red"
    console.print(f"[{overall_color}]DCA Capture Validation: {validation.overall}[/{overall_color}]")
    console.print(f"Saved to: {out}")

    if validation.overall == "FAIL":
        sys.exit(1)


@dca_app.command("summarize-capture")
def dca_summarize_capture(
    capture_dir: Path = typer.Option(get_default_postproc_dir(), "--capture-dir", help="Capture directory"),
    expected_bytes: int = typer.Option(4194304, "--expected-bytes", help="Expected size of adc_data.bin"),
) -> None:
    """Summarize DCA1000 capture artifacts in a directory."""
    from .dca.validate import check_capture_files
    from rich.table import Table
    import datetime
    
    if not capture_dir.exists():
        console.print(f"[red]Capture directory not found: {capture_dir}[/red]")
        sys.exit(1)

    validation = check_capture_files(capture_dir=capture_dir, expected_bytes=expected_bytes)
    
    console.print(f"")
    console.print(f"[bold cyan]DCA Capture Summary[/bold cyan]")
    console.print(f"{'Directory':16} {capture_dir}")
    console.print("")

    # File table
    table = Table(show_header=True, header_style="bold", show_lines=True)
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Size (bytes)", justify="right")
    table.add_column("Detail")
    
    for f in [validation.postproc_file, validation.raw_file]:
        color = "green" if f.status == "PASS" else "yellow" if f.status == "WARN" else "red"
        exists_str = "FOUND" if f.exists else "NOT FOUND"
        table.add_row(
            f.filename,
            f"[{color}]{exists_str} — {f.status}[/{color}]",
            f"{f.size_bytes:,}" if f.size_bytes else "—",
            f.detail
        )
    
    console.print(table)
    
    # Validation records in capture dir
    val_files = sorted(capture_dir.glob("dca_validation_*.json"))
    if val_files:
        console.print(f"")
        console.print(f"[bold]Validation Records:[/bold]")
        for vf in val_files:
            import json
            try:
                rec = json.loads(vf.read_text(encoding="utf-8"))
                ts = rec.get("timestamp", "?")
                overall = rec.get("overall", "?")
                color = "green" if overall == "PASS" else "yellow" if overall == "WARN" else "red"
                console.print(f"  {vf.name:45} [{color}]{overall}[/{color}]  {ts}")
            except Exception:
                console.print(f"  {vf.name} (parse error)")

    # Run logs in capture dir
    result_files = sorted(capture_dir.glob("*_result.json"))
    if result_files:
        console.print(f"")
        console.print(f"[bold]Run Results:[/bold]")
        for rf in result_files:
            import json
            try:
                rec = json.loads(rf.read_text(encoding="utf-8"))
                run_id = rec.get("run_id", "?")
                success = rec.get("success", False)
                err = rec.get("error", "")
                color = "green" if success else "red"
                err_str = f"  error: {err[:60]}" if err else ""
                console.print(f"  [{color}]{run_id}[/{color}] {rf.stem.removeprefix(run_id + '_')}{err_str}")
            except Exception:
                console.print(f"  {rf.name} (parse error)")
    
    console.print("")
    overall_color = "green" if validation.overall == "PASS" else "yellow" if validation.overall == "WARN" else "red"
    console.print(f"[bold]Expected bytes:  {expected_bytes:,}[/bold]")
    console.print(f"[bold]Size model:      256 samples × 4 bytes × 4 RX × 128 chirps × 8 frames = 4,194,304 (validated)[/bold]")
    console.print(f"[bold]Overall:         [{overall_color}]{validation.overall}[/{overall_color}][/bold]")

    if validation.overall == "FAIL":
        sys.exit(1)


# ---------------------------------------------------------------------------
# awr dca capture-smoke
# ---------------------------------------------------------------------------

def _print_project_binding_state(state: Any) -> None:
    if not getattr(state, "bind_requested", False):
        return
    console.print("")
    console.print("[bold]Project Binding[/bold]")
    console.print(f"Project root:       {state.project_root_abs}")
    console.print(f"Project Capture ID: {state.capture_id}")
    console.print(f"Bind requested:     {state.bind_requested}")
    console.print(f"Bind completed:     {state.bind_completed}")
    
    verify_str = "NOT_RUN"
    if getattr(state, "capture_verify_passed", None) is True:
        verify_str = "[green]PASS[/green]"
    elif getattr(state, "capture_verify_passed", None) is False:
        verify_str = "[red]FAIL[/red]"
    console.print(f"Capture verify:     {verify_str}")
    
    if getattr(state, "capture_manifest_path_rel", None):
        console.print(f"Capture manifest:   {state.capture_manifest_path_rel}")
    if getattr(state, "bound_raw_file_rel", None):
        console.print(f"Bound raw file rel: {state.bound_raw_file_rel}")
    if getattr(state, "bound_raw_file_sha256", None):
        console.print(f"Bound raw SHA256:   {state.bound_raw_file_sha256}")
    if getattr(state, "adc_inspect_path_rel", None):
        console.print(f"ADC inspect path rel: {state.adc_inspect_path_rel}")
    if getattr(state, "bind_error", None):
        console.print(f"Bind error:         [red]{state.bind_error}[/red]")
    console.print("")


@capture_smoke_app.command("start")
def dca_capture_smoke_start(
    probe_dir: Path = typer.Option(..., "--probe-dir", help="Directory for output files"),
    capture_dir: Path = typer.Option(get_default_postproc_dir(), "--capture-dir", help="Capture directory"),
    firmware_run_id: str = typer.Option("", "--firmware-run-id", help="Run ID of firmware validation"),
    config_run_id: str = typer.Option("", "--config-run-id", help="Run ID of config validation"),
    confirm_startframe: bool = typer.Option(False, "--confirm-startframe", help="Confirm this workflow will call StartFrame"),
    archive_existing: bool = typer.Option(False, "--archive-existing", help="Archive existing adc_data.bin before capture"),
    allow_overwrite: bool = typer.Option(False, "--allow-overwrite", help="Allow overwriting existing adc_data.bin"),
    expected_bytes: int = typer.Option(4194304, "--expected-bytes", help="Expected adc_data.bin size"),
    project_root: Path = typer.Option(None, "--project-root", help="Project root for capture binding"),
    capture_id: str = typer.Option(None, "--capture-id", help="Existing capture ID to bind to"),
    capture_name: str = typer.Option(None, "--capture-name", help="Name for new auto-created capture"),
    auto_create_capture: bool = typer.Option(False, "--auto-create-capture", help="Auto-create capture from --capture-name"),
    bind_force: bool = typer.Option(False, "--bind-force", help="Allow overwriting existing raw file when binding"),
) -> None:
    """Start a new DCA capture-smoke workflow."""
    from .dca.workflow import start_workflow

    try:
        state = start_workflow(
            probe_dir=probe_dir,
            capture_dir=capture_dir,
            firmware_run_id=firmware_run_id,
            config_run_id=config_run_id,
            confirm_startframe=confirm_startframe,
            expected_bytes=expected_bytes,
            archive_existing=archive_existing,
            allow_overwrite=allow_overwrite,
            project_root=project_root,
            capture_id=capture_id,
            capture_name=capture_name,
            auto_create_capture=auto_create_capture,
            bind_force=bind_force,
        )
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    console.print(f"[green]Workflow started:[/green] [bold cyan]{state.workflow_id}[/bold cyan]")
    if state.bind_requested:
        console.print(f"Project root: {state.project_root_abs}")
        console.print(f"Capture ID:   {state.capture_id}")
    console.print(f"Stage: {state.current_stage}")
    if state.warnings:
        for w in state.warnings:
            console.print(f"[yellow]WARNING: {w}[/yellow]")
    console.print("")
    console.print(f"[bold]Next step:[/bold] {state.pending_operator_action}")
    console.print(f"[cyan]{state.pending_dofile}[/cyan]")
    console.print("")
    console.print("[bold]Next command to run:[/bold]")
    console.print(f"awr dca capture-smoke resume --workflow-id {state.workflow_id} --probe-dir {probe_dir}")


@capture_smoke_app.command("resume")
def dca_capture_smoke_resume(
    workflow_id: str = typer.Option(..., "--workflow-id", help="Workflow ID"),
    probe_dir: Path = typer.Option(None, "--probe-dir", help="Probe directory (auto-detected from state)"),
) -> None:
    """Resume a capture-smoke workflow by one step."""
    from .dca.workflow import load_state as load_wf_state, resume_workflow

    try:
        if probe_dir is None:
            # Try common locations
            for candidate in [Path("ti/probe_logs"), Path(".")]:
                if (candidate / f"dca_capture_smoke_{workflow_id}_state.json").exists():
                    probe_dir = candidate
                    break
            if probe_dir is None:
                console.print("[red]Cannot find workflow state. Specify --probe-dir.[/red]")
                sys.exit(1)

        state = resume_workflow(workflow_id, probe_dir)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    console.print(f"Workflow ID:      [bold cyan]{state.workflow_id}[/bold cyan]")
    console.print(f"Stage:            {state.current_stage}")
    _print_project_binding_state(state)
    if state.warnings:
        for w in state.warnings:
            console.print(f"[yellow]WARNING: {w}[/yellow]")
    if state.errors:
        for e in state.errors:
            console.print(f"[red]ERROR: {e}[/red]")
    console.print("")
    
    if state.dca_setup.run_id:
        console.print(f"DCA Setup Run ID:       {state.dca_setup.run_id}")
    if state.capture_trigger.run_id:
        console.print(f"Capture Trigger Run ID: {state.capture_trigger.run_id}")
    if state.postproc.run_id:
        console.print(f"Postproc Run ID:        {state.postproc.run_id}")
    if state.dca_setup.run_id or state.capture_trigger.run_id or state.postproc.run_id:
        console.print("")

    console.print(f"[bold]Next step:[/bold] {state.pending_operator_action}")
    if state.pending_dofile:
        console.print(f"[cyan]{state.pending_dofile}[/cyan]")
    
    if not state.completed and not state.errors:
        console.print("")
        console.print("[bold]Next command to run:[/bold]")
        console.print(f"awr dca capture-smoke resume --workflow-id {state.workflow_id} --probe-dir {probe_dir}")
        
    if state.completed:
        console.print("")
        console.print("[green]Workflow COMPLETE.[/green]")
        if state.adc_data_bin_sha256:
            console.print(f"SHA256: {state.adc_data_bin_sha256}")
        if state.adc_data_bin_size:
            console.print(f"Size: {state.adc_data_bin_size:,} bytes")
        _print_project_binding_state(state)


@capture_smoke_app.command("status")
def dca_capture_smoke_status(
    workflow_id: str = typer.Option(..., "--workflow-id", help="Workflow ID"),
    probe_dir: Path = typer.Option(None, "--probe-dir", help="Probe directory"),
) -> None:
    """Print status of a capture-smoke workflow."""
    from .dca.workflow import load_state as load_wf_state

    try:
        if probe_dir is None:
            for candidate in [Path("ti/probe_logs"), Path(".")]:
                if (candidate / f"dca_capture_smoke_{workflow_id}_state.json").exists():
                    probe_dir = candidate
                    break
            if probe_dir is None:
                console.print("[red]Cannot find workflow state. Specify --probe-dir.[/red]")
                sys.exit(1)

        state = load_wf_state(workflow_id, probe_dir)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    console.print(f"Workflow ID: [bold cyan]{state.workflow_id}[/bold cyan]")
    console.print(f"Stage:       {state.current_stage}")
    console.print(f"Created:     {state.created_at}")
    console.print(f"Updated:     {state.updated_at}")
    console.print(f"Completed:   {state.completed}")
    console.print(f"Capture dir: {state.capture_dir}")
    _print_project_binding_state(state)
    console.print("")
    if state.dca_setup.run_id:
        console.print(f"DCA Setup Run ID:       {state.dca_setup.run_id}")
    if state.capture_trigger.run_id:
        console.print(f"Capture Trigger Run ID: {state.capture_trigger.run_id}")
    if state.postproc.run_id:
        console.print(f"Postproc Run ID:        {state.postproc.run_id}")
    if state.warnings:
        console.print("")
        for w in state.warnings:
            console.print(f"[yellow]WARNING: {w}[/yellow]")
    if state.errors:
        console.print("")
        for e in state.errors:
            console.print(f"[red]ERROR: {e}[/red]")
    console.print("")
    console.print(f"[bold]Next step:[/bold] {state.pending_operator_action}")
    if state.pending_dofile:
        console.print(f"[cyan]{state.pending_dofile}[/cyan]")

    if not state.completed and not state.errors:
        console.print("")
        console.print("[bold]Next command to run:[/bold]")
        console.print(f"awr dca capture-smoke resume --workflow-id {state.workflow_id} --probe-dir {probe_dir}")


@capture_smoke_app.command("latest")
def dca_capture_smoke_latest(
    probe_dir: Path = typer.Option(None, "--probe-dir", help="Probe directory"),
) -> None:
    """Show the latest capture-smoke workflow."""
    from .dca.workflow import find_latest_state

    if probe_dir is None:
        probe_dir = Path("ti/probe_logs")

    state = find_latest_state(probe_dir)
    if state is None:
        console.print("[yellow]No capture-smoke workflows found.[/yellow]")
        return

    console.print(f"Workflow ID: [bold cyan]{state.workflow_id}[/bold cyan]")
    console.print(f"Stage:       {state.current_stage}")
    console.print(f"Completed:   {state.completed}")
    console.print(f"Updated:     {state.updated_at}")
    _print_project_binding_state(state)
    console.print("")
    
    if state.dca_setup.run_id:
        console.print(f"DCA Setup Run ID:       {state.dca_setup.run_id}")
    if state.capture_trigger.run_id:
        console.print(f"Capture Trigger Run ID: {state.capture_trigger.run_id}")
    if state.postproc.run_id:
        console.print(f"Postproc Run ID:        {state.postproc.run_id}")
    if state.dca_setup.run_id or state.capture_trigger.run_id or state.postproc.run_id:
        console.print("")

    console.print(f"[bold]Next step:[/bold] {state.pending_operator_action}")
    if state.pending_dofile:
        console.print(f"[cyan]{state.pending_dofile}[/cyan]")
        
    if not state.completed and not state.errors:
        console.print("")
        console.print("[bold]Next command to run:[/bold]")
        console.print(f"awr dca capture-smoke resume --workflow-id {state.workflow_id} --probe-dir {probe_dir}")


@dca_app.command("adapters")
def dca_adapters() -> None:
    """List network adapters and score them as DCA1000 candidates."""
    from .dca.adapters import get_adapters, score_adapter
    from rich.table import Table
    
    adapters = get_adapters()
    
    table = Table(title="Network Adapters (DCA1000 Candidates)")
    table.add_column("Alias")
    table.add_column("Index")
    table.add_column("Status")
    table.add_column("IPs")
    table.add_column("Gateway", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Reason")
    
    for a in adapters:
        score, reason, is_safe = score_adapter(a)
        
        score_str = f"[green]{score}[/green]" if score > 0 else f"[red]{score}[/red]"
        gateway_str = "[red]Yes[/red]" if a.has_default_gateway else "[green]No[/green]"
        ip_str = ", ".join(a.ipv4_addresses) if a.ipv4_addresses else "None"
        
        table.add_row(
            a.interface_alias,
            str(a.interface_index),
            a.status,
            ip_str,
            gateway_str,
            score_str,
            reason
        )
        
    console.print(table)


@dca_app.command("configure-adapter")
def dca_configure_adapter(
    interface: str = typer.Option(..., "--interface", help="Interface Alias or Index"),
    yes: bool = typer.Option(False, "--yes", help="Actually execute the configuration"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the PowerShell commands without executing"),
    allow_gateway: bool = typer.Option(False, "--allow-gateway-adapter", help="Allow modifying an adapter that has a default gateway"),
) -> None:
    """Safely configure a network adapter with a static IP for DCA1000."""
    from .dca.adapters import get_adapters, score_adapter
    import subprocess
    
    if not yes and not dry_run:
        console.print("[red]Error: You must specify either --yes or --dry-run.[/red]")
        sys.exit(1)
        
    if yes and dry_run:
        console.print("[red]Error: Cannot specify both --yes and --dry-run.[/red]")
        sys.exit(1)
        
    adapters = get_adapters()
    target = None
    for a in adapters:
        if str(a.interface_index) == interface or a.interface_alias.lower() == interface.lower():
            target = a
            break
            
    if not target:
        console.print(f"[red]Error: Adapter '{interface}' not found.[/red]")
        sys.exit(1)
        
    score, reason, is_safe = score_adapter(target)
    
    if "wi-fi" in target.interface_alias.lower() or "wireless" in target.interface_alias.lower():
        console.print(f"[red]Safety Error: Refusing to modify Wi-Fi adapter '{target.interface_alias}'.[/red]")
        sys.exit(1)
        
    if target.has_default_gateway and not allow_gateway:
        console.print(f"[red]Safety Error: Refusing to modify adapter with a default gateway ('{target.interface_alias}'). Use --allow-gateway-adapter if absolutely sure.[/red]")
        sys.exit(1)
        
    ps_commands = f"""
Set-NetIPInterface -InterfaceAlias "{target.interface_alias}" -Dhcp Disabled
Remove-NetIPAddress -InterfaceAlias "{target.interface_alias}" -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
New-NetIPAddress -InterfaceAlias "{target.interface_alias}" -IPAddress "192.168.33.30" -PrefixLength 24
Set-DnsClientServerAddress -InterfaceAlias "{target.interface_alias}" -ResetServerAddresses
""".strip()

    if dry_run:
        console.print(f"[yellow]Dry-run for adapter '{target.interface_alias}':[/yellow]")
        console.print(ps_commands)
        return
        
    if yes:
        console.print(f"[yellow]Configuring adapter '{target.interface_alias}'...[/yellow]")
        try:
            subprocess.check_call(
                ["powershell", "-NoProfile", "-Command", ps_commands],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            console.print("[green]Success. Run `awr dca preflight` again to verify.[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to configure adapter: {e}[/red]")
            sys.exit(1)

# ---------------------------------------------------------------------------
# awr adc inspect
# ---------------------------------------------------------------------------

@adc_app.command("inspect")
def adc_inspect(
    bin_path: Path = typer.Option(..., "--bin", help="Path to adc_data.bin"),
    frames: int = typer.Option(8, "--frames", help="Number of frames"),
    chirps: int = typer.Option(128, "--chirps", help="Chirps per frame"),
    rx: int = typer.Option(4, "--rx", help="RX channels"),
    samples: int = typer.Option(256, "--samples", help="Samples per chirp"),
    iq_order: str = typer.Option("iq", "--iq-order", help="IQ interleave order: iq or qi"),
    layout: str = typer.Option("frame_chirp_rx_sample", "--layout", help="Cube layout"),
    format_type: str = typer.Option("text", "--format", help="Output format: text or json"),
) -> None:
    """Inspect an ADC binary capture file (no FFT)."""
    from .adc_parser import AdcParserConfig, inspect_adc_file
    import json as json_mod

    config = AdcParserConfig(
        frames=frames, chirps=chirps, rx=rx, samples=samples,
        iq_order=iq_order, layout=layout,
    )
    info = inspect_adc_file(bin_path, config)

    if format_type == "json":
        print(json_mod.dumps(info, indent=2, default=str))
        if info.get("error"):
            sys.exit(1)
        return

    # Text output
    console.print("")
    console.print("[bold cyan]ADC Capture Inspection[/bold cyan]")
    console.print(f"{'Path':20} {info['file_path']}")
    console.print(f"{'File size':20} {info['file_size']:,} bytes")
    console.print(f"{'Expected':20} {info['expected_bytes']:,} bytes")
    console.print(f"{'Size match':20} {info['size_match']}")

    if info.get("error"):
        console.print(f"[red]{'Error':20} {info['error']}[/red]")
        sys.exit(1)

    console.print(f"{'Shape':20} {tuple(info['shape'])}")
    console.print(f"{'Format':20} {config.sample_format}, iq_order={config.iq_order}")
    console.print(f"{'Layout assumption':20} {info['layout_assumption']}")
    console.print(f"{'Layout confirmed':20} [yellow]{info['layout_assumption_confirmed']}[/yellow]")
    console.print(f"{'SHA256':20} {info.get('sha256', 'N/A')}")
    console.print(f"{'All zero':20} {info.get('all_zero', 'N/A')}")
    console.print(f"{'Int16 count':20} {info.get('int16_count', 'N/A'):,}")
    console.print(f"{'Complex count':20} {info.get('complex_count', 'N/A'):,}")
    console.print("")
    console.print(f"{'Real min/max':20} {info.get('real_min', 'N/A')} / {info.get('real_max', 'N/A')}")
    console.print(f"{'Real mean/std':20} {info.get('real_mean', 'N/A'):.2f} / {info.get('real_std', 'N/A'):.2f}")
    console.print(f"{'Imag min/max':20} {info.get('imag_min', 'N/A')} / {info.get('imag_max', 'N/A')}")
    console.print(f"{'Imag mean/std':20} {info.get('imag_mean', 'N/A'):.2f} / {info.get('imag_std', 'N/A'):.2f}")
    console.print(f"{'Zero fraction':20} {info.get('zero_fraction', 'N/A'):.4f}")

    if info.get("first_16_int16_values"):
        console.print(f"{'First 16 int16':20} {info['first_16_int16_values']}")
    if info.get("first_8_complex_values"):
        cvals = [f"{c['real']}+{c['imag']}j" for c in info['first_8_complex_values']]
        console.print(f"{'First 8 complex':20} {cvals}")

    if info.get("per_rx_rms"):
        console.print("")
        console.print("[bold]Per-RX RMS:[/bold]")
        for entry in info["per_rx_rms"]:
            console.print(f"  RX {entry['rx']}: {entry['rms']:.2f}")


# ===========================================================================
# awr project ...
# ===========================================================================

@project_app.command("init")
def project_init_cmd(
    name: str = typer.Argument(..., help="Project name"),
    root: Path = typer.Option(Path("."), "--root", help="Project root directory"),
    postproc_dir: str = typer.Option(
        "C:\\ti\\mmwave_studio_03_01_04_04\\mmWaveStudio\\PostProc",
        "--postproc-dir", help="mmWave Studio PostProc staging directory",
    ),
    probe_dir: str = typer.Option("ti\\probe_logs", "--probe-dir", help="Probe log directory (relative)"),
    expected_bytes: int = typer.Option(4_194_304, "--expected-bytes", help="Expected ADC file size"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing project.json"),
) -> None:
    """Initialize a new project with directory scaffolding."""
    from .project import init_project

    try:
        proj = init_project(
            name=name, root=root, postproc_dir=postproc_dir,
            probe_dir=probe_dir, expected_bytes=expected_bytes, force=force,
        )
        console.print(f"[green]Project initialized:[/green] [bold]{proj['name']}[/bold]")
        console.print(f"  Root (absolute):    {proj['root_path_abs']}")
        console.print(f"  PostProc dir:       {proj['postproc_dir_abs']}")
        console.print(f"  Probe dir (rel):    {proj['probe_dir_rel']}")
        console.print(f"  Expected bytes:     {proj['expected_bytes']:,}")
        console.print(f"  Project ID:         {proj['project_id']}")
    except FileExistsError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@project_app.command("status")
def project_status_cmd(
    root: Path = typer.Option(Path("."), "--root", help="Project root directory"),
    format_type: str = typer.Option("text", "--format", help="Output format: text or json"),
) -> None:
    """Show project status and health checks."""
    from .project import project_status, find_project_root
    import json as json_mod

    try:
        actual_root = find_project_root(root)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    status = project_status(actual_root)

    if format_type == "json":
        print(json_mod.dumps(status, indent=2, default=str))
        return

    console.print("")
    console.print(f"[bold cyan]Project: {status['project_name']}[/bold cyan]")
    console.print(f"  Root:           {status['root_path_abs']}")
    console.print(f"  PostProc dir:   {status['postproc_dir_abs']}")
    pp_ok = "[green]exists[/green]" if status["postproc_dir_exists"] else "[red]MISSING[/red]"
    console.print(f"  PostProc check: {pp_ok}")
    console.print(f"  Probe dir:      {status['probe_dir_rel']}")
    pd_ok = "[green]exists[/green]" if status["probe_dir_exists"] else "[red]MISSING[/red]"
    console.print(f"  Probe check:    {pd_ok}")
    gi_ok = "[green]OK[/green]" if status["gitignore_ok"] else "[yellow]INCOMPLETE[/yellow]"
    console.print(f"  .gitignore:     {gi_ok}")
    console.print(f"  Captures:       {status['capture_count']}")
    
    # Print status breakdown
    counts = status.get("status_counts", {})
    count_str = ", ".join(f"{k}={v}" for k, v in counts.items() if v > 0)
    if count_str:
        console.print(f"  Status breakdown: {count_str}")
        
    if status.get("error_captures"):
        console.print("  [red]Errors:[/red]")
        for err_cap in status["error_captures"]:
            console.print(f"    - {err_cap['capture_id']}")
            
    if status["newest_capture"]:
        n = status["newest_capture"]
        console.print(f"  Newest:         {n['capture_id']} ({n['status']})")


# ===========================================================================
# awr capture ...
# ===========================================================================

@capture_mgmt_app.command("new")
def capture_new_cmd(
    capture_name: str = typer.Argument(..., help="Human-readable capture name"),
    root: Path = typer.Option(Path("."), "--root", help="Project root directory"),
    mode: str = typer.Option("import", "--mode", help="Capture mode: import or direct"),
    notes: str = typer.Option("", "--notes", help="Initial notes"),
) -> None:
    """Create a new capture folder with manifest."""
    from .project import new_capture, find_project_root

    try:
        actual_root = find_project_root(root)
        manifest = new_capture(actual_root, capture_name, mode=mode, notes=notes)
        console.print(f"[green]Capture created:[/green] [bold]{manifest['capture_id']}[/bold]")
        console.print(f"  Name:       {manifest['capture_name']}")
        console.print(f"  Directory:  {manifest['capture_dir_abs']}")
        console.print(f"  Mode:       {manifest['mode']}")
        console.print(f"  Status:     {manifest['status']}")
    except (FileNotFoundError, FileExistsError) as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@capture_mgmt_app.command("import-raw")
def capture_import_raw_cmd(
    capture_id: str = typer.Argument(..., help="Capture ID"),
    source_path: Path = typer.Option(..., "--from", help="Path to source ADC binary"),
    root: Path = typer.Option(Path("."), "--root", help="Project root directory"),
    move: bool = typer.Option(False, "--move", help="Move instead of copy"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing raw file"),
    inspect: bool = typer.Option(True, "--inspect/--no-inspect", help="Run ADC inspection"),
    allow_size_mismatch: bool = typer.Option(False, "--allow-size-mismatch", help="Allow wrong-size files"),
) -> None:
    """Import a raw ADC binary into a capture."""
    from .project import import_raw, find_project_root

    try:
        actual_root = find_project_root(root)
        manifest = import_raw(
            actual_root, capture_id, source_path=source_path,
            move=move, force=force, inspect=inspect,
            allow_size_mismatch=allow_size_mismatch,
        )
        console.print(f"[green]Raw file imported:[/green] {manifest.get('raw_file_rel', '')}")
        console.print(f"  Size:   {manifest.get('actual_raw_file_size', 0):,} bytes")
        console.print(f"  SHA256: {manifest.get('raw_file_sha256', '')}")
        console.print(f"  Status: {manifest.get('status', '')}")
        for w in manifest.get("warnings", []):
            console.print(f"  [yellow]WARNING: {w}[/yellow]")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except FileExistsError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@capture_mgmt_app.command("bind-mmws-output")
def capture_bind_mmws_cmd(
    capture_id: str = typer.Argument(..., help="Capture ID"),
    root: Path = typer.Option(Path("."), "--root", help="Project root directory"),
    postproc_dir: str = typer.Option(None, "--postproc-dir", help="PostProc directory (default from project.json)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing raw file"),
    copy_logs: bool = typer.Option(True, "--copy-logs/--no-copy-logs", help="Copy log/metadata files"),
    inspect: bool = typer.Option(True, "--inspect/--no-inspect", help="Run ADC inspection"),
) -> None:
    """Bind mmWave Studio PostProc output to a capture."""
    from .project import bind_mmws_output, find_project_root

    try:
        actual_root = find_project_root(root)
        manifest = bind_mmws_output(
            actual_root, capture_id,
            postproc_dir=postproc_dir, force=force,
            copy_logs=copy_logs, inspect=inspect,
        )
        console.print(f"[green]PostProc output bound:[/green] {manifest.get('raw_file_rel', '')}")
        console.print(f"  Size:       {manifest.get('actual_raw_file_size', 0):,} bytes")
        console.print(f"  SHA256:     {manifest.get('raw_file_sha256', '')}")
        console.print(f"  Status:     {manifest.get('status', '')}")
        copied = manifest.get("copied_mmws_files", [])
        if copied:
            console.print(f"  Copied:     {len(copied)} metadata files")
            for cf in copied:
                console.print(f"              {cf['dest_rel']}")
        for w in manifest.get("warnings", []):
            console.print(f"  [yellow]WARNING: {w}[/yellow]")
    except (FileNotFoundError, FileExistsError) as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@capture_mgmt_app.command("inspect")
def capture_inspect_cmd(
    capture_id: str = typer.Argument(..., help="Capture ID"),
    root: Path = typer.Option(Path("."), "--root", help="Project root directory"),
    format_type: str = typer.Option("text", "--format", help="Output format: text or json"),
    refresh_adc_inspect: bool = typer.Option(False, "--refresh-adc-inspect", help="Re-run ADC inspection"),
) -> None:
    """Inspect a capture's manifest, raw file, and ADC analysis."""
    from .project import inspect_capture, find_project_root
    import json as json_mod

    try:
        actual_root = find_project_root(root)
        info = inspect_capture(actual_root, capture_id, refresh_adc_inspect=refresh_adc_inspect)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    if format_type == "json":
        print(json_mod.dumps(info, indent=2, default=str))
        return

    console.print("")
    console.print(f"[bold cyan]Capture: {info['capture_id']}[/bold cyan]")
    console.print(f"  Name:       {info['capture_name']}")
    console.print(f"  Status:     {info['status']}")
    console.print(f"  Mode:       {info['mode']}")
    console.print(f"  Created:    {info['created_at']}")
    console.print(f"  Updated:    {info['updated_at']}")
    console.print("")
    raw_ok = "[green]EXISTS[/green]" if info["raw_file_exists"] else "[red]MISSING[/red]"
    console.print(f"  Raw file:   {raw_ok}")
    if info["raw_file_exists"]:
        console.print(f"  Raw size:   {info['raw_file_size']:,} bytes")
        sm = "[green]MATCH[/green]" if info["size_match"] else "[red]MISMATCH[/red]"
        console.print(f"  Size check: {sm} (expected {info['expected_bytes']:,})")
        console.print(f"  SHA256:     {info['raw_file_sha256']}")
    if info.get("adc_inspect"):
        ai = info["adc_inspect"]
        console.print("")
        console.print("  [bold]ADC Inspection:[/bold]")
        if ai.get("shape"):
            console.print(f"    Shape:    {tuple(ai['shape'])}")
        if ai.get("all_zero") is not None:
            console.print(f"    All zero: {ai['all_zero']}")
        if ai.get("layout_assumption"):
            console.print(f"    Layout:   {ai['layout_assumption']} (confirmed={ai.get('layout_assumption_confirmed', False)})")
    for w in info.get("warnings", []):
        console.print(f"  [yellow]WARNING: {w}[/yellow]")
    for e in info.get("errors", []):
        console.print(f"  [red]ERROR: {e}[/red]")


@capture_mgmt_app.command("verify")
def capture_verify_cmd(
    capture_id: str = typer.Argument(..., help="Capture ID"),
    root: Path = typer.Option(Path("."), "--root", help="Project root directory"),
    format_type: str = typer.Option("text", "--format", help="Output format: text or json"),
) -> None:
    """Verify a capture's manifest, files, and hashes."""
    from .project import verify_capture, find_project_root
    import json as json_mod

    try:
        actual_root = find_project_root(root)
        result = verify_capture(actual_root, capture_id)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    if format_type == "json":
        print(json_mod.dumps(result, indent=2, default=str))
        if not result["passed"]:
            sys.exit(1)
        return

    console.print("")
    console.print(f"[bold cyan]Capture Verification: {capture_id}[/bold cyan]")
    
    if result["passed"]:
        console.print("[green]PASS[/green] All checks succeeded.")
    else:
        console.print("[red]FAIL[/red] Verification found errors.")
        
    if result["errors"]:
        console.print("\n[red]Errors:[/red]")
        for err in result["errors"]:
            console.print(f"  - {err}")
            
    if result["warnings"]:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warn in result["warnings"]:
            console.print(f"  - {warn}")
            
    if not result["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    app()
