import os
from pathlib import Path


APP_NAME = "MedInUse"
API_KEY_ENV_NAME = "MEDINUSE_API_KEY"


def user_config_dir() -> Path:
    root = os.getenv("APPDATA") or str(Path.home())
    return Path(root) / APP_NAME


def user_env_path() -> Path:
    return user_config_dir() / ".env"


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def local_env_path() -> Path:
    return project_root() / ".env"


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        key, value = clean.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config() -> dict[str, str]:
    values = {}
    values.update(_parse_env_file(local_env_path()))
    values.update(_parse_env_file(user_env_path()))

    for key, value in values.items():
        os.environ[key] = value

    return values


def get_api_key() -> str:
    load_config()
    return os.getenv(API_KEY_ENV_NAME, "")


def save_api_key(api_key: str) -> Path:
    user_config_dir().mkdir(parents=True, exist_ok=True)
    path = user_env_path()
    path.write_text(f'{API_KEY_ENV_NAME}="{api_key.strip()}"\n', encoding="utf-8")
    os.environ[API_KEY_ENV_NAME] = api_key.strip()
    return path
