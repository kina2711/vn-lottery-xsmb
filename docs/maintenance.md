# Maintenance Guide

## Source Markup Changes

Parser tests use independently authored fixture HTML. When a public source changes markup, update parser selectors in `src/vn_lottery_xsmb/parser/html_parser.py`, add a new fixture that captures the new structure, and keep existing fixtures for regression coverage.

## Failed Collection

Check CLI output and logs for timeout, retry, HTTP status, parse failure, or validation errors. Existing CSV data should remain readable after failures.

## Regenerating Artifacts

```text
vn-lottery analyze
vn-lottery report
vn-lottery visualize
```

For the scheduled path:

```text
vn-lottery run-daily
```

## Authorship Rule

Do not copy code, comments, function names, classes, workflows, fixtures, or documentation from public repositories. Ideas may be treated as domain context only.
