import click
import uvicorn
from ocr_miner.logger import setup_logger
import logging
from multiprocessing import cpu_count
import pathlib
from ocr_miner.config import UPLOAD_FOLDER


def create_required_folders():
    """Create data/uploads folder for save image to this path.
    This path is required.
    """
    p = pathlib.Path(f"./{UPLOAD_FOLDER}")
    p.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        raise FileNotFoundError(
            f"Required folder : {UPLOAD_FOLDER} \n Not found ! Please manually create"
        )


# call function for check and create required folders
create_required_folders()
# initialize looger
setup_logger(logger_name="Ocr miner logger", logfile="ocr_miner.log")


@click.group()
def ocr_miner():
    click.echo("Ocr_miner V1.0")


@ocr_miner.command()
@click.option("--api", "-a", is_flag=True, help="Run api service")
def manage(api: bool):
    """Ioc richer manage cli"""
    if api:
        logging.info("Api started !")
        uvicorn.run(
            "ocr_miner.api.ocr_miner_api:APP",
            workers=cpu_count(),
            host="0.0.0.0",
            port=8000,
            # reload=True,
        )  # enable reload for development purposes
