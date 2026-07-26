#!/usr/bin/env python3
"""Generate static editorial route maps from OSM-derived map data."""

from __future__ import annotations

import argparse
import io
import math
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TILE_SIZE = 256
USER_AGENT = "ITALY_TRIP static route map generator"


DAY1 = {
    "output": ROOT / "assets/maps/day1-ravenna-route.png",
    "zoom": 10,
    "size": (1800, 1125),
    "padding_px": 120,
    "places": {
        "Start": (44.7100177, 11.2283615),
        "Ravenna walking core": (44.4205764, 12.1963122),
        "Ravenna parking": (44.4219, 12.1979),
        "B&B Casa Masoli": (44.4199737, 12.2003868),
        "Comacchio": (44.6958712, 12.1812500),
        "Manifattura dei Marinati": (44.6990038, 12.1752748),
        "Lagoon road": (44.6540, 12.2450),
    },
    "routes": {
        "recommended": {
            "color": "#1769d2",
            "width": 12,
            "coords": ["Start", "Ravenna walking core", "B&B Casa Masoli"],
        },
        "optional": {
            "color": "#d79a19",
            "width": 10,
            "coords": ["Start", "Comacchio", "Manifattura dei Marinati", "Ravenna walking core", "B&B Casa Masoli"],
        },
        "lagoon": {
            "color": "#c84f2c",
            "width": 8,
            "coords": ["Comacchio", "Lagoon road"],
            "dashed": True,
        },
    },
    "poi_clusters": {
        "ravenna": {
            "anchor": "Ravenna walking core",
            "numbers": list(range(2, 20)),
            "grid_offset": (150, -360),
            "columns": 3,
            "x_step": 64,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Matteo della Decima",
            "lat": 44.7100177,
            "lon": 11.2283615,
            "address": "San Matteo della Decima, 40017 San Giovanni in Persiceto BO, Italy",
            "type": "Start",
            "color": "#1769d2",
            "offset": (0, 0),
        },
        {
            "number": 2,
            "name": "Largo Giustiniano Parking",
            "lat": 44.42183,
            "lon": 12.19623,
            "address": "Largo Giustiniano, 48121 Ravenna RA, Italy",
            "type": "Parking",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 3,
            "name": "Basilica di San Vitale",
            "lat": 44.4205557,
            "lon": 12.1963864,
            "address": "Via San Vitale 17, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 4,
            "name": "Mausoleo di Galla Placidia",
            "lat": 44.4209827,
            "lon": 12.1971029,
            "address": "Via Giuliano Argentario 22, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 5,
            "name": "Domus dei Tappeti di Pietra",
            "lat": 44.421223,
            "lon": 12.195474,
            "address": "Via Gian Battista Barbiani 16, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 6,
            "name": "Museo Byron e del Risorgimento, Palazzo Guiccioli",
            "lat": 44.419629,
            "lon": 12.197836,
            "address": "Via Camillo Benso Cavour 54, 48121 Ravenna RA, Italy",
            "type": "Museum",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 7,
            "name": "Pasticceria Veneziana",
            "lat": 44.4194468,
            "lon": 12.1982703,
            "address": "Via Salara 15, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 8,
            "name": "B&B Casa Masoli",
            "lat": 44.4199737,
            "lon": 12.2003868,
            "address": "Via Girolamo Rossi 22, 48121 Ravenna RA, Italy",
            "type": "Accommodation",
            "color": "#2f2a26",
            "cluster": "ravenna",
        },
        {
            "number": 9,
            "name": "Erboristeria Giorgioni",
            "lat": 44.4188773,
            "lon": 12.1994528,
            "address": "Via IV Novembre 43, 48121 Ravenna RA, Italy",
            "type": "Shop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 10,
            "name": "Mercato Coperto",
            "lat": 44.418912,
            "lon": 12.199129,
            "address": "Piazza Andrea Costa 6, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 11,
            "name": "Gioielleria Lugaresi",
            "lat": 44.4179545,
            "lon": 12.1986896,
            "address": "Via Giacomo Matteotti 12, 48121 Ravenna RA, Italy",
            "type": "Shop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 12,
            "name": "Caffe Il Nazionale",
            "lat": 44.4175944,
            "lon": 12.1995888,
            "address": "Piazza del Popolo 28, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 13,
            "name": "Piazza del Popolo",
            "lat": 44.4177596,
            "lon": 12.1993185,
            "address": "Piazza del Popolo, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 14,
            "name": "Leonardi Dolciumi 1957",
            "lat": 44.417228,
            "lon": 12.200015,
            "address": "Via Pellegrino Matteucci 5, 48121 Ravenna RA, Italy",
            "type": "Shop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 15,
            "name": "Tomba di Dante",
            "lat": 44.4161585,
            "lon": 12.2009368,
            "address": "Via Dante Alighieri 9, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 16,
            "name": "Ca' de Ven",
            "lat": 44.4160938,
            "lon": 12.1999840,
            "address": "Via Corrado Ricci 24, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 17,
            "name": "Koko Mosaico",
            "lat": 44.416945,
            "lon": 12.2039917,
            "address": "Via di Roma 136, 48121 Ravenna RA, Italy",
            "type": "Optional stop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 18,
            "name": "Antica Trattoria Al Gallo 1909",
            "lat": 44.4207825,
            "lon": 12.1915981,
            "address": "Via Maggiore 89, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 19,
            "name": "Darsenale - Bizantina Brewpub",
            "lat": 44.423296,
            "lon": 12.212171,
            "address": "Via D'Alaggio 69, 48122 Ravenna RA, Italy",
            "type": "Optional food stop",
            "color": "#1769d2",
            "cluster": "ravenna",
        },
        {
            "number": 20,
            "name": "Comacchio",
            "lat": 44.6958712,
            "lon": 12.1812500,
            "address": "Centro storico, 44022 Comacchio FE, Italy",
            "type": "Optional stop",
            "color": "#d79a19",
            "offset": (-30, -34),
        },
        {
            "number": 21,
            "name": "Manifattura dei Marinati",
            "lat": 44.6990038,
            "lon": 12.1752748,
            "address": "Corso Giuseppe Mazzini 200, 44022 Comacchio FE, Italy",
            "type": "Museum / food heritage",
            "color": "#d79a19",
            "offset": (36, 28),
        },
        {
            "number": 22,
            "name": "Argine degli Angeli",
            "lat": 44.6540,
            "lon": 12.2450,
            "address": "Argine degli Angeli, Valli di Comacchio, 44029 Comacchio FE, Italy",
            "type": "Viewpoint",
            "color": "#c84f2c",
            "offset": (0, 0),
        },
    ],
    "poi_verification": {
        1: "Address and practical start point checked against municipal/mapping data for San Matteo della Decima.",
        2: "Parking existence/address verified from Comune di Ravenna parking guidance; coordinates from OpenStreetMap parking object for Largo Giustiniano.",
        3: "Address verified from Ravenna mosaics/tourism source; coordinates checked against OpenStreetMap/mapping data for Basilica di San Vitale arrival.",
        4: "Address verified from Ravenna mosaics/tourism source; coordinates checked against OpenStreetMap/mapping data for Mausoleo di Galla Placidia arrival.",
        5: "Address verified from Ravenna Citta del Mosaico/RavennAntica tourism data; coordinates checked against OpenStreetMap/mapping data for Domus entrance.",
        6: "Address verified from Musei Byron e del Risorgimento and Comune di Ravenna listings; coordinates checked against OpenStreetMap/mapping data for Palazzo Guiccioli.",
        7: "Address verified from Pasticceria Veneziana official site; coordinates checked against OpenStreetMap/mapping data for storefront arrival.",
        8: "Address verified from Casa Masoli official site; coordinates checked against OpenStreetMap/mapping data for guest arrival.",
        9: "Address verified against venue/mapping data; coordinates checked against OpenStreetMap/mapping data for storefront arrival.",
        10: "Address verified from Comune di Ravenna/Ravenna Turismo listings; coordinates checked against OpenStreetMap/mapping data for Mercato Coperto entrance.",
        11: "Address verified against venue/mapping data; coordinates checked against OpenStreetMap/mapping data for storefront arrival.",
        12: "Address verified against venue/mapping data; coordinates checked against OpenStreetMap/mapping data for cafe arrival.",
        13: "Address verified from Ravenna Turismo/Comune di Ravenna data for Piazza del Popolo; coordinates checked against OpenStreetMap/mapping data for the square.",
        14: "Address verified against venue/mapping data; coordinates checked against OpenStreetMap/mapping data for storefront arrival.",
        15: "Address verified from Ravenna Turismo official listing for Tomba di Dante; coordinates checked against OpenStreetMap/mapping data for the tomb.",
        16: "Address verified against venue/mapping data; coordinates checked against OpenStreetMap/mapping data for restaurant arrival.",
        17: "Address verified from Koko Mosaico official site and Ravenna Citta del Mosaico listing; coordinates checked against OpenStreetMap/mapping data for studio arrival.",
        18: "Address verified against venue/mapping data; coordinates checked against OpenStreetMap/mapping data for restaurant arrival.",
        19: "Address verified against Darsenale/mapping data; coordinates checked against OpenStreetMap/mapping data for brewpub arrival.",
        20: "Practical optional stop set to Comacchio historic centre; coordinates checked against OpenStreetMap/mapping data for centre arrival, not a generic province/town fallback.",
        21: "Address verified from Visit Comacchio and i Marinati di Comacchio official data; coordinates checked against OpenStreetMap/mapping data for Manifattura arrival.",
        22: "Practical viewpoint/trail access checked against OpenStreetMap/mapping data for Argine degli Angeli lagoon route.",
    },
}


def lonlat_to_global_px(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    lat_rad = math.radians(lat)
    scale = TILE_SIZE * 2**zoom
    x = (lon + 180.0) / 360.0 * scale
    y = (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * scale
    return x, y


def global_px_to_tile(px: float) -> int:
    return math.floor(px / TILE_SIZE)


def request_json(url: str) -> dict:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    return response.json()


def osrm_route(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{coords}?overview=full&geometries=geojson"
    )
    data = request_json(url)
    geometry = data["routes"][0]["geometry"]["coordinates"]
    return [(lat, lon) for lon, lat in geometry]


def fetch_tile(zoom: int, x: int, y: int) -> Image.Image:
    url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGB")


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_line(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], color: str, width: int, dashed: bool = False) -> None:
    if not dashed:
        draw.line(points, fill=color, width=width, joint="curve")
        return

    dash = 28
    gap = 18
    for start, end in zip(points, points[1:]):
        x1, y1 = start
        x2, y2 = end
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            continue
        dx = (x2 - x1) / length
        dy = (y2 - y1) / length
        cursor = 0
        while cursor < length:
            segment_end = min(cursor + dash, length)
            draw.line(
                [(x1 + dx * cursor, y1 + dy * cursor), (x1 + dx * segment_end, y1 + dy * segment_end)],
                fill=color,
                width=width,
            )
            cursor += dash + gap


def numbered_marker(draw: ImageDraw.ImageDraw, point: tuple[float, float], number: int, fill: str, font: ImageFont.ImageFont, marker_offset: tuple[int, int] = (0, 0)) -> None:
    x, y = point
    dx, dy = marker_offset
    marker_x = x + dx
    marker_y = y + dy
    if dx or dy:
        draw.line((x, y, marker_x, marker_y), fill=(47, 42, 38, 150), width=2)
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(47, 42, 38, 190), outline="#fffdf6", width=1)

    text = str(number)
    box_w = 58
    box_h = 46
    radius = 8
    box = (
        marker_x - box_w / 2,
        marker_y - box_h / 2,
        marker_x + box_w / 2,
        marker_y + box_h / 2,
    )
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline="#fffdf6", width=5)
    draw.rounded_rectangle(box, radius=radius, outline="#2f2a26", width=1)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        (marker_x - text_w / 2 - bbox[0], marker_y - text_h / 2 - bbox[1]),
        text,
        fill="#fffdf6",
        font=font,
    )


def draw_cluster_grid(
    draw: ImageDraw.ImageDraw,
    anchor: tuple[float, float],
    pois: list[dict],
    grid_origin: tuple[float, float],
    columns: int,
    x_step: int,
    y_step: int,
    font: ImageFont.ImageFont,
) -> None:
    anchor_x, anchor_y = anchor
    grid_x, grid_y = grid_origin
    rows = math.ceil(len(pois) / columns)
    connector_y = grid_y + y_step * (rows - 1) / 2

    draw.line((anchor_x, anchor_y, grid_x - 34, connector_y), fill=(47, 42, 38, 120), width=2)
    draw.ellipse((anchor_x - 7, anchor_y - 7, anchor_x + 7, anchor_y + 7), fill="#2f2a26", outline="#fffdf6", width=2)

    for index, poi in enumerate(pois):
        col = index % columns
        row = index // columns
        numbered_marker(
            draw,
            (grid_x + x_step * col, grid_y + y_step * row),
            poi["number"],
            poi["color"],
            font,
        )


def generate_day1() -> None:
    config = DAY1
    zoom = config["zoom"]

    route_geometries: dict[str, list[tuple[float, float]]] = {}
    all_geo_points = list(config["places"].values())
    for name, route in config["routes"].items():
        points = [config["places"][place] for place in route["coords"]]
        geometry = osrm_route(points)
        route_geometries[name] = geometry
        all_geo_points.extend(geometry)

    global_points = [lonlat_to_global_px(lat, lon, zoom) for lat, lon in all_geo_points]
    min_x = min(x for x, _ in global_points) - config["padding_px"]
    max_x = max(x for x, _ in global_points) + config["padding_px"]
    min_y = min(y for _, y in global_points) - config["padding_px"]
    max_y = max(y for _, y in global_points) + config["padding_px"]

    output_w, output_h = config["size"]
    bounds_w = max_x - min_x
    bounds_h = max_y - min_y
    target_ratio = output_w / output_h
    current_ratio = bounds_w / bounds_h
    if current_ratio > target_ratio:
        extra_h = bounds_w / target_ratio - bounds_h
        min_y -= extra_h / 2
        max_y += extra_h / 2
    else:
        extra_w = bounds_h * target_ratio - bounds_w
        min_x -= extra_w / 2
        max_x += extra_w / 2

    tile_min_x = global_px_to_tile(min_x)
    tile_max_x = global_px_to_tile(max_x)
    tile_min_y = global_px_to_tile(min_y)
    tile_max_y = global_px_to_tile(max_y)

    mosaic = Image.new("RGB", ((tile_max_x - tile_min_x + 1) * TILE_SIZE, (tile_max_y - tile_min_y + 1) * TILE_SIZE), "#eee8dc")
    for tx in range(tile_min_x, tile_max_x + 1):
        for ty in range(tile_min_y, tile_max_y + 1):
            tile = fetch_tile(zoom, tx, ty)
            mosaic.paste(tile, ((tx - tile_min_x) * TILE_SIZE, (ty - tile_min_y) * TILE_SIZE))

    left = int(min_x - tile_min_x * TILE_SIZE)
    top = int(min_y - tile_min_y * TILE_SIZE)
    right = int(max_x - tile_min_x * TILE_SIZE)
    bottom = int(max_y - tile_min_y * TILE_SIZE)
    image = mosaic.crop((left, top, right, bottom)).resize((output_w, output_h), Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 251, 241, 54))
    image = Image.alpha_composite(image, overlay)

    def to_canvas(lat: float, lon: float) -> tuple[float, float]:
        gx, gy = lonlat_to_global_px(lat, lon, zoom)
        return ((gx - min_x) / (max_x - min_x) * output_w, (gy - min_y) / (max_y - min_y) * output_h)

    draw = ImageDraw.Draw(image)
    for name in ("optional", "lagoon", "recommended"):
        route = config["routes"][name]
        points = [to_canvas(lat, lon) for lat, lon in route_geometries[name]]
        draw_line(draw, points, "#fffdf6", route["width"] + 8, route.get("dashed", False))
        draw_line(draw, points, route["color"], route["width"], route.get("dashed", False))

    number_font = load_font(25, bold=True)
    small_font = load_font(22)
    pois_by_number = {poi["number"]: poi for poi in config["pois"]}
    clustered_numbers: set[int] = set()
    for cluster in config.get("poi_clusters", {}).values():
        anchor = to_canvas(*config["places"][cluster["anchor"]])
        grid_origin = (anchor[0] + cluster["grid_offset"][0], anchor[1] + cluster["grid_offset"][1])
        cluster_pois = [pois_by_number[number] for number in cluster["numbers"]]
        draw_cluster_grid(
            draw,
            anchor,
            cluster_pois,
            grid_origin,
            cluster["columns"],
            cluster["x_step"],
            cluster["y_step"],
            number_font,
        )
        clustered_numbers.update(cluster["numbers"])

    for poi in config["pois"]:
        if poi["number"] in clustered_numbers:
            continue
        numbered_marker(
            draw,
            to_canvas(poi["lat"], poi["lon"]),
            poi["number"],
            poi["color"],
            number_font,
            poi.get("offset", (0, 0)),
        )

    draw.rounded_rectangle((32, 32, 615, 165), radius=16, fill=(255, 253, 246, 235), outline="#d8cab4", width=2)
    title_font = load_font(36, bold=True)
    draw.text((56, 50), "Day 1 orientation map", fill="#2f2a26", font=title_font)
    draw.line((60, 116, 160, 116), fill="#1769d2", width=10)
    draw.text((176, 102), "Recommended route", fill="#2f2a26", font=small_font)
    draw.line((60, 148, 160, 148), fill="#d79a19", width=9)
    draw.text((176, 134), "Comacchio alternative", fill="#2f2a26", font=small_font)

    attribution = "Map data and tiles © OpenStreetMap contributors · Routes from OSRM"
    attr_bbox = draw.textbbox((0, 0), attribution, font=small_font)
    draw.rounded_rectangle((output_w - attr_bbox[2] - 50, output_h - 58, output_w - 24, output_h - 20), radius=8, fill=(255, 253, 246, 230))
    draw.text((output_w - attr_bbox[2] - 38, output_h - 53), attribution, fill="#4d453f", font=small_font)

    config["output"].parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(config["output"], quality=94, optimize=True)
    print(config["output"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("day", choices=["day1"], help="Map configuration to generate")
    args = parser.parse_args()
    if args.day == "day1":
        generate_day1()


if __name__ == "__main__":
    main()
