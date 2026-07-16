"""Example 01: Create a new radar project directory."""

from pathlib import Path
from awr2944_dca.lab import RadarProject

# Create a project in a temporary directory
project_dir = Path("./my_radar_project")
project = RadarProject.create(project_dir, name="example-project")

print(f"Project created at: {project.root}")
print(f"Project name: {project.name}")
