# Workflow & Deployment Strategy

This document outlines the end-to-end workflow, from local development to production deployment.

### Git Branching Strategy

We will adopt a Git Flow-based branching model to maintain a clean and deployable `main` branch at all times.

- **`main`**: This branch represents the latest production-ready code. It is protected. Direct commits are forbidden. Code only gets here via a Pull Request from the `develop` branch.
- **`develop`**: This is the primary integration branch for all completed features. It should be stable, but it's where we integrate work before a production release.
- **`feature/*`**: All new work (e.g., `feature/add-player-use-case`, `bugfix/telegram-timeout`) **must** be done on a feature branch created from `develop`.
- **Pull Requests (PRs)**: All merges into `develop` and `main` must be done via a Pull Request, which should require at least one review and passing all automated checks (tests, linting).

### Environments

- **`Local`**: The primary environment for all development and initial manual testing. The system must be fully runnable on a local machine.
- **`Production`**: The live, user-facing application will be hosted on **Render**.

### CI/CD Pipeline

- **Automation Goal**: To automate testing and deployment, ensuring reliability and speed.
- **Trigger**: The CI/CD pipeline will be automatically triggered upon a successful merge into the `main` branch.
- **Pipeline Steps**:
  1.  **Checkout Code**: Pull the latest from the `main` branch.
  2.  **Run Quality Checks**: Execute the entire `pytest` test suite and run `ruff` for linting. The pipeline fails if any check fails.
  3.  **Build**: Build a production-ready artifact (e.g., a Docker image).
  4.  **Deploy**: Automatically push the new build to our hosting service, **Render**, to update the live application.