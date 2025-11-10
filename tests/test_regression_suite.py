import sys

import pytest

if __name__ == "__main__":
    errno = pytest.main(["-q", "--maxfail=1"])
    sys.exit(errno)
