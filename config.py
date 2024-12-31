import yaml
from pathlib import Path
import bcrypt

def load_config():
    config_path = Path(".streamlit/config.yaml")
    if config_path.exists():
        with open(config_path) as file:
            return yaml.safe_load(file)
    return {"users": {}}

def save_config(config):
    config_path = Path(".streamlit/config.yaml")
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, "w") as file:
        yaml.dump(config, file)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())