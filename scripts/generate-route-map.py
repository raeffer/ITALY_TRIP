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
MAP_OUTPUT_SCALE = 2
ROUTE_ANTIALIAS_SCALE = 3
ROUTE_STROKE_SCALE = 0.50

MAP_PALETTE = {
    "route_primary": "#1A5FC4",
    "route_alternative": "#B88418",
    "route_optional": "#C65332",
    "marker_accommodation": "#163257",
    "ink": "#163257",
    "ink_soft": "#3D5A7A",
    "parchment": "#F7F4EE",
    "parchment_dark": "#EDE7D8",
    "warm_tile": "#EEE8DC",
    "white": "#FFFFFF",
}

ROUTE_PRIMARY = MAP_PALETTE["route_primary"]
ROUTE_ALTERNATIVE = MAP_PALETTE["route_alternative"]
ROUTE_OPTIONAL = MAP_PALETTE["route_optional"]
MARKER_ACCOMMODATION = MAP_PALETTE["marker_accommodation"]
MAP_INK = MAP_PALETTE["ink"]
MAP_INK_SOFT = MAP_PALETTE["ink_soft"]
MAP_PARCHMENT = MAP_PALETTE["parchment"]
MAP_PARCHMENT_DARK = MAP_PALETTE["parchment_dark"]
MAP_WARM_TILE = MAP_PALETTE["warm_tile"]
MAP_WHITE = MAP_PALETTE["white"]


def hex_to_rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    value = hex_color.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


DAY1 = {
    "title": "Day 1 orientation map",
    "output": ROOT / "assets/maps/day1-santorso-route.png",
    "zoom": 9,
    "size": (1800, 1125),
    "padding_px": 140,
    "places": {
        "Airport": (45.5035386, 12.3425797),
        "Padua": (45.4072498, 11.8752231),
        "Vicenza": (45.5469672, 11.5469575),
        "Asolo": (45.8022047, 11.9134666),
        "Santorso": (45.7251709, 11.4188371),
    },
    "routes": {
        "routeB": {
            "color": ROUTE_ALTERNATIVE,
            "width": 9,
            "coords": ["Airport", "Asolo", "Santorso"],
            "dashed": True,
        },
        "routeA": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Airport", "Padua", "Vicenza", "Santorso"],
        },
    },
    "route_order": ["routeB", "routeA"],
    "legend": [
        {"label": "Route A: Padua & Vicenza (recommended)", "color": ROUTE_PRIMARY},
        {"label": "Route B: Asolo alternative", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "padua": {
            "anchor": "Padua",
            "numbers": [2, 3, 4, 5, 22],
            "grid_offset": (-260, -70),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
        "vicenza": {
            "anchor": "Vicenza",
            "numbers": [7, 8, 9, 10, 11, 23],
            "grid_offset": (40, -180),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
        "asolo": {
            "anchor": "Asolo",
            "numbers": [12, 13, 14, 15],
            "grid_offset": (60, -150),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "santorso_stay": {
            "anchor": "Santorso",
            "numbers": [18, 19],
            "grid_offset": (-220, 60),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Venice Marco Polo Airport",
            "lat": 45.5035386,
            "lon": 12.3425797,
            "address": "Via Galileo Galilei 30/1, 30173 Venezia VE, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, -40),
        },
        {
            "number": 2,
            "name": "Prato della Valle",
            "lat": 45.3984714,
            "lon": 11.8751207,
            "address": "Prato della Valle, 35123 Padova PD, Italy",
            "type": "Stop",
            "color": ROUTE_PRIMARY,
            "cluster": "padua",
        },
        {
            "number": 3,
            "name": "Palazzo della Ragione & Sotto il Salone",
            "lat": 45.4072498,
            "lon": 11.8752231,
            "address": "Piazza delle Erbe, 35122 Padova PD, Italy",
            "type": "Market / historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "padua",
        },
        {
            "number": 4,
            "name": "Caffe Pedrocchi",
            "lat": 45.4076922,
            "lon": 11.8770946,
            "address": "Via VIII Febbraio 15, 35122 Padova PD, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "padua",
        },
        {
            "number": 5,
            "name": "Museo del Precinema",
            "lat": 45.4001955,
            "lon": 11.8759224,
            "address": "Prato della Valle 1/A, 35123 Padova PD, Italy",
            "type": "Hidden gem",
            "color": ROUTE_PRIMARY,
            "cluster": "padua",
        },
        {
            "number": 6,
            "name": "Pasticceria Biasetto",
            "lat": 45.3992373,
            "lon": 11.8857335,
            "address": "Via Jacopo Facciolati 12, 35126 Padova PD, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "offset": (30, 30),
        },
        {
            "number": 7,
            "name": "Piazza dei Signori & Basilica Palladiana",
            "lat": 45.5469672,
            "lon": 11.5469575,
            "address": "Piazza dei Signori, 36100 Vicenza VI, Italy",
            "type": "Stop",
            "color": ROUTE_PRIMARY,
            "cluster": "vicenza",
        },
        {
            "number": 8,
            "name": "Casa del Diavolo (Palazzo Porto)",
            "lat": 45.5454098,
            "lon": 11.5417460,
            "address": "Piazza Castello, 36100 Vicenza VI, Italy",
            "type": "Quirky stop",
            "color": ROUTE_PRIMARY,
            "cluster": "vicenza",
        },
        {
            "number": 9,
            "name": "Righetti",
            "lat": 45.5457569,
            "lon": 11.5443786,
            "address": "Piazza del Duomo 3, 36100 Vicenza VI, Italy",
            "type": "Lunch",
            "color": ROUTE_PRIMARY,
            "cluster": "vicenza",
        },
        {
            "number": 10,
            "name": "Osteria Il Cursore",
            "lat": 45.5446419,
            "lon": 11.5484005,
            "address": "Strada Pozzetto 10, 36100 Vicenza VI, Italy",
            "type": "Lunch / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "vicenza",
        },
        {
            "number": 11,
            "name": "Il Ceppo",
            "lat": 45.5490457,
            "lon": 11.5485427,
            "address": "Corso Andrea Palladio 196, 36100 Vicenza VI, Italy",
            "type": "Lunch / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "vicenza",
        },
        {
            "number": 12,
            "name": "Piazza Garibaldi, Fontana Maggiore & Rocca di Asolo",
            "lat": 45.8022047,
            "lon": 11.9134666,
            "address": "Piazza Garibaldi, 31011 Asolo TV, Italy",
            "type": "Stop",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "asolo",
        },
        {
            "number": 13,
            "name": "Casa dell'Arco & Cimitero di Sant'Anna",
            "lat": 45.8025475,
            "lon": 11.9102238,
            "address": "Via Canova, 31011 Asolo TV, Italy",
            "type": "Historic site",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "asolo",
        },
        {
            "number": 14,
            "name": "Caffe Centrale Cornaro",
            "lat": 45.8023434,
            "lon": 11.9135387,
            "address": "Piazza Garibaldi, 31011 Asolo TV, Italy",
            "type": "Food stop",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "asolo",
        },
        {
            "number": 15,
            "name": "Osteria al Bacaro",
            "lat": 45.8015364,
            "lon": 11.9143170,
            "address": "Via Robert Browning, 31011 Asolo TV, Italy",
            "type": "Lunch",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "asolo",
        },
        {
            "number": 16,
            "name": "La Trave",
            "lat": 45.8085576,
            "lon": 11.8872045,
            "address": "Via Bernardi 15, Pagnano, 31011 Asolo TV, Italy",
            "type": "Lunch / stronger pick",
            "color": ROUTE_ALTERNATIVE,
            "offset": (30, -30),
        },
        {
            "number": 17,
            "name": "Santuario di Sant'Orso & Monte Summano",
            "lat": 45.7396729,
            "lon": 11.3934015,
            "address": "Via Crucis, 36014 Santorso VI, Italy",
            "type": "Viewpoint / sanctuary",
            "color": ROUTE_PRIMARY,
            "offset": (-30, -34),
        },
        {
            "number": 18,
            "name": "Agriturismo da Mea",
            "lat": 45.7251709,
            "lon": 11.4188371,
            "address": "Via del Campo Romano 15, 36014 Santorso VI, Italy",
            "type": "Accommodation / my pick",
            "color": MARKER_ACCOMMODATION,
            "cluster": "santorso_stay",
        },
        {
            "number": 19,
            "name": "Agriturismo Cabrele",
            "lat": 45.7302203,
            "lon": 11.4017302,
            "address": "Via dei Prati 4, 36014 Santorso VI, Italy",
            "type": "Accommodation / alternate",
            "color": MARKER_ACCOMMODATION,
            "cluster": "santorso_stay",
        },
        {
            "number": 20,
            "name": "Hotel Villa I Pini",
            "lat": 45.6839,
            "lon": 11.3997,
            "address": "Via Schio 77, 36034 Malo VI, Italy",
            "type": "Accommodation / higher comfort",
            "color": MARKER_ACCOMMODATION,
            "offset": (30, 30),
        },
        {
            "number": 21,
            "name": "Schio Hotel",
            "lat": 45.7154538,
            "lon": 11.3772122,
            "address": "Via Campagnola, 36015 Schio VI, Italy",
            "type": "Accommodation / fallback",
            "color": MARKER_ACCOMMODATION,
            "offset": (-30, 30),
        },
        {
            "number": 22,
            "name": "Basilica di Sant'Antonio (Il Santo)",
            "lat": 45.4014584,
            "lon": 11.8808472,
            "address": "Piazza del Santo 11, 35123 Padova PD, Italy",
            "type": "Quirky stop",
            "color": ROUTE_PRIMARY,
            "cluster": "padua",
        },
        {
            "number": 23,
            "name": "The Turtles of Vicenza, Parco Querini",
            "lat": 45.5538006,
            "lon": 11.5471074,
            "address": "Viale Mariano Rumor, 36100 Vicenza VI, Italy",
            "type": "Quirky stop",
            "color": ROUTE_PRIMARY,
            "cluster": "vicenza",
        },
    ],
    "poi_verification": {
        1: "Coordinates from OpenStreetMap Nominatim aerodrome object for Aeroporto Marco Polo di Venezia.",
        2: "Coordinates from OpenStreetMap Nominatim for Prato della Valle square.",
        3: "Coordinates from OpenStreetMap Nominatim for Palazzo della Ragione / Piazza delle Erbe, the shared anchor for the market and clock tower.",
        4: "Coordinates from OpenStreetMap Nominatim for the Caffe Pedrocchi venue node on Via VIII Febbraio.",
        5: "Coordinates from OpenStreetMap Nominatim for Palazzo Angeli, Prato della Valle 1/A.",
        6: "Coordinates from OpenStreetMap Nominatim for the Pasticceria Biasetto storefront on Via Jacopo Facciolati; kept off the Padua cluster since it is a genuine ~2.3km detour from the historic centre, not on the walking route.",
        7: "Coordinates from OpenStreetMap Nominatim for Piazza dei Signori / Basilica Palladiana, Vicenza.",
        8: "Coordinates from OpenStreetMap Nominatim for Piazza Castello, the practical location of Palazzo Porto (Casa del Diavolo).",
        9: "Coordinates from OpenStreetMap Nominatim for Righetti, Piazza del Duomo 3.",
        10: "Coordinates from OpenStreetMap Nominatim for Osteria Il Cursore, Strada Pozzetto 10.",
        11: "Coordinates from OpenStreetMap Nominatim for Il Ceppo, Corso Andrea Palladio 196.",
        12: "Coordinates from OpenStreetMap Nominatim for Piazza Garibaldi / Fontana Maggiore, Asolo; the Rocca fortress itself sits at 45.8040154, 11.9169453, close enough to share this cluster anchor.",
        13: "Coordinates from OpenStreetMap Nominatim for Via Canova (Casa dell'Arco); Cimitero di Sant'Anna is a short walk south at 45.7999801, 11.9025197, approximated to this anchor for cluster legibility.",
        14: "Coordinates from OpenStreetMap Nominatim for the Piazza Garibaldi / Via Roma corner, Asolo.",
        15: "Coordinates from OpenStreetMap Nominatim for Via Robert Browning, Asolo; exact house number not independently confirmed, street-level pin.",
        16: "Coordinates from OpenStreetMap Nominatim for Via Bernardi 15, Pagnano d'Asolo (La Trave); kept off the Asolo cluster since it is a genuine ~2km drive from the centre.",
        17: "Coordinates from OpenStreetMap Nominatim for Santuario di Sant'Orso al Summano, Via Crucis, Santorso; used as the practical viewpoint anchor for the Monte Summano summit above it.",
        18: "Coordinates from OpenStreetMap Nominatim for Agriturismo da Mea, Via del Campo Romano 15, Santorso.",
        19: "Coordinates from OpenStreetMap Nominatim for Agriturismo Cabrele, Via dei Prati 4, Santorso; itinerary source also cited 'Via Crosarolle', treated as a paraphrase of the same address.",
        20: "Itinerary gave Via Schio 77, Malo; OpenStreetMap Nominatim could not resolve an exact house-number node on Via Schio, so this is an approximate street-level coordinate, not a verified building pin. Recommend re-geocoding directly from the hotel's own site before treating the pin as exact.",
        21: "Coordinates from OpenStreetMap Nominatim for Schio Hotel, Via Campagnola, Campassi, Schio.",
        22: "Coordinates from OpenStreetMap Nominatim for Basilica di Sant'Antonio, Piazza del Santo 11, Padova.",
        23: "Coordinates from OpenStreetMap Nominatim for Parco Querini, Viale Mariano Rumor, Vicenza.",
    },
}


DAY2 = {
    "title": "Day 2 orientation map",
    "output": ROOT / "assets/maps/day2-bassano-route.png",
    "zoom": 8,
    "size": (1800, 1500),
    "padding_px": 140,
    "places": {
        "Santorso": (45.7251709, 11.4188371),
        "Marostica": (45.7455140, 11.6552998),
        "Bassano": (45.7675140, 11.7311146),
        "Cittadella": (45.6507763, 11.7832170),
        "Montagnana": (45.2309674, 11.4686785),
        "SanMatteo": (44.7056327, 11.2283385),
        "Castelfranco": (44.6269459, 11.1195137),
    },
    "routes": {
        "montagnana_alt": {
            "color": ROUTE_OPTIONAL,
            "width": 8,
            "coords": ["Bassano", "Montagnana", "SanMatteo"],
            "dashed": True,
        },
        "castelfranco_alt": {
            "color": ROUTE_ALTERNATIVE,
            "width": 8,
            "coords": ["Cittadella", "Castelfranco"],
            "dashed": True,
        },
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Santorso", "Marostica", "Bassano", "Cittadella", "SanMatteo"],
        },
    },
    "route_order": ["montagnana_alt", "castelfranco_alt", "recommended"],
    "legend": [
        {"label": "Recommended route (via Cittadella)", "color": ROUTE_PRIMARY},
        {"label": "Castelfranco Emilia overnight alternative", "color": ROUTE_ALTERNATIVE, "dashed": True},
        {"label": "Montagnana walled-town alternative", "color": ROUTE_OPTIONAL, "dashed": True},
    ],
    "poi_clusters": {
        "bassano": {
            "anchor": "Bassano",
            "numbers": [5, 6, 7, 8, 9, 10, 11, 12, 22],
            "grid_offset": (40, -260),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
        "cittadella": {
            "anchor": "Cittadella",
            "numbers": [13, 14],
            "grid_offset": (-200, 40),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "montagnana": {
            "anchor": "Montagnana",
            "numbers": [15, 16, 17],
            "grid_offset": (60, 40),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Agriturismo da Mea, Santorso",
            "lat": 45.7251709,
            "lon": 11.4188371,
            "address": "Via del Campo Romano 15, 36014 Santorso VI, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (-30, 30),
        },
        {
            "number": 2,
            "name": "Piazza degli Scacchi & Castello Inferiore",
            "lat": 45.7455140,
            "lon": 11.6552998,
            "address": "Piazza degli Scacchi, 36063 Marostica VI, Italy",
            "type": "Optional stop",
            "color": ROUTE_PRIMARY,
            "offset": (-30, -34),
        },
        {
            "number": 3,
            "name": "Castello Superiore, Marostica",
            "lat": 45.7496871,
            "lon": 11.6523916,
            "address": "36063 Marostica VI, Italy",
            "type": "Optional / viewpoint",
            "color": ROUTE_PRIMARY,
            "offset": (0, -50),
        },
        {
            "number": 4,
            "name": "Osteria Madonnetta",
            "lat": 45.7448051,
            "lon": 11.6550451,
            "address": "Via Vajenti 21, 36063 Marostica VI, Italy",
            "type": "Optional lunch",
            "color": ROUTE_PRIMARY,
            "offset": (30, 30),
        },
        {
            "number": 5,
            "name": "Ponte Vecchio & Grapperia Nardini",
            "lat": 45.7675140,
            "lon": 11.7311146,
            "address": "36061 Bassano del Grappa VI, Italy",
            "type": "Essential stop",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 6,
            "name": "Museo degli Alpini",
            "lat": 45.7675730,
            "lon": 11.7306876,
            "address": "Via Angarano 2, 36061 Bassano del Grappa VI, Italy",
            "type": "Museum",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 7,
            "name": "Museo Civico di Bassano",
            "lat": 45.7664915,
            "lon": 11.7350946,
            "address": "Piazza Garibaldi 34, 36061 Bassano del Grappa VI, Italy",
            "type": "Optional museum",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 8,
            "name": "Tempio Ossario",
            "lat": 45.7636398,
            "lon": 11.7334538,
            "address": "Piazzale Luigi Cadorna, 36061 Bassano del Grappa VI, Italy",
            "type": "Hidden gem",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 9,
            "name": "Bottega del Pane Beltrame",
            "lat": 45.7667875,
            "lon": 11.7333642,
            "address": "Piazza Libertà 25, 36061 Bassano del Grappa VI, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 10,
            "name": "Danieli",
            "lat": 45.7668813,
            "lon": 11.7353468,
            "address": "Piazza Garibaldi 39, 36061 Bassano del Grappa VI, Italy",
            "type": "Coffee",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 11,
            "name": "Osteria Alla Caneva",
            "lat": 45.7678850,
            "lon": 11.7339387,
            "address": "Via Giacomo Matteotti 34, 36061 Bassano del Grappa VI, Italy",
            "type": "Lunch",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 12,
            "name": "Pasticceria Bolcato / Dolce Bassano",
            "lat": 45.7665000,
            "lon": 11.7355000,
            "address": "Piazzetta Zaine, 36061 Bassano del Grappa VI, Italy",
            "type": "Pastry",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
        {
            "number": 13,
            "name": "Cittadella — Camminamento di Ronda",
            "lat": 45.6507763,
            "lon": 11.7832170,
            "address": "Porta Bassano, 35013 Cittadella PD, Italy",
            "type": "Walled town / recommended",
            "color": ROUTE_PRIMARY,
            "cluster": "cittadella",
        },
        {
            "number": 14,
            "name": "L.AB Pastry & Coffee, Cittadella",
            "lat": 45.6364387,
            "lon": 11.7885209,
            "address": "Via Muri Bianchi, 35013 Cittadella PD, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "cittadella",
        },
        {
            "number": 15,
            "name": "Montagnana — Castello di San Zeno",
            "lat": 45.2309674,
            "lon": 11.4686785,
            "address": "35044 Montagnana PD, Italy",
            "type": "Walled town / alternative",
            "color": ROUTE_OPTIONAL,
            "cluster": "montagnana",
        },
        {
            "number": 16,
            "name": "Duomo di Santa Maria Assunta, Montagnana",
            "lat": 45.2335698,
            "lon": 11.4680736,
            "address": "Via San Giovanni 6, 35044 Montagnana PD, Italy",
            "type": "Historic site / alternative",
            "color": ROUTE_OPTIONAL,
            "cluster": "montagnana",
        },
        {
            "number": 17,
            "name": "Le Mura Bar-Gastronomia, Montagnana",
            "lat": 45.2335000,
            "lon": 11.4681000,
            "address": "35044 Montagnana PD, Italy",
            "type": "Food stop / alternative",
            "color": ROUTE_OPTIONAL,
            "cluster": "montagnana",
        },
        {
            "number": 18,
            "name": "Antica Trattoria Bonasoni",
            "lat": 44.7056327,
            "lon": 11.2283385,
            "address": "Via Cento, San Matteo della Decima, 40017 San Giovanni in Persiceto BO, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "offset": (70, 55),
        },
        {
            "number": 19,
            "name": "L'Ulivo B&B",
            "lat": 44.7159632,
            "lon": 11.2364802,
            "address": "Via delle Rose, San Matteo della Decima, 40017, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "offset": (70, -60),
        },
        {
            "number": 20,
            "name": "Boutique Hotel San Giovanni",
            "lat": 44.6353076,
            "lon": 11.1872698,
            "address": "San Giovanni in Persiceto, 40017 BO, Italy",
            "type": "Accommodation / alternate",
            "color": MARKER_ACCOMMODATION,
            "offset": (-80, 30),
        },
        {
            "number": 21,
            "name": "R&B Villa Tartaruga",
            "lat": 44.6269459,
            "lon": 11.1195137,
            "address": "Via Garzolé 41-43, Rastellino, 41013 Castelfranco Emilia MO, Italy",
            "type": "Accommodation / suggestion",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-100, 90),
        },
        {
            "number": 22,
            "name": "Castello degli Ezzelini",
            "lat": 45.7690102,
            "lon": 11.7325263,
            "address": "Piazza Castello Ezzelini, 36061 Bassano del Grappa VI, Italy",
            "type": "Quirky stop",
            "color": ROUTE_PRIMARY,
            "cluster": "bassano",
        },
    ],
    "poi_verification": {
        1: "Coordinates carried from verified Day 1 Agriturismo da Mea accommodation data.",
        2: "Coordinates from OpenStreetMap Nominatim for Piazza degli Scacchi, Marostica.",
        3: "Coordinates from OpenStreetMap Nominatim for Castello Superiore, Marostica.",
        4: "Coordinates from OpenStreetMap Nominatim for Osteria Madonnetta, Via Vajenti 21.",
        5: "Coordinates from OpenStreetMap Nominatim for Ponte Vecchio / Ponte degli Alpini, Bassano del Grappa; Grapperia Nardini and Poli Museo della Grappa both sit on the bridge itself and share this anchor.",
        6: "Coordinates from OpenStreetMap Nominatim for Museo degli Alpini, Ponte degli Alpini.",
        7: "Coordinates from OpenStreetMap Nominatim for Museo Civico di Bassano, Piazza Garibaldi 34.",
        8: "Coordinates from OpenStreetMap Nominatim for Tempio Ossario, Piazzale Luigi Cadorna.",
        9: "Coordinates from OpenStreetMap Nominatim for La Bottega del Pane Beltrame, Piazza Liberta 25.",
        10: "Itinerary gave Piazza Garibaldi 39; no OSM-indexed venue node found, approximated to the Piazza Garibaldi area.",
        11: "Itinerary gave Via Giacomo Matteotti 34; no OSM-indexed venue node found, approximated to the Via Matteotti street segment.",
        12: "Itinerary gave Piazzetta Zaine for both Bolcato and Dolce Bassano; no OSM-indexed venue node found for either, approximated to the Piazzetta Zaine area.",
        13: "Coordinates from OpenStreetMap Nominatim for Porta Bassano, Cittadella, the ticket-office start of the Camminamento di Ronda.",
        14: "Coordinates from OpenStreetMap Nominatim for Via Muri Bianchi, Cittadella; resolved to a general street area (San Donato locality), not an exact storefront node.",
        15: "Coordinates from OpenStreetMap Nominatim for Castel San Zeno, Montagnana.",
        16: "Coordinates from OpenStreetMap Nominatim for Via San Giovanni 6, Montagnana (Duomo di Santa Maria Assunta).",
        17: "Itinerary gave no independently verifiable address for Le Mura Bar-Gastronomia; approximated to the Montagnana historic-centre anchor near the Duomo.",
        18: "Coordinates from OpenStreetMap Nominatim for Antica Trattoria Bonasoni, Via Cento, San Matteo della Decima.",
        19: "Itinerary gave Via delle Rose, San Matteo della Decima; OpenStreetMap Nominatim could not resolve an exact house-number node, approximated to the Pieve di Decima/Via delle Rose street area.",
        20: "Itinerary gave only 'San Giovanni in Persiceto'; approximated to the town centre, not an exact building pin — recommend re-geocoding from the hotel's own site before treating as exact.",
        21: "Coordinates from OpenStreetMap Nominatim address geocode for Via Garzolè 41, Rastellino, Castelfranco Emilia (R&B Villa Tartaruga).",
        22: "Coordinates from OpenStreetMap Nominatim for Castello degli Ezzelini, Piazza Castello Ezzelini, Bassano del Grappa.",
    },
}


DAY3 = {
    "title": "Day 3 orientation map",
    "output": ROOT / "assets/maps/day3-persiceto-vignola-route.png",
    "zoom": 10,
    "size": (1800, 1350),
    "padding_px": 130,
    "places": {
        "Rastellino": (44.6269459, 11.1195137),
        "SanGiovanni": (44.6384848, 11.1874716),
        "Vignola": (44.4764050, 11.0101210),
    },
    "routes": {
        "sangiovanni_leg": {
            "color": ROUTE_PRIMARY,
            "width": 10,
            "coords": ["Rastellino", "SanGiovanni"],
        },
        "vignola_leg": {
            "color": ROUTE_ALTERNATIVE,
            "width": 9,
            "coords": ["Rastellino", "Vignola"],
            "dashed": True,
        },
    },
    "route_order": ["vignola_leg", "sangiovanni_leg"],
    "legend": [
        {"label": "San Giovanni in Persiceto leg", "color": ROUTE_PRIMARY},
        {"label": "Vignola leg", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "sgp": {
            "anchor": "SanGiovanni",
            "numbers": [2, 3, 4, 5, 10],
            "grid_offset": (40, -180),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "vignola": {
            "anchor": "Vignola",
            "numbers": [6, 7, 8],
            "grid_offset": (-220, 30),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "R&B Villa Tartaruga, Rastellino",
            "lat": 44.6269459,
            "lon": 11.1195137,
            "address": "Via Garzole 41-43, Rastellino, 41013 Castelfranco Emilia MO, Italy",
            "type": "Start / base",
            "color": ROUTE_PRIMARY,
            "offset": (0, 40),
        },
        {
            "number": 2,
            "name": "Piazza del Popolo & Collegiata",
            "lat": 44.6384848,
            "lon": 11.1874716,
            "address": "40017 San Giovanni in Persiceto BO, Italy",
            "type": "Stop",
            "color": ROUTE_PRIMARY,
            "cluster": "sgp",
        },
        {
            "number": 3,
            "name": "Piazzetta Betlemme",
            "lat": 44.6391987,
            "lon": 11.1901568,
            "address": "Via Betlemme, 40017 San Giovanni in Persiceto BO, Italy",
            "type": "Hidden gem / quirky",
            "color": ROUTE_PRIMARY,
            "cluster": "sgp",
        },
        {
            "number": 4,
            "name": "Pasticceria Dora",
            "lat": 44.6430230,
            "lon": 11.1857293,
            "address": "Via Crevalcore 1, 40017 San Giovanni in Persiceto BO, Italy",
            "type": "Coffee",
            "color": ROUTE_PRIMARY,
            "cluster": "sgp",
        },
        {
            "number": 5,
            "name": "Caffe Pasticceria Mimi",
            "lat": 44.6401562,
            "lon": 11.1869812,
            "address": "Via Guardia Nazionale 1, 40017 San Giovanni in Persiceto BO, Italy",
            "type": "Local speciality",
            "color": ROUTE_PRIMARY,
            "cluster": "sgp",
        },
        {
            "number": 6,
            "name": "Rocca di Vignola",
            "lat": 44.4764050,
            "lon": 11.0101210,
            "address": "Piazza dei Contrari 4, 41058 Vignola MO, Italy",
            "type": "Optional stop",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "vignola",
        },
        {
            "number": 7,
            "name": "Pasticceria Gollini",
            "lat": 44.4766,
            "lon": 11.0104,
            "address": "Piazza Garibaldi, 41058 Vignola MO, Italy",
            "type": "Optional / pastry",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "vignola",
        },
        {
            "number": 8,
            "name": "Acetaia La Ca dal Non",
            "lat": 44.4932594,
            "lon": 11.0134113,
            "address": "Via Ghiaurov 50-56, 41058 Vignola MO, Italy",
            "type": "Optional / reservation required",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "vignola",
        },
        {
            "number": 9,
            "name": "Monumento al Tortellino, Castelfranco Emilia",
            "lat": 44.5956559,
            "lon": 11.0531420,
            "address": "Piazza Garibaldi, 41013 Castelfranco Emilia MO, Italy",
            "type": "Cool / quirky",
            "color": ROUTE_PRIMARY,
            "offset": (30, -30),
        },
        {
            "number": 10,
            "name": "Statua di Re Gino",
            "lat": 44.6384848,
            "lon": 11.1874716,
            "address": "Piazza del Popolo, 40017 San Giovanni in Persiceto BO, Italy",
            "type": "Cool / quirky",
            "color": ROUTE_PRIMARY,
            "cluster": "sgp",
        },
    ],
    "poi_verification": {
        1: "Coordinates from OpenStreetMap Nominatim address geocode for Via Garzole 41, Rastellino, Castelfranco Emilia (R&B Villa Tartaruga); shared with Day 2's accommodation entry.",
        2: "Coordinates from OpenStreetMap Nominatim for Piazza del Popolo, San Giovanni in Persiceto.",
        3: "No dedicated OSM node exists for Piazzetta Betlemme itself; approximated to the Via Betlemme pedestrian street segment, the practical 'walk here' arrival point, not an exact plaza pin.",
        4: "Coordinates from OpenStreetMap Nominatim for Via Crevalcore 1 (Pasticceria Dora cafe node).",
        5: "Itinerary gave Via Guardia Nazionale 1; no OSM-indexed venue node found, approximated to the house-number position on that street from a single food-blog source.",
        6: "Coordinates from OpenStreetMap Nominatim for Piazza dei Contrari 4 (Rocca di Vignola building footprint).",
        7: "No independent geocode found for Pasticceria Gollini; approximated to the adjacent Piazza dei Contrari/Rocca anchor per the itinerary's own 'Piazza Garibaldi, next to the Rocca' description.",
        8: "Coordinates from OpenStreetMap Nominatim for Via Ghiaurov 50-56, Vignola (Acetaia La Ca dal Non).",
        9: "Coordinates from OpenStreetMap Nominatim for Piazza Giuseppe Garibaldi, Castelfranco Emilia.",
        10: "Shares the Piazza del Popolo coordinate (POI 2) — the statue sits in the same square.",
    },
}


DAY4 = {
    "title": "Day 1 orientation map",
    "output": ROOT / "assets/maps/day4-ravenna-route.png",
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
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Start", "Ravenna walking core", "B&B Casa Masoli"],
        },
        "optional": {
            "color": ROUTE_ALTERNATIVE,
            "width": 10,
            "coords": ["Start", "Comacchio", "Manifattura dei Marinati", "Ravenna walking core", "B&B Casa Masoli"],
        },
        "lagoon": {
            "color": ROUTE_OPTIONAL,
            "width": 8,
            "coords": ["Comacchio", "Lagoon road"],
            "dashed": True,
        },
    },
    "route_order": ["optional", "lagoon", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": ROUTE_PRIMARY},
        {"label": "Comacchio alternative", "color": ROUTE_ALTERNATIVE},
    ],
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
            "color": ROUTE_PRIMARY,
            "offset": (0, 0),
        },
        {
            "number": 2,
            "name": "Largo Giustiniano Parking",
            "lat": 44.42183,
            "lon": 12.19623,
            "address": "Largo Giustiniano, 48121 Ravenna RA, Italy",
            "type": "Parking",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 3,
            "name": "Basilica di San Vitale",
            "lat": 44.4205557,
            "lon": 12.1963864,
            "address": "Via San Vitale 17, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 4,
            "name": "Mausoleo di Galla Placidia",
            "lat": 44.4209827,
            "lon": 12.1971029,
            "address": "Via Giuliano Argentario 22, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 5,
            "name": "Domus dei Tappeti di Pietra",
            "lat": 44.421223,
            "lon": 12.195474,
            "address": "Via Gian Battista Barbiani 16, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 6,
            "name": "Museo Byron e del Risorgimento, Palazzo Guiccioli",
            "lat": 44.419629,
            "lon": 12.197836,
            "address": "Via Camillo Benso Cavour 54, 48121 Ravenna RA, Italy",
            "type": "Museum",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 7,
            "name": "Pasticceria Veneziana",
            "lat": 44.4194468,
            "lon": 12.1982703,
            "address": "Via Salara 15, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 8,
            "name": "B&B Casa Masoli",
            "lat": 44.4199737,
            "lon": 12.2003868,
            "address": "Via Girolamo Rossi 22, 48121 Ravenna RA, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "ravenna",
        },
        {
            "number": 9,
            "name": "Erboristeria Giorgioni",
            "lat": 44.4188773,
            "lon": 12.1994528,
            "address": "Via IV Novembre 43, 48121 Ravenna RA, Italy",
            "type": "Shop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 10,
            "name": "Mercato Coperto",
            "lat": 44.418912,
            "lon": 12.199129,
            "address": "Piazza Andrea Costa 6, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 11,
            "name": "Gioielleria Lugaresi",
            "lat": 44.4179545,
            "lon": 12.1986896,
            "address": "Via Giacomo Matteotti 12, 48121 Ravenna RA, Italy",
            "type": "Shop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 12,
            "name": "Caffe Il Nazionale",
            "lat": 44.4175944,
            "lon": 12.1995888,
            "address": "Piazza del Popolo 28, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 13,
            "name": "Piazza del Popolo",
            "lat": 44.4177596,
            "lon": 12.1993185,
            "address": "Piazza del Popolo, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 14,
            "name": "Leonardi Dolciumi 1957",
            "lat": 44.417228,
            "lon": 12.200015,
            "address": "Via Pellegrino Matteucci 5, 48121 Ravenna RA, Italy",
            "type": "Shop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 15,
            "name": "Tomba di Dante",
            "lat": 44.4161585,
            "lon": 12.2009368,
            "address": "Via Dante Alighieri 9, 48121 Ravenna RA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 16,
            "name": "Ca' de Ven",
            "lat": 44.4160938,
            "lon": 12.1999840,
            "address": "Via Corrado Ricci 24, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 17,
            "name": "Koko Mosaico",
            "lat": 44.416945,
            "lon": 12.2039917,
            "address": "Via di Roma 136, 48121 Ravenna RA, Italy",
            "type": "Optional stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 18,
            "name": "Antica Trattoria Al Gallo 1909",
            "lat": 44.4207825,
            "lon": 12.1915981,
            "address": "Via Maggiore 89, 48121 Ravenna RA, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 19,
            "name": "Darsenale - Bizantina Brewpub",
            "lat": 44.423296,
            "lon": 12.212171,
            "address": "Via D'Alaggio 69, 48122 Ravenna RA, Italy",
            "type": "Optional food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ravenna",
        },
        {
            "number": 20,
            "name": "Comacchio",
            "lat": 44.6958712,
            "lon": 12.1812500,
            "address": "Centro storico, 44022 Comacchio FE, Italy",
            "type": "Optional stop",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-30, -34),
        },
        {
            "number": 21,
            "name": "Manifattura dei Marinati",
            "lat": 44.6990038,
            "lon": 12.1752748,
            "address": "Corso Giuseppe Mazzini 200, 44022 Comacchio FE, Italy",
            "type": "Museum / food heritage",
            "color": ROUTE_ALTERNATIVE,
            "offset": (36, 28),
        },
        {
            "number": 22,
            "name": "Argine degli Angeli",
            "lat": 44.6540,
            "lon": 12.2450,
            "address": "Argine degli Angeli, Valli di Comacchio, 44029 Comacchio FE, Italy",
            "type": "Viewpoint",
            "color": ROUTE_OPTIONAL,
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


DAY5 = {
    "title": "Day 2 orientation map",
    "output": ROOT / "assets/maps/day5-san-marino-fano-route.png",
    "zoom": 10,
    "size": (1800, 1125),
    "padding_px": 135,
    "places": {
        "Ravenna start": (44.4199737, 12.2003868),
        "San Marino parking": (43.937384, 12.445192),
        "San Marino core": (43.93623, 12.44695),
        "Guaita Tower": (43.9354691, 12.4493514),
        "La Serenissima": (43.9531511, 12.4685640),
        "Gabicce Monte": (43.960330, 12.761220),
        "San Bartolo viewpoint": (43.943180, 12.817000),
        "Fano old town": (43.84215, 13.01720),
        "Fano port": (43.8511711, 13.0162229),
        "Palazzo Rotati": (43.8442214, 13.0192360),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Ravenna start", "San Marino parking", "San Marino core", "Fano old town", "Palazzo Rotati"],
        },
        "scenic": {
            "color": ROUTE_ALTERNATIVE,
            "width": 10,
            "coords": ["San Marino core", "Gabicce Monte", "San Bartolo viewpoint", "Fano old town"],
        },
    },
    "route_order": ["scenic", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": ROUTE_PRIMARY},
        {"label": "San Bartolo scenic alternative", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "san_marino": {
            "anchor": "San Marino core",
            "numbers": list(range(2, 11)),
            "grid_offset": (-520, -220),
            "columns": 3,
            "x_step": 64,
            "y_step": 58,
        },
        "fano": {
            "anchor": "Fano old town",
            "numbers": list(range(12, 22)),
            "grid_offset": (130, -330),
            "columns": 2,
            "x_step": 68,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "B&B Casa Masoli, Ravenna",
            "lat": 44.4199737,
            "lon": 12.2003868,
            "address": "Via Girolamo Rossi 22, 48121 Ravenna RA, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, 76),
        },
        {
            "number": 2,
            "name": "San Marino P9 Parking",
            "lat": 43.937384,
            "lon": 12.445192,
            "address": "Parcheggio P9, Via Gino Giacomini, 47890 Citta di San Marino, San Marino",
            "type": "Parking",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 3,
            "name": "Guaita Tower & Monte Titano",
            "lat": 43.9354691,
            "lon": 12.4493514,
            "address": "Salita Alla Rocca, 47890 Citta di San Marino, San Marino",
            "type": "Historic site / viewpoint",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 4,
            "name": "Piazza della Liberta & Palazzo Pubblico",
            "lat": 43.9367403,
            "lon": 12.4465224,
            "address": "Piazza della Liberta, 47890 Citta di San Marino, San Marino",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 5,
            "name": "Ristorante Ritrovo dei Lavoratori",
            "lat": 43.9358760,
            "lon": 12.4464272,
            "address": "Androne dei Bastioni 4, 47890 Citta di San Marino, San Marino",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 6,
            "name": "La Terrazza, Hotel Titano",
            "lat": 43.9360252,
            "lon": 12.4469842,
            "address": "Contrada del Collegio 31, 47890 Citta di San Marino, San Marino",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 7,
            "name": "Buca San Francesco",
            "lat": 43.9353605,
            "lon": 12.4468161,
            "address": "Piazzetta del Placito Feretrano 3, 47890 Citta di San Marino, San Marino",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 8,
            "name": "La Serenissima",
            "lat": 43.9531511,
            "lon": 12.4685640,
            "address": "Via Venticinque Marzo 67, 47895 Domagnano, San Marino",
            "type": "Shop / food heritage",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 9,
            "name": "Fantini Pelletteria",
            "lat": 43.9361136,
            "lon": 12.4476454,
            "address": "Contrada dei Magazzeni 23, 47890 Citta di San Marino, San Marino",
            "type": "Shop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 10,
            "name": "Cava dei Balestrieri",
            "lat": 43.9375482,
            "lon": 12.4457523,
            "address": "Via Eugippo, 47890 Citta di San Marino, San Marino",
            "type": "Historic site / optional stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_marino",
        },
        {
            "number": 11,
            "name": "Gabicce Monte / San Bartolo viewpoint",
            "lat": 43.960330,
            "lon": 12.761220,
            "address": "Piazza Valbruna, 61011 Gabicce Monte PU, Italy",
            "type": "Scenic route viewpoint",
            "color": ROUTE_ALTERNATIVE,
            "offset": (0, -44),
        },
        {
            "number": 12,
            "name": "Fano centro storico",
            "lat": 43.840900,
            "lon": 13.016950,
            "address": "Piazza XX Settembre, 61032 Fano PU, Italy",
            "type": "Historic centre",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 13,
            "name": "Arco di Augusto",
            "lat": 43.8430719,
            "lon": 13.0145105,
            "address": "Via Arco d'Augusto, 61032 Fano PU, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 14,
            "name": "Caffe Cavour",
            "lat": 43.8400902,
            "lon": 13.0195547,
            "address": "Via Camillo Benso Conte di Cavour 1, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 15,
            "name": "Caffe del Porto",
            "lat": 43.8511711,
            "lon": 13.0162229,
            "address": "Via Nazario Sauro 270, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 16,
            "name": "Il Caffe del Pasticciere",
            "lat": 43.8385085,
            "lon": 13.0112355,
            "address": "Via della Costituzione 8/A, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 17,
            "name": "Panificio Pasticceria Forno Longhini",
            "lat": 43.8470115,
            "lon": 13.0116548,
            "address": "Viale I Maggio 15/17, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 18,
            "name": "Ristorante Angela",
            "lat": 43.8460841,
            "lon": 13.0255815,
            "address": "Viale Adriatico 13, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 19,
            "name": "La Taverna del Ghiottone",
            "lat": 43.84024,
            "lon": 13.0114404,
            "address": "Via Roma 87/B, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "fano",
        },
        {
            "number": 20,
            "name": "B&B La Casa di Fano",
            "lat": 43.842910,
            "lon": 13.018100,
            "address": "Corso Giacomo Matteotti 173, 61032 Fano PU, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "fano",
        },
        {
            "number": 21,
            "name": "Palazzo Rotati",
            "lat": 43.8442214,
            "lon": 13.0192360,
            "address": "Via Nolfi 49, 61032 Fano PU, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "fano",
        },
    ],
    "poi_verification": {
        1: "Start address carried from verified Day 1 accommodation data for Casa Masoli.",
        2: "Practical San Marino arrival set to P9 parking below the historic centre; coordinates checked against OpenStreetMap parking/mapping data.",
        3: "Address from existing itinerary/tourism data; coordinates checked against mapping data for Guaita/Salita Alla Rocca practical arrival.",
        4: "Address checked against official San Marino civic/tourism naming; coordinates checked against OpenStreetMap Palazzo Pubblico object.",
        5: "Address from existing itinerary; coordinates checked against OpenStreetMap restaurant object.",
        6: "Address from existing itinerary/Hotel Titano data; coordinates checked against OpenStreetMap house address for Contrada del Collegio 31.",
        7: "Address from existing itinerary; coordinates checked against OpenStreetMap restaurant object.",
        8: "Address from existing itinerary/venue data; coordinates retained from existing page and checked against mapping data for Domagnano arrival.",
        9: "Address resolved to Fantini Pelletteria historic-centre shop at Contrada dei Magazzeni 23; coordinates checked against OpenStreetMap address object.",
        10: "Address from existing itinerary; coordinates checked against mapping data for Cava dei Balestrieri.",
        11: "Practical San Bartolo/Gabicce Monte arrival set to Piazza Valbruna viewpoint/parking area; coordinates checked against mapping data.",
        12: "Broad Fano old-town wander anchored to practical Piazza XX Settembre arrival rather than a town centroid; coordinates checked against mapping data.",
        13: "Address from existing itinerary; coordinates checked against OpenStreetMap Arco d'Augusto object.",
        14: "Address from existing itinerary; coordinates checked against OpenStreetMap Caffe Cavour object.",
        15: "Address resolved to Caffe del Porto, Via Nazario Sauro 270; coordinates checked against OpenStreetMap cafe object.",
        16: "Address from existing itinerary; coordinates checked against OpenStreetMap cafe object.",
        17: "Address from existing itinerary; coordinates retained from existing page and checked against mapping data for the bakery arrival.",
        18: "Address from existing itinerary; coordinates checked against OpenStreetMap Hotel/Ristorante Angela object.",
        19: "Address from existing itinerary; coordinates retained from existing page and checked against mapping data for the restaurant arrival.",
        20: "Address from CONTENT.md; coordinates retained from existing page and checked against mapping data for guest arrival.",
        21: "Address from existing itinerary/venue data; coordinates retained from existing page and checked against mapping data for Palazzo Rotati. The older B&B Dimora d'Epoca/Il Palazzo listing resolves to the same practical Fano palazzo area and is treated as an accommodation alias, not a separate mapped stop.",
    },
}


DAY6 = {
    "title": "Day 3 orientation map",
    "output": ROOT / "assets/maps/day6-sirolo-route.png",
    "zoom": 11,
    "size": (1800, 1125),
    "padding_px": 135,
    "places": {
        "Fano start": (43.8442214, 13.0192360),
        "Senigallia": (43.7153671, 13.2205412),
        "Portonovo": (43.5611908, 13.5999370),
        "Sirolo core": (43.5230728, 13.6199227),
        "Conero Camere": (43.5229034, 13.6186971),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Fano start", "Senigallia", "Portonovo", "Sirolo core", "Conero Camere"],
        },
        "direct": {
            "color": ROUTE_ALTERNATIVE,
            "width": 10,
            "coords": ["Fano start", "Sirolo core", "Conero Camere"],
            "dashed": True,
        },
    },
    "route_order": ["direct", "recommended"],
    "legend": [
        {"label": "Recommended coastal route", "color": ROUTE_PRIMARY},
        {"label": "Time-tight direct route", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "sirolo": {
            "anchor": "Sirolo core",
            "numbers": list(range(5, 18)),
            "grid_offset": (150, -380),
            "columns": 3,
            "x_step": 64,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Palazzo Rotati, Fano",
            "lat": 43.8442214,
            "lon": 13.0192360,
            "address": "Via Nolfi 49, 61032 Fano PU, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, -92),
        },
        {
            "number": 2,
            "name": "Rocca Roveresca",
            "lat": 43.7153671,
            "lon": 13.2205412,
            "address": "Piazza del Duca 2, 60019 Senigallia AN, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "offset": (-8, -50),
        },
        {
            "number": 3,
            "name": "Abbazia di Santa Maria di Portonovo",
            "lat": 43.5611908,
            "lon": 13.5999370,
            "address": "Strada Frazione Poggio, Portonovo, 60129 Ancona AN, Italy",
            "type": "Historic site / beach stop",
            "color": ROUTE_PRIMARY,
            "offset": (-48, -46),
        },
        {
            "number": 4,
            "name": "Cooperativa Pescatori di Portonovo",
            "lat": 43.5619,
            "lon": 13.6002,
            "address": "Portonovo beach capanni, Strada Frazione Poggio, 60129 Ancona AN, Italy",
            "type": "Producer / food heritage",
            "color": ROUTE_PRIMARY,
            "offset": (42, 34),
        },
        {
            "number": 5,
            "name": "Centro Visite Parco del Conero",
            "lat": 43.5196861,
            "lon": 13.6180996,
            "address": "Via Peschiera 30/A, 60020 Sirolo AN, Italy",
            "type": "Visitor office / orientation",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 6,
            "name": "Piazza Vittorio Veneto / Balcone Panoramico",
            "lat": 43.5230728,
            "lon": 13.6199227,
            "address": "Piazza Vittorio Veneto, 60020 Sirolo AN, Italy",
            "type": "Viewpoint / historic centre",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 7,
            "name": "Spiaggia Urbani",
            "lat": 43.5236323,
            "lon": 13.6231578,
            "address": "Spiaggia Urbani, 60020 Sirolo AN, Italy",
            "type": "Beach",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 8,
            "name": "Bar Gelateria del Conero",
            "lat": 43.5225245,
            "lon": 13.6201607,
            "address": "Via Italia 1, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 9,
            "name": "Da Giustina",
            "lat": 43.5281358,
            "lon": 13.6135596,
            "address": "Via Cave 1, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 10,
            "name": "La Paranza",
            "lat": 43.5226248,
            "lon": 13.6236777,
            "address": "Spiaggia Urbani, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 11,
            "name": "Osteria Sara",
            "lat": 43.52285,
            "lon": 13.6196845,
            "address": "Piazza Vittorio Veneto 9, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 12,
            "name": "Pa' Panino un bel Po'",
            "lat": 43.5219441,
            "lon": 13.6204501,
            "address": "Via Italia 39, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 13,
            "name": "Bottega dei Sapori Nostrani",
            "lat": 43.5223274,
            "lon": 13.6202173,
            "address": "Via Italia 11/36, 60020 Sirolo AN, Italy",
            "type": "Shop / food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 14,
            "name": "Latteria Elgide",
            "lat": 43.52243,
            "lon": 13.62012,
            "address": "Via Italia 5, 60020 Sirolo AN, Italy",
            "type": "Shop",
            "color": ROUTE_PRIMARY,
            "cluster": "sirolo",
        },
        {
            "number": 15,
            "name": "Conero Camere",
            "lat": 43.5229034,
            "lon": 13.6186971,
            "address": "Via Grilli 14, 60020 Sirolo AN, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "sirolo",
        },
        {
            "number": 16,
            "name": "Diecidodici",
            "lat": 43.5235067,
            "lon": 13.6193663,
            "address": "Via Anacleto Giulietti 10, 60020 Sirolo AN, Italy",
            "type": "Accommodation / food stop",
            "color": MARKER_ACCOMMODATION,
            "cluster": "sirolo",
        },
        {
            "number": 17,
            "name": "San Michele Relais & Spa",
            "lat": 43.5266418,
            "lon": 13.6169719,
            "address": "Via Piave 6, 60020 Sirolo AN, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "sirolo",
        },
    ],
    "poi_verification": {
        1: "Start carried from verified Day 2 Palazzo Rotati accommodation data.",
        2: "Address and coordinates checked against OpenStreetMap Rocca Roveresca attraction object at Piazza del Duca 2.",
        3: "Abbey location checked against existing itinerary data and OpenStreetMap reverse data for Portonovo/Strada Frazione Poggio arrival area.",
        4: "Cooperative mapped to the practical Portonovo beach capanni area described in the itinerary; coordinates checked against OpenStreetMap Portonovo beach/mapping data.",
        5: "Address and coordinates checked against OpenStreetMap Centro Visite Parco del Conero object at Via Peschiera 30/A.",
        6: "Sirolo broad old-town/viewpoint stop anchored to Piazza Vittorio Veneto; coordinates checked against OpenStreetMap square object.",
        7: "Beach stop checked against OpenStreetMap Spiaggia Urbani relation.",
        8: "Address and coordinates checked against OpenStreetMap Gelateria del Conero cafe object at Via Italia 1.",
        9: "Address from existing itinerary; coordinates checked against OpenStreetMap reverse data for Via Cave arrival area.",
        10: "Address from existing itinerary; coordinates checked against OpenStreetMap Spiaggia Urbani/reverse data for beach arrival area.",
        11: "Address from existing itinerary; coordinates checked against OpenStreetMap reverse data for Piazza Vittorio Veneto/Piazzale Marino restaurant area.",
        12: "Address from existing itinerary; coordinates checked against OpenStreetMap reverse data for Via Italia storefront area.",
        13: "Address from existing itinerary; coordinates checked against OpenStreetMap reverse data for Via Italia pedestrian storefront area.",
        14: "Address from existing itinerary/local-source note; coordinates set to practical Via Italia 5 storefront area and checked against nearby OpenStreetMap Via Italia/Gelateria object data.",
        15: "Address from existing itinerary; coordinates checked against OpenStreetMap reverse data for Via Grilli/Giacomo Puccini guest arrival area.",
        16: "Address from existing itinerary; coordinates checked against OpenStreetMap reverse data for Via Anacleto Giulietti arrival area.",
        17: "Address from existing itinerary; coordinates checked against OpenStreetMap reverse data for Via Piave/San Michele pedestrian approach area.",
    },
}


DAY7 = {
    "title": "Day 4 orientation map",
    "output": ROOT / "assets/maps/day7-trabocchi-route.png",
    "zoom": 9,
    "size": (1800, 1125),
    "padding_px": 145,
    "places": {
        "Sirolo start": (43.5229034, 13.6186971),
        "Loreto": (43.4410010, 13.6108062),
        "Picchio": (43.4466094, 13.6175825),
        "Ortona old town": (42.3535835, 14.4032270),
        "Moro cemetery": (42.3368140, 14.4165319),
        "Marina di San Vito": (42.3096483, 14.4445601),
        "Trabocco Turchino": (42.3006606, 14.4608939),
        "Olivastri": (42.2779149, 14.4456199),
        "Pesce Palombo": (42.244760, 14.518930),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Sirolo start", "Ortona old town", "Moro cemetery", "Marina di San Vito"],
        },
        "loreto": {
            "color": ROUTE_ALTERNATIVE,
            "width": 10,
            "coords": ["Sirolo start", "Loreto", "Picchio", "Ortona old town"],
            "dashed": True,
        },
        "trabocchi": {
            "color": ROUTE_OPTIONAL,
            "width": 8,
            "coords": ["Marina di San Vito", "Trabocco Turchino", "Olivastri", "Pesce Palombo"],
            "dashed": True,
        },
    },
    "route_order": ["trabocchi", "loreto", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": ROUTE_PRIMARY},
        {"label": "Loreto optional detour", "color": ROUTE_ALTERNATIVE, "dashed": True},
        {"label": "Trabocchi local add-on", "color": ROUTE_OPTIONAL, "dashed": True},
    ],
    "poi_clusters": {
        "ortona": {
            "anchor": "Ortona old town",
            "numbers": list(range(4, 8)),
            "grid_offset": (-330, -170),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "san_vito": {
            "anchor": "Marina di San Vito",
            "numbers": [9, 10, 11, 13, 14, 15, 16, 17],
            "grid_offset": (130, -300),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Conero Camere, Sirolo",
            "lat": 43.5229034,
            "lon": 13.6186971,
            "address": "Via Grilli 14, 60020 Sirolo AN, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, 48),
        },
        {
            "number": 2,
            "name": "Basilica della Santa Casa",
            "lat": 43.4410010,
            "lon": 13.6108062,
            "address": "Piazza della Madonna 1, 60025 Loreto AN, Italy",
            "type": "Optional historic site",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-58, -44),
        },
        {
            "number": 3,
            "name": "Pasticceria Picchio",
            "lat": 43.4466094,
            "lon": 13.6175825,
            "address": "Via Traversa Don Enzo Rampolla 2, 60025 Loreto Stazione AN, Italy",
            "type": "Food stop",
            "color": ROUTE_ALTERNATIVE,
            "offset": (86, 52),
        },
        {
            "number": 4,
            "name": "Ortona old town / Corso Vittorio Emanuele",
            "lat": 42.3535835,
            "lon": 14.4032270,
            "address": "Corso Vittorio Emanuele, 66026 Ortona CH, Italy",
            "type": "Historic centre",
            "color": ROUTE_PRIMARY,
            "cluster": "ortona",
        },
        {
            "number": 5,
            "name": "Pasticceria Cantelmi Giulio",
            "lat": 42.3535835,
            "lon": 14.4032270,
            "address": "Corso Vittorio Emanuele 73, 66026 Ortona CH, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ortona",
        },
        {
            "number": 6,
            "name": "Castello Aragonese",
            "lat": 42.3588317,
            "lon": 14.4058573,
            "address": "Largo Castello, 66026 Ortona CH, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ortona",
        },
        {
            "number": 7,
            "name": "Moro River Canadian War Cemetery",
            "lat": 42.3368140,
            "lon": 14.4165319,
            "address": "Contrada San Donato, 66026 Ortona CH, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ortona",
        },
        {
            "number": 8,
            "name": "Trabocco Punta Turchino",
            "lat": 42.3006606,
            "lon": 14.4608939,
            "address": "Contrada Portelle, 66038 San Vito Chietino CH, Italy",
            "type": "Viewpoint / trabocco heritage",
            "color": ROUTE_OPTIONAL,
            "offset": (52, -42),
        },
        {
            "number": 9,
            "name": "Marina di San Vito / Costa dei Trabocchi",
            "lat": 42.2963540,
            "lon": 14.4436070,
            "address": "Marina di San Vito, 66038 San Vito Chietino CH, Italy",
            "type": "Beach / coastal base",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 10,
            "name": "Trabocco Vento di Scirocco",
            "lat": 42.3107684,
            "lon": 14.4462617,
            "address": "Via Lungomare di Gualdo, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop / trabocco dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 11,
            "name": "Aldebaran da Rocco e Tommaso",
            "lat": 42.309154,
            "lon": 14.445654,
            "address": "Via Lungomare di Gualdo 4, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 12,
            "name": "Trabocco Pesce Palombo",
            "lat": 42.244760,
            "lon": 14.518930,
            "address": "SS16 Adriatica, Fossacesia Marina, 66022 Fossacesia CH, Italy",
            "type": "Optional food stop",
            "color": ROUTE_OPTIONAL,
            "offset": (0, 46),
        },
        {
            "number": 13,
            "name": "Le Due Palme",
            "lat": 42.292305,
            "lon": 14.443628,
            "address": "Via San Rocco, 66038 San Vito Chietino CH, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 14,
            "name": "Frantoio Oleario Giocondo de Santis",
            "lat": 42.2913838,
            "lon": 14.4447461,
            "address": "Via San Rocco Vecchio 7, 66038 San Vito Chietino CH, Italy",
            "type": "Shop / food heritage",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 15,
            "name": "Azienda Agricola Olivastri Tommaso",
            "lat": 42.2779149,
            "lon": 14.4456199,
            "address": "Via Quercia del Corvo 37, 66038 San Vito Chietino CH, Italy",
            "type": "Winery / shop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 16,
            "name": "B&B La Finestra Sui Trabocchi",
            "lat": 42.3096483,
            "lon": 14.4445601,
            "address": "Via Lungomare di Gualdo 31, 66038 Marina di San Vito CH, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "san_vito",
        },
        {
            "number": 17,
            "name": "Locanda dell'Adriatica",
            "lat": 42.3080635,
            "lon": 14.4459466,
            "address": "Largo Olivieri 5, 66038 Marina di San Vito CH, Italy",
            "type": "Accommodation / food stop",
            "color": MARKER_ACCOMMODATION,
            "cluster": "san_vito",
        },
    ],
    "poi_verification": {
        1: "Start carried from verified Day 3 Conero Camere accommodation data.",
        2: "Address and coordinates checked against OpenStreetMap Santuario della Santa Casa object at Piazza della Madonna 1.",
        3: "Address and coordinates checked against OpenStreetMap Pasticceria Picchio shop object.",
        4: "Broad Ortona old-town stop anchored to the practical Corso Vittorio Emanuele arrival from the existing itinerary, checked against OpenStreetMap road/reverse data.",
        5: "Address from existing itinerary; coordinates use the same practical Corso Vittorio Emanuele 73 arrival area, checked against OpenStreetMap Corso Vittorio Emanuele reverse data.",
        6: "Address and coordinates checked against OpenStreetMap Castello Aragonese object.",
        7: "Address and coordinates checked against OpenStreetMap Moro River Canadian War Cemetery relation.",
        8: "Trabocco Turchino reference mapped to OpenStreetMap Trabocco Punta Turchino object at Contrada Portelle.",
        9: "Broad San Vito Chietino coastal stop anchored to the existing practical Marina di San Vito/Costa dei Trabocchi arrival coordinates, checked against OpenStreetMap coastal mapping context.",
        10: "Address and coordinates checked against OpenStreetMap Trabocco Vento di Scirocco restaurant object.",
        11: "Address and coordinates from existing itinerary, checked against OpenStreetMap/reverse data for Via Lungomare di Gualdo restaurant strip.",
        12: "Address resolved to practical SS16 Fossacesia Marina trabocco arrival; coordinates from reputable mapping context where OSM named-object search was sparse.",
        13: "Address and coordinates from existing itinerary, checked against OpenStreetMap/reverse data for Via San Rocco arrival area.",
        14: "Address and coordinates from existing itinerary, checked against OpenStreetMap/reverse data for Via San Rocco Vecchio arrival area.",
        15: "Address and coordinates from existing itinerary, checked against OpenStreetMap/reverse data for Via Quercia del Corvo winery arrival area.",
        16: "Address from existing itinerary; coordinates checked against OpenStreetMap Via Lungomare di Gualdo 31 nearby object/reverse data for guest arrival.",
        17: "Address and coordinates from existing itinerary, checked against OpenStreetMap/reverse data for Largo Olivieri arrival area.",
    },
}


DAY8 = {
    "title": "Day 5 orientation map",
    "output": ROOT / "assets/maps/day8-san-vito-linger-route.png",
    "zoom": 12,
    "size": (1800, 1125),
    "padding_px": 150,
    "places": {
        "La Finestra": (42.3096483, 14.4445601),
        "Marina di San Vito": (42.2963540, 14.4436070),
        "Via Verde access": (42.309420, 14.444940),
        "Promontorio Dannunziano": (42.2963673, 14.4649437),
        "San Vito-Lanciano station": (42.3048450, 14.4404829),
        "Lanciano centre": (42.2309626, 14.3902022),
        "La Bocconotteria": (42.2186783, 14.3950227),
        "Castel Frentano": (42.197430, 14.356420),
    },
    "routes": {
        "linger": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["La Finestra", "Via Verde access", "Marina di San Vito", "Promontorio Dannunziano", "La Finestra"],
        },
        "lanciano": {
            "color": ROUTE_ALTERNATIVE,
            "width": 10,
            "coords": ["La Finestra", "San Vito-Lanciano station", "Lanciano centre", "La Bocconotteria"],
            "dashed": True,
        },
        "castel_frentano": {
            "color": ROUTE_OPTIONAL,
            "width": 8,
            "coords": ["Lanciano centre", "Castel Frentano"],
            "dashed": True,
        },
    },
    "route_order": ["castel_frentano", "lanciano", "linger"],
    "legend": [
        {"label": "Local linger route", "color": ROUTE_PRIMARY},
        {"label": "Lanciano day-trip option", "color": ROUTE_ALTERNATIVE, "dashed": True},
        {"label": "Castel Frentano bocconotto add-on", "color": ROUTE_OPTIONAL, "dashed": True},
    ],
    "poi_clusters": {
        "san_vito": {
            "anchor": "Marina di San Vito",
            "numbers": [1, 2, 3, 4, 5, 6],
            "grid_offset": (150, -260),
            "columns": 2,
            "x_step": 68,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "B&B La Finestra Sui Trabocchi",
            "lat": 42.3096483,
            "lon": 14.4445601,
            "address": "Via Lungomare di Gualdo 31, 66038 Marina di San Vito CH, Italy",
            "type": "Accommodation / start",
            "color": MARKER_ACCOMMODATION,
            "cluster": "san_vito",
        },
        {
            "number": 2,
            "name": "Locanda dell'Adriatica",
            "lat": 42.3080635,
            "lon": 14.4459466,
            "address": "Largo Olivieri 5, 66038 Marina di San Vito CH, Italy",
            "type": "Accommodation / food stop",
            "color": MARKER_ACCOMMODATION,
            "cluster": "san_vito",
        },
        {
            "number": 3,
            "name": "Via Verde della Costa dei Trabocchi",
            "lat": 42.309420,
            "lon": 14.444940,
            "address": "Via Verde access near Via Lungomare di Gualdo, 66038 Marina di San Vito CH, Italy",
            "type": "Cycle / walking route",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 4,
            "name": "Pasticceria Iezzi Rossana",
            "lat": 42.3079185,
            "lon": 14.4453615,
            "address": "Via Nazionale Adriatica 6, 66038 San Vito Chietino CH, Italy",
            "type": "Food stop / shop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 5,
            "name": "Trabocco Vento di Scirocco",
            "lat": 42.3107684,
            "lon": 14.4462617,
            "address": "Via Lungomare di Gualdo, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 6,
            "name": "Aldebaran da Rocco e Tommaso",
            "lat": 42.309154,
            "lon": 14.445654,
            "address": "Via Lungomare di Gualdo 4, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "san_vito",
        },
        {
            "number": 7,
            "name": "Le Due Palme",
            "lat": 42.292305,
            "lon": 14.443628,
            "address": "Via San Rocco, 66038 San Vito Chietino CH, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "offset": (-62, 18),
        },
        {
            "number": 8,
            "name": "Promontorio Dannunziano",
            "lat": 42.2963673,
            "lon": 14.4649437,
            "address": "Contrada San Fino 31, 66038 San Vito Chietino CH, Italy",
            "type": "Viewpoint / historic site",
            "color": ROUTE_PRIMARY,
            "offset": (86, -14),
        },
        {
            "number": 9,
            "name": "Trabocco Punta Turchino",
            "lat": 42.3006606,
            "lon": 14.4608939,
            "address": "Contrada Portelle, 66038 San Vito Chietino CH, Italy",
            "type": "Trabocco heritage / viewpoint",
            "color": ROUTE_PRIMARY,
            "offset": (86, 48),
        },
        {
            "number": 10,
            "name": "San Vito-Lanciano station",
            "lat": 42.3048450,
            "lon": 14.4404829,
            "address": "Stazione San Vito-Lanciano, SP70, 66038 San Vito Chietino CH, Italy",
            "type": "Transport",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-62, -42),
        },
        {
            "number": 11,
            "name": "Lanciano old town / Piazza del Plebiscito",
            "lat": 42.2309626,
            "lon": 14.3902022,
            "address": "Piazza del Plebiscito, 66034 Lanciano CH, Italy",
            "type": "Optional historic centre",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-52, -42),
        },
        {
            "number": 12,
            "name": "La Bocconotteria",
            "lat": 42.2186783,
            "lon": 14.3950227,
            "address": "Via Ercole Tinari 6, 66034 Lanciano CH, Italy",
            "type": "Food stop / shop",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-42, 46),
        },
        {
            "number": 13,
            "name": "Trattoria Paolucci",
            "lat": 42.2284917,
            "lon": 14.3952913,
            "address": "Via Dalmazia 30, 66034 Lanciano CH, Italy",
            "type": "Food stop",
            "color": ROUTE_ALTERNATIVE,
            "offset": (54, -36),
        },
        {
            "number": 14,
            "name": "Bottega del Bocconotto",
            "lat": 42.197430,
            "lon": 14.356420,
            "address": "Castel Frentano, 66032 Castel Frentano CH, Italy",
            "type": "Optional food heritage / shop",
            "color": ROUTE_OPTIONAL,
            "offset": (0, 0),
        },
    ],
    "poi_verification": {
        1: "Accommodation/start carried from verified Day 4 La Finestra Sui Trabocchi data; coordinates represent practical guest arrival.",
        2: "Accommodation carried from verified Day 4 Locanda dell'Adriatica data; coordinates checked against mapping/reverse data for Largo Olivieri.",
        3: "Via Verde mapped to the practical Marina di San Vito access near the Day 4 accommodation, checked against coastal cycleway context and existing itinerary.",
        4: "Address from existing itinerary; coordinates retained from Day 5 content and checked against OpenStreetMap Via Nazionale Adriatica road/reverse data.",
        5: "Food stop carried from verified Day 4 Trabocco Vento di Scirocco OpenStreetMap restaurant object.",
        6: "Food stop carried from verified Day 4 Aldebaran practical Via Lungomare di Gualdo arrival data.",
        7: "Food stop carried from verified Day 4 Le Due Palme practical Via San Rocco arrival data.",
        8: "Address and coordinates from existing itinerary; checked against OpenStreetMap Contrada Portelle/San Fino road context for the practical headland approach.",
        9: "Trabocco Punta Turchino checked against OpenStreetMap named historic/building object at Contrada Portelle.",
        10: "Station checked against OpenStreetMap San Vito-Lanciano railway station node.",
        11: "Lanciano broad old-town stop anchored to Piazza del Plebiscito practical arrival, checked against OpenStreetMap road/pedestrian square objects.",
        12: "Address from existing itinerary; coordinates retained from Day 5 content and checked against OpenStreetMap Via Ercole Tinari road/reverse data.",
        13: "Address from existing itinerary; coordinates retained from Day 5 content and checked against OpenStreetMap Via Dalmazia road/reverse data.",
        14: "Existing itinerary identifies Bottega del Bocconotto in Castel Frentano but not a street address; mapped to practical Castel Frentano arrival pending local confirmation rather than omitted.",
    },
}

DAY9 = {
    "title": "Day 6 orientation map",
    "output": ROOT / "assets/maps/day9-vasto-termoli-route.png",
    "zoom": 10,
    "size": (1800, 1125),
    "padding_px": 140,
    "places": {
        "La Finestra start": (42.3096483, 14.4445601),
        "Punta Aderci": (42.1800301, 14.6877337),
        "Palazzo d'Avalos": (42.1116174, 14.7102856),
        "Castello Svevo Termoli": (42.0042633, 14.9963357),
        "Residenza Sveva end": (42.0054205, 14.9975873),
    },
    "routes": {
        "vasto": {
            "color": ROUTE_ALTERNATIVE,
            "width": 10,
            "coords": ["La Finestra start", "Palazzo d'Avalos", "Castello Svevo Termoli"],
            "dashed": True,
        },
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["La Finestra start", "Punta Aderci", "Castello Svevo Termoli", "Residenza Sveva end"],
        },
    },
    "route_order": ["vasto", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": ROUTE_PRIMARY},
        {"label": "Vasto historic-centre detour", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "vasto": {
            "anchor": "Palazzo d'Avalos",
            "numbers": [3, 4, 5],
            "grid_offset": (-150, -190),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "termoli": {
            "anchor": "Castello Svevo Termoli",
            "numbers": list(range(6, 18)),
            "grid_offset": (-380, -40),
            "columns": 3,
            "x_step": 64,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "B&B La Finestra Sui Trabocchi",
            "lat": 42.3096483,
            "lon": 14.4445601,
            "address": "Via Lungomare di Gualdo 31, 66038 Marina di San Vito CH, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, 48),
        },
        {
            "number": 2,
            "name": "Riserva Naturale di Punta Aderci",
            "lat": 42.1800301,
            "lon": 14.6877337,
            "address": "Sentiero d'Accesso Punta Aderci, 66054 Vasto CH, Italy",
            "type": "Nature reserve",
            "color": ROUTE_PRIMARY,
            "offset": (0, -50),
        },
        {
            "number": 3,
            "name": "Palazzo d'Avalos",
            "lat": 42.1116174,
            "lon": 14.7102856,
            "address": "Piazza Lucio Valerio Pudente, 66054 Vasto CH, Italy",
            "type": "Optional historic site",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "vasto",
        },
        {
            "number": 4,
            "name": "Loggia Amblingh",
            "lat": 42.1103135,
            "lon": 14.7100671,
            "address": "Vasto old town, 66054 Vasto CH, Italy",
            "type": "Optional viewpoint",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "vasto",
        },
        {
            "number": 5,
            "name": "Pasticceria La Vastese",
            "lat": 42.1229066,
            "lon": 14.7109300,
            "address": "Via Ciccarone 98/A, 66054 Vasto CH, Italy",
            "type": "Optional food stop",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "vasto",
        },
        {
            "number": 6,
            "name": "Castello Svevo",
            "lat": 42.0042633,
            "lon": 14.9963357,
            "address": "Largo Piè di Castello, 86039 Termoli CB, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 7,
            "name": "Cattedrale di Santa Maria della Purificazione",
            "lat": 42.0052965,
            "lon": 14.9971312,
            "address": "Vicoletto Duomo, 86039 Termoli CB, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 8,
            "name": "Vicolo Rejecelle",
            "lat": 42.0049015,
            "lon": 14.9968963,
            "address": "Via Nocchiere Marinucci Salvatore 9, 86039 Termoli CB, Italy",
            "type": "Hidden gem",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 9,
            "name": "Zara Pasticceria",
            "lat": 41.9987825,
            "lon": 14.9828334,
            "address": "Via Argentina 9/15, 86039 Termoli CB, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 10,
            "name": "Ristorante Da Nicolino",
            "lat": 42.0035882,
            "lon": 14.9963207,
            "address": "Via Roma 13, 86039 Termoli CB, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 11,
            "name": "Trattoria Tipica L'Opera",
            "lat": 42.0023494,
            "lon": 14.9946932,
            "address": "Via Adriatica 32, 86039 Termoli CB, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 12,
            "name": "Osteria Dentro le Mura",
            "lat": 42.0045521,
            "lon": 14.9965624,
            "address": "Via Federico Secondo di Svevia 3, 86039 Termoli CB, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 13,
            "name": "Friggitoria Maramimmo",
            "lat": 41.9996161,
            "lon": 14.9965564,
            "address": "Corso Fratelli Brigida 64, 86039 Termoli CB, Italy",
            "type": "Food stop / budget",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 14,
            "name": "Roberti Store",
            "lat": 42.0017114,
            "lon": 14.9974386,
            "address": "Via Alfano 10, 86039 Termoli CB, Italy",
            "type": "Shop",
            "color": ROUTE_PRIMARY,
            "cluster": "termoli",
        },
        {
            "number": 15,
            "name": "Le Dimore nel Borgo",
            "lat": 42.0048803,
            "lon": 14.9974687,
            "address": "Via Maro de Gregorio Pasquale, 86039 Termoli CB, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "termoli",
        },
        {
            "number": 16,
            "name": "La Casa di Lelè",
            "lat": 41.9975505,
            "lon": 14.9970443,
            "address": "Via delle Lampare 8, 86039 Termoli CB, Italy",
            "type": "Accommodation / alternate",
            "color": MARKER_ACCOMMODATION,
            "cluster": "termoli",
        },
        {
            "number": 17,
            "name": "Residenza Sveva Albergo Diffuso",
            "lat": 42.0054205,
            "lon": 14.9975873,
            "address": "Piazza Duomo 11, 86039 Termoli CB, Italy",
            "type": "Accommodation / end",
            "color": MARKER_ACCOMMODATION,
            "cluster": "termoli",
        },
    ],
    "poi_verification": {
        1: "Start carried from verified Day 5 La Finestra Sui Trabocchi accommodation data.",
        2: "Address and coordinates from existing itinerary for the Riserva Naturale di Punta Aderci access trail, checked against OpenStreetMap nature-reserve/trail context.",
        3: "Address and coordinates from existing itinerary for Palazzo d'Avalos, checked against OpenStreetMap Palazzo d'Avalos museum object.",
        4: "Loggia Amblingh has no street address in the itinerary; resolved via OpenStreetMap Nominatim search for the named loggia beside the Palazzo d'Avalos gardens.",
        5: "Address and coordinates from existing itinerary for Pasticceria La Vastese, checked against OpenStreetMap Via Ciccarone shop context.",
        6: "Address and coordinates from existing itinerary for Castello Svevo, checked against OpenStreetMap Castello Svevo (Termoli) object.",
        7: "Itinerary gave only Piazza Duomo; resolved via OpenStreetMap Nominatim place-of-worship search to the Cattedrale di Santa Maria della Purificazione node on Vicoletto Duomo.",
        8: "Address and coordinates from existing itinerary for Vicolo Rejecelle, checked against OpenStreetMap named alley object.",
        9: "Address and coordinates from existing itinerary for Zara Pasticceria, checked against OpenStreetMap Via Argentina shop context.",
        10: "Itinerary gave only Via Roma 13; resolved via OpenStreetMap Nominatim search to a named 'da Nicolino' restaurant node at that address.",
        11: "Itinerary gave only Via Adriatica 32; resolved via OpenStreetMap Nominatim search to a named 'Trattoria L'Opera' restaurant node at that address.",
        12: "Itinerary gave no address; resolved via OpenStreetMap Nominatim name search to a named 'Osteria Dentro le Mura' restaurant node on Via Federico Secondo di Svevia.",
        13: "Friggitoria Maramimmo has no OSM-indexed storefront node; coordinates approximate the Corso Fratelli Brigida street segment nearest house number 64, not an exact building pin.",
        14: "Roberti Store has no OSM-indexed storefront node; coordinates approximate the Via Alfano street segment nearest house number 10, not an exact building pin.",
        15: "Address and coordinates from existing itinerary for Le Dimore nel Borgo, checked against OpenStreetMap Via Maro de Gregorio Pasquale context.",
        16: "Address and coordinates from existing itinerary for La Casa di Lelè, checked against OpenStreetMap Via delle Lampare context.",
        17: "Address and coordinates from existing itinerary for Residenza Sveva Albergo Diffuso, checked against OpenStreetMap Piazza Duomo 11 context; also used as the day's route endpoint.",
    },
}

DAY10 = {
    "title": "Day 7 orientation map",
    "output": ROOT / "assets/maps/day10-vieste-route.png",
    "zoom": 9,
    "size": (1800, 1125),
    "padding_px": 140,
    "places": {
        "Termoli start": (42.0054205, 14.9975873),
        "Lesina": (41.8619097, 15.3532657),
        "Vieste end": (41.8809236, 16.1792922),
        "Foresta Umbra": (41.8447785, 15.9775987),
    },
    "routes": {
        "umbra": {
            "color": ROUTE_ALTERNATIVE,
            "width": 8,
            "coords": ["Vieste end", "Foresta Umbra"],
            "dashed": True,
        },
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Termoli start", "Lesina", "Vieste end"],
        },
    },
    "route_order": ["umbra", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": ROUTE_PRIMARY},
        {"label": "Foresta Umbra optional detour", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "vieste": {
            "anchor": "Vieste end",
            "numbers": list(range(3, 15)),
            "grid_offset": (100, -330),
            "columns": 3,
            "x_step": 64,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Residenza Sveva Albergo Diffuso, Termoli",
            "lat": 42.0054205,
            "lon": 14.9975873,
            "address": "Piazza Duomo 11, 86039 Termoli CB, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, 48),
        },
        {
            "number": 2,
            "name": "Lago di Lesina",
            "lat": 41.8619097,
            "lon": 15.3532657,
            "address": "Lesina FG, Italy",
            "type": "Optional lagoon stop",
            "color": ROUTE_PRIMARY,
            "offset": (0, -50),
        },
        {
            "number": 3,
            "name": "Vieste centro storico & Castello Svevo",
            "lat": 41.8809236,
            "lon": 16.1792922,
            "address": "Viale Federico Secondo di Svevia, 71019 Vieste FG, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 4,
            "name": "Spiaggia di Castello & Pizzomunno",
            "lat": 41.8673500,
            "lon": 16.1753703,
            "address": "Spiaggia di Castello, 71019 Vieste FG, Italy",
            "type": "Beach / viewpoint",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 5,
            "name": "Chianca Amara",
            "lat": 41.8815296,
            "lon": 16.1814304,
            "address": "Via Gregorio XIII, 71019 Vieste FG, Italy",
            "type": "Historic memorial",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 6,
            "name": "Trabucco di San Lorenzo",
            "lat": 41.8954927,
            "lon": 16.1610791,
            "address": "Strada Provinciale 52 Vieste-Peschici, Defensola, 71019 Vieste FG, Italy",
            "type": "Optional trabocco heritage",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 7,
            "name": "Cornetteria Chianca Amara",
            "lat": 41.8814613,
            "lon": 16.1815773,
            "address": "Via Nicolo Cimaglia 4, 71019 Vieste FG, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 8,
            "name": "Bakery Cafe Sant'Antonio",
            "lat": 41.8842286,
            "lon": 16.1696023,
            "address": "Piazzale Aldo Moro 64, 71019 Vieste FG, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 9,
            "name": "Donlù",
            "lat": 41.8809236,
            "lon": 16.1792922,
            "address": "Largo Seggio 8, 71019 Vieste FG, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 10,
            "name": "Osteria degli Archi",
            "lat": 41.8825156,
            "lon": 16.1829919,
            "address": "Via Ripe 2, 71019 Vieste FG, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 11,
            "name": "Box 19",
            "lat": 41.8837530,
            "lon": 16.1765535,
            "address": "Via Santa Maria di Merino 13, 71019 Vieste FG, Italy",
            "type": "Dinner / budget",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 12,
            "name": "Ristorante Al Dragone",
            "lat": 41.8809236,
            "lon": 16.1792922,
            "address": "Via Duomo 8, 71019 Vieste FG, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "vieste",
        },
        {
            "number": 13,
            "name": "Dimora del Dragone",
            "lat": 41.8809236,
            "lon": 16.1792922,
            "address": "Via Duomo 8, 71019 Vieste FG, Italy",
            "type": "Accommodation / end / my pick",
            "color": MARKER_ACCOMMODATION,
            "cluster": "vieste",
        },
        {
            "number": 14,
            "name": "Viesthouse B&B",
            "lat": 41.8832338,
            "lon": 16.1779067,
            "address": "Via Dottor Giuliani 27, 71019 Vieste FG, Italy",
            "type": "Accommodation / alternate",
            "color": MARKER_ACCOMMODATION,
            "cluster": "vieste",
        },
        {
            "number": 15,
            "name": "Foresta Umbra",
            "lat": 41.8447785,
            "lon": 15.9775987,
            "address": "Foresta Umbra, 71018 Vico del Gargano FG, Italy",
            "type": "Optional inland detour",
            "color": ROUTE_ALTERNATIVE,
            "offset": (0, 46),
        },
    ],
    "poi_verification": {
        1: "Start carried from verified Day 6 Residenza Sveva Albergo Diffuso accommodation data.",
        2: "Itinerary gave no specific lagoon-access address; resolved via OpenStreetMap Nominatim to the Lesina village centre, the practical arrival point for the lagoon/fishermen's-hut area.",
        3: "Itinerary gave only a low-precision 41.882/16.176 pair; refined via OpenStreetMap Nominatim to the Castello Svevo di Vieste object.",
        4: "Address and coordinates from existing itinerary for Spiaggia di Castello, checked against OpenStreetMap beach/coastal context.",
        5: "Address and coordinates from existing itinerary for Chianca Amara, checked against OpenStreetMap memorial/reverse data.",
        6: "Itinerary gave no address; resolved via OpenStreetMap Nominatim to the 'Trabucco San Lorenzo' named object on Strada Provinciale 52 toward Peschici.",
        7: "Address and coordinates from existing itinerary for Cornetteria Chianca Amara, checked against OpenStreetMap Via Nicolo Cimaglia shop context.",
        8: "Address and coordinates from existing itinerary for Bakery Cafe Sant'Antonio, checked against OpenStreetMap Piazzale Aldo Moro context.",
        9: "Itinerary gave only Largo Seggio 8, which has no OSM-indexed node; approximated to the Vieste centro storico/Castello Svevo area, not an exact building pin.",
        10: "Itinerary gave only Via Ripe 2; resolved via OpenStreetMap Nominatim to a named 'Osteria degli Archi' restaurant node on Via Vittoria.",
        11: "Itinerary gave only Via Santa Maria di Merino 13, which has no OSM-indexed storefront node; coordinates approximate that street, not an exact building pin.",
        12: "Itinerary gave only Via Duomo 8, which has no OSM-indexed node; approximated to that area, not an exact building pin. Research for the new Accommodation section found this is the same building as B&B Dimora del Dragone (its on-site restaurant is named 'Il Dragone'/'Al Dragone'), confirming the address.",
        13: "New accommodation research: address and host names (Rosa and Pasquale) confirmed via the property's own site; no OSM-indexed node for Via Duomo 8, so approximated to the Castello Svevo/centro storico area, not an exact building pin. Same building as Ristorante Al Dragone (POI 12).",
        14: "New accommodation research: address confirmed via the property's own site (beb.it) at Via Dottor Giuliani 27; coordinates from an OpenStreetMap node at that address (listed under a different business name, 'Alice', at the same building).",
        15: "Itinerary names Foresta Umbra without a specific trailhead; resolved via OpenStreetMap Nominatim to the forest's named area centroid near Vico del Gargano. Presented as a background/orientation reference, not a timed itinerary stop — see the day's own text, which treats it as an aside rather than a planned addition.",
    },
}

DAY11 = {
    "title": "Day 8 orientation map",
    "output": ROOT / "assets/maps/day11-mattinata-route.png",
    "zoom": 11,
    "size": (1800, 1125),
    "padding_px": 140,
    "places": {
        "Vieste start": (41.8809236, 16.1792922),
        "Mattinata end": (41.7142542, 16.0792899),
        "Baia delle Zagare": (41.7311, 16.0857),
        "Pasticceria La Torre": (41.7110463, 16.0511548),
    },
    "routes": {
        "zagare": {
            "color": ROUTE_ALTERNATIVE,
            "width": 8,
            "coords": ["Mattinata end", "Baia delle Zagare"],
            "dashed": True,
        },
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Vieste start", "Mattinata end"],
        },
    },
    "route_order": ["zagare", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": ROUTE_PRIMARY},
        {"label": "Baia delle Zagare there-and-back detour", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "mattinata": {
            "anchor": "Pasticceria La Torre",
            "numbers": [3, 4, 5, 6, 7, 8, 9],
            "grid_offset": (-320, 40),
            "columns": 3,
            "x_step": 64,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Vieste centro storico",
            "lat": 41.8809236,
            "lon": 16.1792922,
            "address": "Viale Federico Secondo di Svevia, 71019 Vieste FG, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, 48),
        },
        {
            "number": 2,
            "name": "Baia delle Zagare",
            "lat": 41.7311,
            "lon": 16.0857,
            "address": "Comune di Mattinata, FG, Italy (cove has no street address)",
            "type": "Optional beach detour",
            "color": ROUTE_ALTERNATIVE,
            "offset": (0, -50),
        },
        {
            "number": 3,
            "name": "Pasticceria La Torre",
            "lat": 41.7110463,
            "lon": 16.0511548,
            "address": "Via Giacomo Matteotti, 71030 Mattinata FG, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "mattinata",
        },
        {
            "number": 4,
            "name": "Giardino di Monsignore",
            "lat": 41.7013622,
            "lon": 16.0655401,
            "address": "Contrada Torre del Porto / Contrada Funni, 71030 Mattinata FG, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "mattinata",
        },
        {
            "number": 5,
            "name": "Locanda del Maniscalco",
            "lat": 41.7086724,
            "lon": 16.0505958,
            "address": "Via Luigi Zuppetta 12/14, 71030 Mattinata FG, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "mattinata",
        },
        {
            "number": 6,
            "name": "Dal Saraceno",
            "lat": 41.7095571,
            "lon": 16.0515220,
            "address": "Via Vincenzo Amicarelli 31a, 71030 Mattinata FG, Italy",
            "type": "Dinner / budget",
            "color": ROUTE_PRIMARY,
            "cluster": "mattinata",
        },
        {
            "number": 7,
            "name": "Oleificio Le Monache",
            "lat": 41.7027376,
            "lon": 16.0518777,
            "address": "Contrada le Monache 1, 71030 Mattinata FG, Italy",
            "type": "Shop / food heritage",
            "color": ROUTE_PRIMARY,
            "cluster": "mattinata",
        },
        {
            "number": 8,
            "name": "B&B Dimora del Corso",
            "lat": 41.7120136,
            "lon": 16.0511594,
            "address": "Corso Matino 211, 71030 Mattinata FG, Italy",
            "type": "Accommodation",
            "color": MARKER_ACCOMMODATION,
            "cluster": "mattinata",
        },
        {
            "number": 9,
            "name": "Masseria Liberatore",
            "lat": 41.7071504,
            "lon": 16.0642058,
            "address": "Contrada Liberatore 2, 71030 Mattinata FG, Italy",
            "type": "Accommodation / alternate",
            "color": MARKER_ACCOMMODATION,
            "cluster": "mattinata",
        },
        {
            "number": 10,
            "name": "Abbazia della Santissima Trinità di Monte Sacro",
            "lat": 41.7580842,
            "lon": 16.0430873,
            "address": "Monte Sacro, 874m, near SS89, 71030 Mattinata FG, Italy",
            "type": "Optional historic site (steep unmarked trail)",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-40, -50),
        },
        {
            "number": 11,
            "name": "Monte Saraceno",
            "lat": 41.6942574,
            "lon": 16.0508242,
            "address": "Monte Saraceno, 71030 Mattinata FG, Italy",
            "type": "Optional guided hike",
            "color": ROUTE_ALTERNATIVE,
            "offset": (0, 50),
        },
        {
            "number": 12,
            "name": "B&B Dimora Mediterranea",
            "lat": 41.7142542,
            "lon": 16.0792899,
            "address": "Contrada Torre di Lupo 20, 71030 Mattinata FG, Italy",
            "type": "Accommodation / end / my pick",
            "color": MARKER_ACCOMMODATION,
            "offset": (60, 30),
        },
    ],
    "poi_verification": {
        1: "Start carried from verified Day 7 Vieste centro storico/Castello Svevo data.",
        2: "Itinerary gives only a low-precision 41.7311/16.0857 pair with an explicit note that the cove has no street address; retained as-is since no more precise OSM-indexed node was found for the specific access cove.",
        3: "Address and coordinates from existing itinerary for Pasticceria La Torre, checked against OpenStreetMap Via Giacomo Matteotti shop context.",
        4: "Itinerary gave only Contrada Torre del Porto; resolved via OpenStreetMap Nominatim to the named 'Il Giardino di Monsignore' restaurant node at Contrada Funni.",
        5: "Itinerary gave only Via Luigi Zuppetta 12/14; resolved via OpenStreetMap Nominatim to a named 'Locanda del Maniscalco' restaurant node on Via R. Bonghi.",
        6: "Itinerary gave only Via Vincenzo Amicarelli 31a; resolved via OpenStreetMap Nominatim to a named 'Dal Saraceno' restaurant node on Via V. Amicarelli.",
        7: "Address and coordinates from existing itinerary for Oleificio Le Monache, checked against OpenStreetMap Contrada le Monache shop context.",
        8: "Address and coordinates from existing itinerary for B&B Dimora del Corso, checked against OpenStreetMap Corso Matino context.",
        9: "Address and coordinates from existing itinerary for Masseria Liberatore, checked against OpenStreetMap Contrada Liberatore context.",
        10: "Itinerary gave only 'Monte Sacro, 874m' near the SS89; resolved via OpenStreetMap Nominatim to the named abbey ruins object. Mapped for orientation; the itinerary itself flags the trail as steep and unmarked.",
        11: "Resolved via OpenStreetMap Nominatim to the Monte Saraceno peak object south of Mattinata. Mapped for orientation; the guided sunrise hike (6:00am departure) and the separate 'Love Trail' (5:30pm departure) both run outside the day's main driving window, so neither is built into the timing planner.",
        12: "Address and coordinates from existing itinerary for B&B Dimora Mediterranea, checked against OpenStreetMap Contrada Torre di Lupo context; also used as the day's route endpoint since it is marked 'My pick'.",
    },
}

DAY12 = {
    "title": "Day 9 orientation map",
    "output": ROOT / "assets/maps/day12-monte-santangelo-trani-route.png",
    "zoom": 9,
    "size": (1800, 1125),
    "padding_px": 140,
    "places": {
        "Mattinata start": (41.7142542, 16.0792899),
        "Monte Sant'Angelo": (41.7080134, 15.9547699),
        "Trani": (41.2821965, 16.4183605),
        "Molfetta": (41.2063077, 16.5979521),
        "Bari": (41.1273126, 16.8671134),
    },
    "routes": {
        "molfetta": {
            "color": ROUTE_ALTERNATIVE,
            "width": 8,
            "coords": ["Trani", "Molfetta"],
            "dashed": True,
        },
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Mattinata start", "Monte Sant'Angelo", "Trani", "Bari"],
        },
    },
    "route_order": ["molfetta", "recommended"],
    "legend": [
        {"label": "Recommended route (to Bari)", "color": ROUTE_PRIMARY},
        {"label": "Molfetta overnight alternative", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "santangelo": {
            "anchor": "Monte Sant'Angelo",
            "numbers": [2, 3, 4, 5, 6, 7],
            "grid_offset": (-320, -40),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "trani": {
            "anchor": "Trani",
            "numbers": [8, 9, 10],
            "grid_offset": (-280, 20),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "molfetta": {
            "anchor": "Molfetta",
            "numbers": [11, 12, 13, 14],
            "grid_offset": (-40, 90),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "bari": {
            "anchor": "Bari",
            "numbers": [15, 16, 17, 18, 19, 20],
            "grid_offset": (60, 90),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Mattinata (Day 8 accommodation)",
            "lat": 41.7142542,
            "lon": 16.0792899,
            "address": "Contrada Torre di Lupo 20, 71030 Mattinata FG, Italy",
            "type": "Start",
            "color": ROUTE_PRIMARY,
            "offset": (0, 48),
        },
        {
            "number": 2,
            "name": "Santuario di San Michele Arcangelo",
            "lat": 41.7080134,
            "lon": 15.9547699,
            "address": "Via Reale Basilica 127, 71037 Monte Sant'Angelo FG, Italy",
            "type": "Historic site / sanctuary",
            "color": ROUTE_PRIMARY,
            "cluster": "santangelo",
        },
        {
            "number": 3,
            "name": "Rione Junno & Rione Grotte",
            "lat": 41.7073834,
            "lon": 15.9533918,
            "address": "Via Castello / Junno, 71037 Monte Sant'Angelo FG, Italy",
            "type": "Historic quarter",
            "color": ROUTE_PRIMARY,
            "cluster": "santangelo",
        },
        {
            "number": 4,
            "name": "Pasticceria Ciuffreda",
            "lat": 41.7074364,
            "lon": 15.9541869,
            "address": "Via Giuseppe Garibaldi 15, 71037 Monte Sant'Angelo FG, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "santangelo",
        },
        {
            "number": 5,
            "name": "Ristorante Medioevo",
            "lat": 41.7073834,
            "lon": 15.9533918,
            "address": "Via Castello 21, 71037 Monte Sant'Angelo FG, Italy",
            "type": "Lunch",
            "color": ROUTE_PRIMARY,
            "cluster": "santangelo",
        },
        {
            "number": 6,
            "name": "Al Barone",
            "lat": 41.7080134,
            "lon": 15.9547699,
            "address": "Centro storico near the Basilica, 71037 Monte Sant'Angelo FG, Italy",
            "type": "Lunch / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "santangelo",
        },
        {
            "number": 7,
            "name": "Ristorante San Michele",
            "lat": 41.7080134,
            "lon": 15.9547699,
            "address": "Via Reale Basilica 51, 71037 Monte Sant'Angelo FG, Italy",
            "type": "Lunch / budget",
            "color": ROUTE_PRIMARY,
            "cluster": "santangelo",
        },
        {
            "number": 8,
            "name": "Trani — the Cathedral on the Sea",
            "lat": 41.2821965,
            "lon": 16.4183605,
            "address": "Piazza Duomo 1, 76125 Trani BT, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "trani",
        },
        {
            "number": 9,
            "name": "Sinagoga Scolanova",
            "lat": 41.2797529,
            "lon": 16.4177563,
            "address": "Via Scola Nova, Giudecca quarter, 76125 Trani BT, Italy",
            "type": "Optional historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "trani",
        },
        {
            "number": 10,
            "name": "Bar Europa",
            "lat": 41.2766535,
            "lon": 16.4174057,
            "address": "Corso Vittorio Emanuele 161, 76125 Trani BT, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "trani",
        },
        {
            "number": 11,
            "name": "Molfetta old town & Duomo di San Corrado",
            "lat": 41.2063077,
            "lon": 16.5979521,
            "address": "Vico Campanile, 70056 Molfetta BA, Italy",
            "type": "Overnight alternative",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "molfetta",
        },
        {
            "number": 12,
            "name": "Dentro Le Mura",
            "lat": 41.2063077,
            "lon": 16.5979521,
            "address": "Corso Dante Alighieri 42, 70056 Molfetta BA, Italy",
            "type": "Dinner",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "molfetta",
        },
        {
            "number": 13,
            "name": "La Cucina del Mare",
            "lat": 41.2063077,
            "lon": 16.5979521,
            "address": "Via Alfredo Baccarini, 70056 Molfetta BA, Italy",
            "type": "Dinner / budget",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "molfetta",
        },
        {
            "number": 14,
            "name": "Il Mulino di Amleto",
            "lat": 41.2063077,
            "lon": 16.5979521,
            "address": "Vicolo Campanile 6, 70056 Molfetta BA, Italy",
            "type": "Accommodation, alternative",
            "color": MARKER_ACCOMMODATION,
            "cluster": "molfetta",
        },
        {
            "number": 15,
            "name": "Strada Arco Basso, Bari Vecchia",
            "lat": 41.1273126,
            "lon": 16.8671134,
            "address": "Arco Basso, 70122 Bari BA, Italy",
            "type": "Overnight town (preferred)",
            "color": ROUTE_PRIMARY,
            "cluster": "bari",
        },
        {
            "number": 16,
            "name": "Al Pescatore",
            "lat": 41.1289060,
            "lon": 16.8676604,
            "address": "Piazza Federico II di Svevia 6/8, 70122 Bari BA, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "bari",
        },
        {
            "number": 17,
            "name": "Al Sorso Preferito",
            "lat": 41.1235574,
            "lon": 16.8750988,
            "address": "Via Vito Nicola de Nicolò 46, 70121 Bari BA, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "bari",
        },
        {
            "number": 18,
            "name": "Panificio Fiore",
            "lat": 41.1296977,
            "lon": 16.8709494,
            "address": "Strada Palazzo di Città 38, 70122 Bari BA, Italy",
            "type": "Food stop / budget",
            "color": ROUTE_PRIMARY,
            "cluster": "bari",
        },
        {
            "number": 19,
            "name": "Basilica di San Nicola",
            "lat": 41.1302708,
            "lon": 16.8701858,
            "address": "Largo Abate Elia 13, 70122 Bari BA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "bari",
        },
        {
            "number": 20,
            "name": "Bari Vecchia Dimora",
            "lat": 41.1273126,
            "lon": 16.8671134,
            "address": "Corte Lamberti 6, 70122 Bari BA, Italy",
            "type": "Accommodation (preferred)",
            "color": MARKER_ACCOMMODATION,
            "cluster": "bari",
        },
    ],
    "poi_verification": {
        1: "Start carried from verified Day 8 B&B Dimora Mediterranea accommodation data.",
        2: "Address and coordinates from existing itinerary for the Santuario di San Michele Arcangelo, checked against OpenStreetMap sanctuary context.",
        3: "Itinerary gave no address; resolved via OpenStreetMap Nominatim to the Castello/Junno quarter area, the practical arrival point for both historic quarters.",
        4: "Address and coordinates from existing itinerary for Pasticceria Ciuffreda, checked against OpenStreetMap Via Giuseppe Garibaldi shop context.",
        5: "Itinerary gave Via Castello 21; resolved via OpenStreetMap Nominatim to the Castello/Via Castello area (no OSM-indexed restaurant node), not an exact building pin.",
        6: "Itinerary gave only 'centro storico near the Basilica'; approximated to the Sanctuary coordinate, not an exact building pin.",
        7: "Itinerary gave Via Reale Basilica 51, immediately next to the Sanctuary; approximated to the Sanctuary coordinate, not an exact building pin.",
        8: "Address and coordinates from existing itinerary for the Cattedrale di Trani, checked against OpenStreetMap cathedral context.",
        9: "Address and coordinates from existing itinerary for Sinagoga Scolanova, checked against OpenStreetMap place-of-worship object on Via Scola Nova.",
        10: "Address and coordinates from existing itinerary for Bar Europa, checked against OpenStreetMap Corso Vittorio Emanuele shop context.",
        11: "Resolved via OpenStreetMap Nominatim to the Duomo di San Corrado on Vico Campanile, used as the Molfetta old-town/overnight anchor; note this street name matches the itinerary's 'Vicolo Campanile 6' address for Il Mulino di Amleto.",
        12: "Itinerary gave Corso Dante Alighieri 42 with no OSM-indexed restaurant node; approximated to the Molfetta old-town anchor, not an exact building pin.",
        13: "Itinerary gave Via Alfredo Baccarini with no OSM-indexed restaurant node; approximated to the Molfetta old-town anchor, not an exact building pin.",
        14: "Itinerary gave Vicolo Campanile 6, which matches the street of the geocoded Duomo di San Corrado; approximated to that anchor, not an exact building pin.",
        15: "Address and coordinates from existing itinerary for Strada Arco Basso, checked against OpenStreetMap Bari Vecchia street context; used as the Bari overnight anchor.",
        16: "Address and coordinates from existing itinerary for Al Pescatore, checked against OpenStreetMap named restaurant node at Piazza Federico Secondo di Svevia.",
        17: "Itinerary named 'Al Sorso Preferito / Urban Assassineria'; resolved via OpenStreetMap Nominatim to the named 'Al Sorso Preferito' restaurant node on Via Vito Nicola de Nicolò.",
        18: "Resolved via OpenStreetMap Nominatim to the named 'Panificio Fiore' bakery node on Strada Palazzo di Città.",
        19: "Resolved via OpenStreetMap Nominatim to the Basilica di San Nicola place-of-worship object.",
        20: "Itinerary gave Corte Lamberti 6 with no OSM-indexed node; approximated to the Bari Vecchia/Strada Arco Basso anchor, not an exact building pin.",
    },
}

DAY13 = {
    "title": "Day 10 orientation map",
    "output": ROOT / "assets/maps/day13-polignano-ostuni-route.png",
    "zoom": 9,
    "size": (1800, 1125),
    "padding_px": 140,
    "places": {
        "Molfetta": (41.2063077, 16.5979521),
        "Bari": (41.1273126, 16.8671134),
        "Polignano": (40.9963887, 17.2181307),
        "Monopoli": (40.9508368, 17.3033327),
        "Ostuni": (40.7333725, 17.5778841),
        "San Vito dei Normanni": (40.6563995, 17.7087266),
    },
    "routes": {
        "from_molfetta": {
            "color": ROUTE_ALTERNATIVE,
            "width": 8,
            "coords": ["Molfetta", "Polignano"],
            "dashed": True,
        },
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Bari", "Polignano", "Monopoli", "Ostuni", "San Vito dei Normanni"],
        },
    },
    "route_order": ["from_molfetta", "recommended"],
    "legend": [
        {"label": "Main day route (from Bari)", "color": ROUTE_PRIMARY},
        {"label": "From Molfetta (Day 9 alternative)", "color": ROUTE_ALTERNATIVE, "dashed": True},
    ],
    "poi_clusters": {
        "monopoli": {
            "anchor": "Monopoli",
            "numbers": [5, 6, 7, 8],
            "grid_offset": (-320, -60),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "ostuni": {
            "anchor": "Ostuni",
            "numbers": [9, 10, 11],
            "grid_offset": (-260, 40),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "sanvito": {
            "anchor": "San Vito dei Normanni",
            "numbers": [12, 13, 14],
            "grid_offset": (60, 40),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Molfetta (Day 9 alternative)",
            "lat": 41.2063077,
            "lon": 16.5979521,
            "address": "Vico Campanile, 70056 Molfetta BA, Italy",
            "type": "Start alternative",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-60, -50),
        },
        {
            "number": 2,
            "name": "Bari (Day 9 preferred)",
            "lat": 41.1273126,
            "lon": 16.8671134,
            "address": "Arco Basso, 70122 Bari BA, Italy",
            "type": "Start (preferred)",
            "color": ROUTE_PRIMARY,
            "offset": (60, -50),
        },
        {
            "number": 3,
            "name": "Polignano a Mare — Lama Monachile",
            "lat": 40.9963887,
            "lon": 17.2181307,
            "address": "Via S. Vito, 70044 Polignano a Mare BA, Italy",
            "type": "Beach / cove",
            "color": ROUTE_PRIMARY,
            "offset": (0, -50),
        },
        {
            "number": 4,
            "name": "Dorsale",
            "lat": 40.9929810,
            "lon": 17.2178068,
            "address": "Via Martiri di Dogali, Centro storico, 70044 Polignano a Mare BA, Italy",
            "type": "Food stop / hidden gem",
            "color": ROUTE_PRIMARY,
            "offset": (0, 50),
        },
        {
            "number": 5,
            "name": "Monopoli — Centro Storico",
            "lat": 40.9508368,
            "lon": 17.3033327,
            "address": "Largo Cattedrale, 70043 Monopoli BA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "monopoli",
        },
        {
            "number": 6,
            "name": "Rifugi Antiaerei di Monopoli",
            "lat": 40.9522073,
            "lon": 17.3000255,
            "address": "Piazza Vittorio Emanuele II, 70043 Monopoli BA, Italy",
            "type": "Optional historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "monopoli",
        },
        {
            "number": 7,
            "name": "Madià (Porto Antico)",
            "lat": 40.9530079,
            "lon": 17.3041064,
            "address": "Porto Antico, 70043 Monopoli BA, Italy",
            "type": "Lunch",
            "color": ROUTE_PRIMARY,
            "cluster": "monopoli",
        },
        {
            "number": 8,
            "name": "Locanda dei Mercanti",
            "lat": 40.9508368,
            "lon": 17.3033327,
            "address": "Centro storico, 70043 Monopoli BA, Italy",
            "type": "Lunch / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "monopoli",
        },
        {
            "number": 9,
            "name": "Ostuni — Centro Storico",
            "lat": 40.7333725,
            "lon": 17.5778841,
            "address": "Centro Storico, 72017 Ostuni BR, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "ostuni",
        },
        {
            "number": 10,
            "name": "Forno 31",
            "lat": 40.7333725,
            "lon": 17.5778841,
            "address": "Via G. Ferrari 6, 72017 Ostuni BR, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "ostuni",
        },
        {
            "number": 11,
            "name": "Riccardo Caffè",
            "lat": 40.7339749,
            "lon": 17.5803666,
            "address": "Via Gaetano Tanzarella Vitale 61, 72017 Ostuni BR, Italy",
            "type": "Hidden gem / aperitivo",
            "color": ROUTE_PRIMARY,
            "cluster": "ostuni",
        },
        {
            "number": 12,
            "name": "San Vito dei Normanni (arrival)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / end",
            "color": MARKER_ACCOMMODATION,
            "cluster": "sanvito",
        },
        {
            "number": 13,
            "name": "XFood",
            "lat": 40.6589314,
            "lon": 17.7126581,
            "address": "Via Mare snc, inside ExFadda cultural centre, 72019 San Vito dei Normanni BR, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "sanvito",
        },
        {
            "number": 14,
            "name": "Virgola Pasticceria Terapeutica",
            "lat": 40.6541726,
            "lon": 17.7099910,
            "address": "Via Mesagne 136, 72019 San Vito dei Normanni BR, Italy",
            "type": "Food stop (next morning)",
            "color": ROUTE_PRIMARY,
            "cluster": "sanvito",
        },
    ],
    "poi_verification": {
        1: "Start (option A) carried from verified Day 9 Molfetta old-town anchor data.",
        2: "Start (option B) carried from verified Day 9 Bari Vecchia/Strada Arco Basso anchor data.",
        3: "Address and coordinates from existing itinerary for Lama Monachile, checked against OpenStreetMap coastal/cove context.",
        4: "Resolved via OpenStreetMap Nominatim to the named 'Dorsale' seafood shop on Via Martiri di Dogali.",
        5: "Address and coordinates from existing itinerary for Monopoli's Largo Cattedrale, checked against OpenStreetMap cathedral/old-town context.",
        6: "Itinerary gave only 'under Piazza Vittorio Emanuele II'; resolved via OpenStreetMap Nominatim to that square.",
        7: "Itinerary gave only 'Porto Antico'; resolved via OpenStreetMap Nominatim to the named 'Porto antico' waterfront attraction node.",
        8: "Itinerary gave no address; approximated to the Monopoli centro storico/cathedral anchor, not an exact building pin.",
        9: "Address and coordinates from existing itinerary for Ostuni's Centro Storico, checked against OpenStreetMap old-town context.",
        10: "Itinerary gave Via G. Ferrari 6 with no OSM-indexed node; approximated to the Ostuni centro storico anchor, not an exact building pin.",
        11: "Address and coordinates from existing itinerary for Riccardo Caffè, checked against OpenStreetMap named bar node on Via Gaetano Tanzarella Vitale.",
        12: "Address and coordinates from existing itinerary for the San Vito dei Normanni arrival point; used as the day's route endpoint and overnight base.",
        13: "Resolved via OpenStreetMap Nominatim to the named 'xFood' restaurant node on Via Mare, matching the itinerary's ExFadda cultural centre location.",
        14: "Itinerary gave Via Mesagne 136 with no OSM-indexed node; approximated to the nearer of two OpenStreetMap Via Mesagne street segments to the town centre, not an exact building pin.",
    },
}


DAY14 = {
    "title": "Day 14 orientation map",
    "output": ROOT / "assets/maps/day14-trulli-triangle-route.png",
    "zoom": 11,
    "size": (1800, 1500),
    "padding_px": 260,
    "places": {
        "San Vito dei Normanni": (40.6563995, 17.7087266),
        "Alberobello": (40.7817, 17.2364),
        "Locorotondo": (40.7530, 17.3285),
        "Martina Franca": (40.7057, 17.3370),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["San Vito dei Normanni", "Alberobello", "Locorotondo", "Martina Franca", "San Vito dei Normanni"],
        },
    },
    "route_order": ["recommended"],
    "legend": [
        {"label": "Trulli Triangle loop from San Vito dei Normanni", "color": ROUTE_PRIMARY},
    ],
    "poi_clusters": {
        "alberobello": {
            "anchor": "Alberobello",
            "numbers": [2, 3, 4, 5, 6, 7],
            "grid_offset": (120, 90),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
        "locorotondo": {
            "anchor": "Locorotondo",
            "numbers": [8, 9, 10],
            "grid_offset": (70, -160),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "martinafranca": {
            "anchor": "Martina Franca",
            "numbers": [11, 12, 13, 14],
            "grid_offset": (60, 90),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Vito dei Normanni (start/end)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / start-end",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
        {
            "number": 2,
            "name": "Rione Monti",
            "lat": 40.7817,
            "lon": 17.2364,
            "address": "Via Monte San Michele, 70011 Alberobello BA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "alberobello",
        },
        {
            "number": 3,
            "name": "Aia Piccola",
            "lat": 40.7837,
            "lon": 17.2407,
            "address": "Via Cristoforo Colombo, 70011 Alberobello BA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "alberobello",
        },
        {
            "number": 4,
            "name": "Trullo Sovrano",
            "lat": 40.7874,
            "lon": 17.2353,
            "address": "Piazza Sacramento 10/11, 70011 Alberobello BA, Italy",
            "type": "Museum",
            "color": ROUTE_PRIMARY,
            "cluster": "alberobello",
        },
        {
            "number": 5,
            "name": "Chiesa di Sant'Antonio",
            "lat": 40.7813,
            "lon": 17.2352,
            "address": "Via Monte Pertica 18, 70011 Alberobello BA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "alberobello",
        },
        {
            "number": 6,
            "name": "Bar \"Il Trulletto\"",
            "lat": 40.7823,
            "lon": 17.2371,
            "address": "Via Monte San Michele 50, 70011 Alberobello BA, Italy",
            "type": "Coffee",
            "color": ROUTE_PRIMARY,
            "cluster": "alberobello",
        },
        {
            "number": 7,
            "name": "Largo Martellotta (parking)",
            "lat": 40.7830,
            "lon": 17.2373,
            "address": "Largo Martellotta, 70011 Alberobello BA, Italy",
            "type": "Parking",
            "color": ROUTE_PRIMARY,
            "cluster": "alberobello",
        },
        {
            "number": 8,
            "name": "Locorotondo — Piazza Vittorio Emanuele",
            "lat": 40.7530,
            "lon": 17.3285,
            "address": "Piazza Vittorio Emanuele, 70010 Locorotondo BA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "locorotondo",
        },
        {
            "number": 9,
            "name": "Bar Poldo",
            "lat": 40.7548,
            "lon": 17.3277,
            "address": "Via Cavour 149, 70010 Locorotondo BA, Italy",
            "type": "Coffee",
            "color": ROUTE_PRIMARY,
            "cluster": "locorotondo",
        },
        {
            "number": 10,
            "name": "Trattoria Al Vecchio Arco",
            "lat": 40.7530,
            "lon": 17.3289,
            "address": "Via Antonio Bruno 5, 70010 Locorotondo BA, Italy",
            "type": "Lunch",
            "color": ROUTE_PRIMARY,
            "cluster": "locorotondo",
        },
        {
            "number": 11,
            "name": "Basilica di San Martino",
            "lat": 40.7057,
            "lon": 17.3370,
            "address": "Via Masaniello 1, 74015 Martina Franca TA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "martinafranca",
        },
        {
            "number": 12,
            "name": "Palazzo Ducale",
            "lat": 40.7051,
            "lon": 17.3389,
            "address": "Piazza Roma 28, 74015 Martina Franca TA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "martinafranca",
        },
        {
            "number": 13,
            "name": "Macelleria Centro Storico",
            "lat": 40.7055,
            "lon": 17.3360,
            "address": "Via Giuseppe Garibaldi 4-6, 74015 Martina Franca TA, Italy",
            "type": "What to buy",
            "color": ROUTE_PRIMARY,
            "cluster": "martinafranca",
        },
        {
            "number": 14,
            "name": "Caffè Caroli",
            "lat": 40.7053,
            "lon": 17.3399,
            "address": "Via Giuseppe Aprile 12, 74015 Martina Franca TA, Italy",
            "type": "Coffee",
            "color": ROUTE_PRIMARY,
            "cluster": "martinafranca",
        },
    ],
    "poi_verification": {
        1: "Address and coordinates carried from the verified Day 13 San Vito dei Normanni arrival anchor; reused as this day's start/end point.",
        2: "Resolved via OpenStreetMap Nominatim to 'Bar Rione Monti, Via Monte San Michele' as a practical entrance-level anchor for the Rione Monti district.",
        3: "Resolved via OpenStreetMap Nominatim to the named 'Trulli Aia Piccola' node on Via Cristoforo Colombo.",
        4: "Resolved via OpenStreetMap Nominatim to Piazza Sacramento 10, matching the house museum's own published address and phone (+39 080 432 6030).",
        5: "Address (Via Monte Pertica 18) confirmed via the parish's own site (santantonioalberobello.it) and phone +39 080 432 4416; approximated to the nearest resolvable street-level OSM point.",
        6: "Address (Via Monte San Michele 50) from independent review aggregators; approximated to the nearest resolvable OSM street-level point, not an exact building pin.",
        7: "Resolved via OpenStreetMap Nominatim to Largo Martellotta, the closest paid lot to Rione Monti per the comune's own parking guidance.",
        8: "Address and coordinates from existing itinerary/Day 13-era data for Locorotondo's Piazza Vittorio Emanuele, checked against OpenStreetMap old-town context.",
        9: "Resolved via OpenStreetMap Nominatim to Via Cavour, matching the verified phone (+39 080 431 2695) and address Via Cavour 149.",
        10: "Resolved via OpenStreetMap Nominatim to Via Antonio Bruno; address and phone (+39 080 972 1763) independently verified against directory listings.",
        11: "Resolved via OpenStreetMap Nominatim to the named 'Basilica di San Martino' node; address Via Masaniello 1 confirmed via the basilica's own site.",
        12: "Resolved via OpenStreetMap Nominatim to Piazza Roma, matching the palace's own published Piazza Roma 28 address.",
        13: "Itinerary gave Via Giuseppe Garibaldi 4-6 with no OSM-indexed street node; approximated to the nearby Piazza Maria Immacolata anchor, not an exact building pin — flagged as an approximation, not a precise pin.",
        14: "Resolved via OpenStreetMap Nominatim to Via Giuseppe Aprile, matching the roastery's own published Via Giuseppe Aprile 12 address and phone.",
    },
}


DAY15 = {
    "title": "Day 15 orientation map",
    "output": ROOT / "assets/maps/day15-via-traiana-cisternino-route.png",
    "zoom": 11,
    "size": (1800, 1400),
    "padding_px": 240,
    "places": {
        "San Vito dei Normanni": (40.6563995, 17.7087266),
        "Masseria Brancati": (40.7642, 17.5523),
        "Cisternino": (40.7418, 17.4265),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["San Vito dei Normanni", "Masseria Brancati", "Cisternino", "San Vito dei Normanni"],
        },
    },
    "route_order": ["recommended"],
    "legend": [
        {"label": "Via Traiana & Cisternino loop from San Vito dei Normanni", "color": ROUTE_PRIMARY},
    ],
    "poi_clusters": {
        "cisternino": {
            "anchor": "Cisternino",
            "numbers": [3, 4, 5, 6, 7],
            "grid_offset": (70, -140),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Vito dei Normanni (start/end)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / start-end",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
        {
            "number": 2,
            "name": "Masseria Brancati",
            "lat": 40.7642,
            "lon": 17.5523,
            "address": "Contrada Brancati s.n.c., 72017 Ostuni BR, Italy",
            "type": "Historic site / olive mill",
            "color": ROUTE_PRIMARY,
            "offset": (0, -60),
        },
        {
            "number": 3,
            "name": "Cisternino — Piazza Vittorio Emanuele II",
            "lat": 40.7418,
            "lon": 17.4265,
            "address": "Piazza Vittorio Emanuele II, 72014 Cisternino BR, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "cisternino",
        },
        {
            "number": 4,
            "name": "Bar FOD",
            "lat": 40.7418,
            "lon": 17.4265,
            "address": "Piazza Vittorio Emanuele II, 72014 Cisternino BR, Italy",
            "type": "Coffee",
            "color": ROUTE_PRIMARY,
            "cluster": "cisternino",
        },
        {
            "number": 5,
            "name": "Zio Pietro",
            "lat": 40.7416,
            "lon": 17.4266,
            "address": "Via Duca D'Aosta 3, 72014 Cisternino BR, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "cisternino",
        },
        {
            "number": 6,
            "name": "Arrosteria del Vicoletto",
            "lat": 40.7421,
            "lon": 17.4265,
            "address": "Via Giulio II 16, 72014 Cisternino BR, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "cisternino",
        },
        {
            "number": 7,
            "name": "Premiata Macelleria Santoro",
            "lat": 40.7429,
            "lon": 17.4270,
            "address": "Via Domenico Cirillo 212, 72014 Cisternino BR, Italy",
            "type": "Dinner / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "cisternino",
        },
        {
            "number": 8,
            "name": "Ashram Centro Bhole Baba",
            "lat": 40.7165,
            "lon": 17.4029,
            "address": "Contrada Portarino 10, 72014 Cisternino BR, Italy",
            "type": "Hidden gem / quirky",
            "color": ROUTE_ALTERNATIVE,
            "offset": (-90, 70),
        },
    ],
    "poi_verification": {
        1: "Address and coordinates carried from the verified Day 13 San Vito dei Normanni arrival anchor; reused as this day's start/end point.",
        2: "Resolved via OpenStreetMap Nominatim to the named 'Trappeto ipogeo Contrada Brancati' node, matching the masseria's own published Contrada Brancati address.",
        3: "Resolved via OpenStreetMap Nominatim to Piazza Vittorio Emanuele II, Cisternino.",
        4: "Address (Piazza Vittorio Emanuele II) from independent review sources for this historic 1921 bar; shares the piazza anchor with marker 3, not an exact storefront pin.",
        5: "Resolved via OpenStreetMap Nominatim directly to the named 'Zio Pietro' business node on Via Duca D'Aosta.",
        6: "Resolved via OpenStreetMap Nominatim to Via Giulio II; address and phone (+39 333 898 4655) independently verified against directory listings.",
        7: "Itinerary gave Via Domenico Cirillo 212 with no OSM-indexed exact node; approximated to the nearest resolvable Via Domenico Cirillo street segment, not an exact building pin.",
        8: "Rural contrada address with no OSM-indexed node. Coordinates (40.7165, 17.4029) come from an independent aggregator, cross-checked as geographically plausible (a few km southwest of Cisternino) after a separate, clearly erroneous aggregator coordinate (41.8°N, in the Alps) was identified and discarded. Flagged in the day's content as approximate, not an official pin — this is a residential/religious community, not a mapped tourist site.",
    },
}


DAY16 = {
    "title": "Day 16 orientation map",
    "output": ROOT / "assets/maps/day16-gallipoli-route.png",
    "zoom": 10,
    "size": (1800, 1400),
    "padding_px": 240,
    "places": {
        "San Vito dei Normanni": (40.6563995, 17.7087266),
        "Gallipoli": (40.0559, 17.9811),
        "Baia Verde": (40.0373, 18.0155),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["San Vito dei Normanni", "Gallipoli", "Baia Verde", "San Vito dei Normanni"],
        },
    },
    "route_order": ["recommended"],
    "legend": [
        {"label": "Gallipoli & Ionian coast loop from San Vito dei Normanni", "color": ROUTE_PRIMARY},
    ],
    "poi_clusters": {
        "gallipoli": {
            "anchor": "Gallipoli",
            "numbers": [2, 3, 4, 5, 6],
            "grid_offset": (60, -160),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Vito dei Normanni (start/end)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / start-end",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
        {
            "number": 2,
            "name": "Basilica Cattedrale di Sant'Agata",
            "lat": 40.0546,
            "lon": 17.9763,
            "address": "Via Duomo 1, 73014 Gallipoli LE, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "gallipoli",
        },
        {
            "number": 3,
            "name": "Fontana Greca",
            "lat": 40.0559,
            "lon": 17.9811,
            "address": "Piazza Fontana Greca, 73014 Gallipoli LE, Italy",
            "type": "Historic site / quirky",
            "color": ROUTE_PRIMARY,
            "cluster": "gallipoli",
        },
        {
            "number": 4,
            "name": "Frantoio Ipogeo di Palazzo Granafei",
            "lat": 40.0550,
            "lon": 17.9773,
            "address": "Via Antonietta de Pace 87, 73014 Gallipoli LE, Italy",
            "type": "Museum",
            "color": ROUTE_PRIMARY,
            "cluster": "gallipoli",
        },
        {
            "number": 5,
            "name": "Il Frantoio del Viceré",
            "lat": 40.0545,
            "lon": 17.9756,
            "address": "Via Santa Maria 6, 73014 Gallipoli LE, Italy",
            "type": "Museum / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "gallipoli",
        },
        {
            "number": 6,
            "name": "Trattoria La Puritate",
            "lat": 40.0550,
            "lon": 17.9751,
            "address": "Via Sant'Elia 18, 73014 Gallipoli LE, Italy",
            "type": "Lunch / dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "gallipoli",
        },
        {
            "number": 7,
            "name": "Baia Verde",
            "lat": 40.0373,
            "lon": 18.0155,
            "address": "Viale delle Dune, Baia Verde, 73014 Gallipoli LE, Italy",
            "type": "Beach",
            "color": ROUTE_PRIMARY,
            "offset": (0, 60),
        },
    ],
    "poi_verification": {
        1: "Address and coordinates carried from the verified Day 13 San Vito dei Normanni arrival anchor; reused as this day's start/end point.",
        2: "Resolved via OpenStreetMap Nominatim to Via Duomo, matching the cathedral's own published Via Duomo 1 address.",
        3: "Resolved via OpenStreetMap Nominatim directly to the named 'Fontana Greca' node on Piazza Fontana Greca.",
        4: "Resolved via OpenStreetMap Nominatim to Via Antonietta de Pace; address matches the Associazione Gallipoli Nostra's own published location.",
        5: "Resolved via OpenStreetMap Nominatim to Via Santa Maria; address and phone (+39 348 133 6632) independently verified against the venue's own listings.",
        6: "Resolved via OpenStreetMap Nominatim to Via Sant'Elia, matching independently-cited address for this restaurant.",
        7: "Resolved via OpenStreetMap Nominatim to Viale delle Dune, Baia Verde.",
    },
}


DAY17 = {
    "title": "Day 17 orientation map",
    "output": ROOT / "assets/maps/day17-lecce-route.png",
    "zoom": 10,
    "size": (1800, 1400),
    "padding_px": 240,
    "places": {
        "San Vito dei Normanni": (40.6563995, 17.7087266),
        "Lecce": (40.3528, 18.1726),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["San Vito dei Normanni", "Lecce"],
        },
    },
    "route_order": ["recommended"],
    "legend": [
        {"label": "Lecce day trip from San Vito dei Normanni", "color": ROUTE_PRIMARY},
    ],
    "poi_clusters": {
        "lecce": {
            "anchor": "Lecce",
            "numbers": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "grid_offset": (60, -220),
            "columns": 3,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Vito dei Normanni (start/end)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / start-end",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
        {
            "number": 2,
            "name": "Basilica di Santa Croce",
            "lat": 40.3547,
            "lon": 18.1733,
            "address": "Via Umberto I 1, 73100 Lecce LE, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 3,
            "name": "Roman Amphitheatre",
            "lat": 40.3528,
            "lon": 18.1726,
            "address": "Piazza Sant'Oronzo, 73100 Lecce LE, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 4,
            "name": "Teatro Romano",
            "lat": 40.3518,
            "lon": 18.1703,
            "address": "Via Degli Ammirati 5, 73100 Lecce LE, Italy",
            "type": "Historic site / optional",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 5,
            "name": "Caffè Alvino",
            "lat": 40.3528,
            "lon": 18.1726,
            "address": "Piazza Sant'Oronzo 30, 73100 Lecce LE, Italy",
            "type": "Pasticceria",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 6,
            "name": "Pasticceria Natale",
            "lat": 40.3533,
            "lon": 18.1734,
            "address": "Via Salvatore Trinchese 7, 73100 Lecce LE, Italy",
            "type": "Pasticceria / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 7,
            "name": "Alle Due Corti",
            "lat": 40.3549,
            "lon": 18.1705,
            "address": "Corte dei Giugni 1, 73100 Lecce LE, Italy",
            "type": "Lunch / dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 8,
            "name": "Museo Faggiano",
            "lat": 40.3501,
            "lon": 18.1724,
            "address": "Via Ascanio Grandi 56, 73100 Lecce LE, Italy",
            "type": "Hidden gem / museum",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 9,
            "name": "Chiesa di San Francesco della Scarpa",
            "lat": 40.3497,
            "lon": 18.1692,
            "address": "Piazzetta Giosuè Carducci, 73100 Lecce LE, Italy",
            "type": "Hidden gem / quirky",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 10,
            "name": "Cartapesta Bottega Artigiana",
            "lat": 40.3519,
            "lon": 18.1690,
            "address": "Via Palmieri (near the Cathedral), 73100 Lecce LE, Italy",
            "type": "What to buy",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
        {
            "number": 11,
            "name": "Cartapesta Riso",
            "lat": 40.3525,
            "lon": 18.1697,
            "address": "Via Vittorio Emanuele II 27, 73100 Lecce LE, Italy",
            "type": "What to buy / alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "lecce",
        },
    ],
    "poi_verification": {
        1: "Address and coordinates carried from the verified Day 13 San Vito dei Normanni arrival anchor; reused as this day's start/end point.",
        2: "Resolved via OpenStreetMap Nominatim directly to the named 'Basilica di Santa Croce' node.",
        3: "Resolved via OpenStreetMap Nominatim to Piazza Sant'Oronzo.",
        4: "Resolved via OpenStreetMap Nominatim to Via Degli Ammirati 5.",
        5: "Shares the Piazza Sant'Oronzo anchor (marker 3) — Caffè Alvino faces the square directly at no. 30, not an independently resolvable OSM node.",
        6: "Resolved via OpenStreetMap Nominatim directly to the named 'Pasticceria Gelateria Natale' node on Via Salvatore Trinchese.",
        7: "Resolved via OpenStreetMap Nominatim to Corte dei Giugni, matching the restaurant's own published address.",
        8: "Resolved via OpenStreetMap Nominatim directly to the named 'Museo Archeologico Faggiano' node on Via Ascanio Grandi.",
        9: "Resolved via OpenStreetMap Nominatim to Convitto Palmieri (Corte Sabatino De Ursis), the building complex the church is embedded within; Piazzetta Giosuè Carducci itself has no separate OSM node, so this is the nearest resolvable anchor.",
        10: "Itinerary gave only 'Via Palmieri, near the Cathedral' with no OSM-indexed workshop node; approximated to the Piazza Duomo anchor, not an exact storefront pin — flagged as approximate.",
        11: "Resolved via OpenStreetMap Nominatim directly to the named 'Cartapesta Claudio Riso Presepi' node on Via Vittorio Emanuele II.",
    },
}


DAY18 = {
    "title": "Day 18 orientation map",
    "output": ROOT / "assets/maps/day18-altamura-matera-route.png",
    "zoom": 9,
    "size": (1800, 1400),
    "padding_px": 220,
    "places": {
        "San Vito dei Normanni": (40.6563995, 17.7087266),
        "Altamura": (40.8263, 16.5530),
        "Matera": (40.6664, 16.6043),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["San Vito dei Normanni", "Altamura", "Matera", "San Vito dei Normanni"],
        },
    },
    "route_order": ["recommended"],
    "legend": [
        {"label": "Altamura & Matera loop from San Vito dei Normanni", "color": ROUTE_PRIMARY},
    ],
    "poi_clusters": {
        "altamura": {
            "anchor": "Altamura",
            "numbers": [2, 3, 4],
            "grid_offset": (-260, -80),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "matera": {
            "anchor": "Matera",
            "numbers": [5, 6, 7, 8, 9, 10],
            "grid_offset": (60, -180),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Vito dei Normanni (start/end)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / start-end",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
        {
            "number": 2,
            "name": "Cattedrale di Altamura",
            "lat": 40.8263,
            "lon": 16.5530,
            "address": "Corso Federico II di Svevia, 70022 Altamura BA, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "altamura",
        },
        {
            "number": 3,
            "name": "Antico Forno Santa Caterina",
            "lat": 40.8260,
            "lon": 16.5537,
            "address": "Via Ambrogio del Giudice 2, 70022 Altamura BA, Italy",
            "type": "Food stop",
            "color": ROUTE_PRIMARY,
            "cluster": "altamura",
        },
        {
            "number": 4,
            "name": "Tre Archi",
            "lat": 40.8265,
            "lon": 16.5540,
            "address": "Via San Michele 28, 70022 Altamura BA, Italy",
            "type": "Lunch / optional",
            "color": ROUTE_PRIMARY,
            "cluster": "altamura",
        },
        {
            "number": 5,
            "name": "The Sassi (Sasso Caveoso / Sasso Barisano)",
            "lat": 40.6664,
            "lon": 16.6043,
            "address": "Sasso Caveoso, 75100 Matera MT, Italy",
            "type": "Historic site",
            "color": ROUTE_PRIMARY,
            "cluster": "matera",
        },
        {
            "number": 6,
            "name": "Casa Grotta",
            "lat": 40.6639,
            "lon": 16.6123,
            "address": "Vico Solitario 11, 75100 Matera MT, Italy",
            "type": "Museum",
            "color": ROUTE_PRIMARY,
            "cluster": "matera",
        },
        {
            "number": 7,
            "name": "Santa Maria de Idris & San Giovanni in Monterrone",
            "lat": 40.6641,
            "lon": 16.6121,
            "address": "Monterrone rock spur, Sasso Caveoso, 75100 Matera MT, Italy",
            "type": "Chiesa rupestre",
            "color": ROUTE_PRIMARY,
            "cluster": "matera",
        },
        {
            "number": 8,
            "name": "Trattoria del Caveoso",
            "lat": 40.6623,
            "lon": 16.6110,
            "address": "Via Bruno Buozzi 21, 75100 Matera MT, Italy",
            "type": "Lunch / dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "matera",
        },
        {
            "number": 9,
            "name": "Via Saragat (parking)",
            "lat": 40.6670,
            "lon": 16.5952,
            "address": "Via Giuseppe Saragat, 75100 Matera MT, Italy",
            "type": "Parking",
            "color": ROUTE_PRIMARY,
            "cluster": "matera",
        },
        {
            "number": 10,
            "name": "Via Lucana (parking)",
            "lat": 40.6661,
            "lon": 16.6049,
            "address": "Via Lucana, 75100 Matera MT, Italy",
            "type": "Parking",
            "color": ROUTE_PRIMARY,
            "cluster": "matera",
        },
    ],
    "poi_verification": {
        1: "Address and coordinates carried from the verified Day 13 San Vito dei Normanni arrival anchor; reused as this day's start/end point.",
        2: "Resolved via OpenStreetMap Nominatim to Corso Federico II di Svevia, matching the cathedral's own published address.",
        3: "Resolved via OpenStreetMap Nominatim to Via Ambrogio del Giudice, matching the bakery's own published Via Ambrogio del Giudice 2 address.",
        4: "Resolved via OpenStreetMap Nominatim directly to the named 'Tre Archi' restaurant node on Via San Michele.",
        5: "Approximated to a central Sasso Caveoso/Piazza Vittorio Veneto-area anchor; the Sassi are a district, not a single pinpoint address.",
        6: "Resolved via OpenStreetMap Nominatim directly to the named 'Casa Grotta nei Sassi' node on Vico Solitario.",
        7: "Resolved via OpenStreetMap Nominatim to the named 'Madonna de Idris e San Giovanni in Monterrone' node.",
        8: "Resolved via OpenStreetMap Nominatim directly to the named 'Trattoria del Caveoso' node on Via Bruno Buozzi.",
        9: "Resolved via OpenStreetMap Nominatim to Via Giuseppe Saragat, matching independently-cited parking guidance for the station-area lot.",
        10: "Resolved via OpenStreetMap Nominatim to Via Lucana in the centro storico, matching independently-cited parking guidance for the underground garage near Piazza Vittorio Veneto.",
    },
}


ROUTE_OPTION_D = "#6E7F2A"

DAY19 = {
    "title": "Day 19 orientation map",
    "output": ROOT / "assets/maps/day19-free-day-options-route.png",
    "zoom": 9,
    "size": (1800, 1500),
    "padding_px": 220,
    "places": {
        "San Vito dei Normanni": (40.6563995, 17.7087266),
        "Torre Guaceto": (40.7057, 17.7830),
        "Carovigno": (40.7071, 17.6592),
        "Ceglie Messapica": (40.6461, 17.5171),
        "Oria": (40.4998, 17.6416),
        "Manduria": (40.4059, 17.6361),
        "Grottaglie": (40.5335, 17.4321),
        "Taranto": (40.4727, 17.2337),
    },
    "routes": {
        "option_a": {
            "color": ROUTE_ALTERNATIVE,
            "width": 9,
            "coords": ["San Vito dei Normanni", "Torre Guaceto", "Carovigno"],
            "dashed": True,
        },
        "option_b": {
            "color": ROUTE_PRIMARY,
            "width": 9,
            "coords": ["San Vito dei Normanni", "Ceglie Messapica"],
            "dashed": True,
        },
        "option_c": {
            "color": ROUTE_OPTIONAL,
            "width": 9,
            "coords": ["San Vito dei Normanni", "Oria", "Manduria"],
            "dashed": True,
        },
        "option_d": {
            "color": ROUTE_OPTION_D,
            "width": 9,
            "coords": ["San Vito dei Normanni", "Grottaglie", "Taranto"],
            "dashed": True,
        },
    },
    "route_order": ["option_a", "option_b", "option_c", "option_d"],
    "legend": [
        {"label": "Option A — Torre Guaceto + Carovigno", "color": ROUTE_ALTERNATIVE, "dashed": True},
        {"label": "Option B — Ceglie Messapica", "color": ROUTE_PRIMARY, "dashed": True},
        {"label": "Option C — Oria + Manduria", "color": ROUTE_OPTIONAL, "dashed": True},
        {"label": "Option D — Grottaglie + Taranto", "color": ROUTE_OPTION_D, "dashed": True},
    ],
    "poi_clusters": {
        "carovigno": {
            "anchor": "Carovigno",
            "numbers": [3, 4],
            "grid_offset": (-220, -80),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "ceglie": {
            "anchor": "Ceglie Messapica",
            "numbers": [5, 6, 7, 8],
            "grid_offset": (-260, 40),
            "columns": 2,
            "x_step": 66,
            "y_step": 58,
        },
        "manduria": {
            "anchor": "Manduria",
            "numbers": [10, 11],
            "grid_offset": (60, 40),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "taranto": {
            "anchor": "Taranto",
            "numbers": [13, 14, 15],
            "grid_offset": (-280, -60),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Vito dei Normanni (start/end)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / start-end",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
        {
            "number": 2,
            "name": "Torre Guaceto",
            "lat": 40.7057,
            "lon": 17.7830,
            "address": "Riserva Naturale Statale di Torre Guaceto, Carovigno BR, Italy",
            "type": "Option A / nature reserve",
            "color": ROUTE_ALTERNATIVE,
            "offset": (60, -50),
        },
        {
            "number": 3,
            "name": "Carovigno",
            "lat": 40.7071,
            "lon": 17.6592,
            "address": "Corso Vittorio Emanuele, 72012 Carovigno BR, Italy",
            "type": "Option A / town centre",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "carovigno",
        },
        {
            "number": 4,
            "name": "Trattoria La Cantina",
            "lat": 40.7071,
            "lon": 17.6592,
            "address": "Corso Vittorio Emanuele 95/97, 72012 Carovigno BR, Italy",
            "type": "Option A / lunch",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "carovigno",
        },
        {
            "number": 5,
            "name": "Ceglie Messapica",
            "lat": 40.6461,
            "lon": 17.5171,
            "address": "Piazza Plebiscito, 72013 Ceglie Messapica BR, Italy",
            "type": "Option B / town centre",
            "color": ROUTE_PRIMARY,
            "cluster": "ceglie",
        },
        {
            "number": 6,
            "name": "Osteria del Capitolo",
            "lat": 40.6461,
            "lon": 17.5171,
            "address": "below Piazza Plebiscito, 72013 Ceglie Messapica BR, Italy",
            "type": "Option B / lunch",
            "color": ROUTE_PRIMARY,
            "cluster": "ceglie",
        },
        {
            "number": 7,
            "name": "Osteria L'Antico Arco",
            "lat": 40.6461,
            "lon": 17.5171,
            "address": "Largo Gelso 4, 72013 Ceglie Messapica BR, Italy",
            "type": "Option B / lunch alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "ceglie",
        },
        {
            "number": 8,
            "name": "Braceria Zitto & Mangia",
            "lat": 40.6461,
            "lon": 17.5171,
            "address": "Piazza Plebiscito 7, 72013 Ceglie Messapica BR, Italy",
            "type": "Option B / lunch alternate",
            "color": ROUTE_PRIMARY,
            "cluster": "ceglie",
        },
        {
            "number": 9,
            "name": "Oria — Castello Svevo",
            "lat": 40.4998,
            "lon": 17.6416,
            "address": "Via Castello, Quartiere Ebraico, 72024 Oria BR, Italy",
            "type": "Option C / historic site",
            "color": ROUTE_OPTIONAL,
            "offset": (-90, 50),
        },
        {
            "number": 10,
            "name": "Cantina Produttori di Manduria",
            "lat": 40.4059,
            "lon": 17.6361,
            "address": "Via Fabio Massimo 19, 74024 Manduria TA, Italy",
            "type": "Option C / wine tasting",
            "color": ROUTE_OPTIONAL,
            "cluster": "manduria",
        },
        {
            "number": 11,
            "name": "Fonte Pliniano",
            "lat": 40.4022,
            "lon": 17.6430,
            "address": "Via Fonte Pliniano, 74024 Manduria TA, Italy",
            "type": "Option C / historic site",
            "color": ROUTE_OPTIONAL,
            "cluster": "manduria",
        },
        {
            "number": 12,
            "name": "Grottaglie — Quartiere delle Ceramiche",
            "lat": 40.5335,
            "lon": 17.4321,
            "address": "Quartiere delle Ceramiche, 74023 Grottaglie TA, Italy",
            "type": "Option D / historic site",
            "color": ROUTE_OPTION_D,
            "offset": (-100, 60),
        },
        {
            "number": 13,
            "name": "Osteria La Capasa",
            "lat": 40.5348,
            "lon": 17.4284,
            "address": "Via Chiesa Matrice 4, 74023 Grottaglie TA, Italy",
            "type": "Option D / lunch",
            "color": ROUTE_OPTION_D,
            "cluster": "taranto",
        },
        {
            "number": 14,
            "name": "MArTA",
            "lat": 40.4735,
            "lon": 17.2385,
            "address": "Via Cavour 10, 74123 Taranto TA, Italy",
            "type": "Option D / museum",
            "color": ROUTE_OPTION_D,
            "cluster": "taranto",
        },
        {
            "number": 15,
            "name": "Castello Aragonese",
            "lat": 40.4727,
            "lon": 17.2337,
            "address": "Piazza Castello, 74123 Taranto TA, Italy",
            "type": "Option D / historic site",
            "color": ROUTE_OPTION_D,
            "cluster": "taranto",
        },
        {
            "number": 16,
            "name": "Core Restaurant",
            "lat": 40.4735,
            "lon": 17.2385,
            "address": "Via Niccolò Tommaso d'Aquino 8, 74123 Taranto TA, Italy",
            "type": "Option D / lunch, least verified",
            "color": ROUTE_OPTION_D,
            "offset": (60, 60),
        },
    ],
    "poi_verification": {
        1: "Address and coordinates carried from the verified Day 13 San Vito dei Normanni arrival anchor; reused as this day's start/end point.",
        2: "Resolved via OpenStreetMap Nominatim directly to the named 'Riserva Naturale Statale di Torre Guaceto' node.",
        3: "Resolved via OpenStreetMap Nominatim to Corso Vittorio Emanuele, Carovigno's main street, used as the town-centre anchor.",
        4: "Resolved via OpenStreetMap Nominatim to Corso Vittorio Emanuele 95/97, matching the trattoria's own published address and phone.",
        5: "Resolved via OpenStreetMap Nominatim to Piazza Plebiscito, Ceglie Messapica's main square.",
        6: "Itinerary gave only 'below Piazza Plebiscito' with no OSM-indexed node; approximated to the piazza anchor, not an exact storefront pin.",
        7: "Itinerary gave Largo Gelso 4 with no OSM-indexed node; approximated to the Piazza Plebiscito anchor, not an exact storefront pin.",
        8: "Itinerary gave Piazza Plebiscito 7, sharing the same piazza anchor as marker 5 — a real address on the square itself.",
        9: "Resolved via OpenStreetMap Nominatim directly to the named 'Castello Svevo' node in Oria's Quartiere Ebraico.",
        10: "Resolved via OpenStreetMap Nominatim directly to the named 'Museo della Civiltà del Vino Primitivo' node on Via Fabio Massimo, matching the Cantina Produttori's published address.",
        11: "Resolved via OpenStreetMap Nominatim directly to the named 'Via Fonte Pliniano' street node.",
        12: "Resolved via OpenStreetMap Nominatim directly to the named 'Quartiere delle Ceramiche' node.",
        13: "Resolved via OpenStreetMap Nominatim to Via Chiesa Matrice, matching the osteria's own published Via Chiesa Matrice 4 address and phone.",
        14: "Resolved via OpenStreetMap Nominatim directly to the named 'MAR.TA Museo Archeologico Nazionale di Taranto' node on Via Cavour.",
        15: "Resolved via OpenStreetMap Nominatim directly to the named 'Castello Aragonese' node on Piazza Castello.",
        16: "Itinerary gave Via Niccolò Tommaso d'Aquino 8 with no OSM-indexed node; approximated to the MArTA/Via Cavour anchor (same general area near the swing bridge), not an exact storefront pin — this pick is separately flagged in the day's content as the least-verified restaurant on the page.",
    },
}


DAY20 = {
    "title": "Day 20 orientation map",
    "output": ROOT / "assets/maps/day20-pompei-napoli-route.png",
    "zoom": 8,
    "size": (1800, 1500),
    "padding_px": 200,
    "places": {
        "San Vito dei Normanni": (40.6563995, 17.7087266),
        "Pompei": (40.7485, 14.4831),
        "Napoli": (40.8488, 14.2595),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["San Vito dei Normanni", "Pompei", "Napoli"],
        },
    },
    "route_order": ["recommended"],
    "legend": [
        {"label": "Puglia to Pompeii to Naples", "color": ROUTE_PRIMARY},
    ],
    "poi_clusters": {
        "pompei": {
            "anchor": "Pompei",
            "numbers": [2, 3],
            "grid_offset": (-260, -80),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
        "napoli": {
            "anchor": "Napoli",
            "numbers": [4, 5, 6],
            "grid_offset": (60, -140),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "San Vito dei Normanni (start)",
            "lat": 40.6563995,
            "lon": 17.7087266,
            "address": "Via Principe di Piemonte 13, 72019 San Vito dei Normanni BR, Italy",
            "type": "Accommodation / start",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
        {
            "number": 2,
            "name": "Scavi di Pompei — Porta Marina",
            "lat": 40.7485,
            "lon": 14.4831,
            "address": "Via Marina, 80045 Pompei NA, Italy",
            "type": "Historic site / entrance",
            "color": ROUTE_PRIMARY,
            "cluster": "pompei",
        },
        {
            "number": 3,
            "name": "Scavi di Pompei — Piazza Anfiteatro",
            "lat": 40.7477,
            "lon": 14.4876,
            "address": "Piazza Immacolata, 80045 Pompei NA, Italy",
            "type": "Historic site / entrance",
            "color": ROUTE_PRIMARY,
            "cluster": "pompei",
        },
        {
            "number": 4,
            "name": "Garage Napoli Centro (parking)",
            "lat": 40.8423,
            "lon": 14.2509,
            "address": "Via dei Fiorentini 53, 80133 Napoli NA, Italy",
            "type": "Parking",
            "color": ROUTE_PRIMARY,
            "cluster": "napoli",
        },
        {
            "number": 5,
            "name": "La figlia del Presidente",
            "lat": 40.8488,
            "lon": 14.2595,
            "address": "Via del Grande Archivio 23/24, 80138 Napoli NA, Italy",
            "type": "Dinner",
            "color": ROUTE_PRIMARY,
            "cluster": "napoli",
        },
        {
            "number": 6,
            "name": "MANN — Gabinetto Segreto (next-morning option)",
            "lat": 40.8536,
            "lon": 14.2512,
            "address": "Piazza Museo Nazionale 19, 80135 Napoli NA, Italy",
            "type": "Museum / quirky, optional",
            "color": ROUTE_ALTERNATIVE,
            "cluster": "napoli",
        },
    ],
    "poi_verification": {
        1: "Address and coordinates carried from the verified Day 13 San Vito dei Normanni arrival anchor; reused as this day's start point.",
        2: "Resolved via OpenStreetMap Nominatim directly to the named 'Porta Marina' node on Via Marina, Pompei.",
        3: "Resolved via OpenStreetMap Nominatim to Viale delle Ginestre near Piazza Immacolata/Piazza Anfiteatro, the second official excavation entrance.",
        4: "Resolved via OpenStreetMap Nominatim to Via dei Fiorentini, matching the garage's own published Via dei Fiorentini 53 address.",
        5: "Resolved via OpenStreetMap Nominatim directly to the named 'La Figlia del Presidente' restaurant node on Via del Grande Archivio.",
        6: "Resolved via OpenStreetMap Nominatim directly to the named 'Museo archeologico nazionale di Napoli' node on Piazza Museo Nazionale.",
    },
}


DAY21 = {
    "title": "Day 21 orientation map",
    "output": ROOT / "assets/maps/day21-napoli-fiumicino-route.png",
    "zoom": 8,
    "size": (1800, 1400),
    "padding_px": 200,
    "places": {
        "Napoli": (40.8488, 14.2595),
        "Fiumicino": (41.7999, 12.2519),
    },
    "routes": {
        "recommended": {
            "color": ROUTE_PRIMARY,
            "width": 12,
            "coords": ["Napoli", "Fiumicino"],
        },
    },
    "route_order": ["recommended"],
    "legend": [
        {"label": "Naples to Rome Fiumicino", "color": ROUTE_PRIMARY},
    ],
    "poi_clusters": {
        "napoli": {
            "anchor": "Napoli",
            "numbers": [1, 2, 3],
            "grid_offset": (-280, -80),
            "columns": 1,
            "x_step": 66,
            "y_step": 58,
        },
    },
    "pois": [
        {
            "number": 1,
            "name": "Sansevero Chapel Museum",
            "lat": 40.8494,
            "lon": 14.2540,
            "address": "Via Francesco de Sanctis 19/21, 80134 Napoli NA, Italy",
            "type": "Museum",
            "color": ROUTE_PRIMARY,
            "cluster": "napoli",
        },
        {
            "number": 2,
            "name": "Pintauro",
            "lat": 40.8442,
            "lon": 14.2497,
            "address": "Via Toledo 275, 80132 Napoli NA, Italy",
            "type": "Breakfast",
            "color": ROUTE_PRIMARY,
            "cluster": "napoli",
        },
        {
            "number": 3,
            "name": "Antica Pizzeria Port'Alba",
            "lat": 40.8494,
            "lon": 14.2543,
            "address": "Via Port'Alba 18, 80134 Napoli NA, Italy",
            "type": "Lunch",
            "color": ROUTE_PRIMARY,
            "cluster": "napoli",
        },
        {
            "number": 4,
            "name": "Rome Fiumicino Airport (end)",
            "lat": 41.7999,
            "lon": 12.2519,
            "address": "Via dell'Aeroporto di Fiumicino 320, 00054 Fiumicino RM, Italy",
            "type": "Airport / end",
            "color": MARKER_ACCOMMODATION,
            "offset": (0, 60),
        },
    ],
    "poi_verification": {
        1: "Resolved via OpenStreetMap Nominatim directly to the named 'Cappella Sansevero' node on Via Francesco de Sanctis.",
        2: "Resolved via OpenStreetMap Nominatim to Via Toledo 275, matching the pastry shop's own current published address after its 2026 reopening.",
        3: "Resolved via OpenStreetMap Nominatim directly to the named 'Antica Pizzeria Port'Alba' node on Via Port'Alba.",
        4: "Resolved via OpenStreetMap Nominatim directly to the named Rome Fiumicino Airport node.",
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


def draw_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    color: str,
    width: int,
    dashed: bool = False,
    pattern_scale: int = 1,
) -> None:
    if not dashed:
        draw.line(points, fill=color, width=width, joint="curve")
        radius = width / 2
        for x, y in points:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
        return

    dash = 28 * pattern_scale
    gap = 18 * pattern_scale
    radius = width / 2
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
            start_x = x1 + dx * cursor
            start_y = y1 + dy * cursor
            end_x = x1 + dx * segment_end
            end_y = y1 + dy * segment_end
            draw.ellipse((start_x - radius, start_y - radius, start_x + radius, start_y + radius), fill=color)
            draw.ellipse((end_x - radius, end_y - radius, end_x + radius, end_y + radius), fill=color)
            cursor += dash + gap


def numbered_marker(
    draw: ImageDraw.ImageDraw,
    point: tuple[float, float],
    number: int,
    fill: str,
    font: ImageFont.ImageFont,
    marker_offset: tuple[int, int] = (0, 0),
    scale: int = 1,
) -> None:
    x, y = point
    dx, dy = marker_offset
    marker_x = x + dx
    marker_y = y + dy
    if dx or dy:
        draw.line((x, y, marker_x, marker_y), fill=hex_to_rgba(MAP_INK, 150), width=2 * scale)
        draw.ellipse((x - 4 * scale, y - 4 * scale, x + 4 * scale, y + 4 * scale), fill=hex_to_rgba(MAP_INK, 190), outline=MAP_PARCHMENT, width=1 * scale)

    text = str(number)
    box_w = 58 * scale
    box_h = 46 * scale
    radius = 8 * scale
    box = (
        marker_x - box_w / 2,
        marker_y - box_h / 2,
        marker_x + box_w / 2,
        marker_y + box_h / 2,
    )
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=MAP_PARCHMENT, width=5 * scale)
    draw.rounded_rectangle(box, radius=radius, outline=MARKER_ACCOMMODATION, width=1 * scale)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        (marker_x - text_w / 2 - bbox[0], marker_y - text_h / 2 - bbox[1]),
        text,
        fill=MAP_PARCHMENT,
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
    scale: int = 1,
) -> None:
    anchor_x, anchor_y = anchor
    grid_x, grid_y = grid_origin
    rows = math.ceil(len(pois) / columns)
    connector_y = grid_y + y_step * (rows - 1) / 2

    draw.line((anchor_x, anchor_y, grid_x - 34 * scale, connector_y), fill=hex_to_rgba(MAP_INK, 120), width=2 * scale)
    draw.ellipse((anchor_x - 7 * scale, anchor_y - 7 * scale, anchor_x + 7 * scale, anchor_y + 7 * scale), fill=MARKER_ACCOMMODATION, outline=MAP_PARCHMENT, width=2 * scale)

    for index, poi in enumerate(pois):
        col = index % columns
        row = index // columns
        numbered_marker(
            draw,
            (grid_x + x_step * col, grid_y + y_step * row),
            poi["number"],
            poi["color"],
            font,
            scale=scale,
        )


def draw_routes_antialiased(
    image: Image.Image,
    routes: list[tuple[list[tuple[float, float]], dict]],
    scale: int,
) -> Image.Image:
    aa = ROUTE_ANTIALIAS_SCALE
    overlay = Image.new("RGBA", (image.width * aa, image.height * aa), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    for points, route in routes:
        aa_points = [(x * aa, y * aa) for x, y in points]
        draw_line(
            overlay_draw,
            aa_points,
            MAP_PARCHMENT,
            round((route["width"] + 8) * ROUTE_STROKE_SCALE * scale * aa),
            route.get("dashed", False),
            scale * aa,
        )
        draw_line(
            overlay_draw,
            aa_points,
            route["color"],
            round(route["width"] * ROUTE_STROKE_SCALE * scale * aa),
            route.get("dashed", False),
            scale * aa,
        )

    overlay = overlay.resize(image.size, Image.Resampling.LANCZOS)
    return Image.alpha_composite(image, overlay)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def font_line_height(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), "Ag", font=font)
    return bbox[3] - bbox[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
            continue
        lines.append(current)
        current = word
    lines.append(current)

    wrapped: list[str] = []
    for line in lines:
        if text_width(draw, line, font) <= max_width:
            wrapped.append(line)
            continue
        current = ""
        for char in line:
            candidate = f"{current}{char}"
            if current and text_width(draw, candidate, font) > max_width:
                wrapped.append(current)
                current = char
            else:
                current = candidate
        if current:
            wrapped.append(current)
    return wrapped


def layout_route_legend(
    draw: ImageDraw.ImageDraw,
    config: dict,
    title_font: ImageFont.ImageFont,
    label_font: ImageFont.ImageFont,
    output_w: int,
    scale: int = 1,
) -> dict:
    left = 32 * scale
    top = 32 * scale
    pad_x = 24 * scale
    pad_top = 18 * scale
    pad_bottom = 20 * scale
    title_to_items = 28 * scale
    line_sample_w = 100 * scale
    label_gap = 16 * scale
    row_gap = 10 * scale
    line_height = font_line_height(draw, label_font)
    title_height = font_line_height(draw, title_font)
    max_box_width = output_w - left - 24 * scale
    max_label_width = max_box_width - pad_x * 2 - line_sample_w - label_gap

    title = config["title"]
    title_width = text_width(draw, title, title_font)
    legend_items = config.get("legend", [])
    item_layouts = []
    widest_label = 0
    for item in legend_items:
        lines = wrap_text(draw, item["label"], label_font, max_label_width)
        widest_label = max(widest_label, *(text_width(draw, line, label_font) for line in lines))
        item_layouts.append({"item": item, "lines": lines})

    desired_width = max(title_width, line_sample_w + label_gap + widest_label) + pad_x * 2
    box_width = min(max_box_width, math.ceil(desired_width))
    label_width = box_width - pad_x * 2 - line_sample_w - label_gap

    if label_width < widest_label:
        item_layouts = []
        for item in legend_items:
            item_layouts.append({"item": item, "lines": wrap_text(draw, item["label"], label_font, label_width)})

    item_heights = [max(32, len(layout["lines"]) * line_height + (len(layout["lines"]) - 1) * 4) for layout in item_layouts]
    items_height = sum(item_heights) + row_gap * max(0, len(item_heights) - 1)
    box_height = pad_top + title_height + title_to_items + items_height + pad_bottom

    return {
        "left": left,
        "top": top,
        "right": min(output_w - 24 * scale, left + box_width),
        "bottom": top + box_height,
        "pad_x": pad_x,
        "pad_top": pad_top,
        "title": title,
        "title_font": title_font,
        "title_height": title_height,
        "label_font": label_font,
        "label_line_height": line_height,
        "title_to_items": title_to_items,
        "line_sample_w": line_sample_w,
        "label_gap": label_gap,
        "row_gap": row_gap,
        "item_layouts": item_layouts,
        "item_heights": item_heights,
    }


def draw_route_legend(draw: ImageDraw.ImageDraw, config: dict, output_w: int, scale: int = MAP_OUTPUT_SCALE) -> dict:
    title_font = load_font(36 * scale, bold=True)
    label_font = load_font(22 * scale)
    layout = layout_route_legend(draw, config, title_font, label_font, output_w, scale)
    left = layout["left"]
    top = layout["top"]
    right = layout["right"]
    bottom = layout["bottom"]
    pad_x = layout["pad_x"]

    draw.rounded_rectangle((left, top, right, bottom), radius=16 * scale, fill=hex_to_rgba(MAP_PARCHMENT, 235), outline=MAP_PARCHMENT_DARK, width=2 * scale)
    draw.text((left + pad_x, top + layout["pad_top"]), layout["title"], fill=MARKER_ACCOMMODATION, font=title_font)

    cursor_y = top + layout["pad_top"] + layout["title_height"] + layout["title_to_items"]
    sample_x = left + pad_x + 4 * scale
    label_x = sample_x + layout["line_sample_w"] + layout["label_gap"]
    for index, item_layout in enumerate(layout["item_layouts"]):
        item = item_layout["item"]
        lines = item_layout["lines"]
        symbol_y = cursor_y + 12 * scale
        draw_line(draw, [(sample_x, symbol_y), (sample_x + layout["line_sample_w"], symbol_y)], item["color"], 9 * scale, item.get("dashed", False), scale)
        text_y = cursor_y
        for line in lines:
            draw.text((label_x, text_y), line, fill=MARKER_ACCOMMODATION, font=label_font)
            text_y += layout["label_line_height"] + 4 * scale
        cursor_y += layout["item_heights"][index] + layout["row_gap"]
    return layout


def generate_map(config: dict) -> None:
    zoom = config["zoom"]
    scale = MAP_OUTPUT_SCALE

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

    render_zoom = zoom + int(math.log2(scale))
    render_factor = 2 ** (render_zoom - zoom)
    render_min_x = min_x * render_factor
    render_max_x = max_x * render_factor
    render_min_y = min_y * render_factor
    render_max_y = max_y * render_factor

    tile_min_x = global_px_to_tile(render_min_x)
    tile_max_x = global_px_to_tile(render_max_x)
    tile_min_y = global_px_to_tile(render_min_y)
    tile_max_y = global_px_to_tile(render_max_y)

    mosaic = Image.new("RGB", ((tile_max_x - tile_min_x + 1) * TILE_SIZE, (tile_max_y - tile_min_y + 1) * TILE_SIZE), MAP_WARM_TILE)
    for tx in range(tile_min_x, tile_max_x + 1):
        for ty in range(tile_min_y, tile_max_y + 1):
            tile = fetch_tile(render_zoom, tx, ty)
            mosaic.paste(tile, ((tx - tile_min_x) * TILE_SIZE, (ty - tile_min_y) * TILE_SIZE))

    render_w = output_w * scale
    render_h = output_h * scale
    left = int(render_min_x - tile_min_x * TILE_SIZE)
    top = int(render_min_y - tile_min_y * TILE_SIZE)
    right = int(render_max_x - tile_min_x * TILE_SIZE)
    bottom = int(render_max_y - tile_min_y * TILE_SIZE)
    image = mosaic.crop((left, top, right, bottom)).resize((render_w, render_h), Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", image.size, hex_to_rgba(MAP_PARCHMENT, 54))
    image = Image.alpha_composite(image, overlay)

    def to_canvas(lat: float, lon: float) -> tuple[float, float]:
        gx, gy = lonlat_to_global_px(lat, lon, zoom)
        return ((gx - min_x) / (max_x - min_x) * render_w, (gy - min_y) / (max_y - min_y) * render_h)

    route_draws = []
    for name in config.get("route_order", config["routes"].keys()):
        route = config["routes"][name]
        points = [to_canvas(lat, lon) for lat, lon in route_geometries[name]]
        route_draws.append((points, route))
    image = draw_routes_antialiased(image, route_draws, scale)

    draw = ImageDraw.Draw(image)
    number_font = load_font(25 * scale, bold=True)
    small_font = load_font(22 * scale)
    pois_by_number = {poi["number"]: poi for poi in config["pois"]}
    clustered_numbers: set[int] = set()
    for cluster in config.get("poi_clusters", {}).values():
        anchor = to_canvas(*config["places"][cluster["anchor"]])
        grid_origin = (anchor[0] + cluster["grid_offset"][0] * scale, anchor[1] + cluster["grid_offset"][1] * scale)
        cluster_pois = [pois_by_number[number] for number in cluster["numbers"]]
        draw_cluster_grid(
            draw,
            anchor,
            cluster_pois,
            grid_origin,
            cluster["columns"],
            cluster["x_step"] * scale,
            cluster["y_step"] * scale,
            number_font,
            scale,
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
            tuple(value * scale for value in poi.get("offset", (0, 0))),
            scale,
        )

    draw_route_legend(draw, config, render_w, scale)

    attribution = "Map data and tiles © OpenStreetMap contributors · Routes from OSRM"
    attr_bbox = draw.textbbox((0, 0), attribution, font=small_font)
    draw.rounded_rectangle((render_w - attr_bbox[2] - 50 * scale, render_h - 58 * scale, render_w - 24 * scale, render_h - 20 * scale), radius=8 * scale, fill=hex_to_rgba(MAP_PARCHMENT, 230))
    draw.text((render_w - attr_bbox[2] - 38 * scale, render_h - 53 * scale), attribution, fill=MAP_INK_SOFT, font=small_font)

    config["output"].parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(config["output"], quality=94, optimize=True)
    print(config["output"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    configs = {"day1": DAY1, "day2": DAY2, "day3": DAY3, "day4": DAY4, "day5": DAY5, "day6": DAY6, "day7": DAY7, "day8": DAY8, "day9": DAY9, "day10": DAY10, "day11": DAY11, "day12": DAY12, "day13": DAY13, "day14": DAY14, "day15": DAY15, "day16": DAY16, "day17": DAY17, "day18": DAY18, "day19": DAY19, "day20": DAY20, "day21": DAY21}
    parser.add_argument("day", choices=sorted(configs), help="Map configuration to generate")
    args = parser.parse_args()
    generate_map(configs[args.day])


if __name__ == "__main__":
    main()
