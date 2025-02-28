# config/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Configuration
    API_URL = os.getenv("API_URL")
    API_AUTHORIZATION = os.getenv("API_AUTHORIZATION")
    
    # SSH Tunnel Configuration
    SSH_HOST = os.getenv("SSH_HOST")
    SSH_PORT = int(os.getenv("SSH_PORT"))
    SSH_USER = os.getenv("SSH_USER")
    SSH_PASSWORD = os.getenv("SSH_PASSWORD")
    
    # PostgreSQL Configuration
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = int(os.getenv("PG_PORT"))
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_DB = os.getenv("PG_DB")