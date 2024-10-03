# file made to showcase functionalities added in seacharts 4.0 integrated within old seacharts functionalities
# for 

if __name__ == "__main__":
    from seacharts import ENC

    enc = ENC()
    enc.display.start()

    coords = [111000, 2482000]
    layer_label = "TSSLPT" #requires TSSLPT listed in S-57 layers in config.yaml

    print(f"depth at coordinates {coords}: {enc.get_depth_at_coord(coords[0], coords[1])}")
    print(f"coordinates {coords} in layer {layer_label}: {enc.is_coord_in_layer(coords[0], coords[1], 'TSSLPT')}")


    center = enc.center
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
    enc.display.show()