"""Example 03: Open an existing capture.

Demonstrates opening a RadarProject and accessing a capture by ID.
Requires a real project directory with at least one capture.
"""

from pathlib import Path
from awr2944_dca.lab import RadarProject

# Open an existing project
project_dir = Path("./my_radar_project")
project = RadarProject.open(project_dir)

# List available captures
for cap in project.captures.list():
    print(f"  {cap.capture_id}  status={cap.status}")

# Access a specific capture (replace with your capture ID)
# capture = project.captures.get("20260714_231258_dca_capture")
# print(f"Capture path: {capture.path}")
