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
# app.add_typer(mmws_app, name="mmws")




dca_app = typer.Typer(help="DCA1000 integration commands")
app.add_typer(dca_app, name="dca")

adc_app = typer.Typer(help="ADC data commands")
app.add_typer(adc_app, name="adc")

# dca_app.add_typer(capture_smoke_app, name="capture-smoke")


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


def ti_connection_probe(
    com: str = typer.Option(None, "--com", help="[DEPRECATED] Use 'awr mmws connection script'"),
    baud: int = typer.Option(921600, "--baud", help="Baud rate"),
    timeout_ms: int = typer.Option(1000, "--timeout-ms", help="Connect timeout in ms"),
) -> None:
    """[DEPRECATED] Use 'awr mmws connection script' instead."""
    console.print("[yellow]DEPRECATED: Use 'awr mmws connection script' instead.[/yellow]")
    mmws_connection_script_cmd(com=com, baud=baud, timeout_ms=timeout_ms)


def ti_connection_status() -> None:
    """[DEPRECATED] Use 'awr mmws connection status' instead."""
    console.print("[yellow]DEPRECATED: Use 'awr mmws connection status' instead.[/yellow]")
    mmws_connection_status()


# ---------------------------------------------------------------------------
# awr mmws scan-scripts
# ---------------------------------------------------------------------------




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









# ---------------------------------------------------------------------------
# awr mmws static plan
# ---------------------------------------------------------------------------



# (Assume this gets injected inside cli.py where mmws_conn_app commands are defined)




















# ---------------------------------------------------------------------------
# awr mmws inspect-execution (no experiment needed)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# awr mmws run-script
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# awr mmws smoke
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# awr mmws rstd-ping (diagnostic, no experiment needed)
# ---------------------------------------------------------------------------




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




# ---------------------------------------------------------------------------
# awr mmws rstd-methods (DLL method introspection via isolated subprocess)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# awr mmws rstd-worker-test (step-level diagnostic, no experiment needed)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# awr mmws rstd-last-error (diagnostic, no experiment needed)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# awr mmws studio launch / attach / status (no experiment needed)
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
# awr mmws lua-command (manual dofile helper)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# awr mmws matlab-bridge *
# ---------------------------------------------------------------------------







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






# awr mmws csharp-bridge *
# ---------------------------------------------------------------------------





















# ---------------------------------------------------------------------------
# lua-launch: cleanup
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# lua-launch: ar1-readonly-probe
# ---------------------------------------------------------------------------



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




# ---------------------------------------------------------------------------
# lua-launch: dll-diagnostics
# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
# lua-launch: startup-lite-v3-probe
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# lua-launch: path-env-probe
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# lua-launch: radarapi-v3-connect-probe
# ---------------------------------------------------------------------------


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












# ---------------------------------------------------------------------------
# gui-connect commands ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â pywinauto GUI-button automation (OFFICIAL)
# ---------------------------------------------------------------------------

_GUI_CONNECT_PRECONDITION = (
    "[cyan]Expected precondition: mmWave Studio is open as admin, "
    "Startup.lua completed, and AWR was power-cycled using "
    "power-before-USB order.[/cyan]"
)




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








# ---------------------------------------------------------------------------
# awr mmws post *
# ---------------------------------------------------------------------------

































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
