if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import seacharts

    size = 20000, 12062                # w, h (east, north) distance in meters
    center = 44300, 6956450          # easting/northing (UTM zone 33N)
    # Norwegian county database name
    files = ['Basisdata_50_Trondelag_25833_Dybdedata_FGDB.gdb']

    enc = seacharts.enc.ENC(size=size, center=center, files=files,
                    new_data=True, multiprocessing=False)

    shore = enc.shore
    land = enc.land
    seabed = enc.seabed

    enc.show_display()

    fig, axs = plt.subplots()
    for layer in seabed.items():
        geometry = layer[1].geometry
        for polygon in geometry:
            east, north = polygon.exterior.xy
            axs.fill(east, north, alpha=0.5, fc='r', ec='none')

    plt.show()
    print("done")
