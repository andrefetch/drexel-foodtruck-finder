import os

# The seed CSVs are the committed source data, so they are resolved against the
# repo rather than against whatever directory the process was launched from.
DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "data"
)


def data_path(filename):
    return os.path.join(DATA_DIR, filename)
