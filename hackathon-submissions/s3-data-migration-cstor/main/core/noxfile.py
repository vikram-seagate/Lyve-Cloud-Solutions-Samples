"""Nox Automation"""
import os
from pathlib import Path
from typing import Callable, List, Any
from functools import partial
import nox


nox.options.reuse_existing_virtualenvs = True

PROJ_DIR: Path = os.path.dirname(__file__)
REPORT_DIR: Path = os.path.join(PROJ_DIR, "reports")
#VENV_PYTHON: Path = os.path.join(VENV_DIR, "bin/python")


#def _wrap_run(session: nox.Session, *args: Any) -> Any:
#    """Wrap calls to venv python"""
#    run_args: tuple = (VENV_PYTHON, "-m", *args)
#    return session.run(*run_args, external=True)


def task_init(session: nox.Session, task_args: List[str]) -> None:
    """Setup python dev environment"""
    session.run(
        "poetry",
        "install",
        external=True,
    )


def task_lint(session: nox.Session, task_args: List[str]) -> None:
    """Static code analysis with linting and fixing"""
    is_ci: bool = bool(os.environ.get("CI", False))
    black_args: List[str] = ["black", "--check", "--diff"] if \
        is_ci else ["black"]
    session.run(*black_args, "src")

    isort_args: List[str] = ["isort", "--check", "--diff"] if \
        is_ci else ["isort"]

    session.run(*isort_args, "--profile", "black", "src")
    session.run("pylint", "src")


def task_test(session: nox.Session, task_args: List[str]) -> None:
    """Run tests"""
    junit_report: Path = os.path.join(REPORT_DIR, "report.xml")
    corbertura_report: Path = os.path.join(REPORT_DIR, "coverage.xml")

    if not os.path.exists(REPORT_DIR):
        os.mkdir(REPORT_DIR)

    session.run(
        "coverage",
        "run",
        "--source",
        "src",
        "-m",
        "pytest",
        "-s",
        f"--junitxml={junit_report}",
    )

    session.run(
        "coverage",
        "report",
        "-m",
    )

    session.run(
        "coverage",
        "xml",
        "-o",
        corbertura_report,
    )

    session.run(
        "coverage",
        "html",
        "-d",
        REPORT_DIR,
    )


def task_release(session: nox.Session, task_args: List[str]) -> None:
    """Build and deploy package to Gitlab PyPi"""
    session.run(
        "poetry",
        "build",
        external=True,
    )

    TWINE_PASSWORD: str = os.environ.get("CI_JOB_TOKEN")
    TWINE_USERNAME: str = "gitlab-ci-token"
    proj_url: str = os.environ.get("CI_API_V4_URL")
    proj_id: str = os.environ.get("CI_PROJECT_ID")
    repo_url: str = f"{proj_url}/projects/{proj_id}/packages/pypi"

    session.run(
        "twine",
        "upload",
        "--repository-url",
        repo_url,
        "dist/*",
        env={
            "TWINE_PASSWORD": TWINE_PASSWORD,
            "TWINE_USERNAME": TWINE_USERNAME,
        },
        external=True,
    )




VENV_TASKS = {
    "lint": task_lint,
    "init": task_init,
    "test": task_test,
    "release": task_release,
}


@nox.session()
def venv(session: nox.Session) -> None:
    """Run all automation in same venv"""

    tasks = list(VENV_TASKS.keys())
    if (not session.posargs) or (session.posargs[0] not in tasks):
        session.error(f"Choose a task from: [{tasks}]")

    task_name: str = session.posargs[0]
    task_args: List[str] = session.posargs[1:] \
        if len(session.posargs) > 1 else []

    VENV_TASKS[task_name](session, task_args)
