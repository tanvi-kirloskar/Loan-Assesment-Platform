from app.services.policy_retriever import (
    build_policy_retriever,
    retrieve_policy,
)


def main():
    index, chunks, model = build_policy_retriever()

    queries = [
        "How should tax return income be verified?",
        "What happens when salary in the bank statement differs from the payslip?",
        "What should happen when applicant names do not match?",
        "Who makes the final financial loan decision?",
        "When should a case go for human review?",
    ]

    for query in queries:
        print(f"\nQUERY: {query}")

        results = retrieve_policy(
            query,
            index,
            chunks,
            model,
            top_k=2,
        )

        for i, result in enumerate(results, start=1):
            print(
                f"  {i}. {result['section']}"
                f" | distance: {result['distance']:.4f}"
            )


if __name__ == "__main__":
    main()