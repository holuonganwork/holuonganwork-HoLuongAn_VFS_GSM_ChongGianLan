"""Write a detailed log and a short worklog index row for each changed Codex turn.

Receives UserPromptSubmit / Stop JSON on stdin. Uses only Python's standard library.
Snapshots contain content hashes and line hashes, never copies of source files.
"""

from __future__ import annotations

import difflib
import hashlib
import html
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

VIETNAM = timezone(timedelta(hours=7))
TEXT_LIMIT = 1024 * 1024
HEADER = "| STT | Thời gian thực hiện (Ngày, giờ) | Tóm tắt công việc | File log chi tiết |"
SEPARATOR = "| --- | --- | --- | --- |"
EXCLUDED_DIRS = {".git", ".local", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact_text(value: object, limit: int | None = None) -> str:
    text = " ".join(str(value or "").split())
    text = re.sub(
        r"(?i)\b(password|passwd|token|api[_-]?key|secret)\s*[:=]\s*\S+",
        r"\1=[ẩn]",
        text,
    )
    if limit and len(text) > limit:
        text = text[: limit - 1] + "…"
    return text


def cell(value: object, limit: int | None = None) -> str:
    """Keep user/model text in a single, inert Markdown table cell."""
    text = compact_text(value, limit)
    text = html.escape(text, quote=False)
    for character in "\\`*_[]|":
        text = text.replace(character, f"&#{ord(character)};")
    return text


def in_scope(name: str) -> bool:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        return False
    if set(path.parts) & EXCLUDED_DIRS or name == "worklog.md":
        return False
    if name.startswith(("logs/", "data/raw/", "data/generated/")):
        return False
    base = path.name.lower()
    return not (
        base == ".env"
        or (base.startswith(".env.") and base != ".env.example")
        or base in {"auth.json", "credentials.json", "id_rsa", "id_ed25519"}
        or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
    )


def snapshot(root: Path) -> dict:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
        timeout=15,
    )
    files = {}
    for raw_name in sorted(set(result.stdout.split(b"\0")) - {b""}):
        name = os.fsdecode(raw_name).replace("\\", "/")
        if not in_scope(name):
            continue
        path = root / name
        # Do not follow a parent directory that points outside this repository.
        if not path.parent.resolve().is_relative_to(root):
            continue
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue  # Tracked deletion, represented by absence from the snapshot.
        entry = {"mode": stat.S_IMODE(info.st_mode), "lines": None}
        if path.is_symlink():
            entry["hash"] = digest(os.fsencode(os.readlink(path)))
            entry["kind"] = "symlink"
        elif stat.S_ISREG(info.st_mode):
            entry["kind"] = "file"
            with path.open("rb") as stream:
                entry["hash"] = hashlib.file_digest(stream, "sha256").hexdigest()
            if info.st_size <= TEXT_LIMIT:
                data = path.read_bytes()
                try:
                    if b"\0" not in data:
                        entry["lines"] = [
                            digest(line.encode("utf-8"))
                            for line in data.decode("utf-8-sig").splitlines(keepends=True)
                        ]
                except UnicodeDecodeError:
                    pass
        else:
            continue
        files[name] = entry
    return files


def line_range(start: int, end: int) -> str:
    return str(start + 1) if end == start + 1 else f"{start + 1}–{end}"


def describe_change(name: str, before: dict | None, after: dict | None) -> str:
    label = "Thêm mới" if before is None else "Xóa" if after is None else "Sửa"
    old = before.get("lines") if before else []
    new = after.get("lines") if after else []
    if old is None or new is None:
        detail = "file nhị phân, liên kết, không phải UTF-8 hoặc >1 MiB; không có số dòng"
    elif before is None:
        detail = f"dòng {line_range(0, len(new))}" if new else "file rỗng"
    elif after is None:
        detail = f"dòng cũ {line_range(0, len(old))}" if old else "file rỗng"
    else:
        details = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            a=old, b=new, autojunk=True
        ).get_opcodes():
            if tag == "insert":
                details.append(f"thêm dòng {line_range(j1, j2)}")
            elif tag == "delete":
                details.append(f"xóa dòng cũ {line_range(i1, i2)}")
            elif tag == "replace":
                details.append(f"dòng {line_range(j1, j2)} (cũ {line_range(i1, i2)})")
        detail = "; ".join(details) or "quyền file, kiểu file hoặc mã hóa thay đổi"
    return f"{label}: {cell(name)} — {detail}"


@contextmanager
def lock(path: Path) -> Iterator[None]:
    """OS lock is automatically released even if a hook process is killed."""
    with path.open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        deadline = time.monotonic() + 10
        while True:
            try:
                stream.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("worklog lock unavailable") from None
                time.sleep(0.05)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def atomic_write(path: Path, text: str) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            os.chmod(temporary, stat.S_IMODE(path.stat().st_mode))
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def append_row(root: Path, state: dict, key: str, changes: list[str], report: str) -> bool:
    path = root / "worklog.md"
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError("worklog must be a local regular file")
    original = path.read_bytes().decode("utf-8-sig") if path.exists() else ""
    marker = f"<!-- codex-worklog:{key} -->"
    if marker in original:
        return False  # Also handles a crash after writing the row but before saving state.
    newline = "\r\n" if "\r\n" in original else "\n"
    if not original:
        original = f"# Nhật ký công việc{newline}{newline}{HEADER}{newline}{SEPARATOR}{newline}"
    lines = original.splitlines(keepends=True)
    header_index = next((i for i, line in enumerate(lines) if line.strip() == HEADER), None)
    if (
        header_index is None
        or header_index + 1 >= len(lines)
        or lines[header_index + 1].strip() != SEPARATOR
    ):
        raise ValueError("expected four-column worklog index table")
    end = header_index + 2
    sequence = 0
    while end < len(lines) and lines[end].lstrip().startswith("|"):
        number = re.match(r"\|\s*(\d+)\s*\|", lines[end])
        if number:
            sequence = max(sequence, int(number.group(1)))
        end += 1
    started = datetime.fromisoformat(state["started"])
    finished = datetime.now(VIETNAM)
    period = f"{started:%d/%m/%Y %H:%M:%S} → {finished:%d/%m/%Y %H:%M:%S} (UTC+7)"
    log_id = state["log_id"]
    if not re.fullmatch(r"AUTO-\d{8}-[0-9a-f]{10}", log_id):
        raise ValueError("invalid internal log id")
    log_directory = root / "logs"
    log_path = log_directory / f"{log_id}.md"
    if log_path.is_symlink() or not log_path.resolve().is_relative_to(root):
        raise ValueError("log must stay in the repository")
    log_directory.mkdir(exist_ok=True)
    details = (
        f"# Nhật ký công việc — {log_id}\n\n"
        f"- Thời gian: {period}\n"
        f"- Mã nội bộ: `{log_id}`\n"
        f"- Số file thay đổi: {len(changes)}\n\n"
        f"## Mục tiêu công việc\n\n{cell(state['goal'])}\n\n"
        f"## Công việc thực hiện\n\nCập nhật {len(changes)} file trong lượt làm việc; "
        "đối chiếu trạng thái trước/sau.\n\n"
        "## Đầu ra công việc\n\n"
        + ("Agent báo cáo: " + cell(report, 3000) if report else "Đã ghi nhận thay đổi file.")
        + "\n\nBáo cáo trên do agent cung cấp; hook không tự xác minh kết quả kiểm thử.\n\n"
        "## Các file và dòng đã thay đổi\n\n"
        + "\n".join(f"- {change}" for change in changes)
        + f"\n\n{marker}\n"
    )
    # Save details before their index link. Retry reuses the same file after a crash.
    if log_path.exists():
        if marker not in log_path.read_text(encoding="utf-8"):
            raise ValueError("refusing to overwrite an unrelated log")
    else:
        atomic_write(log_path, details)
    columns = [
        str(sequence + 1),
        period,
        cell(state["goal"], 160) + f" ({len(changes)} file).",
        f"[{log_id}](logs/{log_id}.md) " + marker,
    ]
    if end and not lines[end - 1].endswith(("\n", "\r")):
        lines[end - 1] += newline
    lines.insert(end, "| " + " | ".join(columns) + " |" + newline)
    atomic_write(path, "".join(lines))
    return True


def handle(root: Path, payload: dict) -> bool:
    root = root.resolve()
    event = payload.get("hook_event_name")
    if event not in {"UserPromptSubmit", "Stop"}:
        return False
    session, turn = payload.get("session_id"), payload.get("turn_id")
    if not isinstance(session, str) or not session or not isinstance(turn, str) or not turn:
        raise ValueError("session_id and turn_id are required")
    cwd = Path(payload.get("cwd", str(root))).resolve()
    if not cwd.is_relative_to(root):
        raise ValueError("hook belongs to a different repository")
    directory = root / ".local" / "worklog-hook"
    if not directory.resolve().is_relative_to(root):
        raise ValueError("state directory must stay in the repository")
    directory.mkdir(parents=True, exist_ok=True)
    key = digest(json.dumps([session, turn]).encode())
    state_path = directory / f"{key}.json"
    with lock(directory / "worklog.lock"):
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else None
        if state and state.get("completed"):
            return False
        if event == "UserPromptSubmit":
            # Steering or duplicate events must not replace the original baseline.
            if state is None:
                started = datetime.now(VIETNAM)
                state = {
                    "started": started.isoformat(),
                    "log_id": f"AUTO-{started:%Y%m%d}-{uuid.uuid4().hex[:10]}",
                    "goal": compact_text(
                        payload.get("prompt") or "Cập nhật dự án theo yêu cầu", 600
                    ),
                    "files": snapshot(root),
                }
                atomic_write(state_path, json.dumps(state, ensure_ascii=False))
            return False
        if state is None:
            # Never attribute the entire dirty working tree to a turn without a baseline.
            raise ValueError("no UserPromptSubmit snapshot for this turn")
        before, after = state["files"], snapshot(root)
        changes = [
            describe_change(name, before.get(name), after.get(name))
            for name in sorted(before.keys() | after.keys())
            if before.get(name) != after.get(name)
        ]
        wrote = bool(changes) and append_row(
            root, state, key, changes, payload.get("last_assistant_message") or ""
        )
        atomic_write(state_path, json.dumps({"completed": True}))
        return wrote


def main() -> int:
    result = {}
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
        if not isinstance(payload, dict):
            raise ValueError("expected an event object")
        handle(Path(__file__).resolve().parents[1], payload)
    except Exception as error:
        # Hook failure must neither block coding nor silently claim a row was written.
        result = {
            "systemMessage": "Worklog hook chưa ghi được nhật ký "
            f"({type(error).__name__}). Xem docs/worklog-hook.md để kiểm tra."
        }
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
