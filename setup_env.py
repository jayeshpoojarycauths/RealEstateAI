#!/usr/bin/env python3
import os
import secrets
import sys
import argparse
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from cryptography.fernet import Fernet
from datetime import datetime
import re

def generate_secret_key() -> str:
    """Generate a secure secret key."""
    return secrets.token_urlsafe(32)

def get_user_input(prompt: str, default: Optional[str] = None, non_interactive: bool = False) -> str:
    """Get user input with a default value."""
    if non_interactive:
        return default if default else ""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def parse_env_file(file_path: Path) -> Dict[str, str]:
    """Parse environment file into dictionary."""
    env_vars = {}
    if not file_path.exists():
        return env_vars
    
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

def generate_env_diff(example_vars: Dict[str, str], env_vars: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """Generate diff between example and actual environment files."""
    diff = {
        "added": {},
        "modified": {},
        "removed": {},
        "unchanged": {}
    }
    
    for key, value in env_vars.items():
        if key not in example_vars:
            diff["added"][key] = value
        elif value != example_vars[key]:
            diff["modified"][key] = {
                "old": example_vars[key],
                "new": value
            }
        else:
            diff["unchanged"][key] = value
    
    for key in example_vars:
        if key not in env_vars:
            diff["removed"][key] = example_vars[key]
    
    return diff

def save_env_diff(diff: Dict[str, Dict[str, str]], output_file: Path) -> None:
    """Save environment diff to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    diff_file = output_file.parent / f"{output_file.stem}_diff_{timestamp}.json"
    
    with open(diff_file, "w") as f:
        json.dump(diff, f, indent=2)
    print(f"Environment diff saved to: {diff_file}")

def encrypt_env_content(content: str, key: Optional[str] = None) -> Tuple[str, str]:
    """Encrypt environment file content."""
    if not key:
        key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_content = f.encrypt(content.encode())
    return encrypted_content.decode(), key.decode()

def decrypt_env_content(encrypted_content: str, key: str) -> str:
    """Decrypt environment file content."""
    f = Fernet(key.encode())
    decrypted_content = f.decrypt(encrypted_content.encode())
    return decrypted_content.decode()

def validate_env_keys(env_vars: Dict[str, str], codebase_path: Path) -> List[str]:
    """Validate environment keys against codebase usage."""
    unused_keys = []
    for key in env_vars:
        # Skip special keys
        if key.startswith(("VITE_", "NEXT_PUBLIC_")):
            continue
        
        # Search for key usage in codebase
        pattern = re.compile(rf'["\']{key}["\']|{key}=')
        found = False
        
        for file_path in codebase_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".py", ".ts", ".tsx", ".js", ".jsx"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        if pattern.search(f.read()):
                            found = True
                            break
                except Exception:
                    continue
        
        if not found:
            unused_keys.append(key)
    
    return unused_keys

def create_minimal_frontend_env(env_file: Path) -> str:
    """Create minimal frontend environment configuration."""
    return """# API Configuration
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000

# Authentication
VITE_AUTH_TOKEN_KEY=auth_token

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_NOTIFICATIONS=false

# Development
VITE_DEV_MODE=true
VITE_ENABLE_MOCK_DATA=false

# CORS
VITE_ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000
"""

def create_minimal_backend_env(env_file: Path) -> str:
    """Create minimal backend environment configuration."""
    return f"""# Project Info
PROJECT_NAME=Real Estate CRM
VERSION=1.0.0
API_V1_STR=/api/v1
ENVIRONMENT=development

# Security
SECRET_KEY={generate_secret_key()}
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=real_estate_crm

# Frontend
FRONTEND_URL=http://localhost:3000
"""

def validate_env_content(content: str, required_keys: Set[str]) -> List[str]:
    """Validate environment file content for required keys."""
    missing_keys = []
    for key in required_keys:
        if f"{key}=" not in content:
            missing_keys.append(key)
    return missing_keys

def update_gitignore(env_files: List[Path]) -> None:
    """Update .gitignore to include environment files."""
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        return

    with open(gitignore, "r") as f:
        content = f.read()

    needs_update = False
    for env_file in env_files:
        if env_file.name not in content:
            needs_update = True
            content += f"\n{env_file.name}"

    if needs_update:
        with open(gitignore, "w") as f:
            f.write(content)
        print(f"Updated .gitignore to include {', '.join(f.name for f in env_files)}")

def setup_frontend_env(dry_run: bool = False, non_interactive: bool = False, defaults: Optional[Dict] = None) -> None:
    """Set up frontend environment configuration."""
    frontend_dir = Path("frontend")
    env_example = frontend_dir / ".env.example"
    env_file = frontend_dir / ".env"
    env_local_file = frontend_dir / ".env.local"

    # Check for existing files
    if env_file.exists() or env_local_file.exists():
        if non_interactive:
            print("Skipping frontend setup in non-interactive mode...")
            return
        overwrite = input("Frontend environment files exist. Overwrite? [y/N]: ").strip().lower()
        if overwrite != "y":
            print("Skipping frontend setup...")
            return

    # Create minimal config if example doesn't exist
    if not env_example.exists():
        print("Warning: frontend/.env.example not found!")
        if not dry_run:
            env_content = create_minimal_frontend_env(env_file)
        else:
            print("Would create minimal frontend environment configuration")
            return
    else:
        print("\nSetting up frontend environment...")
        with open(env_example, "r") as f:
            example_content = f.read()

        # Validate required keys
        required_keys = {"VITE_API_URL", "VITE_AUTH_TOKEN_KEY"}
        missing_keys = validate_env_content(example_content, required_keys)
        if missing_keys:
            print(f"Warning: Missing required keys in .env.example: {', '.join(missing_keys)}")
            if not dry_run:
                env_content = create_minimal_frontend_env(env_file)
            else:
                print("Would create minimal frontend environment configuration")
                return
        else:
            env_content = example_content

        # Get user input for required values
        api_url = get_user_input(
            "Enter API URL",
            defaults.get("VITE_API_URL", "http://localhost:8000/api") if defaults else "http://localhost:8000/api",
            non_interactive
        )
        google_maps_key = get_user_input(
            "Enter Google Maps API Key (optional)",
            defaults.get("VITE_GOOGLE_MAPS_API_KEY", "") if defaults else None,
            non_interactive
        )
        
        # Update content
        env_content = env_content.replace(
            "VITE_API_URL=http://localhost:8000/api",
            f"VITE_API_URL={api_url}"
        )
        
        if google_maps_key:
            env_content = env_content.replace(
                "VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here",
                f"VITE_GOOGLE_MAPS_API_KEY={google_maps_key}"
            )

    # Write files
    if not dry_run:
        if non_interactive:
            # In non-interactive mode, create both files
            with open(env_file, "w") as f:
                f.write(env_content)
            with open(env_local_file, "w") as f:
                f.write(env_content)
            print(f"Created {env_file} and {env_local_file}")
        else:
            # Ask which file to create
            file_choice = input("Create .env or .env.local? [env/local/both]: ").strip().lower()
            if file_choice in ["env", "both"]:
                with open(env_file, "w") as f:
                    f.write(env_content)
                print(f"Created {env_file}")
            if file_choice in ["local", "both"]:
                with open(env_local_file, "w") as f:
                    f.write(env_content)
                print(f"Created {env_local_file}")
        
        # Generate and save diff
        example_vars = parse_env_file(env_example)
        env_vars = parse_env_file(env_file)
        diff = generate_env_diff(example_vars, env_vars)
        save_env_diff(diff, env_file)
        
        # Validate keys against codebase
        unused_keys = validate_env_keys(env_vars, frontend_dir)
        if unused_keys:
            print(f"Warning: The following keys are not used in the codebase: {', '.join(unused_keys)}")
        
        # Update .gitignore
        update_gitignore([env_file, env_local_file])
    else:
        print("Would create frontend environment files")

def setup_backend_env(dry_run: bool = False, non_interactive: bool = False, defaults: Optional[Dict] = None) -> None:
    """Set up backend environment configuration."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    env_local_file = Path(".env.local")

    # Check for existing files
    if env_file.exists() or env_local_file.exists():
        if non_interactive:
            print("Skipping backend setup in non-interactive mode...")
            return
        overwrite = input("Backend environment files exist. Overwrite? [y/N]: ").strip().lower()
        if overwrite != "y":
            print("Skipping backend setup...")
            return

    # Create minimal config if example doesn't exist
    if not env_example.exists():
        print("Warning: .env.example not found!")
        if not dry_run:
            env_content = create_minimal_backend_env(env_file)
        else:
            print("Would create minimal backend environment configuration")
            return
    else:
        print("\nSetting up backend environment...")
        with open(env_example, "r") as f:
            example_content = f.read()

        # Validate required keys
        required_keys = {
            "SECRET_KEY", "POSTGRES_SERVER", "POSTGRES_USER",
            "POSTGRES_PASSWORD", "POSTGRES_DB"
        }
        missing_keys = validate_env_content(example_content, required_keys)
        if missing_keys:
            print(f"Warning: Missing required keys in .env.example: {', '.join(missing_keys)}")
            if not dry_run:
                env_content = create_minimal_backend_env(env_file)
            else:
                print("Would create minimal backend environment configuration")
                return
        else:
            env_content = example_content

        # Get user input for required values
        secret_key = get_user_input(
            "Enter secret key (press Enter to generate)",
            defaults.get("SECRET_KEY", generate_secret_key()) if defaults else generate_secret_key(),
            non_interactive
        )
        db_server = get_user_input(
            "Enter database server",
            defaults.get("POSTGRES_SERVER", "localhost") if defaults else "localhost",
            non_interactive
        )
        db_user = get_user_input(
            "Enter database user",
            defaults.get("POSTGRES_USER", "postgres") if defaults else "postgres",
            non_interactive
        )
        db_password = get_user_input(
            "Enter database password",
            defaults.get("POSTGRES_PASSWORD", "") if defaults else None,
            non_interactive
        )
        db_name = get_user_input(
            "Enter database name",
            defaults.get("POSTGRES_DB", "real_estate_crm") if defaults else "real_estate_crm",
            non_interactive
        )
        
        # Optional configurations
        openai_key = get_user_input(
            "Enter OpenAI API Key (optional)",
            defaults.get("OPENAI_API_KEY", "") if defaults else None,
            non_interactive
        )
        telegram_token = get_user_input(
            "Enter Telegram Bot Token (optional)",
            defaults.get("TELEGRAM_BOT_TOKEN", "") if defaults else None,
            non_interactive
        )
        proxy_url = get_user_input(
            "Enter Scraper Proxy URL (optional)",
            defaults.get("SCRAPER_PROXY_URL", "") if defaults else None,
            non_interactive
        )

        # Update content
        env_content = env_content.replace(
            "SECRET_KEY=your-secret-key-here",
            f"SECRET_KEY={secret_key}"
        ).replace(
            "POSTGRES_SERVER=localhost",
            f"POSTGRES_SERVER={db_server}"
        ).replace(
            "POSTGRES_USER=postgres",
            f"POSTGRES_USER={db_user}"
        ).replace(
            "POSTGRES_PASSWORD=your-secure-password",
            f"POSTGRES_PASSWORD={db_password}"
        ).replace(
            "POSTGRES_DB=real_estate_crm",
            f"POSTGRES_DB={db_name}"
        )

        if openai_key:
            env_content = env_content.replace(
                "OPENAI_API_KEY=your-openai-api-key",
                f"OPENAI_API_KEY={openai_key}"
            )

        if telegram_token:
            env_content = env_content.replace(
                "TELEGRAM_BOT_TOKEN=your-telegram-bot-token",
                f"TELEGRAM_BOT_TOKEN={telegram_token}"
            )

        if proxy_url:
            env_content = env_content.replace(
                "SCRAPER_PROXY_URL=your-proxy-url",
                f"SCRAPER_PROXY_URL={proxy_url}"
            )

    # Write files
    if not dry_run:
        if non_interactive:
            # In non-interactive mode, create both files
            with open(env_file, "w") as f:
                f.write(env_content)
            with open(env_local_file, "w") as f:
                f.write(env_content)
            print(f"Created {env_file} and {env_local_file}")
        else:
            # Ask which file to create
            file_choice = input("Create .env or .env.local? [env/local/both]: ").strip().lower()
            if file_choice in ["env", "both"]:
                with open(env_file, "w") as f:
                    f.write(env_content)
                print(f"Created {env_file}")
            if file_choice in ["local", "both"]:
                with open(env_local_file, "w") as f:
                    f.write(env_content)
                print(f"Created {env_local_file}")
        
        # Generate and save diff
        example_vars = parse_env_file(env_example)
        env_vars = parse_env_file(env_file)
        diff = generate_env_diff(example_vars, env_vars)
        save_env_diff(diff, env_file)
        
        # Validate keys against codebase
        unused_keys = validate_env_keys(env_vars, Path("app"))
        if unused_keys:
            print(f"Warning: The following keys are not used in the codebase: {', '.join(unused_keys)}")
        
        # Update .gitignore
        update_gitignore([env_file, env_local_file])
    else:
        print("Would create backend environment files")

def main() -> None:
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Real Estate CRM Environment Setup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode for CI/CD")
    parser.add_argument("--defaults-from", type=str, help="Path to YAML file containing default values")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt environment files")
    args = parser.parse_args()

    # Load defaults if provided
    defaults = None
    if args.defaults_from:
        try:
            with open(args.defaults_from, "r") as f:
                defaults = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading defaults file: {e}")
            sys.exit(1)

    print("Real Estate CRM Environment Setup")
    print("=================================")
    
    try:
        setup_frontend_env(args.dry_run, args.non_interactive, defaults)
        setup_backend_env(args.dry_run, args.non_interactive, defaults)
        
        if args.encrypt and not args.dry_run:
            # Encrypt environment files
            for env_file in [Path(".env"), Path(".env.local"), Path("frontend/.env"), Path("frontend/.env.local")]:
                if env_file.exists():
                    with open(env_file, "r") as f:
                        content = f.read()
                    encrypted_content, key = encrypt_env_content(content)
                    with open(f"{env_file}.encrypted", "w") as f:
                        f.write(encrypted_content)
                    with open(f"{env_file}.key", "w") as f:
                        f.write(key)
                    print(f"Encrypted {env_file} -> {env_file}.encrypted")
        
        if not args.dry_run:
            print("\nEnvironment setup completed successfully!")
        else:
            print("\nDry run completed. No changes were made.")
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 