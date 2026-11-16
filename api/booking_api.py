from api.base_api import BaseAPI

class BookingAPI(BaseAPI):
    def create(self, payload, token=None):
        return self._request("POST", "/booking", json=payload, token=token)
    def get(self, booking_id):
        return self._request("GET", f"/booking/{booking_id}")
    def list(self, accept="application/json", **filters):
        return self._request(
            "GET",
            "/booking",
            params={k: v for k, v in filters.items() if v is not None} or None,
            headers={"Accept": accept},
        )
    def update(self, booking_id, payload, token=None):
        return self._request("PUT", f"/booking/{booking_id}", json=payload, token=token)
    def delete(self, booking_id, token=None):
        return self._request("DELETE", f"/booking/{booking_id}", token=token)

    def patch(self, booking_id, payload, token=None, accept="application/json"):
        headers = {"Accept": accept}
        if token:
            headers["Cookie"] = f"token={token}"
        return self._request("PATCH", f"/booking/{booking_id}", json=payload, headers=headers)