import pytest
import uuid


@pytest.fixture()
def uid():
    return str(uuid.uuid4())
