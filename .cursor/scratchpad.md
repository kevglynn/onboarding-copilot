# Agent Scratchpad

## Background and Motivation

Cursor Solutions Architect take-home assignment (3rd round, technical).
Build: **Engineering Onboarding Copilot** — a CLI + agent workspace that guides
a new engineer through a safe first contribution to a convention-heavy open-source
Python library (scikit-image as stand-in).

The artifact must demonstrate the full SDLC path: plan, design, build, review,
test, CI/deploy — and serve multiple audiences: engineer, PM, QA, DevOps.

Key insight: this is not a chatbot. It's a workflow tool that compresses
onboarding while improving code quality and reducing review burden.

## Key Challenges and Analysis

- Must be runnable, not a deck — live demo in 45-minute walkthrough
- Must show judgment about context boundaries (approved docs vs random internet)
- Must serve 4 stakeholder roles with different views of the same artifact
- Must demonstrate Cursor-native thinking (rules, modes, agents)
- Scope control: MVP that's polished > sprawling half-built system
- Library choice: scikit-image over OpenCV (Python-native, easier to demo)

## High-level Task Breakdown

1. Project scaffold (pyproject.toml, CLI skeleton, tests, ruff, CI)
2. Library profile: scikit-image (conventions YAML)
3. Contribution planner (`loc plan --task "..."`)
4. Scaffold first contribution (`loc scaffold --task "..."`)
5. Quality checker (`loc check <workspace>`)
6. Multi-role brief generator (`loc brief --role engineer|pm|qa|devops`)
7. Guardrails and approved context boundaries
8. GitHub Actions CI
9. Walkthrough demo script

## Current Status / Progress Tracking

- [x] Planning conversation captured
- [x] GitHub repo created (private, kevglynn/cursor-takehome-assignment)
- [x] Playbook scaffolding complete (Cursor rules, beads, scratchpad)
- [ ] Beads backlog not yet created
- [ ] No implementation started

## Executor's Feedback or Assistance Requests

None yet — awaiting direction on whether to create the beads backlog next
or jump to implementation of bead 1 (project scaffold).

## Lessons

- `gh repo create --source=.` sets a malformed remote when repo already exists — fix with `git remote set-url`
