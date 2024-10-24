import json
import os
import time
from distutils.util import strtobool

import yaml
from github import Github
from invoke import task

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@task()
def init_app(context, env=None):
    # Prevent execute this function more than once
    if not os.environ.get("APP_SETTINGS"):
        # Load the basic configs
        env_vars = load_yaml_from_file(
            os.path.join(BASEDIR, "resources", "settings.yml")
        )

        for name, data in env_vars.items():
            set_env_var(
                context, name, data.get("value"), env, data.get("is_protected", False)
            )


@task(init_app)
def run_app(context):
    run(context, "python -m tvsort_sl.app", False)


def run(context, command, with_venv=True):
    if with_venv:
        command = f"{get_venv_action()} && {command}"

    print(f"Running: {command}")
    context.run(command)


def set_env_var(context, name, value, env, is_protected=True):
    # env codes: t - Travis-CI , None - Dev
    if isinstance(value, dict):
        value = json.dumps(value)

    if env == "t":
        command = f"travis env set {name} '{value}'"
        if not is_protected:
            command = f"{command} --public"

        if command:
            run(context, command, False)

    else:
        print(f"Set local var: {name}={value}")
        os.environ[name] = value


def load_yaml_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def is_unix():
    return os.name == "posix"


def get_venv_action():
    if is_unix():
        return f"source {BASEDIR}/venv/bin/activate"

    return f"{BASEDIR}\\venv\\Scripts\\activate"


@task(init_app)
def test(context, cov=False, file=None):
    # cov - if to use coverage, file - if to run specific file

    command = "pytest -s -p no:warnings"
    if cov:
        command = f"{command} --cov=slots_tracker_server --cov-report term-missing"

    if file:
        command = f"{command} {file}"

    run(context, command)


@task(init_app)
def mutmut(context):
    command = "mutmut run"
    run(context, command)


@task()
def bump_version(context):
    files_to_update = ['setup.py', '.bumpversion.cfg']

    github_client = Github(os.environ['GITHUB_ACCESS_TOKEN'])

    travis_pull_request = os.environ['TRAVIS_PULL_REQUEST']
    travis_pull_request_branch = os.environ['TRAVIS_PULL_REQUEST_BRANCH']
    travis_pull_request_slug = os.environ['TRAVIS_PULL_REQUEST_SLUG']

    try:
        travis_pull_request = int(travis_pull_request)
    except ValueError:
        travis_pull_request = strtobool(travis_pull_request)

    if not travis_pull_request:
        print('Not running on PR')
        return

    # Convert travis_pull_request from string to int
    travis_pull_request = int(travis_pull_request)

    repo = github_client.get_repo(travis_pull_request_slug)
    pull_request = repo.get_pull(travis_pull_request)
    for pull_request_file in pull_request.get_files():
        pr_filename = pull_request_file.filename
        if pr_filename in files_to_update:
            print('Version was already bumped, exiting')
            return

    print('Bumping version')
    run(context, 'bumpversion --verbose patch  --allow-dirty', with_venv=False)

    # Updating GitHub with new changes
    for filename in files_to_update:
        # Separate commits so that Travis will only build the last one
        time.sleep(10)
        file_object = repo.get_contents(path=filename, ref=travis_pull_request_branch)
        with open(filename, encoding="utf-8") as f:
            repo.update_file(file_object.path, f"Update version, file: {filename}", f.read(),
                             file_object.sha, branch=travis_pull_request_branch)
