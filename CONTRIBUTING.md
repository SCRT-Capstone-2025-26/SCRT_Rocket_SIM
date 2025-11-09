# Contributing Guide

*SCRT Rocket Simulation (SCRT_Rocket_SIM)*
*Owner:* SCRT Capstone Team (Forrest Felsch, Kai Turner, Noah Unger-Schulz, Zane Othman-Gomez)

This guide explains how to set up your environment, contribute code, and ensure all submissions meet the team’s **Definition of Done (DoD)** and **quality standards**.

---

## Code of Conduct

All contributors must follow the project’s Code of Conduct.

* Treat others respectfully and professionally in all discussions and code reviews.
* Escalate behavioral issues to the Sprint Lead or course TA if unresolved.
* Report Code of Conduct violations by messaging the current Sprint Lead via Discord DM.

---

## Getting Started

### Prerequisites

* **Python 3.11+**
* **Git** and a GitHub account within the `SCRT-Capstone-2025-26` organization
* **pip** for dependency management
* **Ruff** for linting and formatting
* **pytest** for testing

### Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/SCRT-Capstone-2025-26/SCRT_Rocket_SIM.git
cd SCRT_Rocket_SIM

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run tests to confirm setup
pytest
```

### Environment Variables / Secrets

* Do **not** commit API keys or passwords.
* Store credentials in a local `.env` file and reference it in code via `dotenv`.
* Secrets for CI/CD are managed via **GitHub Actions Secrets** (accessible only to maintainers).

---

## Branching & Workflow

We follow a **feature-branch workflow** built on a stable `main` branch.

* **Default Branch:** `main`

### Workflow Summary

1. Create a feature branch off `main`.
2. Implement and locally test your change.
3. Run `ruff` and `pytest` before committing.
4. Open a **Pull Request (PR)** to `main`.
5. Another team member must review and approve before merging.
6. Rebase (not merge) your branch before submitting the PR to keep history clean.

---

## Issues & Planning

* Use **GitHub Issues** for all new work items and bugs.
* Apply one or more of the following labels:

  * `feature`, `bug`, `documentation`, `testing`, `discussion`
* Include:

  * Summary of issue
  * Expected vs. actual behavior
  * Steps to reproduce (if applicable)
  * Acceptance criteria
* Issues are assigned during **weekly team meetings** or by the **Sprint Lead**.

---

## Commit Messages

We use the [**Conventional Commits**](https://www.conventionalcommits.org/en/v1.0.0/) convention for clear history and automated changelog generation.

**Format:**

```
<type>: <description>

<optional body>
```

**Types:**

* `feat`: new feature
* `fix`: bug fix
* `docs`: documentation changes
* `style`: code style / formatting
* `refactor`: code refactor (no functional change)
* `test`: adding or updating tests
* `chore`: maintenance / build changes

**Examples:**

```
feat: add aerodynamic stability model

---

test: correct pytest workflow path

We moved the workflow folder as part of a previous refactor (see PR #X),
but forgot to update the path in file.example.

---

docs: clarify setup instructions
```

Reference issues using `#<issue-number>` when applicable.

---

## Code Style, Linting & Formatting

We use **Ruff** for linting and code formatting.

* Run checks before committing:

  ```bash
  ruff check .
  ```
* Auto-fix lint errors:

  ```bash
  ruff check . --fix
  ```

All code must follow **PEP8** conventions and use **type hints** where possible.

---

## Testing

Testing ensures code reliability and performance for the simulation.

* Tests live in the `/tests` directory.
* Framework: **pytest**
* Required coverage: **≥90%**

### Commands

```bash
# Run all tests
pytest
```

All new or modified code **must include tests** that verify expected behavior and edge cases.

---

## Pull Requests & Reviews

Before submitting a PR:

1. Ensure all tests pass locally.
2. Confirm CI status checks are passing.
3. Ensure documentation and type hints are updated.
4. Include a clear PR description referencing related issue(s).

**PR Requirements**

* At least **one reviewer approval** required
* All **CI checks** must pass before merge
* **PR size guideline:** Prefer ≤ 400 lines changed; large PRs must be discussed before submission

**Reviewer Expectations**

* Check readability, correctness, and adherence to DoD.
* Provide constructive, respectful feedback.
* Approve only when all checks are met.

---

## CI/CD

We use **GitHub Actions** for Continuous Integration.

* Workflow files: `.github/workflows/`
* Required Jobs (must pass before merge):

  * **Linting:** `ruff`
  * **Testing:** `pytest`
* CI logs available via the **Actions tab** on GitHub.
* Reruns are permitted only by the Sprint Lead or repo admin.

---

## Security & Secrets

* Never hard-code credentials or tokens.
* Store sensitive values in `.env` (local) or GitHub Actions secrets (CI).
* Report security vulnerabilities directly to **Noah Unger-Schulz** via email or private Discord message.
* Dependencies are regularly scanned using **GitHub Dependabot**.

---

## Documentation Expectations

When contributing, update documentation as part of your PR:

* **README.md** for setup or usage changes
* **docs/** directory for architecture and design updates
* **CHANGELOG.md** for user-facing changes
* **Docstrings:** Required for all new functions and classes

---

## Release Process

Versioning follows **Semantic Versioning (SemVer)**:
`MAJOR.MINOR.PATCH`

### Steps

1. Ensure all CI checks pass on `main`.
2. Update `CHANGELOG.md` and version number in `pyproject.toml`.
3. Tag the release, e.g.:

   ```bash
   git tag -a v1.2.0 -m "Stable rocket simulation release"
   git push origin v1.2.0
   ```
4. Verify release build artifacts (if applicable).
5. Rollback process: revert via `git revert` or restore the last stable tag.

---

## Support & Contact

For questions, reach out to the following (team email preferred):

* **Team Contact:** Noah Unger-Schulz – [ungerscn@oregonstate.edu](mailto:ungerscn@oregonstate.edu)
* **Partner Contact:** Cody Eutsler

---

### ✅ Quick Reference Summary

| Category                 | Required Tools/Checks | Command              |
| ------------------------ | --------------------- | -------------------- |
| **Linting**              | Ruff                  | `ruff check .`       |
| **Formatting**           | Ruff (auto-fix)       | `ruff check . --fix` |
| **Testing**              | pytest                | `pytest`             |
| **CI/CD**                | GitHub Actions        | Auto-run on PR       |
| **Review Requirement**   | ≥1 approval           | via GitHub PR        |
| **Coverage Requirement** | ≥90%                  | `pytest --cov`       |

---

### Guidelines Reviewed and Approved by:
* Zane Othman-Gomez
* Forrest Felsch
* Kai Turner
* Noah Unger-Schulz
