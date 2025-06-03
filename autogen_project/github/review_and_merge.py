"""ReviewerAgent: PR diff를 GPT로 리뷰 후 자동 Approve+Merge / Request‑changes"""
import os
import openai
from ..utils.constants import OPENAI_MODEL
from ..utils.github import github_manager


def review_code(diff: str) -> tuple[str, bool]:
    """GPT로 코드를 리뷰합니다."""
    system = "당신은 숙련된 Django 시니어 개발자이자 코드 리뷰어입니다."
    review_prompt = f"""
    다음 Pull Request diff를 리뷰하세요.
    - 버그, 보안, 성능, 스타일 문제를 지적하고 개선안을 제안
    - 문제가 없다면 마지막 줄에 정확히 `LGTM` 만 적으세요.

    ```diff
    {diff}
    ```
    """
    
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": review_prompt}
            ],
            temperature=0
        )
        review = resp.choices[0].message.content.strip()
        is_approved = "LGTM" in review
        return review, is_approved
    except Exception as e:
        print(f"리뷰 생성 중 오류 발생: {str(e)}")
        return f"리뷰 생성 중 오류가 발생했습니다: {str(e)}", False


def main():
    """메인 실행 함수"""
    pr_number = int(os.getenv("PR_NUMBER", os.getenv("GITHUB_REF").split("/")[-2]))
    
    # PR diff 가져오기
    diff = github_manager.get_pr_diff(pr_number)
    
    # 코드 리뷰
    review, is_approved = review_code(diff)
    
    # 리뷰 생성 및 PR 처리
    github_manager.review_pr(pr_number, review, is_approved)


if __name__ == "__main__":
    main()