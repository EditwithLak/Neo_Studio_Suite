# Contributing to Neo Studio Suite

Thanks for your interest in contributing to **Neo Studio Suite**.

This project is built around a simple goal:

**make local Stable Diffusion workflows more reusable, searchable, recoverable, and practical to maintain.**

Neo Studio Suite is a **local-first workflow system** built across two connected parts:

- **Neo Library** — the Forge-side workflow layer
- **Neo Studio** — the standalone local workspace

Because of that, contributions should focus on improving real local workflows rather than adding flashy features with no practical use.

---

## Before you contribute

Please read these first if they are relevant to the part you want to touch:

- `README.md`
- `INSTALLATION.md`
- `MODEL_GUIDE.md`
- `NEO_LIBRARY_GUIDE.md`
- `NEO_STUDIO_GUIDE.md`
- `FAQ_TROUBLESHOOTING.md`

If your change affects setup, models, or usage flow, update the related docs too.

---

## What kinds of contributions are welcome

Contributions are welcome for things like:

- bug fixes
- stability improvements
- UI/UX cleanup
- documentation improvements
- setup and installation fixes
- better error messages
- workflow quality improvements
- import/export reliability
- search, metadata, and caption workflow improvements
- LoRA / TI management improvements
- Prompt Composer / Prompt Studio improvements
- performance fixes that help real local users

Good contributions usually make the tool:

- easier to understand
- easier to maintain
- more reliable
- more reusable
- less annoying in actual day-to-day use

---

## What is usually *not* a good fit

Please avoid contributions that:

- turn the project into a cloud-first tool
- add heavy complexity without solving a real workflow problem
- break the split between **Neo Library** and **Neo Studio**
- assume high-end hardware only
- add hard dependencies where optional ones make more sense
- rewrite large working systems without a strong reason
- add “AI magic” features that reduce control or transparency

This project is meant to support **real local creator workflows**, not chase every shiny thing.

---

## Before opening a pull request

Please do this first:

1. Check whether the issue is already known.
2. Keep the change focused.
3. Make sure the feature or fix fits the project direction.
4. Test your change locally.
5. Update docs if behavior, setup, or user flow changed.

Small, clean pull requests are much easier to review than giant all-in-one rewrites.

---

## Bug reports

If you find a bug, try to include:

- what you expected to happen
- what actually happened
- steps to reproduce it
- which part was affected:
  - Neo Library
  - Neo Studio
  - backend connection
  - captioning
  - prompting
  - metadata
  - import/export
  - setup/install
- screenshots if useful
- error logs if available
- your environment details if relevant:
  - OS
  - Python version
  - Forge / Forge Neo version
  - model/backend used
  - whether optional tools were installed

A vague “it broke” report is hard to act on.
A precise report saves everyone time.

---

## Feature requests

Feature requests are welcome, but they should be grounded in an actual workflow problem.

A strong feature request explains:

- the problem
- why current behavior is not enough
- the workflow impact
- the kind of solution that would help
- whether it belongs in Neo Library or Neo Studio

The best requests are tied to repeatable real use cases, not just “this would be cool.”

---

## Setup for contributors

Neo Studio Suite currently uses:

- `requirements.txt` for core dependencies
- `requirements-optional-tools.txt` for optional tools and heavier extras

### Core install

```bash
pip install -r requirements.txt
```

### Optional tools

Install only if your work needs them:

```bash
pip install -r requirements-optional-tools.txt
```

### Virtual environment example

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-optional-tools.txt
```

If you are only changing docs or lightweight code, you may not need the full optional stack.

---

## Contribution areas

### Neo Library contributions

These usually affect the Forge-side workflow, such as:

- Prompt Composer
- Vault + Maps
- Output Inspector
- Caption Library
- Prompt Bundles / Projects
- LoRA / TI metadata or preview workflows

When contributing here, be careful about anything that could disrupt generation-side usability.

### Neo Studio contributions

These usually affect the standalone workspace, such as:

- Prompt Studio
- Caption Studio
- global search
- prompt QA
- saved prompts / captions
- import / export
- batch captioning
- settings and path management

When contributing here, prioritize clarity, stability, and practical workflow speed.

### Documentation contributions

Docs matter a lot here.

Good doc contributions include:

- setup clarification
- fewer confusing steps
- cleaner explanations
- correcting outdated instructions
- adding missing workflow notes
- improving troubleshooting guidance

If something confused you, fixing the docs is a valid contribution.

---

## Coding expectations

Please try to keep changes:

- readable
- focused
- maintainable
- consistent with the current project structure

### General guidelines

- avoid unnecessary rewrites
- do not rename things casually
- do not introduce giant abstractions unless they clearly help
- prefer clear logic over clever logic
- keep comments useful, not noisy
- preserve user control where possible
- avoid hardcoding paths unless there is a very good reason
- avoid forcing optional tooling into the core path

### UI / workflow changes

For UI or workflow changes:

- keep labels understandable
- reduce friction where possible
- do not hide important actions behind confusing flow
- respect the local-first design of the project
- think about lower- to mid-range hardware users before adding heavier behavior

---

## Testing your changes

Before submitting, test what you changed as directly as possible.

Examples:

- if you changed setup logic, test installation flow
- if you changed Prompt Studio, save and reload prompts
- if you changed captioning, run at least one caption test
- if you changed metadata handling, test recovery on a sample output
- if you changed import/export, do a real round-trip test
- if you changed LoRA / TI scanning, test on actual folders
- if you changed docs, make sure the instructions still match reality

Do not assume a change is safe just because it looks small.

---

## Pull request guidance

When opening a pull request, please include:

- a short summary of what changed
- why the change was made
- which part of the project it affects
- any setup notes
- screenshots if UI changed
- any docs you updated

A good PR title is specific.

Examples:

- `Fix Prompt Studio save path validation`
- `Improve Output Inspector metadata error handling`
- `Clarify optional dependency setup in INSTALLATION.md`

Bad PR titles:

- `Update stuff`
- `Fixes`
- `Changes`
- `Big improvement`

---

## Documentation rules

If your pull request changes any of these, update the relevant docs:

- installation steps
- dependency requirements
- backend setup
- file/folder layout expectations
- feature behavior
- labels, buttons, or menus
- troubleshooting steps

If users need to do something differently after your change, the docs should say so.

---

## Scope discipline

Please keep pull requests narrow.

Good:
- one bug fix
- one feature improvement
- one UI cleanup
- one doc pass
- one import/export fix

Bad:
- bug fix + refactor + UI redesign + new feature + doc rewrite all in one PR

That kind of PR is a review nightmare.

---

## If you are unsure

If you are unsure whether something fits, ask yourself:

- does this solve a real workflow problem?
- does it help local users?
- does it respect the Neo Library / Neo Studio split?
- does it add clarity instead of chaos?
- is the added complexity worth it?

If the answer is mostly “no,” it probably should not be merged.

---

## Code of conduct

Be respectful, direct, and constructive.

That means:

- criticize ideas, not people
- keep feedback specific
- do not be hostile
- do not spam
- do not dump low-effort AI-generated changes without checking them
- do not submit copied code you do not have the right to contribute

This is a practical project. Act like a builder, not a chaos gremlin.

---

## License

By contributing, you agree that your contributions will be released under the same license as the project.

See the `LICENSE` file for details.

---

## Final note

Neo Studio Suite is being built around actual local creative workflows.

The best contributions are the ones that make the tool more stable, more useful, and less messy for real people doing real work.

Thanks for helping make it better.
