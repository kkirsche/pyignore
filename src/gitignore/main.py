from datetime import datetime, UTC
from typer import Typer
from gitignore.client import GithubClient
from gitignore.type_adapters import GitignoreConfig
from tomllib import loads
from tomli_w import dumps
from pathlib import Path

app = Typer()
config_file = Path(".gitignore.toml")
gitignore_file = Path(".gitignore")
run_time = datetime.now(tz=UTC)


@app.command("list")
def list_templates() -> None:
    client = GithubClient()
    for project in sorted(client.list_project_templates()):
        print(project)


@app.command("show")
def show_template(template_name: str) -> None:
    client = GithubClient()
    gitignore = client.get_project_template(template_name)
    print(gitignore.source)


@app.command("add")
def add_template(template_name: str) -> None:
    config_file.touch(exist_ok=True)
    config_str = config_file.read_text(encoding="utf-8")
    config = loads(config_str)
    parsed = GitignoreConfig.model_validate(config)

    client = GithubClient()
    gitignore = client.get_project_template(template_name)

    parsed.templates[gitignore.name] = run_time
    config_str = dumps(parsed.model_dump(mode="json"))
    config_file.write_text(data=config_str, encoding="utf-8")

    gitignore_file.touch(exist_ok=True)
    with gitignore_file.open("a", encoding="utf-8") as f:
        print(f"Adding {template_name}@{run_time}…")
        f.write(gitignore.source)
        f.write("\n")


@app.command("update")
def update_gitignore() -> None:
    config_file.touch(exist_ok=True)
    config_str = config_file.read_text(encoding="utf-8")
    config = loads(config_str)
    parsed = GitignoreConfig.model_validate(config)
    client = GithubClient()
    source = ["# This file is managed by Gitignore and should not be edited manually"]
    for template_name in parsed.templates.keys():
        print(f"Updating to {template_name}@{run_time}…")
        gitignore = client.get_project_template(template_name)
        source.extend(
            [
                f"# start gitignore template={gitignore.name!r}",
                gitignore.source,
                f"# end gitignore template={gitignore.name!r}",
            ]
        )
        parsed.templates[template_name] = run_time
    gitignore_file.touch(exist_ok=True)
    gitignore_file.write_text("\n".join(source), encoding="utf-8")
    config_file.write_text(dumps(parsed.model_dump(mode="json")), encoding="utf-8")


def main() -> None:
    app()
