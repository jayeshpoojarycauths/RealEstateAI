import subprocess
import sys

def run_command(command):
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

def main():
    print("Reordering imports using isort...")
    run_command([sys.executable, "-m", "isort", "app"])

    print("Fixing lint issues using ruff...")
    run_command([sys.executable, "-m", "ruff", "check", "--fix", "app"])

    print("Import clean-up complete.")

if __name__ == "__main__":
    main()
