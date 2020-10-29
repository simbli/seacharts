import os


class NorwegianCharts:
    prefix = 'Basisdata'
    data_type = 'Dybdedata'
    projection = '25833'
    suffix = 'FGDB.zip'
    path_external = 'data', 'external'
    translation = str.maketrans('æøå ', 'eoa_')
    file_template = (prefix, suffix, data_type, projection)
    external_chart_files = next(os.walk(os.path.join(*path_external)))[2]
    supported = ('Agder', 'Hele landet', 'Møre og Romsdal', 'Nordland',
                 'Nordsjøen', 'Norge', 'Oslo', 'Rogaland', 'Svalbard',
                 'Troms og Finnmark', 'Trøndelag',
                 'Vestfold og Telemark',
                 'Vestland', 'Viken')

    def __init__(self, region):
        if isinstance(region, str):
            region = (region,)
        for name in region:
            if name not in self.supported:
                raise ValueError(
                    f"ENC: Invalid region name '{name}', "
                    f"possible candidates are {self.supported}"
                )
        self.names = region
        self.labels = [name.translate(self.translation) for name in region]
        self.file_paths = list(self.validate_files())

    def validate_files(self):
        for name, label in zip(self.names, self.labels):
            for file_name in self.external_chart_files:
                if label in file_name:
                    if self.matches_template(file_name):
                        yield self.zipped_form(file_name)
                        break
                    else:
                        raise ValueError(
                            f"ENC: Region '{name}' should have the form "
                            f"{self.prefix}_<int>_{label}_"
                            f"{self.projection}_{self.data_type}"
                            f"_{self.suffix}"
                        )
            else:
                raise FileNotFoundError(
                    f"ENC: Region FGDB file for '{name}' not found at "
                    f"'{os.path.join(*self.path_external)}'"
                )

    def matches_template(self, string):
        items = string.split('_')
        form = (items[0], items[-1], items[-2], items[-3])
        return True if form == self.file_template else False

    def zipped_form(self, file_name):
        gdb = file_name.replace('.zip', '.gdb')
        return '/'.join(('zip:/', *self.path_external, file_name, gdb))
