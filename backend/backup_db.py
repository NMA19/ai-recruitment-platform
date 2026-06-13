import os
import shutil
from datetime import datetime, UTC

from database import get_db_path


def main():
    source = get_db_path()
    if not os.path.exists(source):
        raise SystemExit(f"Database not found: {source}")

    backup_dir = os.environ.get("BACKUP_DIR", os.path.join(os.path.dirname(__file__), "backups"))
    os.makedirs(backup_dir, exist_ok=True)

    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    target = os.path.join(backup_dir, f"wassit-{stamp}.db")
    shutil.copy2(source, target)
    print(target)


if __name__ == "__main__":
    main()