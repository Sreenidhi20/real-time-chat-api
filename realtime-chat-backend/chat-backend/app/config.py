import os

from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")


if not database_url:
	raise RuntimeError("DATABASE_URL is not configured")

DATABASE_URL: str = database_url
