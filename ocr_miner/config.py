from dynaconf import Dynaconf
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
settings = Dynaconf(
    load_dotenv=True,
    dotenv_path=ROOT_DIR.joinpath("envs", ".env"),
    envvar_prefix_for_dynaconf=False,
)
HOST = settings("HOST")
REDIS_HOST = settings("REDIS_HOST")
USERNAME = settings("USERNAME")
PASSWORD = settings("PASSWORD")
UPLOAD_FOLDER = settings("UPLOAD_FOLDER")
CLOUDFLARE_TURNSTILE = settings("CLOUDFLARE_TURNSTILE")
REDIS_PASSWORD=settings("REDIS_PASSWORD")