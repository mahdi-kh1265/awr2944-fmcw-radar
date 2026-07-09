# Probe Artifact Bundles

Use `tools/collect_probe_artifacts.py` after a failed or suspicious mmWave Studio / AWR2944
probe run when another person or tool needs the logs. The helper only reads the probe log
directory and writes a zip bundle somewhere else; it does not import project hardware modules,
call mmWave Studio, use UI automation, or change the probe logs.

Run it before cleaning up logs or rerunning a workflow that may overwrite the evidence you want
to inspect.

## What gets included

The bundle includes common probe diagnostics:

- `guided_*_state.json`
- `*_manifest.json`
- `*_result.json`
- `*_progress.jsonl`
- `*_snapshot.txt`
- `manual_check_*`
- `gui_connect_windows.txt`
- `validation_*.json`

Each zip also contains `bundle_manifest.json`, which lists every bundled file, its size,
modified time, and SHA-256 hash. Use that manifest to verify that a received zip matches the
files that were collected.

Raw ADC capture files such as `.bin` files are intentionally not included by default. Those files
can be very large and usually need a separate sharing decision.

## Examples

From the repository root, when logs live under `ti/probe_logs`:

```powershell
python tools/collect_probe_artifacts.py --probe-dir ti/probe_logs --out artifacts/debug_bundle.zip
```

To collect only files modified in the last 30 minutes:

```powershell
python tools/collect_probe_artifacts.py --probe-dir ti/probe_logs --latest 30 --out artifacts/latest_probe_bundle.zip
```

From the repository root, when using the `exp_lau_probe` workspace:

```powershell
python tools/collect_probe_artifacts.py --probe-dir exp_lau_probe/ti/probe_logs --out artifacts/debug_bundle.zip
```

The long option is equivalent to `--latest`:

```powershell
python tools/collect_probe_artifacts.py --probe-dir exp_lau_probe/ti/probe_logs --latest-minutes 30 --out artifacts/latest_probe_bundle.zip
```

Write the output zip outside the probe log directory. If the output path is inside `--probe-dir`,
the helper refuses to run so the source log directory stays read-only.

## Sending a Bundle

Send the generated `.zip` file as the attachment or artifact. If the receiving tool can access the
same filesystem, provide the full path to the zip. Keep `bundle_manifest.json` inside the archive;
it gives the recipient the file list, sizes, modified times, and hashes needed to discuss exactly
which probe attempt was packaged.