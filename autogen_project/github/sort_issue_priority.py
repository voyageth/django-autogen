"""Issue prioritiser: 이슈의 우선순위를 자동으로 설정"""
import os
import openai
from github import Github
from ..utils.constants import OPENAI_MODEL


def main():
    """메인 실행 함수"""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

    # 1. 모든 열린 이슈 가져오기
    issues = list(repo.get_issues(state="open"))

    # 2. GPT로 우선순위 설정
    prompt = f"""
    다음 이슈들의 우선순위를 설정하세요.
    각 이슈에 대해 다음 중 하나의 라벨을 부여하세요:
    - priority-high
    - priority-medium
    - priority-low

    이슈 목록:
    {chr(10).join(f"#{i.number}: {i.title}" for i in issues)}
    """

    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # 3. 라벨 적용
    priorities = resp.choices[0].message.content.strip().split("\n")
    for i, p in zip(issues, priorities):
        label = p.split(": ")[1].strip()
        i.add_to_labels(label)


if __name__ == "__main__":
    main()