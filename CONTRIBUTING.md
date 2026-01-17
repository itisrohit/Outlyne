# Contributing to Outlyne

First off, thank you for considering contributing to Outlyne. It is people like you that make the open-source community such an amazing place to learn, inspire, and create.

## Tech Stack & Prerequisites

Before you start, ensure you have the following installed:
- **[Docker Desktop](https://www.docker.com/)**: For containerization.
- **[Bun](https://bun.sh/)**: For frontend tooling and task running.
- **[uv](https://github.com/astral-sh/uv)**: For Python dependency management.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/your-username/Outlyne.git
    cd Outlyne
    ```
3.  **Install dependencies**:
    ```bash
    # Install Python dependencies
    uv sync
    
    # Install Web dependencies
    cd web && bun install && cd ..
    ```
4.  **Run the development server**:
    ```bash
    # Starts both API and Web frontend
    bun run dev
    ```

## Development Guidelines

### Development Workflow
1.  Create a new branch from `main`:
    ```bash
    git checkout -b feature/my-amazing-feature
    # or
    git checkout -b fix/annoying-bug
    ```
2.  Make your changes.
3.  **Verify your changes** before committing.

### Code Style & Linting
We enforce strict linting to maintain code quality. Please run these commands before pushing:

**Python (Backend):**
```bash
# Linting (Ruff + MyPy)
uv run ruff check .
uv run mypy .

# Formatting
uv run ruff format .
```

**TypeScript (Frontend):**
```bash
# Linting & Formatting (Biome)
cd web
bun run lint
bun run lint:fix
```

### Commit Messages
We follow the **[Conventional Commits](https://www.conventionalcommits.org/)** specification.

- `feat: ...` for a new feature
- `fix: ...` for a bug fix
- `docs: ...` for documentation changes
- `style: ...` for visual updates (CSS, etc.)
- `refactor: ...` for code restructuring
- `chore: ...` for maintenance tasks

**Example:**
> `feat(vision): add support for CLIP-L/14 model`

## Submission Guidelines

### Reporting Bugs
- **Search existing issues** to avoid duplicates.
- Open a new issue with a clear title.
- Include:
    - **Steps to reproduce**
    - **Expected behavior**
    - **Actual behavior**
    - **Screenshots** (if applicable)
    - **Environment details** (OS, Docker version, etc.)

### Pull Requests (PRs)
1.  Ensure your code passes all linting tests.
2.  Update documentation if you changed any behavior.
3.  Push to your fork and submit a PR to the `main` branch.
4.  **PR Title:** Use the Conventional Commits format.
5.  **PR Description:** Clearly describe *what* you changed and *why*. Link to related issues (e.g., `Closes #123`).

---

**Happy Coding!** 🌿
