if __name__ == '__main__':
    import pathlib

    import matplotlib.pyplot as plt

    path_to_config = pathlib.Path(__file__).parents[1] / 'seacharts/config.yaml'

    from seacharts.enc import ENC

    enc = ENC()
    enc.show_display()

    shore = enc.shore
    land = enc.land
    seabed = enc.seabed

    fig, axs = plt.subplots()
    for layer in seabed.items():
        geometry = layer[1].geometry
        for polygon in geometry:
            east, north = polygon.exterior.xy
            axs.fill(east, north, alpha=0.5, fc='r', ec='none')

    plt.show()
    print("done")
