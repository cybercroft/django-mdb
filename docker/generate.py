import os
import argparse
from pathlib import Path


def load_env(env_file):
    """Load environment variables from a file."""
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        raise FileNotFoundError(f"Environment file '{env_file}' not found.")
    return env_vars

def check_paths(env_vars, keys):
    """Check if paths for the given keys exist. Create missing directories."""
    missing_paths = []
    for key in keys:
        path = env_vars.get(key)
        if path:
            # Normalize Windows paths for validation
            normalized_path = path.replace('/c/', 'C:\\').replace('/', '\\') if os.name == 'nt' else path
            dir_path = Path(normalized_path)

            # Check if the path exists; if not, try to create iti
            if dir_path.exists():
                print(f"[{key}] path exists: {dir_path}")
            else:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"[{key}] creating Path: {dir_path}")
                except Exception as e:
                    print(f"[{key}] Failed creating Path: {dir_path} ({e})")
                    missing_paths.append(key)
    return missing_paths

def generate_compose(template_path, output_path, env_vars):
    """Generate the docker-compose.yml file from the template."""
    try:
        with open(template_path, 'r') as template_file:
            content = template_file.read()

        # Replace placeholders with environment variables
        for key, value in env_vars.items():
            content = content.replace(f"${{{key}}}", value)

        with open(output_path, 'w') as output_file:
            output_file.write(content)

        print(f"Generated '{output_path}' successfully.")
    except Exception as e:
        print(f"Error generating docker-compose file: {e}")


def main():
    base_dir = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Generate docker-compose.yml from template.")
    parser.add_argument(
        "--env_file",
        default=os.path.join(base_dir, '.env', 'prod.env'), 
        help="Path to the .env file containing environment variables.",
    )
    parser.add_argument(
        "--templ_file",
        default=os.path.join(base_dir, 'docker', 'docker-compose.template.yml'), 
        help="Path to the docker-compose template file.",
    )
    args = parser.parse_args()

    env_file = args.env_file
    template_path = args.templ_file
    output_path=os.path.join(base_dir, 'docker-compose.yml')

    # Load environment variables
    try:
        env_vars = load_env(env_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Check if necessary paths exist or create them
    required_paths = ['STATIC_PATH', 'MEDIA_PATH', 'DATA_PATH']
    missing_paths = check_paths(env_vars, required_paths)
    if missing_paths:
        print("Error: The following paths could not be created:")
        for key in missing_paths:
            print(f"  - {key}: {env_vars.get(key)}")
        return

    # Generate docker-compose.yml
    try:
        generate_compose(template_path, output_path, env_vars)
    except Exception as e:
        print(f"Error generating docker-compose.yml: {e}")


if __name__ == "__main__":
    main()
