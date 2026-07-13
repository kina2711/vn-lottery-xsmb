from pathlib import Path

from vn_lottery_xsmb.parser.html_parser import LotteryHtmlParser
from vn_lottery_xsmb.parser.normalizer import normalize_draw
from vn_lottery_xsmb.storage.models import SourceRecord


def test_normalizer_creates_prize_entries_and_hash() -> None:
    html = Path("tests/fixtures/draw_valid.html").read_text(encoding="utf-8")
    raw = LotteryHtmlParser().parse(html)

    draw = normalize_draw(
        raw,
        SourceRecord(source_name="fixture", source_url="https://example.test/2026-07-13"),
    )

    assert draw.content_hash
    assert draw.prizes[0].last_two_digits == "45"
    assert len(draw.prizes) == 7
