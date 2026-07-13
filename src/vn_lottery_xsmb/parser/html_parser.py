from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from bs4 import BeautifulSoup, Tag


@dataclass(frozen=True)
class RawPrize:
    prize_group: str
    values: list[str]


@dataclass(frozen=True)
class RawDraw:
    draw_date: date
    region: str
    prizes: list[RawPrize]


class LotteryHtmlParser:
    def parse(self, html: str) -> RawDraw:
        soup = BeautifulSoup(html, "lxml")
        root = soup.select_one("[data-date]")
        if root is not None:
            return self._parse_data_attribute_fixture(root)
        return self._parse_minh_ngoc_text(soup)

    def _parse_data_attribute_fixture(self, root: Tag) -> RawDraw:
        draw_date = date.fromisoformat(root["data-date"])
        region = root.get("data-region", "mien-bac")
        prizes: list[RawPrize] = []
        for row in root.select("[data-prize]"):
            group = row.get("data-prize", "").strip()
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            text = " ".join(cells[1:] if len(cells) > 1 else cells)
            values = re.findall(r"\d+", text)
            if group and values:
                prizes.append(RawPrize(group, values))
        if not prizes:
            raise ValueError("could not find prize values in source content")
        return RawDraw(draw_date, region, prizes)

    def _parse_minh_ngoc_text(self, soup: BeautifulSoup) -> RawDraw:
        text = soup.get_text("\n", strip=True)
        date_match = re.search(r"Ngày:\s*(\d{2})/(\d{2})/(\d{4})", text)
        if not date_match:
            date_match = re.search(r"Miền Bắc\s*-\s*(\d{2})/(\d{2})/(\d{4})", text)
        if not date_match:
            raise ValueError("could not find draw date in source content")

        draw_date = date(
            int(date_match.group(3)),
            int(date_match.group(2)),
            int(date_match.group(1)),
        )
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        labels = {
            "Giải ĐB": ("special", 1),
            "Giải nhất": ("first", 1),
            "Giải nhì": ("second", 2),
            "Giải ba": ("third", 6),
            "Giải tư": ("fourth", 4),
            "Giải năm": ("fifth", 6),
            "Giải sáu": ("sixth", 3),
            "Giải bảy": ("seventh", 4),
        }
        prizes: list[RawPrize] = []
        for index, line in enumerate(lines):
            if line not in labels:
                continue
            group, expected = labels[line]
            values: list[str] = []
            cursor = index + 1
            while cursor < len(lines) and len(values) < expected:
                candidate = lines[cursor]
                if candidate in labels or candidate in {"Normal", "2 số", "3 Số", "Xem Bảng Loto"}:
                    break
                if re.fullmatch(r"\d{2,5}", candidate):
                    values.append(candidate)
                cursor += 1
            if values:
                prizes.append(RawPrize(group, values))
        if not prizes:
            raise ValueError("could not find prize values in source content")
        return RawDraw(draw_date, "mien-bac", prizes)
