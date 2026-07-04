import subprocess
from app_utils import find_application
import string
from config import STOP_WORDS

#APPS = {
#    "notepad": "notepad",
#    "calculator": "calc",
#    "paint": "mspaint",
#}

NAME = "Timer"

INTENT = "timer"

DESCRIPTION = "Starts a timer"

VERSION = "1.0"

AUTHOR = "Harshith"

def execute(task):

    print("⏰ Timer skill executed!")