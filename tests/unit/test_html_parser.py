from datetime import date
from pathlib import Path

import pytest

from vn_lottery_xsmb.parser.html_parser import LotteryHtmlParser


def test_html_parser_extracts_draw() -> None:
    html = Path("tests/fixtures/draw_valid.html").read_text(encoding="utf-8")

    draw = LotteryHtmlParser().parse(html)

    assert draw.draw_date == date(2026, 7, 13)
    assert draw.region == "mien-bac"
    assert draw.prizes[0].prize_group == "special"
    assert draw.prizes[0].values == ["12345"]


def test_html_parser_rejects_malformed_content() -> None:
    html = Path("tests/fixtures/draw_malformed.html").read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        LotteryHtmlParser().parse(html)
