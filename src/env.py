import os
from dotenv import load_dotenv

# load environment variables
def get_required_env_variables(var_names):
    # use dotenv to load environment variables from .env file
    if os.path.exists(".env"):
        load_dotenv()
    env_vars = {}
    for var_name in var_names:
        try:
            env_vars[var_name] = os.environ[var_name]
        except KeyError:
            raise ValueError(f"Required environment variable '{var_name}' is not set.")
    return env_vars
