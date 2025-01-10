import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = "ft:gpt-4o-mini-2024-07-18:cylabafrica-ml-team::AnjdsoKG"

ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")
