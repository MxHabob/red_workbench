import sys
print(f"Python: {sys.version}")
try:
    import typer, pydantic, yaml
    print("Dependencies: OK")
except ImportError as exc:
    print(f"Missing dependency: {exc}")
    raise SystemExit(1)
