
from pathlib import Path
import re

from app.vectorstore import semantic_search

EVAL_FILE = Path("eval/search_results.md")


def read_questions():
    if not EVAL_FILE.exists():
        raise FileNotFoundError("eval/search_results.md not found")

    questions = []

    for line in EVAL_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue

        columns = [x.strip() for x in line.strip().strip("|").split("|")]

        if len(columns) < 3:
            continue

        if not columns[0].isdigit():
            continue

        questions.append({
            "number": columns[0],
            "question": columns[1],
            "expected": columns[2]
        })

    if not questions:
        raise ValueError("No evaluation questions found in the Markdown table.")

    return questions


def is_correct(expected, results):
    expected_articles = {
        value.strip().upper()
        for value in re.split(r"[,/]", expected)
        if value.strip()
    }

    if not expected_articles:
        return "Review"

    found_articles = {
        str(result.get("article_no", "")).strip().upper()
        for result in results
    }

    return (
        "Yes"
        if expected_articles.intersection(found_articles)
        else "No"
    )


def main():
    questions = read_questions()

    if len(questions) != 10:
        print(f"Warning: Found {len(questions)} questions, not 10.")

    report = [
        "# SamvidhanSathi Semantic Search Evaluation",
        "",
        "Top 3 results for each evaluation question.",
        ""
    ]

    for item in questions:
        question = item["question"]
        expected = item["expected"]

        print(f"\nTesting {item['number']}: {question}")

        results = semantic_search(question, limit=3)

        report.extend([
            f"## Question {item['number']}: {question}",
            f"- Expected article: {expected}",
            ""
        ])

        if not results:
            report.extend([
                "No search results returned.",
                "",
                "**Correct?:** No",
                "",
                "---",
                ""
            ])
            print("No results returned.")
            continue

        for rank, result in enumerate(results, start=1):
            article = result.get("article_no", "Unknown")
            title = result.get("title", "Unknown")
            source = result.get("source", "Unknown")
            page = result.get("page", "Unknown")
            distance = result.get("distance", "Unknown")

            report.append(
                f"{rank}. **Article {article} – {title}**  \n"
                f"   Source: {source} | Page: {page} | Distance: {distance}"
            )

            print(
                f"  {rank}. Article {article} | "
                f"Source: {source} | Distance: {distance}"
            )

        correctness = is_correct(expected, results)

        report.extend([
            "",
            f"**Correct?:** {correctness}",
            "",
            "---",
            ""
        ])

        print("Correct?:", correctness)

    EVAL_FILE.write_text("\n".join(report), encoding="utf-8")

    print("\nEvaluation completed!")
    print("Updated:", EVAL_FILE)


if __name__ == "__main__":
    main()
