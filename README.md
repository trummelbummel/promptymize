# auto-prompt

[![Release](https://img.shields.io/github/v/release/trummelbummel/auto-prompt)](https://img.shields.io/github/v/release/trummelbummel/auto-prompt)
[![Build status](https://img.shields.io/github/actions/workflow/status/trummelbummel/auto-prompt/main.yml?branch=main)](https://github.com/trummelbummel/auto-prompt/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/trummelbummel/auto-prompt/branch/main/graph/badge.svg)](https://codecov.io/gh/trummelbummel/auto-prompt)
[![Commit activity](https://img.shields.io/github/commit-activity/m/trummelbummel/auto-prompt)](https://img.shields.io/github/commit-activity/m/trummelbummel/auto-prompt)
[![License](https://img.shields.io/github/license/trummelbummel/auto-prompt)](https://img.shields.io/github/license/trummelbummel/auto-prompt)

All models have specific prompt guidelines. This project enables automatic adaptation of prompts to best practices based on documentation and advanced prompt techniques from the literature.

- **Github repository**: <https://github.com/trummelbummel/auto-prompt/>
- **Documentation** <https://trummelbummel.github.io/auto-prompt/>

## Scrape a documentation page

This project includes a small CLI that fetches a documentation page, converts the main content to Markdown, and writes it to `resources/<foldername>/`.

```bash
uv run auto-prompt-scrape \
  "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices" \
  "claude_prompting_best_practices"
```

Some docs sites are rendered with JavaScript. By default, the scraper will fall back to a headless browser (Playwright) if the initial HTML looks like an unrendered “Loading…” shell. The first time you use this mode you may need:

```bash
uv run playwright install chromium
```

Output files:

- `resources/<foldername>/page.md`
- `resources/<foldername>/raw.html`
- `resources/<foldername>/meta.json`

## Web scraper to `resources/context/` (text-only + HTML)

There is also a web scraper under `src/scraper/` that writes **text-only** content to `page.md` and the raw HTML to `source.html` under `resources/context/<folder_name>/`.

Single target:

```bash
uv run auto-prompt-web-scrape one "https://example.com/docs/page" "my_folder"
```

Batch mode from YAML:

```bash
uv run auto-prompt-web-scrape batch scraper_targets.yaml
```

YAML format:

```yaml
targets:
  - folder_name: my_folder
    url: https://example.com/docs/page
```

## Getting started with your project

### 1. Create a New Repository

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:trummelbummel/auto-prompt.git
git push -u origin main
```

### 2. Set Up Your Development Environment

Then, install the environment and the pre-commit hooks with

```bash
make install
```

This will also generate your `uv.lock` file

### 3. Run the pre-commit hooks

Initially, the CI/CD pipeline might be failing due to formatting issues. To resolve those run:

```bash
uv run pre-commit run -a
```

### 4. Commit the changes

Lastly, commit the changes made by the two steps above to your repository.

```bash
git add .
git commit -m 'Fix formatting issues'
git push origin main
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-uv/features/codecov/).

## Releasing a new version



---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
