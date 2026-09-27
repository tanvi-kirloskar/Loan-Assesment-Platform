import unittest

from app.workflows.loan_assessment import route_from_findings


class WorkflowRoutingTests(unittest.TestCase):
    def test_request_information_has_priority(self):
        findings = [
            {
                "finding_type": "SOME_FINDING",
                "severity": "WARNING",
                "message": "Information is required.",
                "action": "REQUEST_INFORMATION",
            },
            {
                "finding_type": "NAME_MISMATCH",
                "severity": "WARNING",
                "message": "Names differ.",
                "action": "REVIEW",
            },
        ]
        self.assertEqual(route_from_findings(findings), "REQUEST_INFORMATION")

    def test_review_finding_routes_to_human_review(self):
        findings = [
            {
                "finding_type": "GROSS_INCOME_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": "Income missing.",
                "action": "REVIEW",
            }
        ]
        self.assertEqual(route_from_findings(findings), "HUMAN_REVIEW")

    def test_clean_findings_continue(self):
        findings = [
            {
                "finding_type": "INCOME_MATCH",
                "severity": "INFO",
                "message": "Income matches.",
                "action": "CONTINUE",
            },
            {
                "finding_type": "NAME_MATCH",
                "severity": "INFO",
                "message": "Name matches.",
                "action": "CONTINUE",
            },
        ]
        self.assertEqual(route_from_findings(findings), "CONTINUE")


if __name__ == "__main__":
    unittest.main()
