"""Nox Automation"""
import os
from pathlib import Path
from typing import Callable, List, Any
from functools import partial
import nox


nox.options.reuse_existing_virtualenvs = True

PROJ_DIR: Path = os.path.dirname(__file__)
REPORT_DIR: Path = os.path.join(PROJ_DIR, "reports")


def task_init(session: nox.Session, task_args: List[str]) -> None:
    """Setup python dev environment"""
    session.install("poetry")
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




VENV_TASKS = {
    "lint": task_lint,
    "init": task_init,
    "test": task_test,
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
