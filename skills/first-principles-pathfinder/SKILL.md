---
name: first-principles-pathfinder
description: Research, compare, probe, and execute the shortest safe path from the current state to a verified outcome using first-principles reasoning. Use when the user asks for the best, fastest, simplest, or least wasteful way to achieve a goal; says 先调研、先搜索、第一性原理、两点之间直线最短、不要急着部署; when several technical or operational approaches compete; or before committing to a crawler, automation stack, open-source project, service, dependency, integration, or custom build. Prefer native capabilities and lightweight composition only when evidence shows they meet the complete goal. Do not use when the user has already fixed and verified the execution route.
---

# First-Principles Pathfinder

Treat the user's outcome as fixed and every proposed tool or implementation as a replaceable hypothesis. Minimize time to a **verified complete result**, not code length, click count, or setup time.

## Non-negotiable rules

1. Define the finish line before choosing a route. Preserve every acceptance check and hard constraint.
2. Inspect existing capabilities before installing anything: local files, built-in tools, authenticated sessions, APIs, CLIs, browser state, and reusable data.
3. Search competing route families. Do not deep-dive the first plausible tutorial or repository.
4. Compare total lifecycle cost: research, setup, execution, verification, cleanup, failure probability, and recovery.
5. Apply hard gates before preferences. Never let speed compensate for missing coverage, unsafe access, or absent authority.
6. Pareto-prune dominated routes. Do not invent a weighted score unless the user explicitly supplies weights.
7. Resolve decisive unknowns with the cheapest discriminating probe before a large deployment.
8. Ignore sunk cost. Failed effort supplies evidence; it does not make that route more valuable.
9. Execute the winning low-risk route and verify the actual outcome end to end.

Read [references/decision-protocol.md](references/decision-protocol.md) before handling an unfamiliar domain, three or more serious candidates, a high-risk route, or uncertainty about when to stop researching.

## Workflow

### 1. Translate the request into a result contract

Write down, briefly:

- current state;
- observable target state;
- acceptance checks;
- hard constraints and prohibited actions;
- user priorities only after the hard constraints;
- available time, storage, compute, credentials, and authority.

Ask only for missing information that would change cost, risk, ownership, or the target state. Choose conservative defaults for low-impact unknowns and name the assumption.

### 2. Inventory the zero-cost starting surface

Inspect what is already available before searching for new infrastructure. A logged-in application, existing export function, local database, browser network trace, built-in API, small shell command, or current Skill can collapse the problem.

Do not install a project merely to learn whether it might work. Check free space before any authorized installation, keep changes isolated and reversible, and record cleanup steps.

### 3. Search by route family

Use the host's available web, code, documentation, browser, and local-search tools. Route through specialized search Skills when present; do not require a specific backend.

Cover at least three materially different families when they are feasible:

- native UI, export, or manual technique;
- documented API or direct protocol already available to the user;
- small script, CLI, library, or composition of existing tools;
- maintained full project or hosted service;
- browser/UI automation;
- human-assisted hybrid.

Search both primary evidence and practitioner evidence. Include queries for `without install`, `manual`, `built-in`, `API`, `CLI`, `existing session`, known failure text, and platform/version constraints. Treat multiple posts that repeat one architecture as one candidate, not independent confirmation.

### 4. Build a candidate ledger

For each serious route record:

- evidence and evidence quality;
- expected coverage and important unknowns;
- success probability as a justified estimate or qualitative band;
- research, setup, execution, verification, cleanup, and failure-recovery time;
- permissions, credentials, storage, risk, invasiveness, and reversibility;
- the cheapest probe that could falsify the route.

Separate observed facts from inference. Never fabricate precise numbers to make the comparison look objective.

### 5. Eliminate, Pareto-prune, and probe

Eliminate any route that fails a hard constraint. On the survivors, say that route A dominates route B only when A is no worse on every material dimension and strictly better on at least one.

If three or more candidates remain or the trade-off is unclear, encode the ledger as described in the reference and run:

```powershell
python scripts/rank_paths.py path\to\ledger.json
```

Use the script as a consistency check, not as a substitute for evidence or judgment.
It defaults `minimum_coverage` to `1.0`; lower it only when the result contract explicitly permits a partial outcome.

When a decisive field is uncertain, run the smallest reversible probe that distinguishes the leading routes. State the prediction, timebox, artifact, success threshold, and rollback before probing.

### 6. Stop searching deliberately

Stop research and select a route when all are true:

- at least one route satisfies every hard constraint and acceptance check;
- fragile assumptions have primary-source or runtime evidence;
- materially different feasible route families have been sampled;
- remaining uncertainty is unlikely to change the winner;
- the expected value of more research is lower than executing and verifying the leader.

Continue searching when the current leader only solves a subset, depends on an untested assumption, or won merely because it was found first.

### 7. Execute with bounded authority

Automatically execute the winning low-risk route when it stays within the user's request. Pause before credentials or login submission, payments, destructive actions, security-sensitive system changes, production mutations, external communication, or a product choice that changes the intended outcome unless the user has already authorized that exact class of action.

Install dependencies only after the route wins, the storage check passes, and installation is authorized. Prefer the smallest isolated dependency set. Preserve rollback and cleanup information.

If execution fails, record which assumption failed, update the ledger, and compare the remaining routes again. Do not silently turn a failed lightweight route into an unlimited debugging project.

### 8. Verify the destination

Test the complete user-visible result against every acceptance check. A command running, a service starting, or one sample succeeding is not completion when the goal asks for all items.

Report:

- verified outcome and evidence;
- selected route and the decisive reason;
- rejected routes in one line each;
- changes, installations, and cleanup state;
- residual limitations or inaccessible data.

Keep intermediate updates concise. Expand the ledger only when the decision is non-obvious or the user asks.
