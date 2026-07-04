"""CLI for AWR2944 + DCA1000 radar research toolkit.

Root command: ``awr``

Existing commands:
    awr doctor                         — Check setup / environment
    awr inspect-config <yaml>          — Validate and display config + derived params
    awr parse <bin> --config <yaml>    — Parse adc_data.bin into radar cube
    awr process <bin> --config <yaml>  — Full DSP pipeline → range profile + range-Doppler
    awr compare-layouts <target>       — Compare candidate binary layouts

Config management:
    awr config new --preset <name>     — Generate capture.yaml from preset
    awr config validate <yaml>         — Deep validation of capture config
    awr config summarize <yaml>        — Human-readable config summary

Experiment management:
    awr experiment init <name>         — Scaffold experiment directory

TI bridge:
    awr ti inspect <file>              — Inspect TI Lua/JSON config file
    awr ti import <file>               — Import TI config to capture.yaml
    awr ti compare <yaml> <ti_file>    — Compare our config vs TI config
    awr ti export-lua-template <yaml>  — Generate Lua template
    awr ti export-dca-config <yaml>    — Generate DCA1000 JSON config
"""

from __future__ import annotations

import platform
import sys
import re
from pathlib import Path

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
mmws_app = typer.Typer(help="mmWave Studio backend controller")
app.add_typer(mmws_app, name="mmws")
mmws_conn_app = typer.Typer(help="Connection-tab control")
mmws_app.add_typer(mmws_conn_app, name="connection")
mmws_studio_app = typer.Typer(help="mmWave Studio process management")
mmws_app.add_typer(mmws_studio_app, name="studio")
mmws_bridge_app = typer.Typer(help="C# RSTD bridge management")
mmws_app.add_typer(mmws_bridge_app, name="csharp-bridge")
mmws_matlab_bridge_app = typer.Typer(help="MATLAB-to-Studio bridge diagnostics")
mmws_app.add_typer(mmws_matlab_bridge_app, name="matlab-bridge")

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
def init_alias(
    name: str = typer.Argument(..., help="Experiment name"),
    preset: str = typer.Option("first-capture", "--preset", "-p", help="Config preset"),
    root: Path = typer.Option(Path("."), "--root", "-r", help="Experiments root dir"),
) -> None:
    """Scaffold a new experiment (alias for 'awr experiment init')."""
    experiment_init(name, preset, root)


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

@app.command("init")
def init_alias(
    name: str = typer.Argument(..., help="Experiment name"),
    preset: str = typer.Option("first-capture", "--preset", "-p", help="Config preset"),
    root: Path = typer.Option(Path("."), "--root", "-r", help="Experiments root dir"),
) -> None:
    """Scaffold a new experiment."""
    from awr2944_dca.api.experiment import Experiment
    try:
        exp = Experiment.init(name, preset, root)
        console.print(f"[green]OK[/green] Scaffolded experiment at {exp.root_dir}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


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
    """Scaffold an experiment directory with config, folders, and notes template."""
    init_alias(name=name, preset=preset, root=root)


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
            console.print(f"  [yellow]• {a}[/yellow]")

    if unknown_fields:
        console.print("\n[red]Unknown fields (could not extract):[/red]")
        for f in unknown_fields:
            console.print(f"  [red]• {f}[/red]")

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


@ti_app.command("export-lua-template")
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


@ti_app.command("find-studio")
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


@ti_app.command("lua-command")
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


@ti_app.command("run-lua")
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


@ti_app.command("connection-probe", deprecated=True)
def ti_connection_probe(
    com: str = typer.Option(None, "--com", help="[DEPRECATED] Use 'awr mmws connection script'"),
    baud: int = typer.Option(921600, "--baud", help="Baud rate"),
    timeout_ms: int = typer.Option(1000, "--timeout-ms", help="Connect timeout in ms"),
) -> None:
    """[DEPRECATED] Use 'awr mmws connection script' instead."""
    console.print("[yellow]DEPRECATED: Use 'awr mmws connection script' instead.[/yellow]")
    mmws_connection_script_cmd(com=com, baud=baud, timeout_ms=timeout_ms)


@ti_app.command("connection-status", deprecated=True)
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
    from awr2944_dca.mmws.catalog import discover_mmws_installations, scan_scripts, write_catalog

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
    from awr2944_dca.mmws.stages import get_stage, StageName

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
    from awr2944_dca.mmws.bridge import StudioBridge, StageStatus
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
        from awr2944_dca.mmws.executor import build_dofile_command
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
    from awr2944_dca.mmws.bridge import StudioBridge, StageStatus
    from awr2944_dca.mmws.stages import StageName

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
    from awr2944_dca.mmws.executor import _is_mmws_running, _find_csharp_bridge
    from awr2944_dca.hardware.ports import get_local_hardware_config, scan_ports
    
    try:
        exp = Experiment.open(".")
        console.print(f"[green]✓[/green] Inside experiment: {exp.root_dir.name}")
    except FileNotFoundError:
        console.print("[red]✗[/red] Not inside an experiment directory.")
        raise typer.Exit(1)
        
    if _is_mmws_running():
        console.print("[green]✓[/green] mmWave Studio is running.")
    else:
        console.print("[red]✗[/red] mmWave Studio is NOT running.")
        
    if _find_csharp_bridge():
        console.print("[green]✓[/green] C# Bridge is built.")
    else:
        console.print("[red]✗[/red] C# Bridge not found. Run: awr mmws csharp-bridge build")
        
    hw = get_local_hardware_config(exp.root_dir)
    com = hw.get("hardware", {}).get("awr_rs232_com")
    if com:
        console.print(f"[green]✓[/green] Local hardware config has awr_rs232_com: {com}")
        
        # Check heuristics
        ports = scan_ports()
        p_info = next((p for p in ports if p.com.upper() == com.upper()), None)
        if p_info:
            if p_info.likely_role == "dca_ftdi_candidate":
                console.print(f"[red]✗[/red] WARNING: {com} is identified as the DCA1000 FTDI port. This is usually wrong for AWR RS232.")
            elif p_info.likely_role == "awr_xds_uart_candidate":
                console.print(f"[yellow]![/yellow] WARNING: {com} is an XDS110 port. AWR2944 usually uses the FTDI port for mmWave Studio RS232.")
            else:
                console.print(f"[green]✓[/green] Port role seems acceptable: {p_info.likely_role}")
        else:
            console.print(f"[yellow]![/yellow] Port {com} is not currently visible in Windows Device Manager.")
            
    else:
        console.print("[red]✗[/red] Local hardware config missing awr_rs232_com. Run: awr ports scan")


def _run_diag_step(com_num: int, baud: int, mode: str, timeout: float, verbose: bool, steps: list[str], script_name: str) -> None:
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.mmws.lua_builder import write_connection_diag_script
    from awr2944_dca.mmws.executor import execute_script
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
    from awr2944_dca.mmws.stages import STATIC_CONFIG_FIELD_MAP, get_stage, StageName

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
    from awr2944_dca.mmws.executor import detect_available_modes

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
    from awr2944_dca.mmws.executor import execute_script, build_dofile_command, wait_for_result_json

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
    from awr2944_dca.mmws.bridge import StudioBridge, StageStatus

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
        from awr2944_dca.mmws.executor import build_dofile_command
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
    from awr2944_dca.mmws.executor import (
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
        "- `Init()` alone is NOT enough — `Connect('127.0.0.1', 2777)` is required",
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
    from awr2944_dca.mmws.executor import (
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
    from awr2944_dca.mmws.executor import run_rstd_introspect, _find_rtttnet_dll

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
    from awr2944_dca.mmws.executor import run_rstd_worker_test as _run_test

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
    from awr2944_dca.mmws.executor import run_rstd_get_last_error, _find_rtttnet_dll

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
    from awr2944_dca.mmws.executor import _find_mmws_exe
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
    from awr2944_dca.mmws.executor import (
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
    from awr2944_dca.mmws.executor import (
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
    from awr2944_dca.mmws.executor import build_dofile_command

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
    from .mmws.matlab_bridge import locate_matlab
    
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
    from .mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (ping)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dummy.lua"
        p.touch()
        res = _execute_matlab_bridge(p, verbose=verbose, timeout=30.0, bridge_mode="ping")
        
    if res.success:
        console.print("[green]✓ MATLAB bridge ping successful![/green]")
    else:
        console.print(f"[red]✗ MATLAB bridge ping failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)

@mmws_matlab_bridge_app.command("send-inline")
def mmws_matlab_bridge_send_inline(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test MATLAB-to-Studio send-inline command."""
    from .mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (send-inline)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dummy.lua"
        p.touch()
        res = _execute_matlab_bridge(p, verbose=verbose, timeout=30.0, bridge_mode="send-inline")
        
    if res.success:
        console.print("[green]✓ MATLAB bridge send-inline successful![/green]")
    else:
        console.print(f"[red]✗ MATLAB bridge send-inline failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)

@mmws_matlab_bridge_app.command("smoke")
def mmws_matlab_bridge_smoke(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test MATLAB-to-Studio RunScript via smoke script."""
    from .mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (smoke)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "smoke.lua"
        p.write_text("WriteToLog(\"SMOKE\\n\")", encoding="utf-8")
        res = _execute_matlab_bridge(p, verbose=verbose, timeout=30.0, bridge_mode="send-command")
        
    if res.success:
        console.print("[green]✓ MATLAB bridge smoke successful![/green]")
    else:
        console.print(f"[red]✗ MATLAB bridge smoke failed: {res.error}[/red]")
        if res.verbose_log:
            for line in res.verbose_log:
                console.print(line)
        raise typer.Exit(1)


@mmws_matlab_bridge_app.command("dofile-test")
def mmws_matlab_bridge_dofile_test(
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
) -> None:
    """Test MATLAB-to-Studio dofile command."""
    from .mmws.executor import _execute_matlab_bridge
    import tempfile
    from pathlib import Path
    
    console.print("[cyan]Testing MATLAB bridge (dofile-test)...[/cyan]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "dofile_test.lua"
        res_file = Path(d) / "matlab_dofile_test_result.json"
        p.write_text(f"WriteToLog(\"DOFILE_TEST\\\\n\")\nres_file=io.open([[{str(res_file).replace('\\\\', '/')}笑]], 'w')\nres_file:write('{{\"success\":true}}')\nres_file:close()", encoding="utf-8")
        # Wait, just write the result file properly
        lua_code = f"""
WriteToLog("DOFILE_TEST\\n")
local f = io.open([[{str(res_file).replace("\\", "/")}笑]], "w")
f:write('{{"success":true}}')
f:close()
""".replace("笑", "")
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
                    console.print("[green]✓ MATLAB bridge dofile-test successful![/green]")
                    return
                else:
                    console.print(f"[red]✗ MATLAB bridge dofile-test Lua result failed: {data}[/red]")
            except Exception as e:
                console.print(f"[red]✗ MATLAB bridge dofile-test JSON error: {e}[/red]")
        else:
            console.print("[red]✗ MATLAB bridge dofile-test failed: lua result json not found[/red]")
    else:
        console.print(f"[red]✗ MATLAB bridge dofile-test failed: {res.error}[/red]")
    
    if res.verbose_log:
        for line in res.verbose_log:
            console.print(line)
    raise typer.Exit(1)

# awr mmws lua-launch *
# ---------------------------------------------------------------------------

def _lua_launch_probe_dir() -> "Path":
    """Return (and create) the lua-launch probe_logs directory."""
    from pathlib import Path
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
    from .mmws.executor import _execute_lua_launch
    from .mmws.lua_builder import build_lua_launch_smoke
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
    from .mmws.executor import _execute_lua_launch
    from .mmws.lua_builder import build_lua_launch_env_probe
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
            "\n[yellow]ar1 is nil — /lua runs before Startup.lua initializes RadarAPI.\n"
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
    from awr2944_dca.mmws.executor import build_csharp_bridge

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
    from .mmws.executor import _execute_via_csharp_bridge
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
        console.print("[green]✓ C# bridge send-inline successful![/green]")
    else:
        console.print(f"[red]✗ C# bridge send-inline failed: {res.error}[/red]")
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
    from awr2944_dca.mmws.executor import _find_csharp_bridge, _find_rtttnet_dll, _RSTD_HOST, _RSTD_PORT

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
    from awr2944_dca.mmws.executor import _find_csharp_bridge, _find_rtttnet_dll

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
    from .mmws.executor import _execute_lua_launch
    from .mmws.lua_builder import build_lua_launch_startup_probe
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
    from .mmws.executor import _execute_lua_launch
    from .mmws.lua_builder import build_lua_launch_rstd_env_probe
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
    from .mmws.executor import _execute_lua_launch
    from .mmws.lua_builder import build_lua_launch_registerdll_probe
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
    from .mmws.executor import _execute_lua_launch
    from .mmws.lua_builder import build_lua_launch_startup_lite_probe
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
    from .mmws.executor import _execute_lua_launch, _is_mmws_running
    from .mmws.lua_builder import build_lua_launch_ar1_readonly_probe
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
    from .mmws.executor import _execute_lua_launch, _is_mmws_running
    from .mmws.lua_builder import build_lua_launch_connect_only
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

