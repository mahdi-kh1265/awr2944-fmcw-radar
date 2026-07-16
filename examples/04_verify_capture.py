"""Example 04: Verify capture integrity.

Shows how to run the capture verification pipeline, which checks
file hashes, ADC data integrity, and metadata completeness.
"""

from pathlib import Path
from awr2944_dca.lab import RadarProject

# Open a project with captures
project_dir = Path("./my_radar_project")
project = RadarProject.open(project_dir)

# Verify all captures
for cap in project.captures.list():
    result = cap.verify()
    status = "PASS" if result.success else "FAIL"
    print(f"  {cap.capture_id}: {status}")
    if not result.success:
        for err in result.errors:
            print(f"    - {err}")
