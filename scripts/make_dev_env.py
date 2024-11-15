import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
base_dir = Path(__file__).resolve().parent.parent

# Specify the .env files to merge to target .env file
src_files = [
    os.path.join(base_dir, '.env', 'base.env'),
    os.path.join(base_dir, '.env', 'db.env'),
]
    
# Specify the target .env file
trg_file = os.path.join(base_dir, '.env', 'dev.env')


# Merge the contents
with open(trg_file, 'w') as outfile:
    for file in src_files:
        with open(file, 'r') as infile:
            outfile.write(infile.read() + '\n')

print(f"Merged {len(src_files)} .env files into {trg_file}")