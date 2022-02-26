from src.db.postgres import *
import os
from pathlib import Path

db = DBUtils()

ddl_path = os.path.dirname(os.path.realpath(__file__)) + '/../sql'

files = os.listdir(str(ddl_path))
files.sort()

print(files)

for file_name in files:
    file_path = Path(ddl_path) / file_name
    with open(str(file_path), 'r', encoding="utf-8") as f:
        script = f.read()
        print()
        print(script)

        db.execute(script)
        print('Done!')

db.close()
