#!/usr/bin/env python3
"""GPM - Light OS package manager."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from typing import Dict

# Ensure repository root is importable from bin/gpm/prog.py
ROOT = Path(__file__).resolve().parents[2]
BIN_ROOT = ROOT / "bin"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lightapi import LightAPI


PACKAGE_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def parse_gpm(text: str) -> Dict[str, object]:
    """Parse custom .gpm format without JSON."""
    data: Dict[str, object] = {}

    # Parse help_menu_description block first.
    help_block_match = re.search(r"help_menu_description:\s*\{(.*?)\}", text, flags=re.S)
    help_menu: Dict[str, str] = {}
    if help_block_match:
        block = help_block_match.group(1)
        for line in block.splitlines():
            item = line.strip()
            if not item or "-" not in item:
                continue
            command, description = item.split("-", 1)
            help_menu[command.strip()] = description.strip()
    data["help_menu_description"] = help_menu

    field_patterns = {
        "pakege_name": r"^\s*pakege_name\s*:\s*(.+?)\s*$",
        "name": r"^\s*name\s*:\s*(.+?)\s*$",
        "author": r"^\s*author\s*:\s*(.+?)\s*$",
        "version": r"^\s*version\s*:\s*(.+?)\s*$",
        "discripton": r"^\s*discripton\s*:\s*(.+?)\s*$",
        "command": r"^\s*command\s*:\s*(.+?)\s*$",
    }

    for key, pattern in field_patterns.items():
        match = re.search(pattern, text, flags=re.M)
        if not match:
            continue
        value = match.group(1).strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        data[key] = value

    return data


def install_package(gpm_path: Path, program_path: Path, api: LightAPI) -> int:
    if not gpm_path.exists():
        api.err("gpm", f"metadata file not found: {gpm_path}")
        return 1
    if not program_path.exists():
        api.err("gpm", f"program file not found: {program_path}")
        return 1

    meta_text = gpm_path.read_text(encoding="utf-8")
    meta = parse_gpm(meta_text)
    package_name = str(meta.get("pakege_name", "")).strip()

    if not package_name:
        api.err("gpm", "invalid .gpm: field 'pakege_name' is required")
        return 1

    if not PACKAGE_NAME_RE.fullmatch(package_name):
        api.err("gpm", f"invalid package name: {package_name}")
        return 1

    BIN_ROOT.mkdir(parents=True, exist_ok=True)

    install_dir = (BIN_ROOT / package_name).resolve()
    try:
        install_dir.relative_to(BIN_ROOT.resolve())
    except ValueError:
        api.err("gpm", "resolved install path escapes bin directory")
        return 1

    install_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(program_path, install_dir / "prog.py")
    shutil.copyfile(gpm_path, install_dir / "info.gpm")

    api.out(f"installed package '{package_name}' -> {install_dir}")
    return 0


def print_help(api: LightAPI) -> None:
    api.out("GPM (Light OS package manager)")
    api.out("Usage:")
    api.out("  gpm help")
    api.out("  gpm parse <path/to/info.gpm>")
    api.out("  gpm install <path/to/info.gpm> <path/to/prog.py>")
    api.out("  gpm host")


def main() -> None:
    api = LightAPI()
    args = sys.argv[1:]

    if not args or args[0] == "help":
        print_help(api)
        api.exit(0)

    cmd = args[0]

    if cmd == "parse":
        if len(args) != 2:
            api.err("gpm parse", "usage: gpm parse <path/to/info.gpm>")
            api.exit(2)

        gpm_path = Path(args[1]).expanduser().resolve()
        if not gpm_path.exists():
            api.err("gpm parse", f"file not found: {gpm_path}")
            api.exit(1)

        parsed = parse_gpm(gpm_path.read_text(encoding="utf-8"))
        for key, value in parsed.items():
            api.out(f"{key}: {value}")
        api.exit(0)

    if cmd == "install":
        if len(args) != 3:
            api.err("gpm install", "usage: gpm install <path/to/info.gpm> <path/to/prog.py>")
            api.exit(2)

        gpm_path = Path(args[1]).expanduser().resolve()
        program_path = Path(args[2]).expanduser().resolve()
        code = install_package(gpm_path, program_path, api)
        api.exit(code)

    if cmd == "host":
        info = api.fetch_hardware()
        if not info:
            api.err("gpm host", "LIGHTOS_HOST_DATA is empty; run core.py first")
            api.exit(1)
        api.out(info)
        api.exit(0)

    api.err("gpm", f"unknown command: {cmd}")
    print_help(api)
    api.exit(2)


if __name__ == "__main__":
    main()
