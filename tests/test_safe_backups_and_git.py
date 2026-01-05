import subprocess

from bldrx.engine import Engine


def _git(*args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


def test_backup_created_before_apply(tmp_path):
    # arrange: create a template with a file that will overwrite an existing file
    templates_dir = tmp_path / "templates"
    t = templates_dir / "safe"
    (t / "existing.txt.j2").parent.mkdir(parents=True, exist_ok=True)
    (t / "existing.txt.j2").write_text("New content {{ project_name }}")

    # dest with existing file
    dest = tmp_path / "project"
    dest.mkdir()
    (dest / "existing.txt").write_text("OLD CONTENT")

    engine = Engine(
        templates_root=templates_dir, user_templates_root=tmp_path / "user_templates"
    )

    # act: apply with backup flag (TDD: currently not implemented)
    list(
        engine.apply_template(
            "safe", dest, {"project_name": "X"}, force=True, backup=True
        )
    )

    # assert: backups dir exists with previous content
    backups_root = dest / ".bldrx" / "backups"
    assert backups_root.exists(), "Backups root should exist"
    # there should be a backup directory with the original file content preserved
    found = False
    for candidate in backups_root.rglob("existing.txt"):
        if candidate.read_text() == "OLD CONTENT":
            found = True
            break
    assert found, "Original file content should be present in backups"


def test_git_commit_created_on_apply(tmp_path):
    # arrange: create template
    templates_dir = tmp_path / "templates"
    t = templates_dir / "safe"
    (t / "existing.txt.j2").parent.mkdir(parents=True, exist_ok=True)
    (t / "existing.txt.j2").write_text("New content for {{ project_name }}")

    dest = tmp_path / "project"
    dest.mkdir()
    (dest / "existing.txt").write_text("OLD CONTENT")

    # initialize git repo and commit old content
    _git("init", cwd=dest)
    _git("config", "user.email", "test@example.com", cwd=dest)
    _git("config", "user.name", "Test User", cwd=dest)
    # disable gpg signing in test repo to keep commits non-interactive in CI/dev envs
    _git("config", "commit.gpgsign", "false", cwd=dest)
    _git("add", ".", cwd=dest)
    _git("commit", "-m", "initial commit", cwd=dest)

    engine = Engine(
        templates_root=templates_dir, user_templates_root=tmp_path / "user_templates"
    )

    # act: apply template with git_commit (TDD: currently not implemented)
    list(
        engine.apply_template(
            "safe",
            dest,
            {"project_name": "X"},
            force=True,
            backup=True,
            git_commit=True,
            git_message="Apply safe template",
        )
    )

    # assert: last git commit message is our message
    res = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=dest,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Apply safe template" in res.stdout
