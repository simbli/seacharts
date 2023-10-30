if __name__ == "__main__":
    import shapely.geometry as geo
    from seacharts.enc import ENC

    size = 9000, 5062
    center = 44300, 6956450
    enc = ENC(new_data=True, size=size, center=center)
    enc.start_display()

    # (id, easting, northing, heading, color)
    ships = [
        (1, 46100, 6957000, 132, "orange"),
        (2, 45000, 6956000, 57, "yellow"),
        (3, 44100, 6957500, 178, "red"),
        (4, 42000, 6955200, 86, "green"),
        (5, 44000, 6955500, 68, "pink"),
    ]

    enc.add_vessels(*ships)

    x, y = center
    width, height = 1900, 1900
    box = geo.Polygon(
        (
            (x - width, y - height),
            (x + width, y - height),
            (x + width, y + height),
            (x - width, y + height),
        )
    )
    areas = list(box.difference(enc.seabed[10].geometry).geoms)
    enc.draw_circle(center, 1000, "yellow", thickness=2, edge_style="--", alpha=0.5)
    enc.draw_rectangle(center, (600, 1200), "blue", rotation=20, alpha=0.5)
    enc.draw_circle(
        center, 700, "green", edge_style=(0, (5, 8)), thickness=3, fill=False
    )
    enc.draw_line(
        [(center[0], center[1] + 800), center, (center[0] - 300, center[1] - 400)],
        "white",
    )
    enc.draw_line(
        [
            (center[0] - 300, center[1] + 400),
            center,
            (center[0] + 200, center[1] - 600),
        ],
        "magenta",
        width=0.0,
        thickness=5.0,
        edge_style=(0, (1, 4)),
    )
    enc.draw_arrow(
        center,
        (center[0] + 700, center[1] + 600),
        "orange",
        head_size=300,
        width=50,
        thickness=5,
    )
    enc.draw_polygon(enc.seabed[100].geometry.geoms[-3], "cyan", alpha=0.5)
    enc.draw_polygon(enc.shore.geometry.geoms[56], "highlight", alpha=0.5)
    for area in areas[3:8] + [areas[14], areas[17]] + areas[18:21]:
        enc.draw_polygon(area, "red", alpha=0.5)
    enc.draw_rectangle(
        center,
        (width, height),
        "pink",
        fill=False,
        edge_style=(0, (10, 10)),
        thickness=1.5,
    )

    enc.show_display()  # Show display indefinitely
