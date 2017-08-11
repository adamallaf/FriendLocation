import os
import pytest
import sys


@pytest.fixture(scope="session", autouse=True)
def setEnvironmentVariables():
    if 'linux' in sys.platform:
        os.environ["TMP"] = "/tmp"

