"""Issue prioritiser: 이슈의 우선순위를 자동으로 설정"""
import os
import re
from openai import OpenAI
from github import Github
from autogen_project.utils.constants import OPENAI_MODEL


def extract_priority_label(line):
    match = re.search(r'(priority-(high|medium|low))', line)
    if match:
        return match.group(1)
    return None


def main():
    """메인 실행 함수"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # 3. 라벨 적용
    priorities = resp.choices[0].message.content.strip().split("\n")
    for i, p in zip(issues, priorities):
        label = extract_priority_label(p)
        if label:
            # 기존 priority 라벨 제거
            for l in i.labels:
                if l.name in ["priority-high", "priority-medium", "priority-low"]:
                    i.remove_from_labels(l)
            i.add_to_labels(label)


if __name__ == "__main__":
    main()