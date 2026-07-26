import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "rank_paths.py"
WECHAT_FIXTURE = SKILL_ROOT / "tests" / "fixtures" / "wechat-paths.json"


def run_ranker(payload_path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(payload_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def run_payload(payload):
    with tempfile.TemporaryDirectory() as directory:
        payload_path = Path(directory) / "ledger.json"
        payload_path.write_text(json.dumps(payload), encoding="utf-8")
        return run_ranker(payload_path)


def complete_candidate(candidate_id, **overrides):
    candidate = {
        "id": candidate_id,
        "approach": candidate_id,
        "hard_constraints": {"complete": True, "safe": True},
        "coverage": 1.0,
        "success_probability": 0.9,
        "minutes": {
            "research": 1,
            "setup": 1,
            "execute": 8,
            "verify": 2,
            "cleanup": 1,
        },
        "failure_cost_minutes": 10,
        "risk": 1,
        "invasiveness": 1,
        "reversible": True,
        "evidence_quality": 2,
        "evidence": ["runtime observation"],
    }
    candidate.update(overrides)
    return candidate


class RankPathsTests(unittest.TestCase):
    def test_wechat_fixture_prefers_direct_session_route(self):
        result = run_ranker(WECHAT_FIXTURE)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["recommended"], "direct-session-technique")
        self.assertEqual(report["pareto_front"], ["direct-session-technique"])
        self.assertIn("exporter-plus-proxy-stack", report["dominated"])

    def test_failed_hard_constraint_is_eliminated_even_when_fastest(self):
        fast_incomplete = complete_candidate(
            "fast-incomplete",
            hard_constraints={"complete": False, "safe": True},
            minutes={
                "research": 0,
                "setup": 0,
                "execute": 1,
                "verify": 1,
                "cleanup": 0,
            },
            failure_cost_minutes=0,
            risk=0,
            invasiveness=0,
        )
        payload = {
            "objective": "Get the complete result",
            "acceptance_checks": ["complete"],
            "candidates": [fast_incomplete, complete_candidate("slower-complete")],
        }

        result = run_payload(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["recommended"], "slower-complete")
        self.assertEqual(
            report["eliminated"],
            [{"id": "fast-incomplete", "failed_constraints": ["complete"]}],
        )

    def test_output_is_deterministic_for_equal_candidates(self):
        payload = {
            "objective": "Choose deterministically",
            "acceptance_checks": ["complete"],
            "candidates": [complete_candidate("route-b"), complete_candidate("route-a")],
        }

        first = run_payload(payload)
        second = run_payload(payload)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout)["recommended"], "route-a")

    def test_partial_coverage_is_eliminated_even_when_marked_feasible(self):
        fast_partial = complete_candidate(
            "fast-partial",
            coverage=0.4,
            minutes={
                "research": 0,
                "setup": 0,
                "execute": 1,
                "verify": 1,
                "cleanup": 0,
            },
            failure_cost_minutes=0,
            risk=0,
            invasiveness=0,
        )
        payload = {
            "objective": "Get every requested item",
            "acceptance_checks": ["full coverage"],
            "candidates": [fast_partial, complete_candidate("complete-route")],
        }

        result = run_payload(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["recommended"], "complete-route")
        self.assertEqual(
            report["eliminated"],
            [{"id": "fast-partial", "failed_constraints": ["minimum_coverage"]}],
        )

    def test_zero_success_probability_is_never_recommended(self):
        impossible = complete_candidate(
            "impossible",
            success_probability=0.0,
            minutes={
                "research": 0,
                "setup": 0,
                "execute": 0,
                "verify": 0,
                "cleanup": 0,
            },
            failure_cost_minutes=0,
            risk=0,
            invasiveness=0,
        )
        payload = {
            "objective": "Reach a possible destination",
            "acceptance_checks": ["route can succeed"],
            "candidates": [impossible, complete_candidate("possible")],
        }

        result = run_payload(payload)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["recommended"], "possible")
        self.assertEqual(
            report["eliminated"],
            [
                {
                    "id": "impossible",
                    "failed_constraints": ["zero_success_probability"],
                }
            ],
        )

    def test_invalid_probability_returns_structured_error(self):
        payload = {
            "objective": "Reject invalid evidence",
            "acceptance_checks": ["valid"],
            "candidates": [complete_candidate("invalid", success_probability=1.2)],
        }

        result = run_payload(payload)

        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.lstrip().startswith("{"), result.stderr)
        error = json.loads(result.stderr)
        self.assertEqual(error["error"], "validation_error")
        self.assertIn("success_probability", error["message"])


if __name__ == "__main__":
    unittest.main()
