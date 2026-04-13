# Branching Conventions

## Branch Structure

- **`main`** — Production-ready code. Only merged into via PR from `develop`.
- **`develop`** — Integration branch. All feature work merges here first.

## Branch Naming

Create branches off `develop` using these prefixes:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/streeteasy-scraper` |
| `fix/` | Bug fixes | `fix/duplicate-listings` |
| `chore/` | Config, deps, tooling | `chore/add-linting` |
| `refactor/` | Code restructuring | `refactor/normalize-data-models` |

## Workflow

1. Create a branch off `develop`: `git checkout -b feature/my-feature develop`
2. Do your work, commit with clear messages.
3. Open a PR into `develop`.
4. Once `develop` is stable, PR into `main` for release.
