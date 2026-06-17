from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_demo_deploy_script_has_required_guardrails():
    script = (REPO_ROOT / "scripts" / "deploy_indufor_demo.sh").read_text(encoding="utf-8")

    required_snippets = [
        "set -euo pipefail",
        'EXPECTED_HOSTNAME="fg-ubuntu"',
        'APP_DIR="/srv/apps/registro_produccion"',
        'ENV_FILE="/srv/env/registro_produccion/indufor_demo.env"',
        "git fetch origin --prune",
        "git switch codex/docker-multi-instance-registro-produccion",
        "git pull --ff-only origin codex/docker-multi-instance-registro-produccion",
        "COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.demo.yml)",
        '"${COMPOSE[@]}" config >/dev/null',
        '"${COMPOSE[@]}" up -d --build "$SERVICE"',
        'HEALTH_URL="http://127.0.0.1:18104/health"',
        'OPENAPI_URL="http://127.0.0.1:18104/openapi.json"',
        'curl -fsS "$HEALTH_URL" >/dev/null',
        'curl -fsS "$OPENAPI_URL" >/dev/null',
        "exec -T indufor_demo python -m app.seed.demo_data",
    ]
    for snippet in required_snippets:
        assert snippet in script

    forbidden_snippets = [
        "nginx",
        "produccion_fg up",
        "docker compose up -d indufor ",
        "cat $ENV_FILE",
        "cat \"$ENV_FILE\"",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in script


def test_demo_env_example_contains_no_real_secret_values():
    env_example = (REPO_ROOT / "docs" / "examples" / "indufor_demo.env.example").read_text(
        encoding="utf-8"
    )

    assert "APP_ENV=staging" in env_example
    assert "APP_INSTANCE=indufor_demo" in env_example
    assert "EXPECTED_DB_NAME=indufor_demo" in env_example
    assert "ALLOW_DEMO_SEED=false" in env_example
    assert "DEMO_SEED_RECORDS=200" in env_example
    assert "CAMBIAR_PASSWORD" in env_example
    assert "vps-922868-x.dattaweb.com" not in env_example
    assert "root:" not in env_example
