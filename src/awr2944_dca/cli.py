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
    import datetime

    import yaml

    from awr2944_dca import __version__
    from awr2944_dca.config.presets import get_preset, list_presets

    try:
        preset_dict = get_preset(preset)
    except KeyError:
        console.print(
            f"[red]Unknown preset '{preset}'.[/red] "
            f"Available: {list_presets()}"
        )
        raise typer.Exit(code=1)

    # Override experiment name
    preset_dict["experiment"]["name"] = name

    exp_dir = root / name
    if exp_dir.exists():
        console.print(f"[red]Directory already exists: {exp_dir}[/red]")
        raise typer.Exit(code=1)

    # Create directory structure
    dirs = [
        exp_dir / "raw",
        exp_dir / "ti_config",
        exp_dir / "screenshots",
        exp_dir / "compare_layouts",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Write capture.yaml
    capture_path = exp_dir / "capture.yaml"
    header = (
        f"# Experiment: {name}\n"
        f"# Preset: {preset}\n"
        f"# Generated by awr2944_dca v{__version__}\n\n"
    )
    yaml_str = yaml.dump(preset_dict, default_flow_style=False, sort_keys=False)
    capture_path.write_text(header + yaml_str, encoding="utf-8")

    # Write manifest.yaml
    manifest = {
        "experiment": name,
        "preset": preset,
        "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool_version": __version__,
        "status": "initialized",
        "notes": "",
    }
    manifest_path = exp_dir / "manifest.yaml"
    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    # Write notes.md template
    notes_path = exp_dir / "notes.md"
    notes_path.write_text(
        f"# {name}\n\n"
        f"## Setup Notes\n\n"
        f"- Preset: {preset}\n"
        f"- Date: \n"
        f"- Operator: \n\n"
        f"## Observations\n\n"
        f"## Issues\n\n",
        encoding="utf-8",
    )

    console.print(f"[green]OK[/green] Experiment initialized: {exp_dir}")
    console.print(f"  capture.yaml  — edit before capture")
    console.print(f"  manifest.yaml — auto-generated metadata")
    console.print(f"  notes.md      — your lab notes")
    console.print(f"  raw/          — place adc_data.bin here")
    console.print(f"  ti_config/    — place TI Lua/JSON files here")
    console.print(f"  screenshots/  — mmWave Studio screenshots")
    console.print(f"  compare_layouts/ — compare-layouts output")


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
