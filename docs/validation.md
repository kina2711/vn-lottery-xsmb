# Validation Notes

Validation date: 2026-07-13

## Commands Run

```text
py -3.13 -m pytest -p no:cacheprovider tests
py -3.13 -m pytest -p no:cacheprovider --cov=vn_lottery_xsmb tests
py -3.13 -m ruff check src tests --no-cache
py -3.13 -m mypy src\vn_lottery_xsmb
```

Results:

- Tests: 32 passed.
- Coverage: 85% total line coverage.
- Ruff: all checks passed.
- Mypy: no issues found in 23 source files.

## Notes

- Tests run with Python 3.13 because it is the available Python runtime satisfying the project requirement of Python 3.12+.
- `python` on this workstation resolves to Python 3.10 and does not have pytest installed.
- Pytest cache was disabled because the sandboxed Windows environment denied cache/temp cleanup in some paths.
- Coverage was run outside the filesystem sandbox after the coverage plugin was denied permission to rename `.coverage` files inside the sandbox.
- BeautifulSoup/lxml emitted a deprecation warning from the installed parser stack; it does not affect project assertions.
