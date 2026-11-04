import pytest, pathlib, yaml, requests

from api.booking_api import BookingAPI
from api.auth_api import AuthAPI
from utils.config_loader import load_config
from utils.logger import get_logger
from api.ping_api import  PingAPI


@pytest.fixture(scope="session", autouse=True)
def service_ready(config):
    url = f"{config['base_url']}/ping"
    try:
        resp = requests.get(url, timeout=3)
    except requests.RequestException:
        pytest.exit(
            f"被测服务未启动：{url}\n"
            "请先在另一个终端运行：cd restful-booker/restful-booker && npm start",
            returncode=1,
        )
    assert resp.status_code == 201, f"/ping 期望 201，实际 {resp.status_code}"


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