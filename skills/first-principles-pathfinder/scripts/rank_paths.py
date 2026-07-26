#!/usr/bin/env python3
"""Validate and rank solution paths without collapsing trade-offs into one score."""

import argparse
import json
import sys
from pathlib import Path


DEFAULT_PRIORITIES = [
    "coverage_desc",
    "expected_minutes_asc",
    "risk_asc",
    "invasiveness_asc",
    "success_probability_desc",
    "evidence_quality_desc",
    "reversible_desc",
]
ALLOWED_PRIORITIES = set(DEFAULT_PRIORITIES)
TIME_FIELDS = ("research", "setup", "execute", "verify", "cleanup")


class ValidationError(ValueError):
    pass


def require_number(value, field, minimum, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError("{} must be a number".format(field))
    if value < minimum or (maximum is not None and value > maximum):
        if maximum is None:
            raise ValidationError("{} must be at least {}".format(field, minimum))
        raise ValidationError(
            "{} must be between {} and {}".format(field, minimum, maximum)
        )
    return float(value)


def validate_candidate(raw, seen_ids):
    if not isinstance(raw, dict):
        raise ValidationError("each candidate must be an object")
    candidate_id = raw.get("id")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValidationError("candidate.id must be a non-empty string")
    if candidate_id in seen_ids:
        raise ValidationError("candidate.id must be unique: {}".format(candidate_id))
    seen_ids.add(candidate_id)

    approach = raw.get("approach")
    if not isinstance(approach, str) or not approach.strip():
        raise ValidationError("{}.approach must be a non-empty string".format(candidate_id))

    constraints = raw.get("hard_constraints")
    if not isinstance(constraints, dict) or not constraints:
        raise ValidationError(
            "{}.hard_constraints must be a non-empty object".format(candidate_id)
        )
    if not all(isinstance(name, str) and isinstance(value, bool) for name, value in constraints.items()):
        raise ValidationError(
            "{}.hard_constraints must map names to booleans".format(candidate_id)
        )

    minutes = raw.get("minutes")
    if not isinstance(minutes, dict):
        raise ValidationError("{}.minutes must be an object".format(candidate_id))
    normalized_minutes = {}
    for name in TIME_FIELDS:
        if name not in minutes:
            raise ValidationError("{}.minutes.{} is required".format(candidate_id, name))
        normalized_minutes[name] = require_number(
            minutes[name], "{}.minutes.{}".format(candidate_id, name), 0
        )

    reversible = raw.get("reversible")
    if not isinstance(reversible, bool):
        raise ValidationError("{}.reversible must be a boolean".format(candidate_id))
    evidence = raw.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(
        isinstance(item, str) and item.strip() for item in evidence
    ):
        raise ValidationError(
            "{}.evidence must be a non-empty list of strings".format(candidate_id)
        )

    candidate = dict(raw)
    candidate["id"] = candidate_id
    candidate["hard_constraints"] = dict(constraints)
    candidate["minutes"] = normalized_minutes
    candidate["coverage"] = require_number(
        raw.get("coverage"), "{}.coverage".format(candidate_id), 0, 1
    )
    candidate["success_probability"] = require_number(
        raw.get("success_probability"),
        "{}.success_probability".format(candidate_id),
        0,
        1,
    )
    candidate["failure_cost_minutes"] = require_number(
        raw.get("failure_cost_minutes"),
        "{}.failure_cost_minutes".format(candidate_id),
        0,
    )
    candidate["risk"] = require_number(
        raw.get("risk"), "{}.risk".format(candidate_id), 0, 3
    )
    candidate["invasiveness"] = require_number(
        raw.get("invasiveness"), "{}.invasiveness".format(candidate_id), 0, 3
    )
    candidate["evidence_quality"] = require_number(
        raw.get("evidence_quality"),
        "{}.evidence_quality".format(candidate_id),
        0,
        3,
    )
    base_minutes = sum(normalized_minutes.values())
    candidate["expected_minutes"] = round(
        base_minutes
        + (1 - candidate["success_probability"])
        * candidate["failure_cost_minutes"],
        3,
    )
    return candidate


def validate_ledger(raw):
    if not isinstance(raw, dict):
        raise ValidationError("ledger must be a JSON object")
    objective = raw.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        raise ValidationError("objective must be a non-empty string")
    acceptance_checks = raw.get("acceptance_checks")
    if not isinstance(acceptance_checks, list) or not acceptance_checks or not all(
        isinstance(item, str) and item.strip() for item in acceptance_checks
    ):
        raise ValidationError("acceptance_checks must be a non-empty list of strings")
    priorities = raw.get("priorities", DEFAULT_PRIORITIES)
    if not isinstance(priorities, list) or not priorities:
        raise ValidationError("priorities must be a non-empty list")
    unknown_priorities = [item for item in priorities if item not in ALLOWED_PRIORITIES]
    if unknown_priorities:
        raise ValidationError(
            "unknown priorities: {}".format(", ".join(map(str, unknown_priorities)))
        )

    minimum_coverage = require_number(
        raw.get("minimum_coverage", 1.0), "minimum_coverage", 0, 1
    )

    raw_candidates = raw.get("candidates")
    if not isinstance(raw_candidates, list) or not raw_candidates:
        raise ValidationError("candidates must be a non-empty list")
    seen_ids = set()
    candidates = [validate_candidate(item, seen_ids) for item in raw_candidates]
    return objective, acceptance_checks, list(priorities), minimum_coverage, candidates


def dominates(left, right):
    comparisons = [
        left["coverage"] >= right["coverage"],
        left["success_probability"] >= right["success_probability"],
        left["evidence_quality"] >= right["evidence_quality"],
        int(left["reversible"]) >= int(right["reversible"]),
        left["expected_minutes"] <= right["expected_minutes"],
        left["risk"] <= right["risk"],
        left["invasiveness"] <= right["invasiveness"],
    ]
    strict = [
        left["coverage"] > right["coverage"],
        left["success_probability"] > right["success_probability"],
        left["evidence_quality"] > right["evidence_quality"],
        int(left["reversible"]) > int(right["reversible"]),
        left["expected_minutes"] < right["expected_minutes"],
        left["risk"] < right["risk"],
        left["invasiveness"] < right["invasiveness"],
    ]
    return all(comparisons) and any(strict)


def priority_value(candidate, priority):
    values = {
        "coverage_desc": -candidate["coverage"],
        "expected_minutes_asc": candidate["expected_minutes"],
        "risk_asc": candidate["risk"],
        "invasiveness_asc": candidate["invasiveness"],
        "success_probability_desc": -candidate["success_probability"],
        "evidence_quality_desc": -candidate["evidence_quality"],
        "reversible_desc": -int(candidate["reversible"]),
    }
    return values[priority]


def rank_ledger(raw):
    (
        objective,
        acceptance_checks,
        priorities,
        minimum_coverage,
        candidates,
    ) = validate_ledger(raw)
    eliminated = []
    eligible = []
    for candidate in candidates:
        failed = sorted(
            name for name, passed in candidate["hard_constraints"].items() if not passed
        )
        if candidate["coverage"] < minimum_coverage:
            failed.append("minimum_coverage")
        if candidate["success_probability"] == 0:
            failed.append("zero_success_probability")
        failed = sorted(failed)
        if failed:
            eliminated.append(
                {"id": candidate["id"], "failed_constraints": failed}
            )
        else:
            eligible.append(candidate)

    dominated_ids = {
        candidate["id"]
        for candidate in eligible
        if any(
            other["id"] != candidate["id"] and dominates(other, candidate)
            for other in eligible
        )
    }
    pareto_ids = {candidate["id"] for candidate in eligible} - dominated_ids

    def sort_key(candidate):
        return (
            0 if candidate["id"] in pareto_ids else 1,
            *[priority_value(candidate, item) for item in priorities],
            candidate["id"],
        )

    ranked_candidates = sorted(eligible, key=sort_key)
    ranked = [
        {
            "id": candidate["id"],
            "expected_minutes": candidate["expected_minutes"],
            "pareto": candidate["id"] in pareto_ids,
        }
        for candidate in ranked_candidates
    ]
    pareto_front = [item["id"] for item in ranked if item["pareto"]]
    return {
        "objective": objective,
        "acceptance_checks": acceptance_checks,
        "minimum_coverage": minimum_coverage,
        "priorities": priorities,
        "eliminated": sorted(eliminated, key=lambda item: item["id"]),
        "eligible": sorted(candidate["id"] for candidate in eligible),
        "dominated": sorted(dominated_ids),
        "pareto_front": pareto_front,
        "ranked": ranked,
        "recommended": pareto_front[0] if pareto_front else None,
    }


def load_json(path_text):
    if path_text == "-":
        return json.load(sys.stdin)
    with Path(path_text).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Apply hard gates, Pareto pruning, and deterministic priorities to solution paths."
    )
    parser.add_argument("ledger", help="Path to a UTF-8 JSON ledger, or - for stdin")
    args = parser.parse_args(argv)
    try:
        report = rank_ledger(load_json(args.ledger))
    except (ValidationError, json.JSONDecodeError, OSError) as exc:
        error_type = "validation_error" if isinstance(exc, ValidationError) else "input_error"
        json.dump(
            {"error": error_type, "message": str(exc)},
            sys.stderr,
            ensure_ascii=False,
        )
        sys.stderr.write("\n")
        return 2
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
