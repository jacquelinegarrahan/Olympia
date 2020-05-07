from pathlib import Path
import configparser
import os
import logging

# create logger
logger = logging.getLogger("olympia")
logger.setLevel(logging.DEBUG)

ROOT_DIR = str(Path(__file__).parent.parent.absolute())

CONFIGS = configparser.SafeConfigParser()
CONFIGS.read(ROOT_DIR + "/config.ini")

os.environ["AWS_PROFILE"] = CONFIGS["AWS"]["profile"]
