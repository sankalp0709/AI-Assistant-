import subprocess
import sys

def run(cmd):
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except Exception:
        return False

def main():
    run(sys.executable + " -m pip install pre-commit")
    run("pre-commit install")
    print("pre-commit ready")

if __name__ == "__main__":
    main()
