import os

_path_external = 'data', 'external'
_external_chart_files = next(os.walk(os.path.join(*_path_external)))[2]
supported_regions = ('Agder', 'Hele landet', 'Møre og Romsdal', 'Nordland',
                     'Nordsjøen', 'Norge', 'Oslo', 'Rogaland', 'Svalbard',
                     'Troms og Finnmark', 'Trøndelag',
                     'Vestfold og Telemark',
                     'Vestland', 'Viken')


class Region:
    prefix = 'Basisdata'
    data_type = 'Dybdedata'
    projection = '25833'
    suffix = 'FGDB.zip'

    def __init__(self, name: str):
        if name in supported_regions:
            if name == 'Hele landet':
                self.name = 'Norge'
            else:
                self.name = name
        else:
            raise RegionNameError(
                f"Region '{name}' not valid, possible candidates are "
                f"{supported_regions}"
            )
        self.file_name = self._validate_file_name()

    @property
    def id(self):
        string = self.name
        for s, r in [('æ', 'e'), ('ø', 'o'), ('å', 'a'), (' ', '_')]:
            string = string.replace(s, r)
        return string

    @property
    def zip_path(self):
        db_file = self.file_name.replace('.zip', '.gdb')
        return '/'.join(('zip:/', *_path_external, self.file_name, db_file))

    def _validate_file_name(self):
        for file_name in _external_chart_files:
            if self.id in file_name:
                if self._file_name_matches_template(file_name):
                    return file_name
                else:
                    raise InvalidRegionFileError(
                        f"Region '{self.name}' should have the form "
                        f"{Region.prefix}_<int>_{self.id}_"
                        f"{Region.projection}_{Region.data_type}"
                        f"_{Region.suffix}"
                    )
        else:
            raise RegionFileNotFoundError(
                f"Region '{self.name}' not found in path "
                f"'{os.path.join(*_path_external)}'"
            )

    def _file_name_matches_template(self, string):
        items = string.split('_')
        form = (items[0], items[-1], items[-2], items[-3])
        template = (self.prefix, self.suffix, self.data_type, self.projection)
        return True if form == template else False


class RegionNameError(NameError):
    pass


class RegionFileNotFoundError(FileExistsError):
    pass


class InvalidRegionFileError(NameError):
    pass
