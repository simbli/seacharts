from enum import Enum, auto


class MapFormat(Enum):
    """
    Enumeration representing various map formats supported by the application.

    The enumeration includes the following formats:

    - FGDB: File Geodatabase format, used primarily in Esri's GIS software.
    - S57: IHO S-57 format, used for nautical chart data exchange.

    This enum can be used to specify the desired map format when working with spatial data.
    """
    FGDB = auto()
    S57 = auto()
