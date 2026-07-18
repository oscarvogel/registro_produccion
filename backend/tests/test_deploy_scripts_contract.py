from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_remote_deploy_script_has_safe_release_contract():
    script = read("deploy_produccion_fg.sh")

    required_fragments = [
        "RELEASE_MANIFEST.txt",
        "EXPECTED_COMMIT",
        "pre_deploy_",
        "frontend.next",
        "frontend.previous",
        "restore_backup",
        "curl -fsS \"$HEALTH_URL\"",
        "curl -fsSI \"$PUBLIC_URL\"",
        "sha256sum",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in script]
    assert missing == []


def test_windows_package_script_builds_manifested_package_without_env_files():
    script = read("scripts/build_deploy_package.ps1")

    required_fragments = [
        "git rev-parse HEAD",
        "git rev-parse origin/main",
        "python -m pytest",
        "npm run test",
        "npm run build",
        "RELEASE_MANIFEST.txt",
        "backend/app",
        "backend/requirements.txt",
        "frontend/dist",
        "deploy_produccion_fg.sh",
        "backend/.env",
        "frontend/.env",
        "__pycache__",
        "tar -czf",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in script]
    assert missing == []


def test_github_main_docker_deploy_has_safe_contract():
    script = read("scripts/deploy_main_fasa195.sh")

    required_fragments = [
        'EXPECTED_HOSTNAME="${EXPECTED_HOSTNAME:-fg-ubuntu}"',
        'APP_DIR="${APP_DIR:-/srv/apps/registro_produccion}"',
        'REMOTE="origin"',
        'BRANCH="main"',
        "--check",
        "--deploy",
        "--yes",
        "flock",
        "git status --porcelain",
        "git fetch --prune",
        "git merge-base --is-ancestor",
        "git merge --ff-only",
        "registro_produccion:${target_commit}",
        "docker compose config",
        "python -m compileall",
        "import app.main",
        "indufor produccion_fg",
        "http://127.0.0.1:18004/health",
        "http://127.0.0.1:18005/health",
        ".deploy-backups",
        "rollback",
        "trap handle_signal INT TERM",
        "rollback_failed",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in script]
    assert missing == []


def test_github_main_runbook_documents_safe_operator_flow():
    runbook = read("docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md")
    required = [
        "--check",
        "--deploy",
        "--yes",
        "indufor",
        "produccion_fg",
        "indufor_demo",
        "Nginx",
        ".env",
        "rollback",
    ]

    missing = [fragment for fragment in required if fragment not in runbook]
    assert missing == []


def test_production_deploy_package_applies_idempotent_db_migrations():
    package_script = read("scripts/build_deploy_package.ps1")
    deploy_script = read("deploy_produccion_fg.sh")
    migration = read("db_migrations/20260708_personal_unidad_negocio.sql")

    package_fragments = [
        "db_migrations",
        "20260708_personal_unidad_negocio.sql",
    ]
    deploy_fragments = [
        "Aplicando migraciones DB",
        "DATABASE_URL",
        "mysql --defaults-extra-file",
        'for migration in "$migrations_dir"/*.sql',
    ]
    migration_fragments = [
        "CREATE TABLE IF NOT EXISTS personal_unidad_negocio",
        "INSERT IGNORE INTO personal_unidad_negocio",
        "REFERENCES personal",
        "REFERENCES unidadnegocio",
    ]

    missing = [fragment for fragment in package_fragments if fragment not in package_script]
    missing += [fragment for fragment in deploy_fragments if fragment not in deploy_script]
    missing += [fragment for fragment in migration_fragments if fragment not in migration]
    assert missing == []


def test_admin_actas_crud_contract_is_registered():
    schemas = read("backend/app/schemas/admin.py")
    admin_routes = read("backend/app/api/routes/admin_legacy.py")
    catalog_routes = read("backend/app/api/routes/admin_catalogs.py")

    required_fragments = [
        "class ActaCreate",
        "class ActaUpdate",
        "class ActaAdminResponse",
        "def list_actas_admin",
        "def create_acta",
        "def update_acta",
        "def delete_acta",
        '"/actas"',
        '"/actas/{acta_id}"',
        "ActaAdminResponse",
    ]

    combined = "\n".join([schemas, admin_routes, catalog_routes])
    missing = [fragment for fragment in required_fragments if fragment not in combined]
    assert missing == []
