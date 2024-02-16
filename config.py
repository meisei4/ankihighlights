import os
from dotenv import load_dotenv

load_dotenv('.env')

ENVIRONMENT = os.getenv('FLASK_ENV', 'testing')

if ENVIRONMENT == "testing":
    load_dotenv('.env.local', override=True)
elif ENVIRONMENT == "production":
    load_dotenv('..env.container', override=True)
