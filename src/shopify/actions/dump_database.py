"""Action for dumping the Postgres database to a timestamped SQL file"""

import subprocess
from datetime import datetime
from pathlib import Path

from src.lib.logger import logger


def dump_database(output_dir: str = "./dumps"):
    """Dump the database to a timestamped SQL file via docker exec."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = out_path / f"dump-coop-{timestamp}.sql"

    logger.info(f"Dumping database to {filename}")

    with open(filename, "w", encoding="utf-8") as f:
        result = subprocess.run(
            [
                "docker", "exec", "-t", "azure-db",
                "pg_dump", "-U", "root", "-d", "azure",
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            check=False,
        )

    if result.returncode != 0:
        logger.error(f"pg_dump failed: {result.stderr.decode()}")
        filename.unlink(missing_ok=True)
        raise RuntimeError("Database dump failed")

    logger.success(f"Database dumped to {filename}")
    return filename
