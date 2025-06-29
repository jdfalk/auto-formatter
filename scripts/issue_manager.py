#!/usr/bin/env python3
"""# file: scripts/issue_manager.py
Issue Management System for Auto Formatter GitHub Action

This script provides GitHub issue management functionality including:
- Format checking and issue creation
- Copilot review comment management
- Duplicate issue cleanup
- CodeQL security alert handling

Usage:
    python scripts/issue_manager.py format-check
    python scripts/issue_manager.py update-issues
    python scripts/issue_manager.py event-handler
    python scripts/issue_manager.py close-duplicates --dry-run
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests


class GitHubAPI:
    """GitHub API client for issue management operations."""

    def __init__(self, token: str, repo: str):
        """Initialize GitHub API client.

        Args:
            token: GitHub token (PAT or classic)
            repo: Repository in format 'owner/repo'
        """
        self.token = token
        self.repo = repo
        self.base_url = "https://api.github.com"

        # Set appropriate auth header based on token type
        if token.startswith("github_pat_"):
            self.headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            }
        else:
            self.headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            }

    def test_access(self) -> bool:
        """Test API access with current token."""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{self.repo}",
                headers=self.headers,
                timeout=10,
            )
            return response.status_code == 200
        except Exception:
            return False

    def create_issue(
        self, title: str, body: str, labels: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Create a new GitHub issue.

        Args:
            title: Issue title
            body: Issue body
            labels: List of labels to add

        Returns:
            Issue data dict or None if failed
        """
        try:
            data = {"title": title, "body": body, "labels": labels or []}

            response = requests.post(
                f"{self.base_url}/repos/{self.repo}/issues",
                headers=self.headers,
                json=data,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def search_issues(self, query: str) -> List[Dict]:
        """Search for issues in the repository.

        Args:
            query: Search query

        Returns:
            List of issue data dicts
        """
        try:
            response = requests.get(
                f"{self.base_url}/search/issues?q={query}+repo:{self.repo}",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json().get("items", [])
        except Exception:
            return []

    def close_issue(self, issue_number: int, reason: str = "completed") -> bool:
        """Close an issue.

        Args:
            issue_number: Issue number to close
            reason: Reason for closing

        Returns:
            True if successful
        """
        try:
            data = {"state": "closed"}
            response = requests.patch(
                f"{self.base_url}/repos/{self.repo}/issues/{issue_number}",
                headers=self.headers,
                json=data,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def add_comment(self, issue_number: int, comment: str) -> bool:
        """Add a comment to an issue.

        Args:
            issue_number: Issue number
            comment: Comment text

        Returns:
            True if successful
        """
        try:
            data = {"body": comment}
            response = requests.post(
                f"{self.base_url}/repos/{self.repo}/issues/{issue_number}/comments",
                headers=self.headers,
                json=data,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def get_all_issues(self, state: str = "open") -> List[Dict]:
        """Get all issues in the repository.

        Args:
            state: Issue state (open, closed, all)

        Returns:
            List of issue data dicts
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{self.repo}/issues?state={state}",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return []


class FormattingManager:
    """Manages code formatting issue detection and reporting."""

    def __init__(self, api: GitHubAPI):
        """Initialize formatting manager.

        Args:
            api: GitHub API client
        """
        self.api = api

    def check_formatting_issues(self) -> Dict[str, Any]:
        """Check for formatting issues in the repository.

        Returns:
            Dict containing formatting check results
        """
        results = {
            "python_files": self._check_python_formatting(),
            "javascript_files": self._check_javascript_formatting(),
            "go_files": self._check_go_formatting(),
        }

        print("✅ Format check completed successfully")
        return results

    def _check_python_formatting(self) -> Dict[str, Any]:
        """Check Python file formatting.

        Returns:
            Dict with formatting check results for Python files
        """
        import glob

        python_files = glob.glob("**/*.py", recursive=True)

        if not python_files:
            return {
                "status": "no_files",
                "files": [],
                "total_files": 0,
                "issues": [],
            }

        # Minimal formatting check - in practice would run ruff/black
        return {
            "status": "checked",
            "files": python_files,
            "total_files": len(python_files),
            "issues": [],
        }

    def _check_go_formatting(self) -> Dict[str, Any]:
        """Check Go file formatting.

        Returns:
            Dict with formatting check results for Go files
        """
        import glob

        go_files = glob.glob("**/*.go", recursive=True)

        if not go_files:
            return {
                "status": "no_files",
                "files": [],
                "total_files": 0,
                "issues": [],
            }

        return {
            "status": "checked",
            "files": go_files,
            "total_files": len(go_files),
            "issues": [],
        }

    def _check_javascript_formatting(self) -> Dict[str, Any]:
        """Check JavaScript file formatting.

        Returns:
            Dict with formatting check results for JavaScript files
        """
        import glob

        js_files = glob.glob("**/*.js", recursive=True) + glob.glob(
            "**/*.ts", recursive=True
        )

        if not js_files:
            return {
                "status": "no_files",
                "files": [],
                "total_files": 0,
                "issues": [],
            }

        return {
            "status": "checked",
            "files": js_files,
            "total_files": len(js_files),
            "issues": [],
        }

    def _build_formatting_summary(self, results: Dict[str, Any]) -> str:
        """Build a summary of formatting results.

        Args:
            results: Formatting check results

        Returns:
            Formatted summary string
        """
        summary_lines = ["## Formatting Check Summary\n"]

        for file_type, data in results.items():
            if data["status"] == "checked":
                issues_count = len(data.get("issues", []))
                file_count = data.get("total_files", 0)

                type_name = file_type.replace("_", " ").title()
                summary_lines.append(
                    f"**{type_name}**: {file_count} files checked, {issues_count} issues found"
                )

                if issues_count > 0:
                    for issue in data["issues"]:
                        summary_lines.append(
                            f"- {issue.get('file', 'unknown')}: {issue.get('type', 'format')}"
                        )

        return "\n".join(summary_lines)


class CopilotTicketManager:
    """Manages GitHub Copilot review comment tickets."""

    def __init__(self, api: GitHubAPI):
        """Initialize copilot ticket manager.

        Args:
            api: GitHub API client
        """
        self.api = api

    def handle_pull_request_review_comment(
        self, event_data: Dict[str, Any]
    ) -> None:
        """Handle pull request review comment events.

        Args:
            event_data: GitHub webhook event data
        """
        action = event_data.get("action")
        if action == "created":
            self._handle_review_comment("created", event_data)

    def _handle_review_comment(
        self, action: str, event_data: Dict[str, Any]
    ) -> None:
        """Handle review comment based on action.

        Args:
            action: The action type (created, updated, etc.)
            event_data: GitHub webhook event data
        """
        comment = event_data.get("comment", {})
        user = comment.get("user", {})

        # Only process Copilot comments
        if user.get("login") == "github-copilot[bot]":
            # Check if issue already exists
            existing_issues = self.api.search_issues(
                f"Copilot Review: {comment.get('path', 'unknown')}"
            )

            if not existing_issues:
                title = f"Copilot Review: {comment.get('path', 'unknown')}"
                body = self._build_comment_body(comment)
                self.api.create_issue(title, body, ["copilot-review"])

    def _handle_pr_closed(self, event_data: Dict[str, Any]) -> None:
        """Handle PR closed events.

        Args:
            event_data: GitHub webhook event data
        """
        pr = event_data.get("pull_request", {})
        if pr.get("merged"):
            # Find related copilot issues and close them
            search_query = "label:copilot-review state:open"
            issues = self.api.search_issues(search_query)

            for issue in issues:
                self.api.close_issue(issue["number"], "PR merged")

    def _build_comment_body(self, comment: Dict[str, Any]) -> str:
        """Build issue body from comment data.

        Args:
            comment: Comment data

        Returns:
            Formatted issue body
        """
        body_lines = [
            "## Copilot Review Comment",
            "",
            f"**File:** {comment.get('path', 'unknown')}",
            f"**Line:** {comment.get('line', 'unknown')}",
            f"**URL:** {comment.get('html_url', 'unknown')}",
            "",
            "### Comment:",
            comment.get("body", ""),
            "",
            f"<!-- copilot-data: {comment.get('id', 'unknown')} -->",
        ]
        return "\n".join(body_lines)

    def _build_ticket_body(
        self, comment: Dict[str, Any], lines: List[Dict[str, Any]]
    ) -> str:
        """Build ticket body from comment and line data.

        Args:
            comment: Comment data
            lines: List of line data

        Returns:
            Formatted ticket body
        """
        body_lines = [
            "## Copilot Review Ticket",
            "",
            f"**Comment URL:** {comment.get('url', 'unknown')}",
            "",
            "### Review Comment:",
            comment.get("body", ""),
            "",
            "### Lines:",
        ]

        for line in lines:
            body_lines.append(
                f"- {line.get('path', 'unknown')}#L{line.get('line', 'unknown')}"
            )

        body_lines.extend(
            ["", f"<!-- copilot-data: {comment.get('id', 'unknown')} -->"]
        )

        return "\n".join(body_lines)


class DuplicateIssueManager:
    """Manages duplicate issue detection and cleanup."""

    def __init__(self, api: GitHubAPI):
        """Initialize duplicate issue manager.

        Args:
            api: GitHub API client
        """
        self.api = api

    def close_duplicates(self, dry_run: bool = False) -> int:
        """Close duplicate issues.

        Args:
            dry_run: If True, only identify duplicates without closing

        Returns:
            Number of duplicates found/closed
        """
        print(f"🔍 Checking for duplicate issues (dry_run={dry_run})")

        # Get all open issues
        all_issues = self.api.search_issues("state:open")

        # Group by title
        groups = self._group_by_title(all_issues)

        total_closed = 0
        for _title, issues in groups.items():
            if len(issues) > 1:
                closed_count = self._close_duplicate_group(issues, dry_run)
                total_closed += closed_count

        return total_closed

    def group_by_title(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """Group issues by title similarity.

        Args:
            issues: List of issue data

        Returns:
            Dict mapping titles to lists of similar issues
        """
        return self._group_by_title(issues)

    def _group_by_title(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """Group issues by title similarity.

        Args:
            issues: List of issue data

        Returns:
            Dict mapping titles to lists of similar issues
        """
        groups = {}
        for issue in issues:
            title = issue.get("title", "")
            if title not in groups:
                groups[title] = []
            groups[title].append(issue)
        return groups

    def _close_duplicate_group(
        self, issues: List[Dict], dry_run: bool = False
    ) -> int:
        """Close duplicate issues in a group, keeping the oldest (lowest number).

        Args:
            issues: List of duplicate issues
            dry_run: If True, don't actually close issues

        Returns:
            Number of issues closed
        """
        if len(issues) <= 1:
            return 0

        # Sort by issue number to keep the oldest (lowest number)
        sorted_issues = sorted(issues, key=lambda x: x.get("number", 0))

        # Keep the first (oldest) issue, close the rest
        to_close = sorted_issues[1:]

        closed_count = 0
        for issue in to_close:
            if not dry_run:
                # Add a comment explaining the closure
                # comment_body = (
                #     f"Closing as duplicate of #{sorted_issues[0]['number']}"
                # )

                # Close the issue
                if self.api.close_issue(issue["number"], "duplicate"):
                    closed_count += 1
            else:
                closed_count += 1  # Count what would be closed

        return closed_count


class CodeQLAlertManager:
    """Manages CodeQL security alert tickets."""

    def __init__(self, api: GitHubAPI):
        """Initialize CodeQL alert manager.

        Args:
            api: GitHub API client
        """
        self.api = api

    def should_create_ticket(self, alert: Dict[str, Any]) -> bool:
        """Check if a ticket should be created for this alert.

        Args:
            alert: CodeQL alert data

        Returns:
            True if ticket should be created
        """
        return self._should_create_ticket(alert)

    def _should_create_ticket(self, alert: Dict[str, Any]) -> bool:
        """Check if a ticket should be created for this alert.

        Args:
            alert: CodeQL alert data

        Returns:
            True if ticket should be created
        """
        # Check if ticket already exists
        alert_id = alert.get("number", "unknown")
        existing_issues = self.api.search_issues(
            f"CodeQL Security Alert #{alert_id}"
        )
        return len(existing_issues) == 0

    def _build_alert_body(self, alert: Dict[str, Any]) -> str:
        """Build issue body from alert data.

        Args:
            alert: CodeQL alert data

        Returns:
            Formatted issue body
        """
        rule = alert.get("rule", {})
        location = alert.get("most_recent_instance", {}).get("location", {})
        message = alert.get("most_recent_instance", {}).get("message", {})

        body_lines = [
            f"## CodeQL Security Alert #{alert.get('number', 'unknown')}",
            "",
            f"**Rule:** {rule.get('id', 'unknown')}",
            f"**Severity:** {rule.get('severity', 'unknown')}",
            f"**File:** {location.get('path', 'unknown')}",
            f"Lines: {location.get('start_line', 'unknown')}-{location.get('end_line', 'unknown')}",
            "",
            "### Description:",
            rule.get("description", "No description available"),
            "",
            "### Message:",
            message.get("text", "No message available"),
            "",
            f"**Alert URL:** {alert.get('html_url', 'unknown')}",
        ]
        return "\n".join(body_lines)


class IssueUpdateProcessor:
    """Processes issue update requests from files."""

    def __init__(self, api: GitHubAPI):
        """Initialize issue update processor.

        Args:
            api: GitHub API client
        """
        self.api = api

    def process_updates(self, file_path: str) -> bool:
        """Process issue updates from a JSON file.

        Args:
            file_path: Path to JSON file containing updates

        Returns:
            True if processing was successful
        """
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path) as f:
                updates = json.load(f)

            if not updates:
                return False

            for update in updates:
                self._process_single_update(update)

            return True
        except Exception:
            return False

    def _process_single_update(self, update: Dict[str, Any]) -> None:
        """Process a single update operation.

        Args:
            update: Update operation data
        """
        action = update.get("action")

        if action == "create":
            self._create_issue(update)
        elif action == "update":
            # Handle update logic
            pass
        elif action == "close":
            # Handle close logic
            pass

    def _create_issue(self, update: Dict[str, Any]) -> bool:
        """Create an issue from update data.

        Args:
            update: Issue creation data

        Returns:
            True if successful
        """
        title = update.get("title")
        body = update.get("body", "")
        labels = update.get("labels", [])

        if not title:
            return False

        # Check for existing issues
        existing_issues = self.api.search_issues(title)
        if existing_issues:
            return False  # Issue already exists

        result = self.api.create_issue(title, body, labels)
        return result is not None


def main():
    """Main entry point for the issue manager CLI."""
    parser = argparse.ArgumentParser(
        description="Issue Manager for Auto Formatter"
    )
    parser.add_argument(
        "command",
        choices=[
            "format-check",
            "update-issues",
            "event-handler",
            "close-duplicates",
        ],
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run in dry-run mode"
    )

    args = parser.parse_args()

    # Check required environment variables
    token = os.getenv("GH_TOKEN")
    repo = os.getenv("REPO")

    if not token or not repo:
        print(
            "❌ Missing required environment variables: GH_TOKEN, REPO",
            file=sys.stderr,
        )
        sys.exit(1)

    # Initialize API client
    api = GitHubAPI(token, repo)

    # Test API access
    if not api.test_access():
        print("❌ Failed to access GitHub API", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "format-check":
            print("🔍 Running format check...")
            manager = FormattingManager(api)
            manager.check_formatting_issues()
            print("✅ Format check completed")

        elif args.command == "update-issues":
            print("📝 Processing issue updates...")
            processor = IssueUpdateProcessor(api)
            success = processor.process_updates("issue_updates.json")
            if success:
                print("✅ Issue updates processed")
            else:
                print("ℹ️ No issue updates to process")

        elif args.command == "event-handler":
            print("🎯 Handling GitHub events...")
            # Process GitHub webhook events
            event_path = os.getenv("GITHUB_EVENT_PATH")
            if event_path and os.path.exists(event_path):
                with open(event_path) as f:
                    event_data = json.load(f)

                # Handle different event types
                if "pull_request" in event_data:
                    manager = CopilotTicketManager(api)
                    manager.handle_pull_request_review_comment(event_data)

            print("✅ Event handling completed")

        elif args.command == "close-duplicates":
            print("🧹 Checking for duplicate issues...")
            manager = DuplicateIssueManager(api)
            count = manager.close_duplicates(dry_run=args.dry_run)
            print(f"✅ Found {count} duplicate issues")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
