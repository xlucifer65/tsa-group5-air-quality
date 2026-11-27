"""Fail CI when any individual Jupyter notebook output exceeds 5 MB."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MAX_OUTPUT_BYTES = 5 * 1024 * 1024


def output_size(output: dict[str, Any]) -> int:
    """Return the UTF-8 encoded size of one notebook output."""
    return len(json.dumps(output, ensure_ascii=False).encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook_directory", type=Path)
    args = parser.parse_args()

    oversized_outputs: list[str] = []
    for path in sorted(args.notebook_directory.glob("*.ipynb")):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for cell_number, cell in enumerate(notebook.get("cells", []), start=1):
            for output_number, output in enumerate(cell.get("outputs", []), start=1):
                size = output_size(output)
                if size > MAX_OUTPUT_BYTES:
                    oversized_outputs.append(
                        f"{path}: cell {cell_number}, output {output_number} is {size} bytes"
                    )

    if oversized_outputs:
        raise SystemExit("\n".join(oversized_outputs))


if __name__ == "__main__":
    main()
