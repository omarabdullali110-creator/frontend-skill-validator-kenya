# Unlocking Displaced Talent: Front-End Skills Validator (Kenya)

A lightweight Python CLI tool built for the **Power Learn Project (ILO Cohort) Mini-Hackathon** under the theme **"Unlocking Displaced Talent: Pathways for Skilled Refugees"** (Track 1: **Credential Recognition & Skills Validation**).

## Problem & Kenya Context
Refugees living in Nairobi, Kakuma, Kalobeyei, and Dadaab often hold technical talent or foreign qualifications from countries such as Somalia, South Sudan, DRC, Ethiopia, and Burundi, yet face "brain waste" when certificates are lost during displacement or await formal equation through the Kenya National Qualifications Authority (KNQA).

Aligned with Recognition of Prior Learning (RPL) principles and Kenya's Refugee Inclusion framework (Refugees Act, 2021), this tool separates **paper credential status** from **demonstrated front-end web development skills** so candidates are evaluated fairly on real code and portfolios.

## Project Files
- `rubric_frontend.json`: Front-end competency weights, scoring rules (`0`–`2`), Kenya credential/onboarding notes, and concrete bridging tasks.
- `candidates_sample.json`: Sample displaced candidates across Nairobi, Kakuma/Kalobeyei, and Dadaab with varied credential statuses.
- `validate_frontend_talent.py`: Standard-library Python script (`json`, `argparse`, `pathlib`, `datetime`) that scores candidates, flags skill gaps, and generates reports.
- `output/validation_report.md`: Human-readable report for mentors, NGOs, and hiring partners.
- `output/validation_results.json`: Structured JSON output for dashboards or talent-matching pipelines.

## How to Run
Requires Python 3.9+ (no external packages needed):

```bash
python validate_frontend_talent.py --rubric rubric_frontend.json --input candidates_sample.json --out-dir output
```

## SDG & Scalability Alignment
- **SDG 4 (Quality Education):** Turns every identified skill gap (`0/2` or `1/2`) into a specific, low-cost practical bridging task.
- **SDG 8 (Decent Work):** Connects vetted refugee front-end developers in Kenya to formal, remote, or freelance opportunities without blocking them on missing paperwork.
- **Low-Overhead Scalability:** Processes entire cohorts in seconds from structured JSON files and can be adapted to new roles (e.g., Data Analytics or Back-End) simply by swapping the JSON rubric.
