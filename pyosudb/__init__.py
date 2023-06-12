from pyosudb.osudb import parse_osudb
from pyosudb.collectiondb import parse_collectiondb
from pyosudb.scoresdb import parse_scoresdb

try:
    from importlib import metadata
    __version__ = metadata.version(__package__)
except ImportError:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__package__).version

__all__ = ["parse_osudb", "parse_collectiondb", "parse_scoresdb"]
