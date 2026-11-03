from api.base_api import BaseAPI

class AuthAPI(BaseAPI):
    def login(self, username, password):
        return self._request("POST", "/auth", json={"username":username, "password":password})