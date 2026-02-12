
import importlib
import importlib.util
import os
from pydantic_settings import BaseSettings

PACKAGE_NAME: str = "pingme"  # Make sure to adjust this to your package name
DEV_MODE: bool = (
    False  # set below to override, as this is in an export block it'll be exported while the dev mode section is not
)

PACKAGE_DIR = None
try:
    spec = importlib.util.find_spec(PACKAGE_NAME)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    PACKAGE_DIR = os.path.dirname(module.__file__)
except ImportError:
    DEV_MODE = True
except AttributeError:
    DEV_MODE = True
PROJECT_DIR = os.getcwd()  # override value in dev mode
if PROJECT_DIR.endswith("nbs"):
    DEV_MODE = True
    PROJECT_DIR = os.path.split(PROJECT_DIR)[0]


class Settings(BaseSettings):
    """
    Base settings class for the package, primarily to gain config_file for dev mode through pydantic
    """

    app_name: str = "PingMe"
    config_file: str = ""

    @classmethod
    def create(cls):
        """Factory method to create settings based on environment"""
        if DEV_MODE:
            return cls(config_file=f"{PROJECT_DIR}/config/config.env")
        else:
            return cls()


settings = Settings().create()

import logging
import os
import sys


# Set up logging
def setup_logging(log_level=None):
    """Configure logging for the application
    
    Args:
        log_level (logging.Level): The logging level to use, if None it will default to DEBUG in dev mode and INFO in production mode
    """
    log_level = log_level or (logging.DEBUG if DEV_MODE else logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if DEV_MODE:
        log_dir = os.path.join(PROJECT_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(log_dir, "pingme.log"))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Create a logger for pingme
    logger = logging.getLogger("pingme")

    return logger


# Initialize logger
logger = setup_logging()


import os
import sys

# Common to template
# add into settings.ini, requirements, package name is python-dotenv, for conda build ensure `conda config --add channels conda-forge`
import dotenv  # for loading config from .env files, https://pypi.org/project/python-dotenv/
import envyaml  # Allows to loads env vars into a yaml file, https://github.com/thesimj/envyaml

from fastcore.script import call_parse

# Project specific libraries
import shutil  # using shell utilities


def set_env_variables(config_path: str, overide_env_vars: bool = True) -> bool:
    """
    Load dot env sets environmental values from a file, if the value already exists it will not be overwritten unless override is set to True.
    If we have multiple .env files then we need to apply the one which we want to take precedence last with overide.

    Order of precedence: .env file > environment variables > default values
    When developing, making a change to the config will not be reflected until the environment is restarted

    Set the env vars first, this is needed for the card.yaml to replace ENV variables
    NOTE: You need to adjust PROJECT_NAME to your package name for this to work, the exception is only for dev purposes
    This here checks if your package is installed, such as through pypi or through pip install -e  [.dev] for development. If it is then it'll go there and use the config files there as your default values.

    Args:
        config_path (str): path to the config file
        overide_env_vars (bool): if True, will overwrite existing env variables

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        dotenv.load_dotenv(f"{PACKAGE_DIR}/config/config.default.env", override=False)
    except Exception as e:
        print(f"Error: {PACKAGE_DIR}/config/config.default.env does not exist")
        return False

    # 2. set values from file:
    if os.path.isfile(config_path):
        dotenv.load_dotenv(config_path, override=overide_env_vars)

    return True


def get_config(config_path: str = None, overide_env_vars: bool = True) -> dict:
    """
    Load the config.env from the config path, the config.env should reference the config.yaml file, which will be loaded and returned as
    a dictionary. The config.yaml file should be in the same directory as the config.env file.

    Args:
        config_path (str): The path to the config.env file
        overide_env_vars (bool): If the env vars should be overriden by the config.yaml file

    Returns:
        dict: The config.yaml file as a dictionary, it'll also replace any ENV variables in the yaml file
    """
    if config_path is None:
        config_path = ""
    # First sets environment with variables from config_path, then uses those variables to fill in appropriate values in the config.yaml file, the yaml file is then returned as a dict
    # If you want user env variables to take precedence over the config.yaml file then set overide_env_vars to False
    set_env_variables(config_path, overide_env_vars)

    config: dict = envyaml.EnvYAML(
        os.environ.get(
            "CORE_YAML_CONFIG_FILE", f"{PACKAGE_DIR}/config/config.default.yaml"
        ),
        strict=False,
    ).export()
    

    
    # loop through all environmental variables and print the ones with "WEBHOOK" in the name
    prefix = 'PINGME_WEBHOOK_URL_'
    for k, v in os.environ.items():
        if k.startswith(prefix):
            channel_name = k[len(prefix):].lower()
            config["pingme"]["options"]["webhook"]["channels"][channel_name] = v

    
    return config


# create a os.PathLike object
config = get_config(os.environ.get("CORE_CONFIG_FILE", ""))


def show_project_env_vars(config: dict) -> None:
    """
    Show all the project environment variables, this is useful for debugging and seeing what is being set

    Args:
        config (dict): The dictionary of all the environment variables

    Returns:
        None
    """
    for k, v in config.items():
        # If ENV var starts with PROJECTNAME_ then print
        if k.startswith(config["CORE_PROJECT_VARIABLE_PREFIX"]):
            print(f"{k}={v}")



def tool_is_present(tool_name: str) -> bool:
    """
    Check if a tool is present in the current environment

    Args:
        tool_name (str): The name of the tool to check

    Returns:
        bool: True if the tool is present, False otherwise
    """
    return shutil.which(tool_name) is not None

def tools_are_present(tool_names: list) -> bool:
    """
    Check if all tools are present in the current environment

    Args:
        tool_names (list): A list of tools to check

    Returns:
        bool: True if all tools are present, False otherwise
    """
    tools_present: bool = True
    for tool in tool_names:
        if not tool_is_present(tool):
            print(f"Tool {tool} is not present in current environment", file=sys.stderr)
            tools_present = False
    return tools_present


def hello_world(name: str = "Not given") -> str:
    """
    A simple function that returns a hello world message with a name, for testing purposes
    """
    return f"Hello World! My name is {name}"

@call_parse
def cli(
    name: str,  # Your name
    config_file: str = None,  # config file to set env vars from
):
    """
    This will print Hello World! with your name

    Args:
        name (str): Your name
        config_file (str): The path to the config file, if not provided it will use the default config file
    """
    config = get_config(config_file)  # Set env vars and get config variables
    if name is not None:
        config["example"]["input"]["name"] = name

    print(hello_world(config["example"]["input"]["name"]))




