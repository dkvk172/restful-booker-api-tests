import pytest, pathlib, yaml

from api.booking_api import BookingAPI
from api.auth_api import AuthAPI
from utils.config_loader import load_config
from utils.logger import get_logger

@pytest.fixture(scope="session")
def config():
    return load_config()

@pytest.fixture(scope="session")
def logger():
    return get_logger()

@pytest.fixture(scope="session")
def token(config, logger):
    resp = AuthAPI(config,logger).login(config['auth']['username'], config['auth']['password'])
    assert resp.status_code == 200
    return resp.json()['token']

@pytest.fixture
def booking_api(config, logger):
    return BookingAPI(config,logger)

@pytest.fixture
def booking_payload():
    path = pathlib.Path(__file__).parent.parent/"data"/"booking.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))

@pytest.fixture
def create_booking(booking_api, booking_payload, token):
    booking_id = booking_api.create(booking_payload, token).json()['bookingid']
    yield booking_id
    booking_api.delete(booking_id, token)