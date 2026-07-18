import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")


def bash_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/{resolved.drive[0].lower()}{resolved.as_posix()[2:]}"


@dataclass
class DeployHarness:
    root: Path

    @property
    def call_log(self) -> Path:
        return self.root / "calls.log"

    @property
    def calls(self) -> str:
        return self.call_log.read_text(encoding="utf-8") if self.call_log.exists() else ""

    def run(
        self,
        *arguments: str,
        git_status: str = "",
        merge_base_exit: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "EXPECTED_HOSTNAME": "test-host",
                "APP_DIR": str(self.root / "app"),
                "ENV_DIR": str(self.root / "env"),
                "BACKUP_DIR": str(self.root / "backups"),
                "LOCK_FILE": str(self.root / "deploy.lock"),
                "CALL_LOG": str(self.call_log),
                "FAKE_GIT_STATUS": git_status,
                "FAKE_MERGE_BASE_EXIT": str(merge_base_exit),
            }
        )
        script = REPO_ROOT / "scripts/deploy_main_fasa195.sh"
        return subprocess.run(
            [
                str(BASH),
                "-c",
                'export PATH="$1:$PATH"; shift; exec "$@"',
                "deploy-test",
                bash_path(self.root / "fake-bin"),
                bash_path(script),
                *arguments,
            ],
            cwd=self.root / "app",
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )


def write_fake(path: Path, body: str) -> None:
    path.write_text(f"#!/usr/bin/env bash\nset -eu\n{body}\n", encoding="utf-8", newline="\n")
    path.chmod(0o755)


@pytest.fixture
def deploy_harness(tmp_path: Path) -> DeployHarness:
    app_dir = tmp_path / "app"
    env_dir = tmp_path / "env"
    fake_bin = tmp_path / "fake-bin"
    app_dir.mkdir()
    (app_dir / ".git").mkdir()
    env_dir.mkdir()
    fake_bin.mkdir()
    (env_dir / "indufor.env").write_text("APP_INSTANCE=indufor\n", encoding="utf-8")
    (env_dir / "produccion_fg.env").write_text(
        "APP_INSTANCE=produccion_fg\n", encoding="utf-8"
    )

    write_fake(
        fake_bin / "hostname",
        """
printf '%s\\n' test-host
""",
    )
    write_fake(
        fake_bin / "flock",
        """
printf 'flock %s\\n' "$*" >>"$CALL_LOG"
""",
    )
    write_fake(
        fake_bin / "git",
        """
printf 'git %s\\n' "$*" >>"$CALL_LOG"
case "$*" in
  "status --porcelain") printf '%s' "${FAKE_GIT_STATUS:-}" ;;
  "rev-parse origin/main") printf '%s\\n' target-commit ;;
  "rev-parse HEAD") printf '%s\\n' current-commit ;;
  "rev-parse main") printf '%s\\n' current-main ;;
  "merge-base --is-ancestor"*) exit "${FAKE_MERGE_BASE_EXIT:-0}" ;;
  "show-ref --verify --quiet refs/heads/main") exit 0 ;;
esac
""",
    )
    write_fake(
        fake_bin / "docker",
        """
printf 'docker %s\\n' "$*" >>"$CALL_LOG"
case "$*" in
  "compose config --services") printf '%s\\n' indufor produccion_fg ;;
esac
""",
    )
    write_fake(fake_bin / "curl", """printf 'curl %s\\n' "$*" >>"$CALL_LOG" """)
    write_fake(fake_bin / "sleep", """:""")

    return DeployHarness(tmp_path)


def test_check_rejects_dirty_checkout(deploy_harness: DeployHarness):
    result = deploy_harness.run("--check", git_status=" M backend/app/main.py")

    assert result.returncode != 0
    assert "checkout is not clean" in result.stderr
    assert "docker compose up" not in deploy_harness.calls


def test_check_rejects_non_fast_forward_main(deploy_harness: DeployHarness):
    result = deploy_harness.run("--check", merge_base_exit=1)

    assert result.returncode != 0
    assert "not a fast-forward" in result.stderr


def test_check_is_read_only(deploy_harness: DeployHarness):
    result = deploy_harness.run("--check")

    assert result.returncode == 0
    assert "git merge --ff-only" not in deploy_harness.calls
    assert "docker compose build" not in deploy_harness.calls
    assert "docker compose up" not in deploy_harness.calls
