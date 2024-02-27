import os
from dotenv import load_dotenv

def load_environment():
    ENVIRONMENT = os.getenv('FLASK_ENV', 'testing')
 # TODO: figure out how to load based on env context vv
    if ENVIRONMENT == "testing":
        dotenv_path = '.env.local'
    elif ENVIRONMENT == "production":
        dotenv_path = '.env.container'
    else:
        dotenv_path = '.env'  # default to the main .env file

    load_dotenv()
