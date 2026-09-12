import hashlib
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from scripts import codex_worklog_hook as hook


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "dự án thử hook"
    root.mkdir()
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    (root / ".gitignore").write_text(".local/\nignored/\n", encoding="utf-8")
    (root / "existing.py").write_text("before = 1\nkeep = 2\nremove = 3\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore", "existing.py"], cwd=root, check=True)
    (root / "new_before_turn.py").write_text("already untracked\n", encoding="utf-8")
    template = (
        "# Worklog\n\n"
        + hook.HEADER
        + "\n"
        + hook.SEPARATOR
        + "\n| 18 | old | old goal | old log |\n"
        + "\n## Mẫu thêm bản ghi cho phiên sau\n\n"
        + hook.HEADER
        + "\n"
        + hook.SEPARATOR
        + "\n| <STT> | time | goal | log file |\n"
    )
    (root / "worklog.md").write_bytes(template.replace("\n", "\r\n").encode("utf-8"))
    return root


def event(root: Path, name: str, turn: str = "turn-1", **kwargs) -> dict:
    return {
        "hook_event_name": name,
        "session_id": "test-session",
        "turn_id": turn,
        "cwd": str(root),
        "prompt": "Sửa kiểm tra tài xế | giữ tiếng Việt",
        "last_assistant_message": "Đã sửa.\nTest: 3 passed | 0 failed.",
    } | kwargs


def rows(root: Path) -> list[str]:
    return [
        line
        for line in (root / "worklog.md").read_text(encoding="utf-8").splitlines()
        if "<!-- codex-worklog:" in line
    ]


def detail_logs(root: Path) -> list[Path]:
    return sorted((root / "logs").glob("AUTO-*.md"))


def start(root: Path, turn: str = "turn-1") -> None:
    assert not hook.handle(root, event(root, "UserPromptSubmit", turn))


def stop(root: Path, turn: str = "turn-1") -> bool:
    return hook.handle(root, event(root, "Stop", turn))


def test_qa_with_preexisting_dirty_files_does_not_write(repo: Path):
    (repo / "existing.py").write_text("dirty before turn\n", encoding="utf-8")
    original = (repo / "worklog.md").read_bytes()
    start(repo)
    assert not stop(repo)
    assert (repo / "worklog.md").read_bytes() == original


def test_details_go_to_log_and_only_summary_link_goes_to_index(repo: Path):
    original = (repo / "worklog.md").read_bytes()
    start(repo)
    (repo / "existing.py").write_text("before = 9\nkeep = 2\n", encoding="utf-8")
    (repo / "mới.py").write_text("one\ntwo\n", encoding="utf-8")
    (repo / "new_before_turn.py").unlink()
    assert stop(repo)
    row = rows(repo)[0]
    assert row.startswith("| 19 |")
    assert "AUTO-" in row and "UTC+7" in row
    assert "(3 file)" in row
    assert "existing.py" not in row and "Agent báo cáo" not in row
    details = detail_logs(repo)[0].read_text(encoding="utf-8")
    assert "Cập nhật 3 file" in details
    assert "Sửa: existing.py — dòng 1 (cũ 1); xóa dòng cũ 3" in details
    assert "Thêm mới: mới.py — dòng 1–2" in details
    assert "Xóa: new&#95;before&#95;turn.py — dòng cũ 1" in details
    assert "Agent báo cáo" in details and "Test: 3 passed" in details
    assert f"](logs/{detail_logs(repo)[0].name})" in row
    assert "test-session" not in row and "turn-1" not in row
    assert len(row.split("|")) == 6  # Four cells, plus the two outer boundaries.
    current = (repo / "worklog.md").read_bytes()
    assert current.replace((row + "\r\n").encode("utf-8"), b"") == original


def test_duplicate_start_preserves_baseline_and_duplicate_stop_is_idempotent(repo: Path):
    start(repo)
    (repo / "existing.py").write_text("edited\n", encoding="utf-8")
    start(repo)
    assert stop(repo)
    assert not stop(repo)
    assert len(rows(repo)) == 1
    assert len(detail_logs(repo)) == 1


def test_new_turn_skips_previous_changes_and_increments_sequence(repo: Path):
    start(repo)
    (repo / "existing.py").write_text("first turn\n", encoding="utf-8")
    assert stop(repo)
    start(repo, "turn-2")
    assert not stop(repo, "turn-2")
    start(repo, "turn-3")
    (repo / "new_before_turn.py").write_text("third turn\n", encoding="utf-8")
    assert stop(repo, "turn-3")
    assert len(rows(repo)) == 2
    assert rows(repo)[1].startswith("| 20 |")
    latest_link = rows(repo)[1].split("](logs/")[1].split(")")[0]
    assert "existing.py" not in (repo / "logs" / latest_link).read_text(encoding="utf-8")


def test_no_net_changes_and_only_log_output_changes_are_ignored(repo: Path):
    original = (repo / "existing.py").read_bytes()
    start(repo)
    (repo / "existing.py").write_text("temporary edit\n", encoding="utf-8")
    (repo / "existing.py").write_bytes(original)
    with (repo / "worklog.md").open("a", encoding="utf-8") as stream:
        stream.write("\nManual note\n")
    (repo / "logs").mkdir()
    (repo / "logs" / "manual.md").write_text("manual log note\n", encoding="utf-8")
    assert not stop(repo)
    assert rows(repo) == []
    assert detail_logs(repo) == []


def test_ignored_data_and_secret_files_do_not_trigger_log(repo: Path):
    start(repo)
    for name in ["ignored/data.csv", "data/raw/driver.csv", "data/generated/run.json", ".env"]:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("private contents\n", encoding="utf-8")
    assert not stop(repo)
    assert rows(repo) == []


def test_snapshot_keeps_hashes_instead_of_source_contents(repo: Path):
    (repo / "existing.py").write_text("source_that_must_not_be_copied\n", encoding="utf-8")
    start(repo)
    state = next((repo / ".local/worklog-hook").glob("*.json")).read_text(encoding="utf-8")
    assert "source_that_must_not_be_copied" not in state
    assert hashlib.sha256((repo / "existing.py").read_bytes()).hexdigest() in state


def test_binary_empty_and_large_files_log_without_invented_line_numbers(repo: Path):
    start(repo)
    (repo / "image.bin").write_bytes(b"\x00\xff\x01")
    (repo / "empty.py").touch()
    (repo / "large.txt").write_bytes(b"a" * (hook.TEXT_LIMIT + 1))
    assert stop(repo)
    row = detail_logs(repo)[0].read_text(encoding="utf-8")
    assert "Thêm mới: empty.py — file rỗng" in row
    assert "Thêm mới: image.bin — file nhị phân" in row
    assert "Thêm mới: large.txt — file nhị phân" in row
    assert "không có số dòng" in row


def test_missing_baseline_never_logs_all_uncommitted_files(repo: Path):
    original = (repo / "worklog.md").read_bytes()
    with pytest.raises(ValueError, match="no UserPromptSubmit"):
        stop(repo)
    assert (repo / "worklog.md").read_bytes() == original


def test_crash_after_append_does_not_duplicate_row_on_retry(repo: Path, monkeypatch):
    start(repo)
    (repo / "existing.py").write_text("edited\n", encoding="utf-8")
    original_write = hook.atomic_write

    def fail_completion(path: Path, text: str):
        if text == '{"completed": true}':
            raise OSError("simulated disk failure")
        original_write(path, text)

    with monkeypatch.context() as context:
        context.setattr(hook, "atomic_write", fail_completion)
        with pytest.raises(OSError, match="disk failure"):
            stop(repo)
    assert len(rows(repo)) == 1
    assert not stop(repo)
    assert len(rows(repo)) == 1
    assert len(detail_logs(repo)) == 1


def test_missing_worklog_is_created_with_four_columns(repo: Path):
    (repo / "worklog.md").unlink()
    start(repo)
    (repo / "existing.py").write_text("edited\n", encoding="utf-8")
    assert stop(repo)
    assert rows(repo)[0].startswith("| 1 |")


def test_unknown_table_format_is_preserved(repo: Path):
    (repo / "worklog.md").write_text("User notes without a table\n", encoding="utf-8")
    original = (repo / "worklog.md").read_bytes()
    start(repo)
    (repo / "existing.py").write_text("edited\n", encoding="utf-8")
    with pytest.raises(ValueError, match="four-column"):
        stop(repo)
    assert (repo / "worklog.md").read_bytes() == original
    assert detail_logs(repo) == []


def test_cell_escapes_markup_and_common_inline_secrets():
    result = hook.cell("a | b\n<script> password=secret123 token=abc <!-- hi -->")
    assert "|" not in result and "\n" not in result and "<script>" not in result
    assert "secret123" not in result and "abc" not in result
    assert "[ẩn]" not in result  # Brackets are escaped too.
    assert "&lt;script&gt;" in result


def install_cli_script(root: Path) -> Path:
    script = root / "scripts" / "codex_worklog_hook.py"
    script.parent.mkdir(exist_ok=True)
    shutil.copyfile(hook.__file__, script)
    return script


def invoke(script: Path, payload: dict | str) -> dict:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(script)],
        input=json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else payload,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
        check=True,
    )
    assert result.stderr == ""
    return json.loads(result.stdout)


def test_real_cli_accepts_utf8_json_from_subdirectory_and_skips_qa(repo: Path):
    script = install_cli_script(repo)
    cwd = str(repo / "scripts")
    assert invoke(script, event(repo, "UserPromptSubmit", cwd=cwd)) == {}
    (repo / "existing.py").write_text("đã sửa\n", encoding="utf-8")
    assert invoke(script, event(repo, "Stop", cwd=cwd)) == {}
    assert len(rows(repo)) == 1
    assert invoke(script, event(repo, "UserPromptSubmit", "qa", cwd=cwd)) == {}
    assert invoke(script, event(repo, "Stop", "qa", cwd=cwd)) == {}
    assert len(rows(repo)) == 1


@pytest.mark.parametrize("payload", ["not JSON", "[]", "{}"])
def test_bad_input_never_blocks_codex(repo: Path, payload: str):
    script = install_cli_script(repo)
    result = invoke(script, payload)
    assert result == {} or "systemMessage" in result
    assert "decision" not in result and "continue" not in result
    assert rows(repo) == []
    assert detail_logs(repo) == []


def test_concurrent_stop_processes_do_not_duplicate_or_lose_rows(repo: Path):
    script = install_cli_script(repo)
    for turn in ["first", "second"]:
        start(repo, turn)
    (repo / "existing.py").write_text("edited\n", encoding="utf-8")
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(invoke, script, event(repo, "Stop", turn))
            for turn in ["first", "second", "first", "second"]
        ]
        assert [future.result() for future in futures] == [{}, {}, {}, {}]
    assert len(rows(repo)) == 2
    assert rows(repo)[0].startswith("| 19 |")
    assert rows(repo)[1].startswith("| 20 |")
    assert len(detail_logs(repo)) == 2


def test_retry_after_log_saved_but_index_write_failed(repo: Path, monkeypatch):
    start(repo)
    (repo / "existing.py").write_text("edited\n", encoding="utf-8")
    original_write = hook.atomic_write

    def fail_index(path: Path, text: str):
        if path.name == "worklog.md":
            raise OSError("index unavailable")
        original_write(path, text)

    with monkeypatch.context() as context:
        context.setattr(hook, "atomic_write", fail_index)
        with pytest.raises(OSError, match="index unavailable"):
            stop(repo)
    assert rows(repo) == []
    assert len(detail_logs(repo)) == 1
    assert stop(repo)
    assert len(rows(repo)) == len(detail_logs(repo)) == 1


def test_payload_cannot_redirect_writes_outside_repository(repo: Path):
    with pytest.raises(ValueError, match="different repository"):
        hook.handle(repo, event(repo, "UserPromptSubmit", cwd=str(repo.parent)))
    assert not (repo / ".local").exists()
