"""Goal → Issue generator: project_goals.md의 목표를 GitHub 이슈로 변환"""
import os
import json
import re
from openai import OpenAI
from github import Github
from autogen_project.utils.constants import OPENAI_MODEL


def main():
    """메인 실행 함수"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

    # 1. project_goals.md 읽기
    with open("project_goals.md", "r") as f:
        goals = f.read()

    # 2. GPT로 이슈 생성
    prompt = f"""
    다음 프로젝트 목표를 GitHub 이슈로 변환하세요.
    각 이슈는 다음 형식의 JSON 배열로 출력하세요:
    [
      {{"title": "이슈 제목", "body": "이슈 설명", "labels": ["label1", "label2"]}},
      ...
    ]

    프로젝트 목표:
    {goals}
    """

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # 3. 이슈 생성
    issues = json.loads(response.choices[0].message.content)
    for issue in issues:
        repo.create_issue(
            title=issue["title"],
            body=issue["body"],
            labels=issue["labels"]
        )


if __name__ == "__main__":
    main()