# Probe Bundle Reports

`tools/report_probe_bundle.py` reads a zip created by `tools/collect_probe_artifacts.py` and
writes a Markdown summary of the bundled probe logs. It is an offline, read-only helper: it reads
only the zip file, does not call mmWave Studio, does not use UI automation, and does not import
hardware-facing project modules.

The report is useful when a bundle needs a quick triage pass before another person or tool digs
into the raw JSON and JSONL files.

## Create a Bundle

From the repository root, collect probe logs into a zip first:

```powershell
python tools/collect_probe_artifacts.py --probe-dir exp_lau_probe/ti/probe_logs --out artifacts/exp_lau_probe_bundle.zip
```

For the root probe log directory, or when sharing only recent files:

```powershell
python tools/collect_probe_artifacts.py --probe-dir ti/probe_logs --latest 30 --out artifacts/root_probe_latest_bundle.zip
```

Raw ADC `.bin` files are not included by the collector by default. If a report warns that `.bin`
files are present, treat that bundle as a manually assembled or otherwise unusual artifact.

## Generate a Report

Write the report to a Markdown file:

```powershell
python tools/report_probe_bundle.py --bundle artifacts/exp_lau_probe_bundle.zip --out artifacts/exp_lau_probe_report.md
```

Or write the report to stdout:

```powershell
python tools/report_probe_bundle.py --bundle artifacts/root_probe_latest_bundle.zip
```

The report includes bundle metadata, guided workflow state snapshots, run result summaries,
progress-log command summaries, validation records, and suspicious findings such as missing
manifests, raw `.bin` files, failed results, failed progress commands, and mismatches between
guided state and linked result files.

## Share a Report

Send the generated `.md` file when someone needs a readable triage summary. If the recipient needs
to verify hashes, reproduce parsing, or inspect full errors, also send the original bundle zip so
they can read `bundle_manifest.json` and the raw probe artifacts.

A report is not a replacement for hardware validation. It can summarize what the bundled logs say,
but it cannot prove that the device, firmware, capture card, or mmWave Studio session is currently
healthy.