import json
import os

import yaml
from github import Github
from invoke import task

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@task()
def init_app(c, env=None):
    # Prevent execute this function more than once
    if not os.environ.get("APP_SETTINGS"):
        # Load the basic configs
        env_vars = load_yaml_from_file(
            os.path.join(BASEDIR, "resources", "settings.yml")
        )

        for name, data in env_vars.items():
            set_env_var(
                c, name, data.get("value"), env, data.get("is_protected", False)
            )


@task(init_app)
def run_app(c, env=None):
    run(c, "python -m tvsort_sl.app", False)


def run(c, command, with_venv=True):
    if with_venv:
        command = "{} && {}".format(get_venv_action(), command)

    print("Running: {}".format(command))
    c.run(command)


def set_env_var(c, name, value, env, is_protected=True):
    # env codes: t - Travis-CI , None - Dev
    if isinstance(value, dict):
        value = json.dumps(value)

    if env == "t":
        command = "travis env set {} '{}'".format(name, value)
        if not is_protected:
            command = "{} --public".format(command)

        if command:
            run(c, command, False)

    else:
        print(f"Set local var: {name}={value}")
        os.environ[name] = value


def load_yaml_from_file(file_path):
    with open(file_path, "r") as stream:
        return yaml.safe_load(stream)


def is_unix():
    return os.name == "posix"


def get_venv_action():
    if is_unix():
        return f"source {BASEDIR}/venv/bin/activate"
    else:
        return f"{BASEDIR}\\venv\\Scripts\\activate"


@task(init_app)
def test(c, cov=False, file=None):
    # cov - if to use coverage, file - if to run specific file

    command = "pytest -s -p no:warnings"
    if cov:
        command = "{} --cov=slots_tracker_server --cov-report term-missing".format(
            command
        )
    if file:
        command = "{} {}".format(command, file)

    run(c, command)


@task(init_app)
def mutmut(c):
    command = "mutmut run"
    run(c, command)


@task()
def bump_version(c):
    files_to_update = ['setup.py', '.bumpversion.cfg']
    branch_name = 'develop'

    github_client = Github(os.environ['GITHUB_ACCESS_TOKEN'])
    repo = github_client.get_repo('shlomiLan/tvsort_sl')

    pr = repo.get_pull(68)
    for pr_file in pr.get_files():
        pr_filename = pr_file.filename
        if pr_filename in files_to_update:
            print('Version was already bumped, exiting')
            return

    print('Bumping version')
    print(run(c, 'bumpversion --verbose patch  --allow-dirty', with_venv=False))

    # Updating GitHub with new changes
    for filename in files_to_update:
        file_object = repo.get_contents(path=filename, ref=branch_name)
        with open(filename) as f:
            repo.update_file(file_object.path, "Update version, file: {}".format(filename), f.read(),
                             file_object.sha, branch=branch_name)
