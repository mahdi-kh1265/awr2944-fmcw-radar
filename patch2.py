with open('src/awr2944_dca/cli.py', 'a', encoding='utf-8') as f:
    f.write('''

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
''')
