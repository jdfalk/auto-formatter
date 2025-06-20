#!/usr/bin/env python3
"""
# file: test/test_action.py
Tests for the auto-formatter GitHub Action components.

This test suite validates the issue manager script and related functionality.
Run with: python -m pytest test/test_action.py -v
"""

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from issue_manager import (
        CodeQLAlertManager,
        CopilotTicketManager,
        DuplicateIssueManager,
        FormattingManager,
        GitHubAPI,
        IssueUpdateProcessor,
    )
except ImportError as e:
    pytest.skip(f"Could not import issue_manager: {e}", allow_module_level=True)


class TestGitHubAPI:
    """Tests for the GitHubAPI class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api = GitHubAPI("test_token", "test/repo")

    def test_init(self):
        """Test GitHubAPI initialization."""
        assert self.api.token == "test_token"
        assert self.api.repo == "test/repo"
        assert "Authorization" in self.api.headers

    def test_headers_with_pat_token(self):
        """Test header generation with PAT token."""
        api = GitHubAPI("github_pat_test123", "test/repo")
        assert api.headers["Authorization"] == "Bearer github_pat_test123"

    def test_headers_with_classic_token(self):
        """Test header generation with classic token."""
        api = GitHubAPI("ghp_test123", "test/repo")
        assert api.headers["Authorization"] == "token ghp_test123"

    @patch('requests.get')
    def test_test_access_success(self, mock_get):
        """Test successful API access test."""
        mock_get.return_value.status_code = 200
        assert self.api.test_access() is True

    @patch('requests.get')
    def test_test_access_failure(self, mock_get):
        """Test failed API access test."""
        mock_get.return_value.status_code = 404
        assert self.api.test_access() is False

    @patch('requests.post')
    def test_create_issue_success(self, mock_post):
        """Test successful issue creation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"number": 123, "title": "Test Issue"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.api.create_issue("Test Issue", "Test Body", ["bug"])

        assert result is not None
        assert result["number"] == 123
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_create_issue_failure(self, mock_post):
        """Test failed issue creation."""
        mock_post.side_effect = Exception("API Error")

        result = self.api.create_issue("Test Issue", "Test Body")
        assert result is None

    @patch('requests.get')
    def test_search_issues(self, mock_get):
        """Test issue search functionality."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [{"number": 1, "title": "Test Issue"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        results = self.api.search_issues("test query")

        assert len(results) == 1
        assert results[0]["number"] == 1


class TestIssueUpdateProcessor:
    """Tests for the IssueUpdateProcessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api = MagicMock()
        self.processor = IssueUpdateProcessor(self.mock_api)

    def test_process_updates_no_file(self):
        """Test processing when update file doesn't exist."""
        result = self.processor.process_updates("nonexistent.json")
        assert result is False

    def test_process_updates_empty_file(self):
        """Test processing with empty update file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_file = f.name

        try:
            result = self.processor.process_updates(temp_file)
            assert result is False
        finally:
            os.unlink(temp_file)

    def test_process_create_update(self):
        """Test processing create action."""
        updates = [
            {
                "action": "create",
                "title": "Test Issue",
                "body": "Test Body",
                "labels": ["bug"]
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(updates, f)
            temp_file = f.name

        try:
            # Mock successful search (no existing issues)
            self.mock_api.search_issues.return_value = []
            self.mock_api.create_issue.return_value = {"number": 123}

            result = self.processor.process_updates(temp_file)
            assert result is True
            self.mock_api.create_issue.assert_called_once()
        finally:
            os.unlink(temp_file)

    def test_create_issue_already_exists(self):
        """Test creating issue when it already exists."""
        update = {
            "action": "create",
            "title": "Existing Issue",
            "body": "Test Body"
        }

        # Mock existing issue found
        self.mock_api.search_issues.return_value = [{"number": 456}]

        result = self.processor._create_issue(update)
        assert result is False
        self.mock_api.create_issue.assert_not_called()


class TestFormattingManager:
    """Tests for the FormattingManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api = MagicMock()
        self.manager = FormattingManager(self.mock_api)

    def test_check_python_formatting_no_files(self):
        """Test Python formatting check with no files."""
        with patch('glob.glob') as mock_glob:
            mock_glob.return_value = []
            result = self.manager._check_python_formatting()
            assert result["status"] == "no_files"
            assert result["files"] == []

    def test_check_go_formatting_no_files(self):
        """Test Go formatting check with no files."""
        with patch('glob.glob') as mock_glob:
            mock_glob.return_value = []
            result = self.manager._check_go_formatting()
            assert result["status"] == "no_files"

    @patch('glob.glob')
    def test_check_python_formatting_with_files(self, mock_glob):
        """Test Python formatting check with files present."""
        mock_glob.return_value = ["test1.py", "test2.py"]

        with patch('subprocess.run') as mock_run:
            # Mock ruff returning no issues
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "[]"

            result = self.manager._check_python_formatting()
            assert result["status"] == "checked"
            assert len(result["files"]) == 2

    def test_build_formatting_summary(self):
        """Test building formatting summary."""
        results = {
            "python_files": {
                "status": "checked",
                "total_files": 5,
                "issues": [{"file": "test.py", "type": "format"}]
            },
            "go_files": {
                "status": "no_files",
                "total_files": 0,
                "issues": []
            }
        }

        summary = self.manager._build_formatting_summary(results)
        assert "Python Files" in summary
        assert "5" in summary  # file count
        assert "1" in summary  # issue count
        assert "test.py" in summary


class TestCopilotTicketManager:
    """Tests for the CopilotTicketManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api = MagicMock()
        self.manager = CopilotTicketManager(self.mock_api)

    def test_handle_review_comment_created(self):
        """Test handling of created review comment."""
        event_data = {
            "action": "created",
            "comment": {
                "id": 123,
                "body": "Test comment",
                "user": {"login": "github-copilot[bot]"},
                "path": "test.py",
                "line": 10,
                "html_url": "https://github.com/test/test/pull/1#issuecomment-123"
            }
        }

        self.mock_api.search_issues.return_value = []  # No existing issues
        self.mock_api.create_issue.return_value = {"number": 456}

        self.manager._handle_review_comment("created", event_data)
        self.mock_api.create_issue.assert_called_once()

    def test_handle_pr_closed_merged(self):
        """Test handling of merged PR closure."""
        event_data = {
            "pull_request": {
                "number": 123,
                "merged": True
            }
        }

        self.mock_api.search_issues.return_value = [
            {"number": 456},
            {"number": 789}
        ]
        self.mock_api.close_issue.return_value = True

        self.manager._handle_pr_closed(event_data)
        assert self.mock_api.close_issue.call_count == 2

    def test_build_ticket_body(self):
        """Test building ticket body."""
        comment = {
            "body": "This needs improvement",
            "url": "https://github.com/test/test/pull/1#issuecomment-123"
        }
        lines = [
            {
                "id": 123,
                "path": "test.py",
                "line": 10,
                "url": "https://github.com/test/test/pull/1#discussion_r123"
            }
        ]

        body = self.manager._build_ticket_body(comment, lines)
        assert "This needs improvement" in body
        assert "test.py#L10" in body
        assert "copilot-data:" in body


class TestDuplicateIssueManager:
    """Tests for the DuplicateIssueManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api = MagicMock()
        self.manager = DuplicateIssueManager(self.mock_api)

    def test_group_by_title(self):
        """Test grouping issues by title."""
        issues = [
            {"number": 1, "title": "Bug fix needed"},
            {"number": 2, "title": "Bug fix needed"},
            {"number": 3, "title": "Different issue"},
            {"number": 4, "title": "Bug fix needed"}
        ]

        groups = self.manager._group_by_title(issues)
        assert len(groups["Bug fix needed"]) == 3
        assert len(groups["Different issue"]) == 1

    def test_close_duplicate_group(self):
        """Test closing duplicate issues."""
        issues = [
            {"number": 3, "title": "Test"},
            {"number": 1, "title": "Test"},  # Should be kept (lowest number)
            {"number": 2, "title": "Test"}
        ]

        self.mock_api.add_comment.return_value = True
        self.mock_api.close_issue.return_value = True

        closed_count = self.manager._close_duplicate_group(issues)
        assert closed_count == 2  # Two duplicates closed
        assert self.mock_api.close_issue.call_count == 2

    def test_close_duplicates_dry_run(self):
        """Test dry run mode."""
        self.mock_api.get_all_issues.return_value = [
            {"number": 1, "title": "Duplicate"},
            {"number": 2, "title": "Duplicate"}
        ]

        closed_count = self.manager.close_duplicates(dry_run=True)
        assert closed_count == 0  # Nothing actually closed
        self.mock_api.close_issue.assert_not_called()


class TestCodeQLAlertManager:
    """Tests for the CodeQLAlertManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api = MagicMock()
        self.manager = CodeQLAlertManager(self.mock_api)

    def test_should_create_ticket_no_existing(self):
        """Test ticket creation when no existing ticket."""
        alert = {
            "number": 123,
            "rule": {"id": "test-rule"}
        }

        self.mock_api.search_issues.return_value = []
        result = self.manager._should_create_ticket(alert)
        assert result is True

    def test_should_create_ticket_existing(self):
        """Test ticket creation when ticket already exists."""
        alert = {
            "number": 123,
            "rule": {"id": "test-rule"}
        }

        self.mock_api.search_issues.return_value = [{"number": 456}]
        result = self.manager._should_create_ticket(alert)
        assert result is False

    def test_build_alert_body(self):
        """Test building alert issue body."""
        alert = {
            "number": 123,
            "rule": {
                "id": "security-rule",
                "description": "Test security issue",
                "severity": "high",
                "security_severity_level": "critical"
            },
            "most_recent_instance": {
                "location": {
                    "path": "test.py",
                    "start_line": 10,
                    "end_line": 15
                },
                "message": {
                    "text": "Security vulnerability detected"
                }
            },
            "html_url": "https://github.com/test/test/security/code-scanning/123",
            "state": "open",
            "created_at": "2023-01-01T00:00:00Z"
        }

        body = self.manager._build_alert_body(alert)
        assert "CodeQL Security Alert #123" in body
        assert "security-rule" in body
        assert "test.py" in body
        assert "Lines: 10-15" in body
        assert "Security vulnerability detected" in body


@pytest.fixture
def temp_env():
    """Fixture for temporary environment variables."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


class TestMainFunction:
    """Tests for the main function and CLI interface."""

    @patch('sys.argv', ['issue_manager.py', 'format-check'])
    @patch.dict(os.environ, {'GH_TOKEN': 'test_token', 'REPO': 'test/repo'})
    def test_main_format_check_command(self):
        """Test main function with format-check command."""
        with patch('issue_manager.GitHubAPI') as mock_api_class:
            mock_api = MagicMock()
            mock_api.test_access.return_value = True
            mock_api_class.return_value = mock_api

            with patch('issue_manager.FormattingManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_manager.check_formatting_issues.return_value = {}
                mock_manager_class.return_value = mock_manager

                # Import and call main - should not raise exception
                from issue_manager import main
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0  # Successful exit

    def test_missing_environment_variables(self):
        """Test behavior when required environment variables are missing."""
        with patch.dict(os.environ, {}, clear=True), patch('sys.argv', ['issue_manager.py', 'format-check']):
            from issue_manager import main
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
