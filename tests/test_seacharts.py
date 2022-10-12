if __name__ == '__main__':
    import seacharts.enc as senc

    size = 20000, 12062                # w, h (east, north) distance in meters
    center = 44300, 6956450          # easting/northing (UTM zone 33N)
    # Norwegian county database name
    files = ['Basisdata_15_More_og_Romsdal_25833_Dybdedata_FGDB.gdb']

    enc = senc.ENC(size=size, center=center, files=files, new_data=True)

    print(enc.seabed[0])
    print(enc.shore)
    print(enc.land)

    enc.show_display()
