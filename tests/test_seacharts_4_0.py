# file made to showcase functionalities added in seacharts 4.0 integrated within old seacharts functionalities
# for 

if __name__ == "__main__":
    import shapely.geometry as geo
    from seacharts import ENC

    enc = ENC()
    enc.display.start()

    coords = [111000, 2482000]
    layer_label = "TSSLPT" #requires TSSLPT listed in S-57 layers in config.yaml

    print(f"depth at coordinates {coords}: {enc.get_depth_at_coord(coords[0], coords[1])}")
    print(f"coordinates {coords} in layer {layer_label}: {enc.is_coord_in_layer(coords[0], coords[1], 'TSSLPT')}")


    center = enc.center
    x, y = center
    width = 2000
    height = 2000
    enc.display.draw_circle(
        center, 20000, "yellow", thickness=2, edge_style="--", alpha=0.5
    )
    enc.display.draw_rectangle(center, (6000, 12000), "blue", rotation=20, alpha=0.5)
    enc.display.draw_circle(
        center, 10000, "green", edge_style=(0, (5, 8)), thickness=3, fill=False
    )
    enc.display.draw_line(
        [(center[0], center[1] + 800), center, (center[0] - 300, center[1] - 400)],
        "white",
    )
    box = geo.Polygon(
        (
            (x - width, y - height),
            (x + width, y - height),
            (x + width, y + height),
            (x - width, y + height),
        )
    )
    areas = list(box.difference(enc.seabed[10].geometry).geoms)
    for area in areas[3:8] + [areas[14], areas[17]] + areas[18:21]:
        enc.display.draw_polygon(area, "red", alpha=0.5)
    enc.display.show()