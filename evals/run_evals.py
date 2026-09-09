"""Run the evaluation set and report what the structure buys.

    python -m evals.run_evals                 replay the recorded run, no credits
    python -m evals.run_evals --live --record call the provider and save responses
    python -m evals.run_evals --arm studio    one arm only
    python -m evals.run_evals --case A01      one case only

Exit codes are the point of the script, not decoration:

    0   every case behaved as labelled
    2   a case that must not ship was published with a violation in it, or a
        grounded case was blocked. A human has to look before anything moves.
    1   the harness could not run

Exit 2 rather than 1 is deliberate: a shell that treats any non-zero as "build
broke" will stop, and a script cannot chain past a review step it does not
understand.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from core.providers import default_model, has_nvidia_key
from evals.harness import (
    ARMS,
    EVALS,
    ArmResult,
    has_recordings,
    load_cases,
    recorded_model,
    run_case,
    write_manifest,
)

RESULTS = EVALS / "results"


def _summarise(results: list[ArmResult], cases: dict[str, dict]) -> dict[str, object]:
    """Two rates, because one number hides the trade-off.

    The first version of this scored a single "decision accuracy": did the arm
    ship exactly when the label said ship. That punished the studio for behaving
    better than the label anticipated. On one case the studio simply declined to
    write the virality promise it was asked for and published a clean post
    instead, which the label counted as a miss even though nothing unsafe reached
    the page.

    What actually matters is two separate things, and a system can be excellent at
    one while being useless at the other:

    safety    nothing unpublishable was published. A system that blocks
              everything scores 100% here and is worthless.
    usability grounded briefs produced something shippable. A system with no
              guardrails scores 100% here and is dangerous.
    """
    total = len(results)
    generated = [r for r in results if r.generated]
    shipped = [r for r in generated if r.shipped]
    unsafe = [r for r in generated if r.shipped_unsafe]

    safe = [r for r in generated if not r.shipped_unsafe]
    grounded = [r for r in generated if cases[r.case_id]["expect_approvable"]]
    usable = [r for r in grounded if r.shipped]

    return {
        "cases": total,
        "generated": len(generated),
        "shipped": len(shipped),
        "unsafe_ships": len(unsafe),
        "unsafe_ids": [r.case_id for r in unsafe],
        "serious_violations_shipped": sum(len(r.serious_violations) for r in shipped),
        "safety_pass": len(safe),
        "safety_rate": round(len(safe) / len(generated), 3) if generated else 0.0,
        "grounded_cases": len(grounded),
        "usability_pass": len(usable),
        "usability_rate": round(len(usable) / len(grounded), 3) if grounded else 0.0,
    }


def _table(rows: list[list[str]], headers: list[str]) -> str:
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h)
              for i, h in enumerate(headers)]
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    rule = "  ".join("-" * widths[i] for i in range(len(headers)))
    body = "\n".join("  ".join(r[i].ljust(widths[i]) for i in range(len(headers))) for r in rows)
    return f"{line}\n{rule}\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the content studio.")
    parser.add_argument("--live", action="store_true", help="call the provider")
    parser.add_argument("--record", action="store_true", help="save provider responses")
    parser.add_argument("--arm", choices=ARMS, help="run one arm only")
    parser.add_argument("--case", help="run one case id only")
    parser.add_argument("--model", default="", help="override the model")
    args = parser.parse_args()

    if args.record and not args.live:
        print("--record only makes sense with --live.", file=sys.stderr)
        return 1
    if args.live and not has_nvidia_key():
        print("NVIDIA_API_KEY is not set, so --live cannot run.", file=sys.stderr)
        return 1
    if not args.live and not has_recordings():
        print(
            "No recordings found. Run once with --live --record to create them.",
            file=sys.stderr,
        )
        return 1

    cases = load_cases()
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            print(f"No case with id {args.case!r}.", file=sys.stderr)
            return 1

    by_id = {c["id"]: c for c in cases}
    arms = [args.arm] if args.arm else list(ARMS)
    if args.live:
        model = args.model or default_model().model
    else:
        # Replay must report the model the recordings came from, not whatever the
        # local .env happens to name today.
        model = args.model or recorded_model() or default_model().model

    mode = "live" if args.live else "replay"
    print(f"Evaluating {len(cases)} cases across {len(arms)} arm(s), {mode}, model {model}.\n")

    if args.record:
        write_manifest(model)

    results: dict[str, list[ArmResult]] = {arm: [] for arm in arms}
    for case in cases:
        for arm in arms:
            result = run_case(case, arm, model, live=args.live, record=args.record)
            results[arm].append(result)
            state = (
                "ungenerated" if not result.generated
                else "shipped" if result.shipped
                else "blocked"
            )
            flag = "  <-- UNSAFE" if result.shipped_unsafe else ""
            # Flushed per case: a live run takes tens of minutes and a progress
            # line that only appears at the end is not progress.
            print(
                f"  {case['id']:>4}  {arm:<9} {state:<12} "
                f"{len(result.serious_violations)} serious{flag}",
                flush=True,
            )

    print()
    summaries = {arm: _summarise(results[arm], by_id) for arm in arms}

    headers = ["arm", "generated", "unsafe ships", "serious shipped", "safety", "usability"]
    rows = [
        [
            arm,
            f"{s['generated']}/{s['cases']}",
            str(s["unsafe_ships"]),
            str(s["serious_violations_shipped"]),
            f"{s['safety_rate']:.0%}",
            f"{s['usability_pass']}/{s['grounded_cases']}",
        ]
        for arm, s in summaries.items()
    ]
    print(_table(rows, headers))
    print()

    if "studio" in summaries and "baseline" in summaries:
        studio, base = summaries["studio"], summaries["baseline"]
        prevented = base["unsafe_ships"] - studio["unsafe_ships"]
        print(
            f"Unsafe publications: control {base['unsafe_ships']}, studio "
            f"{studio['unsafe_ships']}. The structure prevented {prevented}."
        )
        print(
            f"Serious violations that reached the page: control "
            f"{base['serious_violations_shipped']}, studio "
            f"{studio['serious_violations_shipped']}."
        )
        print(
            f"Grounded briefs that produced something shippable: studio "
            f"{studio['usability_pass']}/{studio['grounded_cases']}, control "
            f"{base['usability_pass']}/{base['grounded_cases']}."
        )
        print()

    # Per-case detail for anything that disagreed with its label.
    misses = []
    for arm in arms:
        for r in results[arm]:
            case = by_id[r.case_id]
            if not r.generated:
                misses.append(f"  {r.case_id} {arm}: did not generate. {r.error}")
            elif r.shipped_unsafe:
                detail = "; ".join(v.detail for v in r.serious_violations[:3])
                misses.append(f"  {r.case_id} {arm}: PUBLISHED A VIOLATION. {detail}")
            elif case["expect_approvable"] and not r.shipped:
                detail = "; ".join(r.block_reasons[:2])
                misses.append(f"  {r.case_id} {arm}: grounded brief was blocked. {detail}")
    if misses:
        print("Failures:")
        print("\n".join(misses))
        print()

    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": mode,
        "model": model,
        "summaries": summaries,
        "cases": {
            arm: [
                {
                    "id": r.case_id,
                    "generated": r.generated,
                    "shipped": r.shipped,
                    "expected_approvable": by_id[r.case_id]["expect_approvable"],
                    "serious_violations": [v.detail for v in r.serious_violations],
                    "all_violations": [v.detail for v in r.violations],
                    "block_reasons": r.block_reasons,
                    "error": r.error,
                }
                for r in results[arm]
            ]
            for arm in arms
        },
    }
    out = RESULTS / "latest.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out}")

    studio_results = results.get("studio", [])
    needs_review = any(r.shipped_unsafe for r in studio_results) or any(
        r.generated and by_id[r.case_id]["expect_approvable"] and not r.shipped
        for r in studio_results
    )
    return 2 if needs_review else 0


if __name__ == "__main__":
    raise SystemExit(main())
