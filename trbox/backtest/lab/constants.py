from pathlib import Path

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 7000
DEFAULT_PATH = '.'
PY_SUFFIX = '.py'
RUNDIR_PREFIX = '.result'
FRONTEND_LOCAL_DIR = Path(Path(__file__).parent,
                          '../../frontend/trbox-lab/out/')
DEFAULT_FILENAME = 'index.html'
ENTRY_POINT = Path(FRONTEND_LOCAL_DIR, DEFAULT_FILENAME)
