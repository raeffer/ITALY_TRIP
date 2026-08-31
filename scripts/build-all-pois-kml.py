#!/usr/bin/env python3
"""Build one Organic Maps bookmark file from the 21 audited daily KMLs."""

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
MAPS = ROOT / "assets" / "maps"
OUTPUT = MAPS / "italy-trip-all-pois.kml"
KML_NAMESPACE = "http://www.opengis.net/kml/2.2"
EXPECTED_POI_COUNT = 301

ET.register_namespace("", KML_NAMESPACE)


def qname(name: str) -> str:
    return f"{{{KML_NAMESPACE}}}{name}"


def main() -> None:
    root = ET.Element(qname("kml"))
    document = ET.SubElement(root, qname("Document"))
    ET.SubElement(document, qname("name")).text = "Italy Road Trip — All 301 POIs"
    ET.SubElement(document, qname("description")).text = (
        "All audited points from the 21-day Italy Road Trip Companion. "
        "Bookmark names begin with the full-trip day and daily marker number."
    )

    count = 0
    for day in range(1, 22):
        source = MAPS / f"day{day}-pois.kml"
        placemarks = ET.parse(source).findall(f".//{qname('Placemark')}")
        for placemark in placemarks:
            combined = deepcopy(placemark)
            name = combined.find(qname("name"))
            if name is None or not name.text:
                raise ValueError(f"Placemark without a name in {source}")
            name.text = f"D{day:02d}-{name.text}"
            document.append(combined)
            count += 1

    if count != EXPECTED_POI_COUNT:
        raise ValueError(f"Expected {EXPECTED_POI_COUNT} POIs, found {count}")

    ET.indent(root, space="  ")
    ET.ElementTree(root).write(OUTPUT, encoding="UTF-8", xml_declaration=True)
    print(f"Wrote {OUTPUT} ({count} POIs)")


if __name__ == "__main__":
    main()
