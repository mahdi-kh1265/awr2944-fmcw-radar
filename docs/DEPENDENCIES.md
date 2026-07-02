# Dependencies

Preferred stack:

- Python 3.12+
- uv for package management
- Typer + Rich for CLI
- Pydantic v2 for config validation
- NumPy + SciPy for core DSP
- xarray for labelled cubes
- Zarr/HDF5 for large array storage
- Polars/Parquet for tables, detections, sweep summaries
- Matplotlib for static figures
- Plotly + Streamlit/Dash for dashboard/replay/live preview
- pytest + hypothesis for tests
- Ruff for lint/format
- MATLAB Engine API optional only

Do not make MATLAB required for core operation.
