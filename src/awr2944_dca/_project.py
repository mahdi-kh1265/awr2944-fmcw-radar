import subprocess
import logging
from pathlib import Path

# Note: We will import RadarProject dynamically or inject it to avoid circular imports during transition.
logger = logging.getLogger(__name__)

def _create_project(project_root: Path, name: str, git_init: bool = False):
    """Internal implementation for creating a new RadarProject."""
    from awr2944_dca.lab import RadarProject
    import uuid
    
    if project_root.exists():
        raise FileExistsError(f"Cannot create project: {project_root} already exists.")
        
    project_root.mkdir(parents=True)
    
    if git_init:
        try:
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
        except FileNotFoundError:
            logger.warning("git not found, skipping git initialization.")
        except subprocess.CalledProcessError as e:
            logger.warning(f"git init failed: {e.stderr}")
            
    # Always write .gitignore
    gitignore_path = project_root / ".gitignore"
    with open(gitignore_path, "w") as f:
        f.write("# AWR2944 Ignore rules\n")
        f.write("# Machine-local configuration\n")
        f.write(".awr2944/local.toml\n\n")
        f.write("# Capture data\n")
        f.write("captures/\n\n")
        f.write("# Binary artifacts\n")
        f.write("*.bin\n")
        f.write("*.dat\n")
        f.write("*.mat\n")
        f.write("*.npy\n")
        f.write("*.npz\n\n")
        f.write("# Executed notebooks\n")
        f.write("*_executed.ipynb\n")
        f.write("*_output.ipynb\n\n")
        f.write("# Temporary artifacts\n")
        f.write("__pycache__/\n")
        f.write("*.pyc\n")
        f.write(".pytest_cache/\n")
            
    # Initialize configuration
    from awr2944_dca._config import ProjectConfig
    config = ProjectConfig(project_root)
    config.portable.project_name = name
    config.portable.project_id = uuid.uuid4().hex[:12]
    config.save()
    
    # Create standard directories
    (project_root / "profiles").mkdir(exist_ok=True)
    (project_root / "captures").mkdir(exist_ok=True)
    (project_root / "scripts").mkdir(exist_ok=True)
    (project_root / "notebooks").mkdir(exist_ok=True)
    
    # Write a default profile
    default_profile = project_root / "profiles" / "smoke_v1.toml"
    with open(default_profile, "w") as f:
        f.write("# Default smoke profile\n[profile]\nname = \"smoke_v1\"\n")
        
    # Write README
    readme_path = project_root / "README.md"
    with open(readme_path, "w") as f:
        f.write(f"# {name}\n\n")
        f.write("AWR2944 radar project. See `awr2944.toml` for portable configuration.\n")
        
    return RadarProject(project_root)


def create_project(name: str, parent: str | Path, git_init: bool = False):
    """
    Create a new project.
    Creates <parent>/<name>/ with full scaffolding.
    Raises FileExistsError if the directory already exists.
    """
    base_path = Path(parent).resolve()
    project_root = base_path / name
    return _create_project(project_root, name, git_init)


def create_project_at(path: str | Path, git_init: bool = False):
    """
    Create a new project at an exact path.
    The directory's basename becomes the project name.
    Raises FileExistsError if the directory already exists.
    """
    project_root = Path(path).resolve()
    return _create_project(project_root, project_root.name, git_init)


def open_project(path: str | Path):
    """
    Opens a RadarProject at the explicit path.
    """
    from awr2944_dca.lab import RadarProject
    
    project_root = Path(path).resolve()
    if not project_root.is_dir():
        raise FileNotFoundError(f"Project directory not found: {project_root}")
        
    # Check for awr2944.toml or project.json
    has_toml = (project_root / "awr2944.toml").exists()
    has_json = (project_root / "project.json").exists()
    
    if not (has_toml or has_json):
        raise FileNotFoundError(f"Not a valid RadarProject (missing awr2944.toml or project.json): {project_root}")
        
    return RadarProject(project_root)


def open_project_here():
    """
    Auto-discovers the project root starting from the current working directory.
    Walks up the directory tree looking for awr2944.toml or project.json.
    """
    from awr2944_dca.lab import RadarProject
    
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / "awr2944.toml").exists() or (current / "project.json").exists():
            return RadarProject(current)
        current = current.parent
        
    raise FileNotFoundError("Could not find a RadarProject in the current directory or any parent.")
