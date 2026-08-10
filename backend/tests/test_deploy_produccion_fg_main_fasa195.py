import io
import os
import re
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path

import pytest


pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="Test designed for Windows Git Bash (bash.exe + drive-letter paths).",
)


REPO_ROOT = Path(__file__).resolve().parents[2]
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")


def bash_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/{resolved.drive[0].lower()}{resolved.as_posix()[2:]}"


def write_fake(path: Path, body: str) -> None:
    path.write_text(
        f"#!/usr/bin/env bash\nset -eu\n{body}\n",
        encoding="utf-8",
        newline="\n",
    )
    path.chmod(0o755)


def add_tar_text(archive: tarfile.TarFile, name: str, content: str) -> None:
    payload = content.encode("utf-8")
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def write_deploy_package(path: Path, *, include_frontend_asset: bool = True) -> None:
    with tarfile.open(path, "w:gz") as archive:
        add_tar_text(archive, "backend/app/main.py", "APP = 'target'\n")
        add_tar_text(archive, "backend/requirements.txt", "fastapi\n")
        add_tar_text(
            archive,
            "frontend/dist/index.html",
            '<div id="app"></div><script src="/assets/index-target.js"></script>\n',
        )
        if include_frontend_asset:
            add_tar_text(
                archive,
                "frontend/dist/assets/index-target.js",
                "console.log('target')\n",
            )
        add_tar_text(
            archive,
            "RELEASE_MANIFEST.txt",
            "name=registro_produccion\n"
            "commit=target-commit\n"
            "short_commit=target\n"
            "branch=main\n"
            "built_at=2026-08-01T00:00:00Z\n",
        )


@dataclass
class DeployHarness:
    root: Path

    @property
    def source_dir(self) -> Path:
        return self.root / "source"

    @property
    def app_parent(self) -> Path:
        return self.root / "published"

    @property
    def package(self) -> Path:
        return self.root / "registro_produccion_deploy_target.tar.gz"

    @property
    def calls(self) -> str:
        call_log = self.root / "calls.log"
        return call_log.read_text(encoding="utf-8") if call_log.exists() else ""

    @property
    def manifest(self) -> dict[str, str]:
        manifests = sorted((self.root / "backups").glob("deploy_*.env"))
        assert manifests
        return dict(
            line.split("=", 1)
            for line in manifests[-1].read_text(encoding="utf-8").splitlines()
            if "=" in line
        )

    def run(
        self,
        mode: str,
        *extra_arguments: str,
        target_commit: str = "target-commit",
        source_head: str = "target-commit",
        deployed_is_ancestor: bool = True,
        changed_files: str = "",
        git_status: str = "",
        fail_target_health: bool = False,
        fail_rollback: bool = False,
        change_indufor_after_deploy: bool = False,
        fail_frontend_publish: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "SOURCE_DIR": bash_path(self.source_dir),
                "APP_PARENT": bash_path(self.app_parent),
                "BACKUP_DIR": bash_path(self.root / "backups"),
                "LOCK_FILE": bash_path(self.root / "deploy.lock"),
                "CALL_LOG": bash_path(self.root / "calls.log"),
                "FAKE_STATE_DIR": bash_path(self.root),
                "FAKE_TARGET_COMMIT": target_commit,
                "FAKE_SOURCE_HEAD": source_head,
                "FAKE_DEPLOYED_IS_ANCESTOR": "1" if deployed_is_ancestor else "0",
                "FAKE_CHANGED_FILES": changed_files,
                "FAKE_GIT_STATUS": git_status,
                "FAKE_FAIL_TARGET_HEALTH": "1" if fail_target_health else "0",
                "FAKE_FAIL_ROLLBACK": "1" if fail_rollback else "0",
                "FAKE_CHANGE_INDUFOR_AFTER_DEPLOY": (
                    "1" if change_indufor_after_deploy else "0"
                ),
                "FAKE_FAIL_FRONTEND_PUBLISH": "1" if fail_frontend_publish else "0",
            }
        )
        script = REPO_ROOT / "scripts/deploy_produccion_fg_main_fasa195.sh"
        return subprocess.run(
            [
                str(BASH),
                "-c",
                'export PATH="$1:$PATH"; shift; exec "$@"',
                "deploy-test",
                bash_path(self.root / "fake-bin"),
                bash_path(script),
                mode,
                *extra_arguments,
                bash_path(self.package),
            ],
            cwd=self.source_dir,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )


@pytest.fixture
def deploy_harness(tmp_path: Path) -> DeployHarness:
    source_dir = tmp_path / "source"
    app_parent = tmp_path / "published"
    frontend_dir = app_parent / "frontend"
    fake_bin = tmp_path / "fake-bin"
    for directory in (source_dir / ".git", frontend_dir, fake_bin, tmp_path / "backups"):
        directory.mkdir(parents=True)

    (source_dir / "docker-compose.yml").write_text(
        "services:\n  produccion_fg:\n    image: registro_produccion:latest\n",
        encoding="utf-8",
    )
    (frontend_dir / "index.html").write_text("old frontend", encoding="utf-8")
    (app_parent / "RELEASE_MANIFEST.txt").write_text(
        "name=registro_produccion\n"
        "commit=deployed-commit\n"
        "short_commit=deployed\n"
        "branch=main\n",
        encoding="utf-8",
    )
    write_deploy_package(tmp_path / "registro_produccion_deploy_target.tar.gz")

    write_fake(fake_bin / "hostname", "printf '%s\\n' fg-ubuntu")
    write_fake(fake_bin / "flock", "printf 'flock %s\\n' \"$*\" >>\"$CALL_LOG\"")
    write_fake(
        fake_bin / "git",
        r'''
printf 'git %s\n' "$*" >>"$CALL_LOG"
case "$*" in
  "rev-parse --is-inside-work-tree") printf '%s\n' true ;;
  "status --porcelain") printf '%s' "${FAKE_GIT_STATUS:-}" ;;
  "fetch --prune origin") : ;;
  "rev-parse origin/main") printf '%s\n' "${FAKE_TARGET_COMMIT:-target-commit}" ;;
  "rev-parse HEAD") printf '%s\n' "${FAKE_SOURCE_HEAD:-target-commit}" ;;
  "merge-base --is-ancestor deployed-commit "*)
    [[ "${FAKE_DEPLOYED_IS_ANCESTOR:-1}" == "1" ]]
    ;;
  "diff --name-only deployed-commit "*" -- db_migrations")
    printf '%s' "${FAKE_CHANGED_FILES:-}"
    ;;
esac
''',
    )
    write_fake(
        fake_bin / "docker",
        r'''
printf 'docker %s\n' "$*" >>"$CALL_LOG"
case "$*" in
  "compose -f docker-compose.yml config --services")
    printf '%s\n' produccion_fg
    ;;
  "inspect -f {{.Id}}|{{.Image}} registro_produccion_indufor")
    if [[ -f "$FAKE_STATE_DIR/target-deployed" && "${FAKE_CHANGE_INDUFOR_AFTER_DEPLOY:-0}" == "1" ]]; then
      printf '%s\n' changed-indufor-container\|changed-indufor-image
    else
      printf '%s\n' indufor-container-id\|indufor-image-id
    fi
    ;;
  "inspect -f {{.Id}}|{{.Image}} registro_produccion_indufor_demo")
    printf '%s\n' demo-container-id\|demo-image-id
    ;;
  "inspect -f {{.Image}} registro_produccion_produccion_fg")
    if [[ -f "$FAKE_STATE_DIR/target-deployed" ]]; then
      printf '%s\n' target-image-id
    else
      printf '%s\n' old-image-id
    fi
    ;;
  "inspect -f {{.State.Health.Status}} registro_produccion_produccion_fg")
    if [[ -f "$FAKE_STATE_DIR/target-deployed" && "${FAKE_FAIL_TARGET_HEALTH:-0}" == "1" ]]; then
      printf '%s\n' unhealthy
    else
      printf '%s\n' healthy
    fi
    ;;
  "image inspect registro_produccion:target-commit --format {{.Id}}")
    printf '%s\n' target-image-id
    ;;
  "tag old-image-id registro_produccion:rollback-"*) : ;;
  "compose -f docker-compose.yml -f "*" up -d --no-build --no-deps --force-recreate produccion_fg")
    if grep -q 'registro_produccion:rollback-' "$5"; then
      rm -f "$FAKE_STATE_DIR/target-deployed"
      [[ "${FAKE_FAIL_ROLLBACK:-0}" != "1" ]]
    else
      touch "$FAKE_STATE_DIR/target-deployed"
    fi
    ;;
esac
''',
    )
    write_fake(fake_bin / "curl", "printf 'curl %s\\n' \"$*\" >>\"$CALL_LOG\"")
    write_fake(fake_bin / "sleep", ":")
    write_fake(
        fake_bin / "mv",
        r'''
printf 'mv %s\n' "$*" >>"$CALL_LOG"
if [[ "${FAKE_FAIL_FRONTEND_PUBLISH:-0}" == "1" && "$1" == *"/frontend.next-"* && "$2" == */frontend ]]; then
  exit 1
fi
exec /usr/bin/mv "$@"
''',
    )

    return DeployHarness(tmp_path)


def test_check_is_read_only(deploy_harness: DeployHarness):
    result = deploy_harness.run("--check")

    assert result.returncode == 0, result.stderr
    assert "docker build" not in deploy_harness.calls
    assert "docker compose -f docker-compose.yml up" not in deploy_harness.calls


def test_check_rejects_package_not_built_from_origin_main(deploy_harness: DeployHarness):
    result = deploy_harness.run("--check", target_commit="different-main")

    assert result.returncode != 0
    assert "package commit does not match origin/main" in result.stderr


def test_check_rejects_diverged_or_newer_production(deploy_harness: DeployHarness):
    result = deploy_harness.run("--check", deployed_is_ancestor=False)

    assert result.returncode != 0
    assert "deployed commit is not an ancestor" in result.stderr


def test_check_rejects_source_checkout_not_at_origin_main(deploy_harness: DeployHarness):
    result = deploy_harness.run("--check", source_head="older-main")

    assert result.returncode != 0
    assert "source checkout does not match origin/main" in result.stderr


def test_check_aborts_when_range_contains_db_migrations(deploy_harness: DeployHarness):
    result = deploy_harness.run(
        "--check", changed_files="db_migrations/20260801_schema.sql\n"
    )

    assert result.returncode != 0
    assert "database migrations require a separate procedure" in result.stderr


def test_check_rejects_package_when_referenced_frontend_asset_is_missing(
    deploy_harness: DeployHarness,
):
    write_deploy_package(deploy_harness.package, include_frontend_asset=False)

    result = deploy_harness.run("--check")

    assert result.returncode != 0
    assert "package frontend asset not found" in result.stderr


def test_deploy_requires_yes_when_non_interactive(deploy_harness: DeployHarness):
    result = deploy_harness.run("--deploy")

    assert result.returncode != 0
    assert "interactive terminal or --yes" in result.stderr
    assert "docker build" not in deploy_harness.calls


def test_deploy_updates_only_produccion_fg(deploy_harness: DeployHarness):
    result = deploy_harness.run("--deploy", "--yes")

    assert result.returncode == 0, result.stderr
    assert re.search(
        r"docker compose -f docker-compose\.yml -f \S+ up -d --no-build "
        r"--no-deps --force-recreate produccion_fg",
        deploy_harness.calls,
    )
    assert "registro_produccion:latest" not in deploy_harness.calls
    assert "force-recreate indufor\n" not in deploy_harness.calls
    assert "force-recreate indufor_demo\n" not in deploy_harness.calls


def test_success_records_backend_frontend_and_unchanged_neighbors(
    deploy_harness: DeployHarness,
):
    result = deploy_harness.run("--deploy", "--yes")

    assert result.returncode == 0, result.stderr
    assert "target_commit=target-commit" in result.stdout
    assert "produccion_fg_health=healthy" in result.stdout
    assert "frontend_asset=assets/index-target.js" in result.stdout
    assert "indufor_unchanged=yes" in result.stdout
    assert "indufor_demo_unchanged=yes" in result.stdout


def test_failed_health_restores_image_frontend_and_manifest(
    deploy_harness: DeployHarness,
):
    result = deploy_harness.run("--deploy", "--yes", fail_target_health=True)

    assert result.returncode != 0
    assert "docker tag old-image-id registro_produccion:latest" not in deploy_harness.calls
    assert deploy_harness.calls.count("--force-recreate produccion_fg") == 2
    assert deploy_harness.manifest["status"] == "rolled_back"
    assert (deploy_harness.app_parent / "frontend" / "index.html").read_text(
        encoding="utf-8"
    ) == "old frontend"


def test_failed_rollback_is_reported_truthfully(deploy_harness: DeployHarness):
    result = deploy_harness.run(
        "--deploy", "--yes", fail_target_health=True, fail_rollback=True
    )

    assert result.returncode != 0
    assert deploy_harness.manifest["status"] == "rollback_failed"
    assert "rollback failed" in result.stderr


def test_neighbor_invariant_failure_triggers_rollback(deploy_harness: DeployHarness):
    result = deploy_harness.run(
        "--deploy", "--yes", change_indufor_after_deploy=True
    )

    assert result.returncode != 0
    assert "indufor changed during deploy" in result.stderr
    assert "docker tag old-image-id registro_produccion:latest" not in deploy_harness.calls
    assert deploy_harness.calls.count("--force-recreate produccion_fg") == 2
    assert deploy_harness.manifest["status"] == "rolled_back"


def test_partial_frontend_switch_restores_previous_frontend(
    deploy_harness: DeployHarness,
):
    result = deploy_harness.run("--deploy", "--yes", fail_frontend_publish=True)

    assert result.returncode != 0
    assert (deploy_harness.app_parent / "frontend" / "index.html").read_text(
        encoding="utf-8"
    ) == "old frontend"
    assert deploy_harness.manifest["status"] == "rolled_back"
