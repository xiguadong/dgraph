from pathlib import Path
from examples._shared.runner import run_semantic

if __name__ == "__main__":
    result = run_semantic(Path(__file__).resolve().parent)
    if not result.get("ok"):
        raise SystemExit(result)
    print(result["artifacts"]["svg"])
