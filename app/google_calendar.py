from fastapi import FastAPI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
logger.debug(f"Loading environment variables from: {env_path}")
load_dotenv(dotenv_path=env_path)

# Log the environment variable to verify it is loaded correctly
google_service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
logger.debug(f"GOOGLE_SERVICE_ACCOUNT_FILE: {google_service_account_file}")

SCOPES = ['https://www.googleapis.com/auth/calendar']

app = FastAPI()

def get_google_calendar_service():
    try:
        if google_service_account_file is None:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable is not set")
        logger.debug(f"Service account file path: {google_service_account_file}")

        # Check if the file exists
        if not os.path.exists(google_service_account_file):
            raise FileNotFoundError(f"Service account file not found: {google_service_account_file}")

        credentials = service_account.Credentials.from_service_account_file(
            google_service_account_file,
            scopes=SCOPES
        )
        return build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        logger.error(f"Error setting up Google Calendar service: {e}")
        return None