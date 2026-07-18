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

    def latest_manifest(self) -> dict[str, str]:
        manifests = sorted((self.root / "backups").glob("deploy_*.env"))
        assert manifests
        return dict(
            line.split("=", 1)
            for line in manifests[-1].read_text(encoding="utf-8").splitlines()
            if "=" in line
        )

    def run(
        self,
        *arguments: str,
        git_status: str = "",
        merge_base_exit: int = 0,
        target_commit: str = "target-commit",
        fail_health: str = "",
        fail_rollback_service: str = "",
        extra_env: dict[str, str] | None = None,
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
                "FAKE_TARGET_COMMIT": target_commit,
                "FAKE_STATE_DIR": str(self.root),
                "FAKE_FAIL_HEALTH": fail_health,
                "FAKE_FAIL_ROLLBACK_SERVICE": fail_rollback_service,
            }
        )
        if extra_env:
            env.update(extra_env)
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
  "rev-parse origin/main") printf '%s\\n' "${FAKE_TARGET_COMMIT:-target-commit}" ;;
  "rev-parse HEAD")
    if [[ -f "$FAKE_STATE_DIR/merged" ]]; then
      printf '%s\\n' "${FAKE_TARGET_COMMIT:-target-commit}"
    else
      printf '%s\\n' current-commit
    fi
    ;;
  "rev-parse main") printf '%s\\n' current-main ;;
  "branch --show-current") printf '%s\\n' old-branch ;;
  "merge-base --is-ancestor"*) exit "${FAKE_MERGE_BASE_EXIT:-0}" ;;
  "show-ref --verify --quiet refs/heads/main") exit 0 ;;
  "merge --ff-only origin/main") touch "$FAKE_STATE_DIR/merged" ;;
esac
""",
    )
    write_fake(
        fake_bin / "docker",
        """
printf 'docker %s\\n' "$*" >>"$CALL_LOG"
case "$*" in
  "compose config --services") printf '%s\\n' indufor produccion_fg ;;
  "compose -f docker-compose.yml -f "*" config --images")
    override_file="$5"
    awk '/image:/ {print $2}' "$override_file"
    ;;
  "compose -f docker-compose.yml -f "*" up -d --no-build --force-recreate "*)
    service="${*: -1}"
    if [[ -n "${FAKE_FAIL_ROLLBACK_SERVICE:-}" &&
          "$service" == "$FAKE_FAIL_ROLLBACK_SERVICE" &&
          -f "$FAKE_STATE_DIR/health-fail-count" ]]; then
      exit 1
    fi
    ;;
  "inspect -f {{.Image}} registro_produccion_indufor")
    printf '%s\\n' old-indufor-image
    ;;
  "inspect -f {{.Image}} registro_produccion_produccion_fg")
    printf '%s\\n' old-produccion-image
    ;;
  "inspect -f {{.State.Health.Status}}"*)
    container="${*: -1}"
    if [[ -n "${FAKE_FAIL_HEALTH:-}" && "$container" == "$FAKE_FAIL_HEALTH" ]]; then
      count_file="$FAKE_STATE_DIR/health-fail-count"
      count=0
      [[ -f "$count_file" ]] && count="$(cat "$count_file")"
      count=$((count + 1))
      printf '%s' "$count" >"$count_file"
      if [[ "$count" -le 30 ]]; then
        printf '%s\\n' unhealthy
      else
        printf '%s\\n' healthy
      fi
    else
      printf '%s\\n' healthy
    fi
    ;;
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


def test_deploy_builds_commit_image_and_updates_services_in_order(
    deploy_harness: DeployHarness,
):
    result = deploy_harness.run("--deploy", "--yes", target_commit="abc123")

    assert result.returncode == 0, result.stderr
    calls = deploy_harness.calls.splitlines()
    assert "git switch main" in calls
    assert "git merge --ff-only origin/main" in calls
    assert "docker build --tag registro_produccion:abc123 ." in calls
    indufor_call = next(
        index
        for index, call in enumerate(calls)
        if "up -d --no-build --force-recreate indufor" in call
    )
    produccion_call = next(
        index
        for index, call in enumerate(calls)
        if "up -d --no-build --force-recreate produccion_fg" in call
    )
    assert indufor_call < produccion_call
    assert any("http://127.0.0.1:18004/health" in call for call in calls)
    assert any("http://127.0.0.1:18005/health" in call for call in calls)


def test_deploy_requires_yes_when_not_interactive(deploy_harness: DeployHarness):
    result = deploy_harness.run("--deploy")

    assert result.returncode != 0
    assert "interactive terminal or --yes" in result.stderr
    assert "docker build" not in deploy_harness.calls


def test_indufor_failure_restores_only_indufor(deploy_harness: DeployHarness):
    result = deploy_harness.run(
        "--deploy", "--yes", fail_health="registro_produccion_indufor"
    )

    assert result.returncode != 0
    assert "rollback_service indufor old-indufor-image" in result.stdout
    assert "rollback_service produccion_fg" not in result.stdout
    assert not any(
        "up -d --no-build --force-recreate produccion_fg" in call
        for call in deploy_harness.calls.splitlines()
    )


def test_produccion_failure_restores_both_services(deploy_harness: DeployHarness):
    result = deploy_harness.run(
        "--deploy",
        "--yes",
        fail_health="registro_produccion_produccion_fg",
    )

    assert result.returncode != 0
    assert "rollback_service produccion_fg old-produccion-image" in result.stdout
    assert "rollback_service indufor old-indufor-image" in result.stdout
    assert deploy_harness.calls.count("http://127.0.0.1:18004/health") >= 2
    assert "http://127.0.0.1:18005/health" in deploy_harness.calls


def test_manifest_records_previous_and_target_state(deploy_harness: DeployHarness):
    result = deploy_harness.run("--deploy", "--yes", target_commit="abc123")

    assert result.returncode == 0, result.stderr
    manifest = deploy_harness.latest_manifest()
    assert manifest["target_commit"] == "abc123"
    assert manifest["previous_indufor_image"] == "old-indufor-image"
    assert manifest["previous_produccion_fg_image"] == "old-produccion-image"


def test_failed_rollback_is_reported_truthfully(deploy_harness: DeployHarness):
    result = deploy_harness.run(
        "--deploy",
        "--yes",
        fail_health="registro_produccion_indufor",
        fail_rollback_service="indufor",
    )

    assert result.returncode != 0
    assert "rollback failed" in result.stderr
    assert deploy_harness.latest_manifest()["status"] == "rollback_failed"


def test_origin_main_cannot_be_overridden_from_environment(
    deploy_harness: DeployHarness,
):
    result = deploy_harness.run(
        "--check",
        extra_env={"REMOTE": "attacker", "BRANCH": "unsafe"},
    )

    assert result.returncode == 0, result.stderr
    assert "git fetch --prune origin" in deploy_harness.calls
    assert "git rev-parse origin/main" in deploy_harness.calls
    assert "attacker" not in deploy_harness.calls
    assert "unsafe" not in deploy_harness.calls


def test_success_output_contains_live_evidence(deploy_harness: DeployHarness):
    result = deploy_harness.run("--deploy", "--yes", target_commit="abc123")

    assert result.returncode == 0, result.stderr
    assert "indufor_image=" in result.stdout
    assert "produccion_fg_image=" in result.stdout
    assert "indufor_health_url=http://127.0.0.1:18004/health" in result.stdout
    assert (
        "produccion_fg_health_url=http://127.0.0.1:18005/health" in result.stdout
    )
