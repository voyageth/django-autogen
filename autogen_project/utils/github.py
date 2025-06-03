"""GitHub 관련 기능을 제공하는 유틸리티 모듈"""
import os
import base64
import requests
from typing import Optional, List, Dict, Any
from github import Github, Repository
from autogen_project.utils.constants import GITHUB_REVIEW_EVENTS


class GitHubManager:
    """GitHub 작업을 관리하는 클래스"""
    
    def __init__(self, repo: Repository):
        """초기화"""
        self.repo = repo
        self.repo_name = repo.name
        self.token = os.getenv("GITHUB_TOKEN")
        self.api_url = f"https://api.github.com/repos/{self.repo_name}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }
        self.github = Github(self.token)
        self.repo = self.github.get_repo(self.repo_name)

    def create_branch(self, branch: str, base: str = "main") -> None:
        """새로운 브랜치를 생성합니다."""
        sha = requests.get(
            f"{self.api_url}/git/ref/heads/{base}",
            headers=self.headers
        ).json()["object"]["sha"]
        
        resp = requests.post(
            f"{self.api_url}/git/refs",
            headers=self.headers,
            json={"ref": f"refs/heads/{branch}", "sha": sha}
        )
        resp.raise_for_status()

    def upsert_file(
        self,
        path: str,
        content: str,
        branch: str,
        message: str
    ) -> None:
        """파일을 생성하거나 업데이트합니다."""
        b64 = base64.b64encode(content.encode()).decode()
        url = f"{self.api_url}/contents/{path}"
        data = {
            "message": message,
            "content": b64,
            "branch": branch
        }
        
        resp = requests.put(url, headers=self.headers, json=data)
        if resp.status_code == 409:  # file exists → get sha then update
            sha = resp.json()["content"]["sha"]
            data["sha"] = sha
            resp = requests.put(url, headers=self.headers, json=data)
        resp.raise_for_status()

    def create_pr(
        self,
        title: str,
        branch: str,
        body: str
    ) -> str:
        """Pull Request를 생성합니다."""
        resp = requests.post(
            f"{self.api_url}/pulls",
            headers=self.headers,
            json={
                "title": title,
                "head": branch,
                "base": "main",
                "body": body
            }
        )
        resp.raise_for_status()
        return resp.json()["html_url"]

    def review_pr(
        self,
        pr_number: int,
        review: str,
        is_approved: bool
    ) -> None:
        """PR을 리뷰합니다."""
        pr = self.repo.get_pull(pr_number)
        event = (
            GITHUB_REVIEW_EVENTS["APPROVE"]
            if is_approved
            else GITHUB_REVIEW_EVENTS["REQUEST_CHANGES"]
        )
        
        pr.create_review(
            body=review,
            event=event
        )
        
        if is_approved:
            self.merge_pr(pr)

    def merge_pr(self, pr) -> None:
        """PR을 머지합니다."""
        if pr.mergeable:
            pr.merge(
                merge_method="squash",
                commit_title=f"Merge PR #{pr.number}: {pr.title}",
                commit_message=pr.body
            )

    def get_pr_diff(self, pr_number: int) -> str:
        """PR의 diff를 가져옵니다."""
        pr = self.repo.get_pull(pr_number)
        return pr.patch

    def get_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None
    ) -> List[Any]:
        """이슈 목록을 가져옵니다."""
        return list(self.repo.get_issues(state=state, labels=labels))

    def create_issue(
        self,
        title: str,
        body: str,
        labels: List[str]
    ) -> Any:
        """새로운 이슈를 생성합니다."""
        return self.repo.create_issue(
            title=title,
            body=body,
            labels=labels
        )

    def fetch_current_issue(self) -> Optional[Any]:
        """현재 작업 중인 이슈를 가져옵니다.
        
        Returns:
            Optional[Any]: 'now-working' 라벨이 있는 첫 번째 이슈 또는 None
        """
        issues = self.repo.get_issues(
            state="open",
            labels=[self.repo.get_label("now-working")]
        )
        return issues[0] if issues.totalCount else None

    def get_pr_changes(self, pr) -> str:
        """PR의 변경사항을 가져옵니다."""
        return "\n".join(f"{f.filename}: {f.patch}" for f in pr.get_files())

    def get_existing_issues(self):
        """기존 이슈 목록을 가져옵니다."""
        issues = []
        for issue in self.repo.get_issues(state="open"):
            issues.append({
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "labels": [label.name for label in issue.labels]
            })
        return issues


# 싱글톤 인스턴스 생성
github_manager = GitHubManager(Github(os.getenv("GITHUB_TOKEN")).get_repo(os.getenv("GITHUB_REPOSITORY")))