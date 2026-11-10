#!/usr/bin/env python3
"""Remaps newline and send keys for installed Codex/Claude Code CLIs. 
- Enter = newline;
- Alt+Enter = send

Requires Python 3.11+. Run as your normal user, without sudo.
Usage: python3 set-cli-enter-keys.py [--dry-run]
Respects CODEX_HOME and CLAUDE_CONFIG_DIR. Existing files get timestamped
backups before modification. Repeated runs make no changes if already set.
Restart Codex afterward; Claude Code reloads keybindings automatically.
"""

import argparse
import copy
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

try:
    import tomllib
except ImportError:
    sys.exit("Python 3.11 or newer is required.")


def codex_config(text):
    """Patch only the two TOML entries, preserving other configuration/comments."""
    before = tomllib.loads(text)
    expected = copy.deepcopy(before)
    desired = {"composer": ("submit", ["alt-enter"]),
               "editor": ("insert_newline", ["enter"])}
    keymap = expected.setdefault("tui", {}).setdefault("keymap", {})
    for context, (key, value) in desired.items():
        keymap.setdefault(context, {})[key] = value
    if before == expected:
        return text

    lines = text.splitlines(keepends=True)
    for context, (key, value) in desired.items():
        table = "tui.keymap." + context
        # Handle conventional bare or quoted table components with whitespace.
        component = lambda s: r'(?:' + s + r'|"' + s + r'"|\x27' + s + r'\x27)'
        header = re.compile(r'^\s*\[\s*' + r'\s*\.\s*'.join(
            component(s) for s in table.split('.')) + r'\s*\]\s*(?:#.*)?$')
        start = next((i for i, line in enumerate(lines) if header.match(line)), None)
        assignment = key + " = " + json.dumps(value) + "\n"
        if start is None:
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.extend(["\n[" + table + "]\n", assignment])
            continue
        # A table header cannot start inside a value because we skip complete
        # assignments, including multiline arrays and strings, below.
        i = start + 1
        found = False
        while i < len(lines):
            line = lines[i]
            if line.lstrip().startswith("["):
                break
            if not line.strip() or line.lstrip().startswith("#"):
                i += 1
                continue
            end = i + 1
            while True:
                try:
                    entry = tomllib.loads("".join(lines[i:end]))
                    break
                except tomllib.TOMLDecodeError:
                    if end == len(lines):
                        raise ValueError("Cannot safely locate TOML entries")
                    end += 1
            if key in entry:
                lines[i:end] = [assignment]
                found = True
                break
            i = end
        if not found:
            lines.insert(start + 1, assignment)
    result = "".join(lines)
    if tomllib.loads(result) != expected:
        raise ValueError("Unusual TOML layout: refusing to change unrelated settings")
    return result


def claude_config(text):
    data = json.loads(text) if text.strip() else {}
    if not isinstance(data, dict):
        raise ValueError("Claude keybindings must be a JSON object")
    before = copy.deepcopy(data)
    blocks = data.setdefault("bindings", [])
    if not isinstance(blocks, list):
        raise ValueError("Claude bindings must be an array")
    chat_blocks = []
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Invalid Claude binding block")
        if block.get("context") == "Chat":
            bindings = block.setdefault("bindings", {})
            if not isinstance(bindings, dict):
                raise ValueError("Chat bindings must be an object")
            bindings.update({"enter": "chat:newline", "alt+enter": "chat:submit"})
            chat_blocks.append(block)
    if not chat_blocks:
        blocks.append({"context": "Chat", "bindings": {
            "enter": "chat:newline", "alt+enter": "chat:submit"}})
    return text if data == before else json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def update(path, transform, dry_run):
    # Resolve symlinks so an existing configuration symlink stays intact.
    path = path.expanduser().resolve()
    exists = path.exists()
    original = path.read_bytes() if exists else b""
    result = transform(original.decode("utf-8"))
    if result.encode("utf-8") == original:
        print(f"Already configured: {path}")
        return
    if dry_run:
        print(f"Would {'update' if exists else 'create'}: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if exists:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = path.with_name(path.name + ".bak." + stamp)
        shutil.copy2(path, backup)
        print(f"Backup: {backup}")
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        if exists:
            shutil.copymode(path, temporary)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"Configured: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Check without writing files")
    args = parser.parse_args()
    home = Path.home()
    targets = [
        ("codex", Path(os.environ.get("CODEX_HOME") or home / ".codex") / "config.toml", codex_config),
        ("claude", Path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude") / "keybindings.json", claude_config),
    ]
    failed = False
    for command, path, transform in targets:
        if shutil.which(command) is None:
            print(f"Skipped {command}: not found in PATH")
            continue
        try:
            update(path, transform, args.dry_run)
        except (OSError, ValueError, TypeError, AttributeError) as error:
            # Avoid including configuration text, which could contain secrets.
            print(f"ERROR: {command}: configuration could not be updated ({type(error).__name__}). "
                  "Check syntax, layout, and permissions.", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
