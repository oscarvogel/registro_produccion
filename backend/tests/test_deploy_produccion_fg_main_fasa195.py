import io
import os
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path

import pytest


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
        deployed_is_ancestor: bool = True,
        changed_files: str = "",
        git_status: str = "",
        fail_target_health: bool = False,
        fail_rollback: bool = False,
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
                "FAKE_DEPLOYED_IS_ANCESTOR": "1" if deployed_is_ancestor else "0",
                "FAKE_CHANGED_FILES": changed_files,
                "FAKE_GIT_STATUS": git_status,
                "FAKE_FAIL_TARGET_HEALTH": "1" if fail_target_health else "0",
                "FAKE_FAIL_ROLLBACK": "1" if fail_rollback else "0",
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
    with tarfile.open(tmp_path / "registro_produccion_deploy_target.tar.gz", "w:gz") as archive:
        add_tar_text(archive, "backend/app/main.py", "APP = 'target'\n")
        add_tar_text(archive, "backend/requirements.txt", "fastapi\n")
        add_tar_text(
            archive,
            "frontend/dist/index.html",
            '<div id="app"></div><script src="/assets/index-target.js"></script>\n',
        )
        add_tar_text(archive, "frontend/dist/assets/index-target.js", "console.log('target')\n")
        add_tar_text(
            archive,
            "RELEASE_MANIFEST.txt",
            "name=registro_produccion\n"
            "commit=target-commit\n"
            "short_commit=target\n"
            "branch=main\n"
            "built_at=2026-08-01T00:00:00Z\n",
        )

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
    printf '%s\n' indufor-container-id\|indufor-image-id
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
  "tag registro_produccion:target-commit registro_produccion:latest")
    touch "$FAKE_STATE_DIR/target-tagged"
    ;;
  "tag old-image-id registro_produccion:latest")
    rm -f "$FAKE_STATE_DIR/target-tagged"
    touch "$FAKE_STATE_DIR/rollback-tagged"
    ;;
  "compose -f docker-compose.yml up -d --no-build --no-deps --force-recreate produccion_fg")
    if [[ -f "$FAKE_STATE_DIR/rollback-tagged" ]]; then
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


def test_check_aborts_when_range_contains_db_migrations(deploy_harness: DeployHarness):
    result = deploy_harness.run(
        "--check", changed_files="db_migrations/20260801_schema.sql\n"
    )

    assert result.returncode != 0
    assert "database migrations require a separate procedure" in result.stderr


def test_deploy_requires_yes_when_non_interactive(deploy_harness: DeployHarness):
    result = deploy_harness.run("--deploy")

    assert result.returncode != 0
    assert "interactive terminal or --yes" in result.stderr
    assert "docker build" not in deploy_harness.calls


def test_deploy_updates_only_produccion_fg(deploy_harness: DeployHarness):
    result = deploy_harness.run("--deploy", "--yes")

    assert result.returncode == 0, result.stderr
    assert (
        "docker compose -f docker-compose.yml up -d --no-build --no-deps "
        "--force-recreate produccion_fg"
    ) in deploy_harness.calls
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
    assert "docker tag old-image-id registro_produccion:latest" in deploy_harness.calls
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
