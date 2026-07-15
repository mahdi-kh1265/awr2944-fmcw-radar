import pytest
import shutil
from pathlib import Path
from awr2944_dca.lab import RadarProject

def test_radar_project_create(tmp_path):
    project = RadarProject.create(name="test_proj", parent=tmp_path)
    
    # Check structure
    assert (tmp_path / "test_proj" / "awr2944.toml").exists()
    assert (tmp_path / "test_proj" / ".awr2944" / "local.toml").exists()
    assert (tmp_path / "test_proj" / "profiles" / "smoke_v1.toml").exists()
    assert (tmp_path / "test_proj" / "captures").is_dir()
    assert (tmp_path / "test_proj" / "scripts").is_dir()
    assert (tmp_path / "test_proj" / "notebooks").is_dir()
    assert (tmp_path / "test_proj" / "README.md").exists()
    
    assert project.config.portable.project_name == "test_proj"

def test_radar_project_open(tmp_path):
    project = RadarProject.create(name="test_proj2", parent=tmp_path)
    
    project2 = RadarProject.open(tmp_path / "test_proj2")
    assert project2.root == tmp_path / "test_proj2"
    assert project2.config.portable.project_name == "test_proj2"

def test_radar_project_open_here(tmp_path, monkeypatch):
    project = RadarProject.create(name="test_proj3", parent=tmp_path)
    
    import os
    # Change current working directory to inside the project
    subdir = project.root / "captures" / "sub"
    subdir.mkdir(parents=True)
    
    monkeypatch.chdir(subdir)
    
    project3 = RadarProject.open_here()
    assert project3.root == project.root
