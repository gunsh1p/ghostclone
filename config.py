import os

from dotenv import load_dotenv

load_dotenv()

API_BASE = os.environ.get("API_BASE", "https://git.culab.ru/api/v4")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
if ACCESS_TOKEN is None:
    raise ValueError("ACCESS_TOKEN can't be None")
PROJECT_TEMPLATE_BASE = os.environ.get(
    "PROJECT_TEMPLATE_BASE",
    "courses/fundamentals-of-industrial-programming-2025/fundamentals-of-industrial-programming-2025-",
)
PROJECTS_REGEX_BASE = os.environ.get(
    "PROJECTS_REGEX_BASE",
    "^courses/fundamentals-of-industrial-programming-2025/fundamentals-of-industrial-programming-2025-\\d+/(Java|Golang|Python)+$",
)
TECH_TASKS_REGEX_BASE = os.environ.get(
    "TECH_TASKS_REGEX_BASE",
    "https://git\\.culab\\.ru/bsc-development-basics-2nd-semester/dev-basics-2025-longreads/[^\\s)]+",
)
