# Investment Project — Auto Commit Policy v0.1

## Purpose

Investment project decisions, lessons learned, and rule changes should remain reproducible and auditable. Git persistence is therefore the default, not an optional final step.

## Default Rule

After each substantive investment session or decision-making task:

1. Identify lessons learned.
2. Check whether an existing rule, workflow, or governance document needs to change.
3. If there is a material lesson, rule change, research result, or decision record, save it to the investment repository automatically.
4. Use a concise Conventional Commit-style message.
5. Report the commit SHA and affected path(s) after saving.

## What Must Be Saved

- New or revised investment rules
- Lessons learned that change future analysis
- Portfolio allocation/risk-policy changes
- Validated research findings that affect the decision framework
- Important market-session findings when they establish or modify a reusable rule
- Handover/governance changes

## What Does Not Require a Commit

Routine conversational clarification, transient market commentary with no reusable conclusion, or duplicate information that adds no durable project knowledge does not require a new commit.

## Commit Granularity

Prefer one focused commit per logical change. Avoid bundling unrelated lessons or rules into a single commit.

## Safety Check

Before writing, verify the target repository/path and whether the file already exists. For existing files, fetch the current content/blob SHA before updating. Never overwrite an existing file blindly.

## Session Closing Standard

The default closing sequence is:

`Lesson Learned → Rule Change Check → Git Save Decision → Commit if needed → Report SHA`

This policy is effective immediately for the Investment project.
