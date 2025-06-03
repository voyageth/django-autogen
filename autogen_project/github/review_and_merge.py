"""PR 리뷰어: PR을 자동으로 리뷰하고 머지"""
import os
from openai import OpenAI
from github import Github
from autogen_project.utils.constants import OPENAI_MODEL
from autogen_project.utils.github import GitHubManager


def main():
    """메인 실행 함수"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    github_manager = GitHubManager(repo)

    # 1. 모든 열린 PR 가져오기
    prs = list(repo.get_pulls(state="open"))

    for pr in prs:
        # 2. GPT로 리뷰
        prompt = f"""
        다음 PR을 리뷰하세요:
        제목: {pr.title}
        설명: {pr.body}
        변경사항: {github_manager.get_pr_changes(pr)}
        """

        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        # 3. 리뷰 작성
        review = resp.choices[0].message.content.strip()
        pr.create_review(body=review, event="APPROVE")

        # 4. 머지
        pr.merge()


if __name__ == "__main__":
    main()