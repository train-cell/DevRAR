# Contributing

Start with `AGENTS.md`, `PLAN.md`, the product and design briefs, and the report
schema. Keep source compatibility claims tied to reproducible synthetic fixtures.
Never attach private transcripts, database files, access tokens or generated
personal reports to an issue or pull request.

Use Python 3.11+, create a virtual environment, then run:

~~~console
python -m pip install -e ".[dev,compressed]"
python -m pytest -q -p no:cacheprovider --cov=devrar --cov-fail-under=100
python -m ruff check src tests
python -m build
~~~

For browser verification:

~~~console
python -m pip install -e ".[browser]"
python -m playwright install chromium
~~~

Set `DEVRAR_BROWSER_TESTS=1` in your shell, then run
`python -m pytest -q tests/test_browser.py -p no:cacheprovider`.
The suite uses isolated headless Chromium, synthetic data and local files. It
writes ignored screenshots and video under `artifacts/`.

Implementation identifiers use Greeklish under the project's conventions;
public UI and usage docs use English. Functions need descriptive docstrings.
Add meaningful regression tests for parsing, arithmetic, attribution and privacy
changes. UI changes need rendered desktop/mobile checks, including reduced motion.

Submit a feature branch and pull request. Maintainers decide when to merge.
For a wrong count, provide the smallest synthetic reproduction, source shape,
DevRAR version, timezone/filters and expected versus actual totals.
