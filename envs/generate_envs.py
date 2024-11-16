import os
import argparse
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_PATH = os.path.join(BASE_DIR, "static")
MEDIA_PATH = os.path.join(BASE_DIR, "media")
DATA_PATH = os.path.join(BASE_DIR, "db")

# Determine the system's platform (Windows or Linux)
if os.name == 'nt':  # Windows
    STATIC_PATH_ENV = STATIC_PATH.replace("C:\\", "/c/").replace("\\", "/")
    MEDIA_PATH_ENV = MEDIA_PATH.replace("C:\\", "/c/").replace("\\", "/")
    DATA_PATH_ENV = DATA_PATH.replace("C:\\", "/c/").replace("\\", "/")
else:  # Linux
    STATIC_PATH_ENV = STATIC_PATH
    MEDIA_PATH_ENV = MEDIA_PATH
    DATA_PATH_ENV = DATA_PATH

# Template directory
TEMPLATE_DIR = os.path.join(BASE_DIR, "envs", "templates")
ENV_DIR = os.path.join(BASE_DIR, ".env")


def read_env_file(file_path):
    """Reads a .env file and returns its content as a dictionary."""
    env_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_dict[key] = value
    return env_dict


def merge_dicts(*dicts):
    """Merges multiple dictionaries, with later dictionaries overriding earlier ones."""
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged


def write_env_file(file_path, env_dict, should_replace):
    """Writes a dictionary to a .env file. Skips if file exists and should_replace is False."""
    if os.path.exists(file_path) and not should_replace:
        print(f"Skipped {file_path} (file exists, use --replace to overwrite)")
        return
    with open(file_path, 'w') as file:
        for key, value in env_dict.items():
            file.write(f"{key}={value}\n")
    print(f"Generated {file_path}")


def generate_dev_env(info, target_dir, replace):
    """Generates dev.env file based on the merged info."""
    target_path = os.path.join(target_dir, 'dev.env')
    should_replace = replace in ('all', 'dev')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    write_env_file(target_path, info, should_replace)


def generate_prod_env(info, target_dir, replace):
    """Generates prod.env file based on the merged info."""
    target_path = os.path.join(target_dir, 'prod.env')
    should_replace = replace in ('all', 'prod')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    write_env_file(target_path, info, should_replace)


def generate_db_env(info, target_dir, replace):
    """Generates db.env file based on the db info."""
    target_path = os.path.join(target_dir, 'db.env')
    should_replace = replace in ('all', 'db')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    write_env_file(target_path, info, should_replace)


def main():
    parser = argparse.ArgumentParser(
        description="Generate .env files from templates."
    )
    parser.add_argument(
        '--target_dir',
        type=str,
        default=ENV_DIR,
        help=f"Target directory to save .env files (default: {ENV_DIR})."
    )
    parser.add_argument(
        '--replace',
        type=str,
        choices=['all', 'prod', 'dev', 'db'],
        default=None,
        help="Specify which files to replace: all, prod, dev, or db (default: skip existing files)."
    )    
    args = parser.parse_args()

    target_dir = args.target_dir
    replace = args.replace

    # Read source .env files into dictionaries
    base = read_env_file(os.path.join(TEMPLATE_DIR, 'base.env'))
    dev = read_env_file(os.path.join(TEMPLATE_DIR, 'dev.env'))
    prod = read_env_file(os.path.join(TEMPLATE_DIR, 'prod.env'))
    ver = read_env_file(os.path.join(TEMPLATE_DIR, 'ver.env'))
    db = read_env_file(os.path.join(TEMPLATE_DIR, 'db.env'))

    # Add dynamic paths to the base dict
    base.update({
        'STATIC_PATH': STATIC_PATH_ENV,
        'MEDIA_PATH': MEDIA_PATH_ENV,
        'DATA_PATH': DATA_PATH_ENV,
    })

    # Prepare merged dictionaries for each target file
    dev_info = merge_dicts(dev, base, db, ver)
    prod_info = merge_dicts(prod, base, ver)
    db_info = db

    # Generate target .env files
    generate_dev_env(dev_info, target_dir, replace)
    generate_prod_env(prod_info, target_dir, replace)
    generate_db_env(db_info, target_dir, replace)


if __name__ == "__main__":
    main()