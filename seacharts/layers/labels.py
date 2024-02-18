"""
Contains dictionaries of supported regional database labels.
"""
NORWEGIAN_LABELS = dict(
    Seabed=[
        dict(
            layer="dybdeareal",  # depth area
            depth="minimumsdybde",  # minimum depth
        ),
        dict(
            layer="grunne",  # shallows
            depth="dybde",  # depth
        )
    ],
    Land=[
        "landareal",  # land area
    ],
    Shore=[
        "ikkekartlagtsjomaltomr",  # unmapped ocean areas
        "landareal",  # land area (shore area includes all land)
        "skjer",  # rocks
        "torrfall",  # dry fall
    ],
)
