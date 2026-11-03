from api.base_api import BaseAPI

class BookingAPI(BaseAPI):
    def create(self, payload, token=None):
        return self._request("POST", "/booking", json=payload, token=token)
    def get(self, booking_id):
        return self._request("GET", f"/booking/{booking_id}")
    def update(self, booking_id, payload, token=None):
        return self._request("PUT", f"/booking/{booking_id}", json=payload, token=token)
    def delete(self, booking_id, token=None):
        return self._request("DELETE", f"/booking/{booking_id}", token=token)