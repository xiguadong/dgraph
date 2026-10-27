from pathlib import Path
from examples._shared.runner import run_sysml

if __name__ == "__main__":
    result = run_sysml(Path(__file__).resolve().parent)
    if not result.get("ok"):
        raise SystemExit(result)
    print(result["artifacts"]["svg"])
