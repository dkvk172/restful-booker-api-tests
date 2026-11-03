from api.base_api import BaseAPI

class PingAPI(BaseAPI):
    def ping(self):
        self.log.info("health check")
        return self._request("GET", "/ping")