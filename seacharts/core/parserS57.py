from seacharts.core import DataParser


class S57Parser(DataParser):
    def _is_map_type(self, path):
        if path.is_dir():
            for p in path.iterdir():
                if p.suffix is ".000":
                    return True
