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
    "title": "Day 1 orientation map",
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
    "route_order": ["optional", "lagoon", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": "#1769d2"},
        {"label": "Comacchio alternative", "color": "#d79a19"},
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


DAY2 = {
    "title": "Day 2 orientation map",
    "output": ROOT / "assets/maps/day2-san-marino-fano-route.png",
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
            "color": "#1769d2",
            "width": 12,
            "coords": ["Ravenna start", "San Marino parking", "San Marino core", "Fano old town", "Palazzo Rotati"],
        },
        "scenic": {
            "color": "#d79a19",
            "width": 10,
            "coords": ["San Marino core", "Gabicce Monte", "San Bartolo viewpoint", "Fano old town"],
        },
    },
    "route_order": ["scenic", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": "#1769d2"},
        {"label": "San Bartolo scenic alternative", "color": "#d79a19", "dashed": True},
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
            "color": "#1769d2",
            "offset": (0, 76),
        },
        {
            "number": 2,
            "name": "San Marino P9 Parking",
            "lat": 43.937384,
            "lon": 12.445192,
            "address": "Parcheggio P9, Via Gino Giacomini, 47890 Citta di San Marino, San Marino",
            "type": "Parking",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 3,
            "name": "Guaita Tower & Monte Titano",
            "lat": 43.9354691,
            "lon": 12.4493514,
            "address": "Salita Alla Rocca, 47890 Citta di San Marino, San Marino",
            "type": "Historic site / viewpoint",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 4,
            "name": "Piazza della Liberta & Palazzo Pubblico",
            "lat": 43.9367403,
            "lon": 12.4465224,
            "address": "Piazza della Liberta, 47890 Citta di San Marino, San Marino",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 5,
            "name": "Ristorante Ritrovo dei Lavoratori",
            "lat": 43.9358760,
            "lon": 12.4464272,
            "address": "Androne dei Bastioni 4, 47890 Citta di San Marino, San Marino",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 6,
            "name": "La Terrazza, Hotel Titano",
            "lat": 43.9360252,
            "lon": 12.4469842,
            "address": "Contrada del Collegio 31, 47890 Citta di San Marino, San Marino",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 7,
            "name": "Buca San Francesco",
            "lat": 43.9353605,
            "lon": 12.4468161,
            "address": "Piazzetta del Placito Feretrano 3, 47890 Citta di San Marino, San Marino",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 8,
            "name": "La Serenissima",
            "lat": 43.9531511,
            "lon": 12.4685640,
            "address": "Via Venticinque Marzo 67, 47895 Domagnano, San Marino",
            "type": "Shop / food heritage",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 9,
            "name": "Fantini Pelletteria",
            "lat": 43.9361136,
            "lon": 12.4476454,
            "address": "Contrada dei Magazzeni 23, 47890 Citta di San Marino, San Marino",
            "type": "Shop",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 10,
            "name": "Cava dei Balestrieri",
            "lat": 43.9375482,
            "lon": 12.4457523,
            "address": "Via Eugippo, 47890 Citta di San Marino, San Marino",
            "type": "Historic site / optional stop",
            "color": "#1769d2",
            "cluster": "san_marino",
        },
        {
            "number": 11,
            "name": "Gabicce Monte / San Bartolo viewpoint",
            "lat": 43.960330,
            "lon": 12.761220,
            "address": "Piazza Valbruna, 61011 Gabicce Monte PU, Italy",
            "type": "Scenic route viewpoint",
            "color": "#d79a19",
            "offset": (0, -44),
        },
        {
            "number": 12,
            "name": "Fano centro storico",
            "lat": 43.840900,
            "lon": 13.016950,
            "address": "Piazza XX Settembre, 61032 Fano PU, Italy",
            "type": "Historic centre",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 13,
            "name": "Arco di Augusto",
            "lat": 43.8430719,
            "lon": 13.0145105,
            "address": "Via Arco d'Augusto, 61032 Fano PU, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 14,
            "name": "Caffe Cavour",
            "lat": 43.8400902,
            "lon": 13.0195547,
            "address": "Via Camillo Benso Conte di Cavour 1, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 15,
            "name": "Caffe del Porto",
            "lat": 43.8511711,
            "lon": 13.0162229,
            "address": "Via Nazario Sauro 270, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 16,
            "name": "Il Caffe del Pasticciere",
            "lat": 43.8385085,
            "lon": 13.0112355,
            "address": "Via della Costituzione 8/A, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 17,
            "name": "Panificio Pasticceria Forno Longhini",
            "lat": 43.8470115,
            "lon": 13.0116548,
            "address": "Viale I Maggio 15/17, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 18,
            "name": "Ristorante Angela",
            "lat": 43.8460841,
            "lon": 13.0255815,
            "address": "Viale Adriatico 13, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 19,
            "name": "La Taverna del Ghiottone",
            "lat": 43.84024,
            "lon": 13.0114404,
            "address": "Via Roma 87/B, 61032 Fano PU, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "fano",
        },
        {
            "number": 20,
            "name": "B&B La Casa di Fano",
            "lat": 43.842910,
            "lon": 13.018100,
            "address": "Corso Giacomo Matteotti 173, 61032 Fano PU, Italy",
            "type": "Accommodation",
            "color": "#2f2a26",
            "cluster": "fano",
        },
        {
            "number": 21,
            "name": "Palazzo Rotati",
            "lat": 43.8442214,
            "lon": 13.0192360,
            "address": "Via Nolfi 49, 61032 Fano PU, Italy",
            "type": "Accommodation",
            "color": "#2f2a26",
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


DAY3 = {
    "title": "Day 3 orientation map",
    "output": ROOT / "assets/maps/day3-sirolo-route.png",
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
            "color": "#1769d2",
            "width": 12,
            "coords": ["Fano start", "Senigallia", "Portonovo", "Sirolo core", "Conero Camere"],
        },
        "direct": {
            "color": "#d79a19",
            "width": 10,
            "coords": ["Fano start", "Sirolo core", "Conero Camere"],
            "dashed": True,
        },
    },
    "route_order": ["direct", "recommended"],
    "legend": [
        {"label": "Recommended coastal route", "color": "#1769d2"},
        {"label": "Time-tight direct route", "color": "#d79a19", "dashed": True},
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
            "color": "#1769d2",
            "offset": (0, -92),
        },
        {
            "number": 2,
            "name": "Rocca Roveresca",
            "lat": 43.7153671,
            "lon": 13.2205412,
            "address": "Piazza del Duca 2, 60019 Senigallia AN, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "offset": (-8, -50),
        },
        {
            "number": 3,
            "name": "Abbazia di Santa Maria di Portonovo",
            "lat": 43.5611908,
            "lon": 13.5999370,
            "address": "Strada Frazione Poggio, Portonovo, 60129 Ancona AN, Italy",
            "type": "Historic site / beach stop",
            "color": "#1769d2",
            "offset": (-48, -46),
        },
        {
            "number": 4,
            "name": "Cooperativa Pescatori di Portonovo",
            "lat": 43.5619,
            "lon": 13.6002,
            "address": "Portonovo beach capanni, Strada Frazione Poggio, 60129 Ancona AN, Italy",
            "type": "Producer / food heritage",
            "color": "#1769d2",
            "offset": (42, 34),
        },
        {
            "number": 5,
            "name": "Centro Visite Parco del Conero",
            "lat": 43.5196861,
            "lon": 13.6180996,
            "address": "Via Peschiera 30/A, 60020 Sirolo AN, Italy",
            "type": "Visitor office / orientation",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 6,
            "name": "Piazza Vittorio Veneto / Balcone Panoramico",
            "lat": 43.5230728,
            "lon": 13.6199227,
            "address": "Piazza Vittorio Veneto, 60020 Sirolo AN, Italy",
            "type": "Viewpoint / historic centre",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 7,
            "name": "Spiaggia Urbani",
            "lat": 43.5236323,
            "lon": 13.6231578,
            "address": "Spiaggia Urbani, 60020 Sirolo AN, Italy",
            "type": "Beach",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 8,
            "name": "Bar Gelateria del Conero",
            "lat": 43.5225245,
            "lon": 13.6201607,
            "address": "Via Italia 1, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 9,
            "name": "Da Giustina",
            "lat": 43.5281358,
            "lon": 13.6135596,
            "address": "Via Cave 1, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 10,
            "name": "La Paranza",
            "lat": 43.5226248,
            "lon": 13.6236777,
            "address": "Spiaggia Urbani, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 11,
            "name": "Osteria Sara",
            "lat": 43.52285,
            "lon": 13.6196845,
            "address": "Piazza Vittorio Veneto 9, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 12,
            "name": "Pa' Panino un bel Po'",
            "lat": 43.5219441,
            "lon": 13.6204501,
            "address": "Via Italia 39, 60020 Sirolo AN, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 13,
            "name": "Bottega dei Sapori Nostrani",
            "lat": 43.5223274,
            "lon": 13.6202173,
            "address": "Via Italia 11/36, 60020 Sirolo AN, Italy",
            "type": "Shop / food stop",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 14,
            "name": "Latteria Elgide",
            "lat": 43.52243,
            "lon": 13.62012,
            "address": "Via Italia 5, 60020 Sirolo AN, Italy",
            "type": "Shop",
            "color": "#1769d2",
            "cluster": "sirolo",
        },
        {
            "number": 15,
            "name": "Conero Camere",
            "lat": 43.5229034,
            "lon": 13.6186971,
            "address": "Via Grilli 14, 60020 Sirolo AN, Italy",
            "type": "Accommodation",
            "color": "#2f2a26",
            "cluster": "sirolo",
        },
        {
            "number": 16,
            "name": "Diecidodici",
            "lat": 43.5235067,
            "lon": 13.6193663,
            "address": "Via Anacleto Giulietti 10, 60020 Sirolo AN, Italy",
            "type": "Accommodation / food stop",
            "color": "#2f2a26",
            "cluster": "sirolo",
        },
        {
            "number": 17,
            "name": "San Michele Relais & Spa",
            "lat": 43.5266418,
            "lon": 13.6169719,
            "address": "Via Piave 6, 60020 Sirolo AN, Italy",
            "type": "Accommodation",
            "color": "#2f2a26",
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


DAY4 = {
    "title": "Day 4 orientation map",
    "output": ROOT / "assets/maps/day4-trabocchi-route.png",
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
            "color": "#1769d2",
            "width": 12,
            "coords": ["Sirolo start", "Ortona old town", "Moro cemetery", "Marina di San Vito"],
        },
        "loreto": {
            "color": "#d79a19",
            "width": 10,
            "coords": ["Sirolo start", "Loreto", "Picchio", "Ortona old town"],
            "dashed": True,
        },
        "trabocchi": {
            "color": "#c84f2c",
            "width": 8,
            "coords": ["Marina di San Vito", "Trabocco Turchino", "Olivastri", "Pesce Palombo"],
            "dashed": True,
        },
    },
    "route_order": ["trabocchi", "loreto", "recommended"],
    "legend": [
        {"label": "Recommended route", "color": "#1769d2"},
        {"label": "Loreto optional detour", "color": "#d79a19", "dashed": True},
        {"label": "Trabocchi local add-on", "color": "#c84f2c", "dashed": True},
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
            "color": "#1769d2",
            "offset": (0, 48),
        },
        {
            "number": 2,
            "name": "Basilica della Santa Casa",
            "lat": 43.4410010,
            "lon": 13.6108062,
            "address": "Piazza della Madonna 1, 60025 Loreto AN, Italy",
            "type": "Optional historic site",
            "color": "#d79a19",
            "offset": (-58, -44),
        },
        {
            "number": 3,
            "name": "Pasticceria Picchio",
            "lat": 43.4466094,
            "lon": 13.6175825,
            "address": "Via Traversa Don Enzo Rampolla 2, 60025 Loreto Stazione AN, Italy",
            "type": "Food stop",
            "color": "#d79a19",
            "offset": (86, 52),
        },
        {
            "number": 4,
            "name": "Ortona old town / Corso Vittorio Emanuele",
            "lat": 42.3535835,
            "lon": 14.4032270,
            "address": "Corso Vittorio Emanuele, 66026 Ortona CH, Italy",
            "type": "Historic centre",
            "color": "#1769d2",
            "cluster": "ortona",
        },
        {
            "number": 5,
            "name": "Pasticceria Cantelmi Giulio",
            "lat": 42.3535835,
            "lon": 14.4032270,
            "address": "Corso Vittorio Emanuele 73, 66026 Ortona CH, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "ortona",
        },
        {
            "number": 6,
            "name": "Castello Aragonese",
            "lat": 42.3588317,
            "lon": 14.4058573,
            "address": "Largo Castello, 66026 Ortona CH, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "ortona",
        },
        {
            "number": 7,
            "name": "Moro River Canadian War Cemetery",
            "lat": 42.3368140,
            "lon": 14.4165319,
            "address": "Contrada San Donato, 66026 Ortona CH, Italy",
            "type": "Historic site",
            "color": "#1769d2",
            "cluster": "ortona",
        },
        {
            "number": 8,
            "name": "Trabocco Punta Turchino",
            "lat": 42.3006606,
            "lon": 14.4608939,
            "address": "Contrada Portelle, 66038 San Vito Chietino CH, Italy",
            "type": "Viewpoint / trabocco heritage",
            "color": "#c84f2c",
            "offset": (52, -42),
        },
        {
            "number": 9,
            "name": "Marina di San Vito / Costa dei Trabocchi",
            "lat": 42.2963540,
            "lon": 14.4436070,
            "address": "Marina di San Vito, 66038 San Vito Chietino CH, Italy",
            "type": "Beach / coastal base",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 10,
            "name": "Trabocco Vento di Scirocco",
            "lat": 42.3107684,
            "lon": 14.4462617,
            "address": "Via Lungomare di Gualdo, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop / trabocco dinner",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 11,
            "name": "Aldebaran da Rocco e Tommaso",
            "lat": 42.309154,
            "lon": 14.445654,
            "address": "Via Lungomare di Gualdo 4, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 12,
            "name": "Trabocco Pesce Palombo",
            "lat": 42.244760,
            "lon": 14.518930,
            "address": "SS16 Adriatica, Fossacesia Marina, 66022 Fossacesia CH, Italy",
            "type": "Optional food stop",
            "color": "#c84f2c",
            "offset": (0, 46),
        },
        {
            "number": 13,
            "name": "Le Due Palme",
            "lat": 42.292305,
            "lon": 14.443628,
            "address": "Via San Rocco, 66038 San Vito Chietino CH, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 14,
            "name": "Frantoio Oleario Giocondo de Santis",
            "lat": 42.2913838,
            "lon": 14.4447461,
            "address": "Via San Rocco Vecchio 7, 66038 San Vito Chietino CH, Italy",
            "type": "Shop / food heritage",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 15,
            "name": "Azienda Agricola Olivastri Tommaso",
            "lat": 42.2779149,
            "lon": 14.4456199,
            "address": "Via Quercia del Corvo 37, 66038 San Vito Chietino CH, Italy",
            "type": "Winery / shop",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 16,
            "name": "B&B La Finestra Sui Trabocchi",
            "lat": 42.3096483,
            "lon": 14.4445601,
            "address": "Via Lungomare di Gualdo 31, 66038 Marina di San Vito CH, Italy",
            "type": "Accommodation",
            "color": "#2f2a26",
            "cluster": "san_vito",
        },
        {
            "number": 17,
            "name": "Locanda dell'Adriatica",
            "lat": 42.3080635,
            "lon": 14.4459466,
            "address": "Largo Olivieri 5, 66038 Marina di San Vito CH, Italy",
            "type": "Accommodation / food stop",
            "color": "#2f2a26",
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


DAY5 = {
    "title": "Day 5 orientation map",
    "output": ROOT / "assets/maps/day5-san-vito-linger-route.png",
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
            "color": "#1769d2",
            "width": 12,
            "coords": ["La Finestra", "Via Verde access", "Marina di San Vito", "Promontorio Dannunziano", "La Finestra"],
        },
        "lanciano": {
            "color": "#d79a19",
            "width": 10,
            "coords": ["La Finestra", "San Vito-Lanciano station", "Lanciano centre", "La Bocconotteria"],
            "dashed": True,
        },
        "castel_frentano": {
            "color": "#c84f2c",
            "width": 8,
            "coords": ["Lanciano centre", "Castel Frentano"],
            "dashed": True,
        },
    },
    "route_order": ["castel_frentano", "lanciano", "linger"],
    "legend": [
        {"label": "Local linger route", "color": "#1769d2"},
        {"label": "Lanciano day-trip option", "color": "#d79a19", "dashed": True},
        {"label": "Castel Frentano bocconotto add-on", "color": "#c84f2c", "dashed": True},
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
            "color": "#2f2a26",
            "cluster": "san_vito",
        },
        {
            "number": 2,
            "name": "Locanda dell'Adriatica",
            "lat": 42.3080635,
            "lon": 14.4459466,
            "address": "Largo Olivieri 5, 66038 Marina di San Vito CH, Italy",
            "type": "Accommodation / food stop",
            "color": "#2f2a26",
            "cluster": "san_vito",
        },
        {
            "number": 3,
            "name": "Via Verde della Costa dei Trabocchi",
            "lat": 42.309420,
            "lon": 14.444940,
            "address": "Via Verde access near Via Lungomare di Gualdo, 66038 Marina di San Vito CH, Italy",
            "type": "Cycle / walking route",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 4,
            "name": "Pasticceria Iezzi Rossana",
            "lat": 42.3079185,
            "lon": 14.4453615,
            "address": "Via Nazionale Adriatica 6, 66038 San Vito Chietino CH, Italy",
            "type": "Food stop / shop",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 5,
            "name": "Trabocco Vento di Scirocco",
            "lat": 42.3107684,
            "lon": 14.4462617,
            "address": "Via Lungomare di Gualdo, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 6,
            "name": "Aldebaran da Rocco e Tommaso",
            "lat": 42.309154,
            "lon": 14.445654,
            "address": "Via Lungomare di Gualdo 4, 66038 Marina di San Vito CH, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "cluster": "san_vito",
        },
        {
            "number": 7,
            "name": "Le Due Palme",
            "lat": 42.292305,
            "lon": 14.443628,
            "address": "Via San Rocco, 66038 San Vito Chietino CH, Italy",
            "type": "Food stop",
            "color": "#1769d2",
            "offset": (-62, 18),
        },
        {
            "number": 8,
            "name": "Promontorio Dannunziano",
            "lat": 42.2963673,
            "lon": 14.4649437,
            "address": "Contrada San Fino 31, 66038 San Vito Chietino CH, Italy",
            "type": "Viewpoint / historic site",
            "color": "#1769d2",
            "offset": (86, -14),
        },
        {
            "number": 9,
            "name": "Trabocco Punta Turchino",
            "lat": 42.3006606,
            "lon": 14.4608939,
            "address": "Contrada Portelle, 66038 San Vito Chietino CH, Italy",
            "type": "Trabocco heritage / viewpoint",
            "color": "#1769d2",
            "offset": (86, 48),
        },
        {
            "number": 10,
            "name": "San Vito-Lanciano station",
            "lat": 42.3048450,
            "lon": 14.4404829,
            "address": "Stazione San Vito-Lanciano, SP70, 66038 San Vito Chietino CH, Italy",
            "type": "Transport",
            "color": "#d79a19",
            "offset": (-62, -42),
        },
        {
            "number": 11,
            "name": "Lanciano old town / Piazza del Plebiscito",
            "lat": 42.2309626,
            "lon": 14.3902022,
            "address": "Piazza del Plebiscito, 66034 Lanciano CH, Italy",
            "type": "Optional historic centre",
            "color": "#d79a19",
            "offset": (-52, -42),
        },
        {
            "number": 12,
            "name": "La Bocconotteria",
            "lat": 42.2186783,
            "lon": 14.3950227,
            "address": "Via Ercole Tinari 6, 66034 Lanciano CH, Italy",
            "type": "Food stop / shop",
            "color": "#d79a19",
            "offset": (-42, 46),
        },
        {
            "number": 13,
            "name": "Trattoria Paolucci",
            "lat": 42.2284917,
            "lon": 14.3952913,
            "address": "Via Dalmazia 30, 66034 Lanciano CH, Italy",
            "type": "Food stop",
            "color": "#d79a19",
            "offset": (54, -36),
        },
        {
            "number": 14,
            "name": "Bottega del Bocconotto",
            "lat": 42.197430,
            "lon": 14.356420,
            "address": "Castel Frentano, 66032 Castel Frentano CH, Italy",
            "type": "Optional food heritage / shop",
            "color": "#c84f2c",
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
) -> dict:
    left = 32
    top = 32
    pad_x = 24
    pad_top = 18
    pad_bottom = 20
    title_to_items = 28
    line_sample_w = 100
    label_gap = 16
    row_gap = 10
    line_height = font_line_height(draw, label_font)
    title_height = font_line_height(draw, title_font)
    max_box_width = output_w - left - 24
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
        "right": min(output_w - 24, left + box_width),
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


def draw_route_legend(draw: ImageDraw.ImageDraw, config: dict, output_w: int) -> dict:
    title_font = load_font(36, bold=True)
    label_font = load_font(22)
    layout = layout_route_legend(draw, config, title_font, label_font, output_w)
    left = layout["left"]
    top = layout["top"]
    right = layout["right"]
    bottom = layout["bottom"]
    pad_x = layout["pad_x"]

    draw.rounded_rectangle((left, top, right, bottom), radius=16, fill=(255, 253, 246, 235), outline="#d8cab4", width=2)
    draw.text((left + pad_x, top + layout["pad_top"]), layout["title"], fill="#2f2a26", font=title_font)

    cursor_y = top + layout["pad_top"] + layout["title_height"] + layout["title_to_items"]
    sample_x = left + pad_x + 4
    label_x = sample_x + layout["line_sample_w"] + layout["label_gap"]
    for index, item_layout in enumerate(layout["item_layouts"]):
        item = item_layout["item"]
        lines = item_layout["lines"]
        symbol_y = cursor_y + 12
        draw_line(draw, [(sample_x, symbol_y), (sample_x + layout["line_sample_w"], symbol_y)], item["color"], 9, item.get("dashed", False))
        text_y = cursor_y
        for line in lines:
            draw.text((label_x, text_y), line, fill="#2f2a26", font=label_font)
            text_y += layout["label_line_height"] + 4
        cursor_y += layout["item_heights"][index] + layout["row_gap"]
    return layout


def generate_map(config: dict) -> None:
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
    for name in config.get("route_order", config["routes"].keys()):
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

    draw_route_legend(draw, config, output_w)

    attribution = "Map data and tiles © OpenStreetMap contributors · Routes from OSRM"
    attr_bbox = draw.textbbox((0, 0), attribution, font=small_font)
    draw.rounded_rectangle((output_w - attr_bbox[2] - 50, output_h - 58, output_w - 24, output_h - 20), radius=8, fill=(255, 253, 246, 230))
    draw.text((output_w - attr_bbox[2] - 38, output_h - 53), attribution, fill="#4d453f", font=small_font)

    config["output"].parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(config["output"], quality=94, optimize=True)
    print(config["output"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    configs = {"day1": DAY1, "day2": DAY2, "day3": DAY3, "day4": DAY4, "day5": DAY5}
    parser.add_argument("day", choices=sorted(configs), help="Map configuration to generate")
    args = parser.parse_args()
    generate_map(configs[args.day])


if __name__ == "__main__":
    main()
