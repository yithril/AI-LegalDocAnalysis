from dynaconf import Dynaconf
from pathlib import Path

# Get the config directory path
config_path = Path(__file__).parent / "files"

# Initialize Dynaconf
settings = Dynaconf(
    envvar_prefix="LDA",
    settings_files=[
        str(config_path / "settings.toml"),      # Default/base settings
        str(config_path / "development.toml"),   # Development overrides
        str(config_path / "production.toml"),    # Production overrides
    ],
    environments=True,
    load_dotenv=True,
) 