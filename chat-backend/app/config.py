import os

from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")


if not database_url:
	raise RuntimeError("DATABASE_URL is not configured")

DATABASE_URL: str = database_url

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
	raise RuntimeError("JWT_SECRET is not configured")

CORS_ORIGINS = [
	origin.strip()
	for origin in os.getenv(
		"CORS_ORIGINS",
		"http://localhost:3000,http://localhost:5173",
	).split(",")
	if origin.strip()
]

ALGORITHM = "HS256"
