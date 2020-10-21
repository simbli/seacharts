import os


class Region:
    prefix = 'Basisdata'
    data_type = 'Dybdedata'
    projection = '25833'
    suffix = 'FGDB.zip'
    path_external = 'data', 'external'
    external_chart_files = next(os.walk(os.path.join(*path_external)))[2]
    supported = ('Agder', 'Hele landet', 'Møre og Romsdal', 'Nordland',
                 'Nordsjøen', 'Norge', 'Oslo', 'Rogaland', 'Svalbard',
                 'Troms og Finnmark', 'Trøndelag',
                 'Vestfold og Telemark',
                 'Vestland', 'Viken')

    def __init__(self, name: str):
        if name in self.supported:
            if name == 'Hele landet':
                self.name = 'Norge'
            else:
                self.name = name
        else:
            raise ValueError(
                f"ENC: Invalid region name '{name}', "
                f"possible candidates are {self.supported}"
            )
        self.file_name = self.validate_file_name()

    @property
    def id(self):
        string = self.name
        for s, r in [('æ', 'e'), ('ø', 'o'), ('å', 'a'), (' ', '_')]:
            string = string.replace(s, r)
        return string

    @property
    def zip_path(self):
        gdb = self.file_name.replace('.zip', '.gdb')
        return '/'.join(('zip:/', *self.path_external, self.file_name, gdb))

    def validate_file_name(self):
        for file_name in self.external_chart_files:
            if self.id in file_name:
                if self.file_name_matches_template(file_name):
                    return file_name
                else:
                    raise ValueError(
                        f"ENC: Region '{self.name}' should have the form "
                        f"{Region.prefix}_<int>_{self.id}_"
                        f"{Region.projection}_{Region.data_type}"
                        f"_{Region.suffix}"
                    )
        else:
            raise FileExistsError(
                f"ENC: Region FGDB file for '{self.name}' not found at "
                f"'{os.path.join(*self.path_external)}'"
            )

    def file_name_matches_template(self, string):
        items = string.split('_')
        form = (items[0], items[-1], items[-2], items[-3])
        template = (self.prefix, self.suffix, self.data_type, self.projection)
        return True if form == template else False
