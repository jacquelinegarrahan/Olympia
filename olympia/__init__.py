from pathlib import Path
import configparser
import os

ROOT_DIR = str(Path(__file__).parent.parent)

CONFIGS = configparser.SafeConfigParser()
CONFIGS.read(ROOT_DIR + "/config.ini") 

os.environ["AWS_PROFILE"]=CONFIGS["AWS"]["profile"]