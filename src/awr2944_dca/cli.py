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
def ports_scan() -> None:
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
    table.add_column("Role", style="cyan")
    table.add_column("Confidence")
    
    for p in ports:
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
    mmws_connection_script(com=com, baud=baud, timeout_ms=timeout_ms)


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
def mmws_connection_script(
    com: str = typer.Option(None, "--com", help="COM port (e.g., COM6)"),
    baud: int = typer.Option(921600, "--baud", help="Baud rate"),
    timeout_ms: int = typer.Option(1000, "--timeout-ms", help="Connect timeout in ms"),
) -> None:
    """Generate a connection-only Lua script for mmWave Studio."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.mmws.bridge import ManualOneShotBridge
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
    bridge = ManualOneShotBridge(log_dir)
    script = bridge.generate_connection_script(com_num, baud, timeout_ms)

    console.print(f"[green]Generated {script.name}[/green] (COM{com_num}, baud={baud})")
    console.print("Run it in mmWave Studio Lua Shell:")
    console.print(f"  [cyan]awr ti lua-command {script} --copy[/cyan]")
    console.print("Then check: [cyan]awr mmws connection status[/cyan]")


@mmws_conn_app.command("status")
def mmws_connection_status() -> None:
    """Check the result of the connection-only stage."""
    from awr2944_dca.api.experiment import Experiment
    from awr2944_dca.mmws.bridge import ManualOneShotBridge, StageStatus
    from awr2944_dca.mmws.stages import StageName

    try:
        exp = Experiment.open(".")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)

    log_dir = exp.root_dir / "ti" / "probe_logs"
    bridge = ManualOneShotBridge(log_dir)
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

