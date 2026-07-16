# Legacy mmWave Studio Automation

This project previously utilized a bridge to the TI mmWave Studio GUI for configuration and capture triggers. This involved:
- A C# \RSTD\ bridge (\MmwsRstdBridge.exe\)
- Automated generation of \.lua\ scripts
- \pywinauto\ based GUI automation

**Status: Retired**

The entire mmWave Studio automation stack has been removed in favor of the decoupled, headless \sdk_demo_uart_cli\ transport. Production configurations and data captures are now performed without invoking the mmWave Studio GUI.

## Recovery

If legacy mmWave Studio components, scripts, or probes are needed for reference, they have been preserved in:
- Git Tag/Branch: \rchive/pre-cleanup-2026-07-15- External ZIP: \wr2944-historical-archives/historical_archive.zip\ (stored securely off-repository)

All related source modules (\wr2944_dca.legacy_mmws\), tests, CLI commands, and Lua templates have been removed from the \main\ branch.
