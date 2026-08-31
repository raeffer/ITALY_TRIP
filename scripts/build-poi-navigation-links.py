#!/usr/bin/env python3
"""Add stable destination actions to every numbered POI on all day pages."""

import argparse
from html import unescape
from pathlib import Path
import re
from urllib.parse import quote
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
KML_NAMESPACE = {"k": "http://www.opengis.net/kml/2.2"}
EXPECTED_POI_COUNT = 301
LEGEND_PATTERN = re.compile(r'<div class="poi-legend".*?</ol>', re.DOTALL)
ITEM_PATTERN = re.compile(r"<li\b[^>]*>.*?</li>", re.DOTALL)
NAME_PATTERN = re.compile(r"<b>(.*?)</b>", re.DOTALL)
GPS_PATTERN = re.compile(r"GPS:\s*(?:approx\.\s*)?(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)")
NAV_PATTERN = re.compile(r'<br><span class="poi-navigation-links web-only">.*?</span>')
TAG_PATTERN = re.compile(r"<[^>]+>")


def navigation_html(name: str, lat: str, lon: str) -> str:
    organic_name = quote(name, safe="")
    organic = f"https://omaps.app/map?v=1&amp;ll={lat},{lon}&amp;n={organic_name}"
    google = (
        "https://www.google.com/maps/dir/?api=1"
        f"&amp;destination={lat}%2C{lon}&amp;dir_action=navigate"
    )
    return (
        '<br><span class="poi-navigation-links web-only">'
        f'<a class="map-link" href="{organic}" target="_blank" rel="noopener" '
        'title="Open in Organic Maps, then tap Route to">Organic Maps — tap Route to</a> '
        f'<a class="map-fallback-link" href="{google}" target="_blank" rel="noopener" '
        'title="Navigate from your current location in Google Maps">Google — navigate now</a>'
        "</span>"
    )


def update_item(item: str) -> str:
    item = NAV_PATTERN.sub("", item)
    gps = GPS_PATTERN.search(item)
    name_match = NAME_PATTERN.search(item)
    if gps is None or name_match is None:
        raise ValueError(f"Numbered POI is missing a name or GPS value: {item[:120]}")
    name = " ".join(unescape(TAG_PATTERN.sub("", name_match.group(1))).split())
    nav = navigation_html(name, gps.group(1), gps.group(2))
    return item.replace("</small>", f"{nav}</small>", 1)


def expected_page(page: Path) -> tuple[str, int]:
    source = page.read_text()
    legend = LEGEND_PATTERN.search(source)
    if legend is None:
        raise ValueError(f"No numbered POI legend found in {page}")
    updated_legend, count = ITEM_PATTERN.subn(lambda match: update_item(match.group(0)), legend.group(0))
    expected_count = len(
        ET.parse(ROOT / f"assets/maps/{page.stem}-pois.kml").findall(".//k:Placemark", KML_NAMESPACE)
    )
    if count != expected_count:
        raise ValueError(f"{page}: expected {expected_count} POIs, updated {count}")
    return source[: legend.start()] + updated_legend + source[legend.end() :], count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if any page needs regeneration")
    args = parser.parse_args()
    changed = []
    total = 0
    for day in range(1, 22):
        page = ROOT / f"days/day{day}.html"
        expected, count = expected_page(page)
        total += count
        if expected != page.read_text():
            changed.append(page)
            if not args.check:
                page.write_text(expected)

    if total != EXPECTED_POI_COUNT:
        raise ValueError(f"Expected {EXPECTED_POI_COUNT} POIs, found {total}")
    if args.check and changed:
        raise SystemExit("POI navigation links need regeneration: " + ", ".join(str(path) for path in changed))
    action = "Checked" if args.check else "Updated"
    print(f"{action} {total} POI navigation actions across 21 day pages")


if __name__ == "__main__":
    main()
