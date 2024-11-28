import sys, os
from shapely.geometry import MultiPolygon, Polygon
# file made to showcase functionalities added in seacharts 4.0 integrated within old seacharts functionalities
# for 

if __name__ == "__main__":
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, root_path)

    import shapely.geometry as geo
    from seacharts import ENC
    config_path = os.path.join('tests','config_sc4.yaml')
    enc = ENC(config_path)
    enc.display.start()

    coords = [111000, 2482000]
    layer_label = "TSSLPT" #requires TSSLPT listed in S-57 layers in config.yaml

    print(f"depth at coordinates {coords}: {enc.get_depth_at_coord(coords[0], coords[1])}")
    print(f"coordinates {coords} in layer {layer_label}: {enc.is_coord_in_layer(coords[0], coords[1], 'TSSLPT')}")
    print(f"ORIENT field val at {coords} is {enc.get_param_value_at_coords(coords[0], coords[1], 'TSSLPT', 'ORIENT')}")

    center = enc.center
    x, y = center
    width = 50000
    height = 50000
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
    difference_result = box.difference(enc.seabed[0].geometry)

    if isinstance(difference_result, MultiPolygon):
        areas = list(difference_result.geoms)
    elif isinstance(difference_result, Polygon):
        areas = [difference_result] 
    else:
        areas = []

    for area in areas:
        enc.display.draw_polygon(area, "red", alpha=0.5)
    enc.display.show()