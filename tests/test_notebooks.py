import sys
from pathlib import Path

def test_notebooks_importable(tmp_path):
    # Ensure notebooks can be parsed and do not execute hardware commands
    import json
    
    notebooks_dir = Path("notebooks")
    if not notebooks_dir.exists():
        return
        
    for nb_path in notebooks_dir.glob("*.ipynb"):
        content = json.loads(nb_path.read_text(encoding="utf-8"))
        for cell in content.get("cells", []):
            if cell["cell_type"] == "code":
                source = "".join(cell["source"])
                # We expect the notebooks to use the API
                if "awr2944_dca" in source:
                    assert "ar1." not in source  # No direct hardware commands
