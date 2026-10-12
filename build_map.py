"""Build an EPScript map without an EUD Editor project (Python 3.9+)."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parent


def project_path(value: str) -> Path:
    path = Path(value)
    return (ROOT / path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/build.json")
    parser.add_argument("--input", help="Override base SCX path (relative to project root)")
    parser.add_argument("--output", help="Override output SCX path")
    parser.add_argument("--euddraft", help="Override euddraft executable")
    parser.add_argument("--check", action="store_true", help="Validate without compiling")
    args = parser.parse_args()
    try:
        config = json.loads(project_path(args.config).read_text(encoding="utf-8-sig"))
        paths = {}
        for key in ("input", "output", "entry"):
            value = getattr(args, key, None) or config[key]
            if not isinstance(value, str) or not value.strip() or any(c in value for c in "\r\n[]"):
                raise ValueError(f"Invalid {key} path")
            paths[key] = project_path(value)
        source, output, entry = (paths[k] for k in ("input", "output", "entry"))
        if not source.is_file() or source.suffix.lower() != ".scx":
            raise ValueError(f"Base SCX not found: {source}")
        if not entry.is_file() or entry.suffix.lower() not in (".eps", ".py"):
            raise ValueError(f"EPScript/Python entry not found: {entry}")
        if output.suffix.lower() != ".scx" or output in (source, entry):
            raise ValueError("Output must be a separate .scx file")
        if ROOT not in output.parents:
            raise ValueError("Output must remain inside the project")
        configured = args.euddraft or os.environ.get("EUDDRAFT_PATH") or config.get("euddraft") or "euddraft"
        executable = shutil.which(configured)
        if not executable:
            candidate = project_path(configured)
            if candidate.is_file():
                executable = str(candidate)
        if not executable:
            raise ValueError("euddraft not found; set --euddraft or EUDDRAFT_PATH")
        print(f"Input:  {source}\nEntry:  {entry}\nOutput: {output}\nTool:   {executable}", flush=True)
        if args.check:
            print("Configuration OK (compilation not run).")
            return 0

        # A unique staging path prevents stale output from being reported as success.
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        work = ROOT / "build" / stamp
        work.mkdir(parents=True)
        staged = work / "map.scx"
        recipe = work / "map.eds"
        recipe.write_text(
            f"[main]\ninput: {source.as_posix()}\noutput: {staged.as_posix()}\n\n"
            f"[{entry.as_posix()}]\n",
            encoding="utf-8",
        )
        logs = ROOT / "build" / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        log_path = logs / f"{stamp}.log"
        print(f"Log: {log_path}", flush=True)
        # .eds compiles once; .edd would enter a persistent watch loop.
        with log_path.open("wb") as log:
            result = subprocess.run(
                [executable, str(recipe)], cwd=ROOT,
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            )
        if result.returncode or not staged.is_file() or not staged.stat().st_size:
            print(log_path.read_text(encoding="utf-8", errors="replace"), file=sys.stderr)
            raise ValueError(f"Build failed (exit {result.returncode}); see {log_path}")
        output.parent.mkdir(parents=True, exist_ok=True)
        staged.replace(output)
        print(f"Built: {output}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
