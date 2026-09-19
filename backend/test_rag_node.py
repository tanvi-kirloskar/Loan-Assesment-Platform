from app.services.loan_graph import policy_retrieval_node


def main():
    state = {
        "policy_query": (
            "How should payslip and tax return income be verified?"
        )
    }

    result = policy_retrieval_node(state)

    print("\n=== RAG NODE TEST ===")
    print("Retrieved chunks:", len(result["retrieved_policy"]))

    for chunk in result["retrieved_policy"]:
        print(f"\nSection: {chunk['section']}")
        print(f"Distance: {chunk['distance']:.4f}")


if __name__ == "__main__":
    main()