if __name__ == '__main__':
    import sys
    print(sys.path)
    import seacharts.enc as senc

    size = 9000, 5062                # w, h (east, north) distance in meters
    center = 44300, 6956450          # easting/northing (UTM zone 33N)
    # Norwegian county database name
    files = ['Basisdata_15_More_og_Romsdal_25832_Dybdedata_FGDB.gdb']

    enc = ENC(size=size, center=center,
              files=files, new_data=True)
