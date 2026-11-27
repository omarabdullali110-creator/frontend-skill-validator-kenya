import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def classify_readiness(pct: float, thresholds: dict) -> tuple[str, str]:
    high = float(thresholds.get("placement_ready_min_pct", 80.0))
    mid = float(thresholds.get("short_bridging_min_pct", 55.0))
    if pct >= high:
        return (
            "Ready for Hiring / Technical Screening",
            "Recommend directly to Kenya tech employers, remote fellowships, or paid freelance projects without waiting for physical certificates.",
        )
    if pct >= mid:
        return (
            "Short Bridging Track (2-4 Weeks)",
            "Complete the targeted micro-projects below with mentor feedback, then re-score for employer matching.",
        )
    return (
        "Foundational Upskilling Track",
        "Place into structured PLP / community hub front-end sprints focusing on JavaScript fundamentals and GitHub portfolio publishing.",
    )


def evaluate_candidate(candidate: dict, rubric: dict) -> dict:
    target_max = float(rubric.get("target_score_per_skill", 2))
    thresholds = rubric.get("readiness_thresholds", {})
    cred_notes_map = rubric.get("credential_status_notes", {})
    kenya_access_map = rubric.get("kenya_onboarding_notes", {})
    competencies = rubric.get("competencies", [])

    scores = candidate.get("skill_scores", {})
    total_weight = sum(float(c.get("weight", 0.0)) for c in competencies) or 1.0

    weighted_earned = 0.0
    weighted_possible = 0.0
    competency_results = []
    bridging_plan = []

    for comp in competencies:
        cid = comp["id"]
        cname = comp["name"]
        weight = float(comp.get("weight", 0.0)) / total_weight
        raw_score = scores.get(cid, 0)

        if not isinstance(raw_score, (int, float)) or raw_score < 0 or raw_score > target_max:
            raise ValueError(
                f"Invalid score '{raw_score}' for '{cid}' in candidate '{candidate.get('candidate_id')}'. "
                f"Expected a number between 0 and {target_max}."
            )

        ratio = raw_score / target_max
        weighted_earned += ratio * weight
        weighted_possible += weight

        is_gap = raw_score < target_max
        status = "Met" if not is_gap else ("Partial Gap" if raw_score > 0 else "Priority Gap")

        competency_results.append({
            "id": cid,
            "name": cname,
            "score": raw_score,
            "max_score": target_max,
            "weight_pct": round(weight * 100, 1),
            "status": status,
        })

        if is_gap:
            bridging_plan.append({
                "competency": cname,
                "current_score": f"{raw_score}/{target_max}",
                "priority": "High" if raw_score == 0 else "Medium",
                "action": comp.get("bridging_action", "Complete targeted front-end practice exercise."),
            })

    readiness_pct = round((weighted_earned / (weighted_possible or 1.0)) * 100, 1)
    tier_label, next_step = classify_readiness(readiness_pct, thresholds)

    cred_status = candidate.get("credential_status", "missing_documents_displacement")
    cred_note = cred_notes_map.get(
        cred_status,
        "Credential status recorded separately from demonstrated front-end competencies.",
    )

    access_status = candidate.get("work_access_status", "Pending Documentation")
    access_note = kenya_access_map.get(
        access_status,
        "Verify Refugee ID / work authorization pathway alongside remote portfolio opportunities.",
    )

    return {
        "candidate_id": candidate.get("candidate_id", "UNKNOWN"),
        "display_label": candidate.get("display_label", "Candidate"),
        "location_hub": candidate.get("location_hub", "Kenya"),
        "credential_status": cred_status,
        "credential_handling_note": cred_note,
        "work_access_status": access_status,
        "kenya_onboarding_note": access_note,
        "portfolio_or_repo": candidate.get("portfolio_url_or_repo", "Not provided"),
        "readiness_score_pct": readiness_pct,
        "readiness_tier": tier_label,
        "recommended_next_step": next_step,
        "reviewer_notes": candidate.get("reviewer_notes", ""),
        "competencies": competency_results,
        "bridging_plan": bridging_plan,
    }


def render_markdown(evaluations: list[dict], rubric: dict) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    role_title = rubric.get("role_title", "Front-End Web Developer")
    sdgs = ", ".join(rubric.get("sdg_alignment", []))

    ready_count = sum(1 for e in evaluations if e["readiness_score_pct"] >= 80.0)
    bridging_count = sum(1 for e in evaluations if 55.0 <= e["readiness_score_pct"] < 80.0)
    foundational_count = sum(1 for e in evaluations if e["readiness_score_pct"] < 55.0)

    lines = [
        "# Kenya Skilled Refugee Front-End Skills Validation Report",
        "",
        f"- **Role Rubric:** {role_title}",
        f"- **SDG Alignment:** {sdgs}",
        f"- **Generated:** {generated_at}",
        f"- **Cohort Size:** {len(evaluations)} candidates",
        f"- **Cohort Summary:** {ready_count} Ready | {bridging_count} Short Bridging | {foundational_count} Foundational Upskilling",
        "",
        "> **Privacy & RPL Fairness Note:** Technical scores evaluate demonstrated front-end skills independently of missing or unverified foreign certificates (aligned with Recognition of Prior Learning principles in Kenya). Avoid storing sensitive asylum case numbers or personal ID numbers in validation reports.",
        "",
        "---",
        "",
    ]

    for ev in evaluations:
        lines.extend([
            f"## {ev['candidate_id']} — {ev['display_label']}",
            "",
            f"- **Location / Hub:** {ev['location_hub']}",
            f"- **Readiness Score:** **{ev['readiness_score_pct']}%** ({ev['readiness_tier']})",
            f"- **Credential Status:** `{ev['credential_status']}` — {ev['credential_handling_note']}",
            f"- **Kenya Work / Onboarding Status:** `{ev['work_access_status']}` — {ev['kenya_onboarding_note']}",
            f"- **Portfolio / Repo:** {ev['portfolio_or_repo']}",
            f"- **Recommended Action:** {ev['recommended_next_step']}",
        ])
        if ev["reviewer_notes"]:
            lines.append(f"- **Evidence / Reviewer Notes:** {ev['reviewer_notes']}")
        lines.extend([
            "",
            "| Competency | Weight | Score | Status |",
            "| --- | ---: | ---: | --- |",
        ])
        for c in ev["competencies"]:
            lines.append(
                f"| {c['name']} | {c['weight_pct']}% | {c['score']}/{c['max_score']} | {c['status']} |"
            )
        lines.append("")

        lines.append("### Targeted Bridging Plan")
        lines.append("")
        if ev["bridging_plan"]:
            for item in ev["bridging_plan"]:
                lines.append(
                    f"* **{item['competency']}** (Score: {item['current_score']}, Priority: {item['priority']}): {item['action']}"
                )
        else:
            lines.append("* All target front-end competencies met; ready for employer technical interview or paid placement.")
        lines.extend(["", "---", ""])

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate front-end web developer skills for refugees in Kenya without penalizing missing credentials."
    )
    parser.add_argument("--rubric", default="rubric_frontend.json", help="Path to rubric JSON file")
    parser.add_argument("--input", default="candidates_sample.json", help="Path to candidates JSON file")
    parser.add_argument("--out-dir", default="output", help="Directory for generated output files")
    args = parser.parse_args()

    rubric_path = Path(args.rubric)
    input_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    candidates = json.loads(input_path.read_text(encoding="utf-8"))

    if not isinstance(candidates, list):
        raise ValueError("Input JSON must contain a list of candidate objects.")

    evaluations = [evaluate_candidate(cand, rubric) for cand in candidates]

    json_out = out_dir / "validation_results.json"
    md_out = out_dir / "validation_report.md"

    json_out.write_text(json.dumps(evaluations, indent=2), encoding="utf-8")
    md_out.write_text(render_markdown(evaluations, rubric), encoding="utf-8")

    print(f"Evaluated {len(evaluations)} candidates in Kenya cohort.")
    print(f"JSON summary saved to: {json_out}")
    print(f"Markdown report saved to: {md_out}")


if __name__ == "__main__":
    main()
