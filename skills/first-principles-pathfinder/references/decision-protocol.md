# Decision Protocol

## Contents

1. [Derive the real objective](#derive-the-real-objective)
2. [Model total path cost](#model-total-path-cost)
3. [Search without first-result bias](#search-without-first-result-bias)
4. [Grade evidence](#grade-evidence)
5. [Build the candidate ledger](#build-the-candidate-ledger)
6. [Apply hard gates and Pareto dominance](#apply-hard-gates-and-pareto-dominance)
7. [Design the minimum discriminating probe](#design-the-minimum-discriminating-probe)
8. [Stop research at the right time](#stop-research-at-the-right-time)
9. [Execute, learn, and fall back](#execute-learn-and-fall-back)
10. [Worked WeChat-comments comparison](#worked-wechat-comments-comparison)
11. [Common failure modes](#common-failure-modes)

## Derive the real objective

Begin with the difference between the current state and the requested state. Do not begin with a tool name.

Represent the task as:

- `S`: current state and resources;
- `G`: observable target state;
- `A`: acceptance checks proving `G`;
- `H`: hard constraints that no route may violate;
- `P`: preferences used only among feasible routes.

Tools, repositories, services, scraping frameworks, and automation techniques are candidate routes `r`, not requirements, unless the user explicitly makes one part of `G` or `H`.

Use falsifiable acceptance checks. Replace “抓到评论” with checks such as “all discoverable articles processed,” “all publicly visible selected comments and visible replies exported,” “no unpublished data claimed,” and “output count and spot checks recorded.”

Do not optimize a proxy. A route that starts quickly but covers one article does not beat a slower route if the target is every article.

## Model total path cost

Use this comparison model:

```text
T_expected(r) = T_research
              + T_setup
              + T_execute
              + T_verify
              + T_cleanup
              + (1 - P_success) × T_failure_recovery
```

Keep completeness, legality, safety, and authority outside this formula as hard gates. Time cannot compensate for failure there.

Treat estimates as ranges when evidence is weak. A useful honest estimate is `15–30 min, medium confidence`; an invented `21.7 min` is not.

Account for:

- installation and build time;
- authentication and permission friction;
- platform-version compatibility;
- rate limits and pagination;
- transformation and output formatting;
- end-to-end verification at the requested scale;
- system restoration, secret deletion, and process cleanup;
- likely failure recovery and switching cost.

Do not count time already spent as a benefit. Sunk cost changes current state only when it produced a reusable working asset or new evidence.

## Search without first-result bias

### Inventory before internet search

Inspect the starting surface first:

- existing files, databases, caches, logs, and exports;
- installed CLIs, libraries, Skills, MCP tools, and browser tools;
- authenticated desktop or browser sessions already controlled by the user;
- native menus, developer tools, network requests, and documented APIs;
- small transformations that compose existing capabilities.

This is not a reason to avoid web research. It determines which search questions matter.

### Generate route families

Search for architectures, not just products. Use several of these families:

1. Native/manual: built-in export, copy, query, or existing UI behavior.
2. Direct interface: documented API, local database, network protocol, or platform endpoint already accessible to the user.
3. Lightweight composition: shell command, short script, CLI, library, browser developer tools, or existing session.
4. Packaged system: maintained repository, desktop app, container, hosted service, or full automation stack.
5. UI automation: browser or desktop interaction when no stable data interface exists.
6. Human-assisted hybrid: ask the user to perform the one security-sensitive or visual step that collapses the rest of the workflow.

Do not assume “manual” means slow or “open source” means reusable. Measure the full path.

### Query from the bottleneck

Search the exact outcome and the suspected bottleneck. Useful modifiers include:

```text
<outcome> without installing
<outcome> built-in export
<outcome> direct API OR endpoint
<outcome> CLI OR script
<outcome> existing authenticated session
<exact error message>
<platform version> <outcome>
site:github.com <outcome> issue
```

Search primary code and issues for what a project actually does. Search practitioner sources such as CSDN, Stack Overflow, V2EX, Reddit, blogs, or videos for shortcuts, operational traps, and current breakage. Verify secondary claims against source code, official behavior, or a probe.

Stop counting sources and start counting independent mechanisms. Ten tutorials wrapping the same repository are one route family.

## Grade evidence

Use a small ordinal scale; do not pretend it is continuous science:

- `3` — current end-to-end runtime observation, or current primary source code directly establishing the behavior;
- `2` — current official documentation, maintainer issue, or reproducible independent report;
- `1` — secondary tutorial, forum account, benchmark without full reproduction, or older evidence;
- `0` — intuition, marketing claim, stale snippet, or unverified inference.

Record the evidence text or URL and its date/version when fragility matters. Distinguish:

- **fact**: directly observed or stated by a primary source;
- **inference**: conclusion supported by facts;
- **assumption**: unresolved condition that could invalidate the route.

Probe high-impact assumptions even when a tutorial sounds authoritative.

## Build the candidate ledger

Use prose or a table for two simple candidates. Use JSON plus `scripts/rank_paths.py` when there are at least three serious candidates, many constraints, or a contested choice.

Example schema:

```json
{
  "objective": "Export every publicly visible comment",
  "acceptance_checks": ["all articles covered", "counts verified"],
  "minimum_coverage": 1.0,
  "priorities": [
    "coverage_desc",
    "expected_minutes_asc",
    "risk_asc",
    "invasiveness_asc",
    "success_probability_desc",
    "evidence_quality_desc",
    "reversible_desc"
  ],
  "candidates": [
    {
      "id": "native-route",
      "approach": "Use the existing authenticated client and direct requests",
      "hard_constraints": {
        "public_only": true,
        "complete": true,
        "authorized": true
      },
      "coverage": 1.0,
      "success_probability": 0.9,
      "minutes": {
        "research": 10,
        "setup": 0,
        "execute": 30,
        "verify": 10,
        "cleanup": 2
      },
      "failure_cost_minutes": 15,
      "risk": 1,
      "invasiveness": 0,
      "reversible": true,
      "evidence_quality": 3,
      "evidence": ["Observed with one complete account export"]
    }
  ]
}
```

Use these scales consistently:

- `coverage`: `0.0–1.0`, relative to the complete requested outcome;
- `success_probability`: `0.0–1.0`, justified by evidence rather than confidence theater;
- `risk`: `0` none, `1` low/reversible, `2` meaningful user or system exposure, `3` high or potentially irreversible;
- `invasiveness`: `0` no change, `1` isolated/local change, `2` several dependencies or persistent config, `3` system-wide/service-level change;
- `evidence_quality`: the `0–3` scale above;
- `reversible`: whether the route has a specific reliable rollback.

Every hard constraint must be named and boolean. A `false` value eliminates the route; do not hide it inside a lower score.
`minimum_coverage` defaults to `1.0`. Lower it only when the user's result contract explicitly accepts a partial outcome.
A candidate with `success_probability = 0` is also eliminated because it cannot reach the target under any preference ordering.

Run the comparison from the Skill directory:

```powershell
python scripts/rank_paths.py C:\path\to\ledger.json
```

The script reports eliminated candidates, the Pareto front, dominated candidates, deterministic ranking, and the recommendation. It deliberately does not emit a weighted scalar score.

## Apply hard gates and Pareto dominance

Apply decisions in this order:

1. Eliminate routes that fail any hard constraint.
2. Eliminate routes that cannot meet the acceptance checks at required scale.
3. Mark A as dominating B only when A is no worse on coverage, probability, evidence, reversibility, expected time, risk, and invasiveness, and strictly better on at least one.
4. Keep non-dominated trade-offs on the Pareto front.
5. Sort the front by the user's explicit priorities. Use the default order only when the user did not express a different preference.

The default order is completeness/coverage, expected verified time, risk, invasiveness, success probability, evidence quality, then reversibility. Coverage comes first because delivering the wrong subset quickly is not a shortcut to the requested destination.

If route rankings depend on guessed values, do not debate the guesses. Design a probe.

## Design the minimum discriminating probe

A useful probe changes the route decision. It is not a small version of an already-selected build.

Write five items before probing:

1. **Question:** Which uncertainty separates the leaders?
2. **Predictions:** What result would support each route?
3. **Artifact:** What smallest output proves the result?
4. **Budget:** Maximum time, storage, requests, and retries.
5. **Rollback:** How temporary changes and sensitive data will be removed.

Prefer probes such as:

- call one endpoint with one already-authorized item;
- inspect one source file for pagination or credential behavior;
- export one representative record through a native feature;
- run a dependency's `--help`, dry run, or preflight rather than deploying it;
- compare one result count against the visible source.

Do not use a one-item success to prove all-item scalability. The probe must test the uncertainty it claims to resolve.

## Stop research at the right time

Stop when:

- one or more routes satisfy every hard constraint;
- the leading route has strong evidence for its fragile assumptions;
- at least three materially different feasible route families were sampled, or unavailable families were explicitly ruled out;
- another search is unlikely to move a route onto or off the Pareto front;
- the cost of the next useful fact exceeds its expected reduction in execution/recovery cost.

Continue when:

- the leader solves only a convenient subset;
- all candidates are variants of the same mechanism;
- the route depends on an untested login, pagination, scale, version, or permission assumption;
- evidence is only a copied tutorial or repository description;
- the current route leads only because work has already begun.

Use a research timebox as a forcing function, not as permission to choose an incomplete route. At the timebox boundary, either select a proven feasible route, run the highest-value probe, or report that no route is yet proven.

## Execute, learn, and fall back

Before execution, state the chosen route in one sentence and name the decisive evidence. Keep the decision brief unless the choice is contested.

For installation:

- confirm the route has already won;
- check available storage and platform compatibility;
- isolate dependencies where practical;
- record created paths, processes, ports, services, certificates, proxies, and environment changes;
- define cleanup before starting.

On failure, classify it:

- **route-invalidating:** access unavailable, required coverage impossible, incompatible platform, or unacceptable risk;
- **probe-inconclusive:** the experiment did not test the intended uncertainty;
- **correctable execution issue:** typo, temporary network error, or documented setup defect within the route's original budget;
- **scope expansion:** fixing it requires a new service, broad permission, or substantial architecture not included in the estimate.

Update the ledger after route-invalidating evidence or scope expansion. Do not silently grant a failed route more time because it is familiar.

## Worked WeChat-comments comparison

Goal: export all publicly visible selected comments and visible replies across all discoverable articles of a WeChat Official Account. Do not claim access to unpublished comments.

Observed routes in the motivating case:

- **Direct authenticated-session technique:** found through general search and practitioner reports; used lightweight techniques without deploying a project; produced more than ten thousand comments across the article set in about 1.5 hours.
- **`wechat-article-exporter + wxdown-service`:** required project setup plus a local interception proxy; after about one hour produced one article's public comment section in the observed attempt.

For that environment and objective, the direct route had stronger observed coverage, lower setup cost, lower invasiveness, and better total throughput. It therefore dominated the deployed stack; the number of GitHub stars or sophistication of the stack could not reverse that result.

This is evidence for the decision process, not a timeless ban on either project. If authentication behavior, endpoints, account scope, or platform versions change, probe those assumptions again. Never use a “direct” route to bypass access controls or retrieve data the user is not authorized to access.

The key lesson is not “always avoid open source.” It is: compare the shortest complete path before turning a candidate repository into the plan.

## Common failure modes

- **First-result fixation:** treating the first credible tutorial as the architecture.
- **Repository bias:** assuming a full project is safer or faster because it is popular.
- **Deployment momentum:** installing before verifying that the route covers the target.
- **Local optimization:** minimizing setup while ignoring execution at full scale.
- **Metric gaming:** allowing a weighted score to compensate for a failed constraint.
- **False precision:** assigning unsupported decimal estimates.
- **Source-count illusion:** counting copied tutorials as independent evidence.
- **Probe mismatch:** testing one record and claiming all-record completeness.
- **Sunk-cost escalation:** debugging a route beyond its original budget without re-ranking.
- **Verification collapse:** declaring success because the tool ran rather than because the user's finish line was reached.
