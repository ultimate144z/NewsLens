# Helper functions used across modules
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

def load_config(config_name: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_name: Name of config file (without .yaml extension)
        
    Returns:
        Dictionary containing configuration
    """
    config_path = Path(__file__).parent.parent / "config" / f"{config_name}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_env_variable(var_name: str, default: str = None) -> str:
    """
    Get environment variable with optional default
    
    Args:
        var_name: Name of environment variable
        default: Default value if not found
        
    Returns:
        Value of environment variable
    """
    value = os.getenv(var_name, default)
    
    if value is None:
        raise ValueError(f"Environment variable {var_name} not found and no default provided")
    
    return value


def ensure_dir_exists(directory: Path) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Path to directory
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent


def get_data_dir(subdir: str = None) -> Path:
    """
    Get path to data directory
    
    Args:
        subdir: Optional subdirectory (raw, processed, etc.)
        
    Returns:
        Path to data directory
    """
    data_dir = get_project_root() / "data"
    
    if subdir:
        data_dir = data_dir / subdir
        
    ensure_dir_exists(data_dir)
    return data_dir
