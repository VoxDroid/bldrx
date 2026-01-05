from pathlib import Path

from bldrx.engine import Engine


def test_apply_github_templates(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "repo"
    metadata = {
        "project_name": "tplproj",
        "author_name": "Tester",
        "email": "t@example.com",
        "github_username": "tester",
    }
    _results = list(engine.apply_template("github", dest, metadata, force=True))
    # root-level files
    assert (dest / "CONTRIBUTING.md").exists()
    assert (dest / "CODE_OF_CONDUCT.md").exists()
    assert (dest / "SUPPORT.md").exists()
    # .github-specific files
    assert (dest / ".github" / "funding.yml").exists()
    assert (dest / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").exists()
    assert (dest / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").exists()
    # check content replacement
    assert "tester" in (dest / "CONTRIBUTING.md").read_text()
    assert "t@example.com" in (dest / "CODE_OF_CONDUCT.md").read_text()


def test_apply_ci_and_lint_templates(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "repo2"
    metadata = {
        "project_name": "ciproj",
        "author_name": "CI Bot",
        "email": "ci@example.com",
    }
    _results = list(engine.apply_template("ci", dest, metadata, force=True))
    assert (dest / "ci.yml").exists()
    assert "ciproj" in (dest / "ci.yml").read_text()
    # lint
    _results2 = list(engine.apply_template("lint", dest, metadata, force=True))
    assert (dest / "pyproject.toml").exists()
    assert "ciproj" in (dest / "pyproject.toml").read_text()
    # eslint
    _results3 = list(engine.apply_template("lint", dest, metadata, force=True))
    assert (dest / ".eslintrc.js").exists()
    # prettierrc
    assert (dest / ".prettierrc").exists()


def test_apply_docker_and_prettier_templates(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "dockproj"
    metadata = {
        "project_name": "dockproj",
        "author_name": "Docker Bot",
        "email": "dock@example.com",
    }
    _results = list(engine.apply_template("docker", dest, metadata, force=True))
    assert (dest / "Dockerfile").exists()
    assert "dockproj" in (dest / "Dockerfile").read_text()
    assert (dest / ".dockerignore").exists()


def test_apply_node_and_react_templates(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "nodeproj"
    metadata = {
        "project_name": "nodeproj",
        "author_name": "Node Dev",
        "email": "node@example.com",
    }
    _results = list(engine.apply_template("node-api", dest, metadata, force=True))
    assert (dest / "package.json").exists()
    assert "nodeproj" in (dest / "package.json").read_text()
    assert (dest / "src" / "index.js").exists()

    dest2 = tmp_path / "reactproj"
    metadata2 = {
        "project_name": "reactproj",
        "author_name": "React Dev",
        "email": "react@example.com",
    }
    _results2 = list(engine.apply_template("react-app", dest2, metadata2, force=True))
    assert (dest2 / "package.json").exists()
    assert "reactproj" in (dest2 / "package.json").read_text()
    assert (dest2 / "src" / "App.js").exists()
