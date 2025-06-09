import sys
import os
import types
import importlib.util
from pathlib import Path
import pytest

# Ensure autogen_project package is importable for other modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.github'))

from autogen_project.github.sort_issue_priority import extract_priority_label


def load_safe_branch_name():
    """Load safe_branch_name from coder_agent without triggering GitHub API."""
    module_path = (
        Path(__file__).resolve().parents[1]
        / '.github'
        / 'autogen_project'
        / 'agents'
        / 'coder_agent.py'
    )
    spec = importlib.util.spec_from_file_location(
        'autogen_project.agents.coder_agent', module_path
    )
    module = importlib.util.module_from_spec(spec)
    module.__package__ = 'autogen_project.agents'
    # Stub modules that cause side effects
    sys.modules.setdefault('openai', types.ModuleType('openai'))
    sys.modules.setdefault(
        'autogen_project.utils.github',
        types.SimpleNamespace(github_manager=None),
    )
    sys.modules.setdefault(
        'autogen_project.utils.constants',
        types.SimpleNamespace(OPENAI_MODEL='test'),
    )
    sys.modules.setdefault('autogen_project', types.ModuleType('autogen_project'))
    sys.modules.setdefault('autogen_project.agents', types.ModuleType('autogen_project.agents'))
    spec.loader.exec_module(module)  # type: ignore
    return module.safe_branch_name


safe_branch_name = load_safe_branch_name()


@pytest.mark.parametrize(
    "issue_number,title,expected",
    [
        (5, "Fix login bug", "autogen/5-fix-login-bug"),
        (12, "Add user model!", "autogen/12-add-user-model"),
        (34, "로그인 기능 추가", "autogen/34---"),
        (
            9,
            "Long title with more than thirty characters to check",
            "autogen/9-long-title-with-more-than-thir",
        ),
    ],
)
def test_safe_branch_name(issue_number, title, expected):
    assert safe_branch_name(issue_number, title) == expected


@pytest.mark.parametrize(
    "line,expected",
    [
        ("#1 fix bug priority-high", "priority-high"),
        ("something priority-medium text", "priority-medium"),
        ("low priority-low end", "priority-low"),
        ("no label here", None),
    ],
)
def test_extract_priority_label(line, expected):
    assert extract_priority_label(line) == expected

