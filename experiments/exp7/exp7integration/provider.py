"""Selected-metadata provider port. No create/payment API; lazy HTTP only."""
from pathlib import Path
from exp7ops.evidence import require, strict, successful_instance_response, selected_credit


class NativeHTTP:
    def __init__(self, credential_path):
        self.credential_path = Path(credential_path)

    def request(self, method, path):
        import urllib.request
        import urllib.error
        token = self.credential_path.read_text().strip()
        require(token and "\n" not in token, "provider credential unavailable")
        request = urllib.request.Request("https://console.vast.ai/api/v0"+path, method=method,
                                         headers={"Authorization": "Bearer "+token, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, response.read()
        except BaseException:
            # Never propagate a urllib exception with a URL/header/body to logs.
            raise ValueError("provider transport failed") from None


class BoundProvider:
    def __init__(self, *, instance, credential_path=None, http=None):
        require(type(instance) is int and instance > 0, "approved exact provider instance")
        require((credential_path is None) != (http is None), "exactly one provider transport")
        self.instance = instance
        self.http = NativeHTTP(credential_path) if http is None else http
        require(callable(getattr(self.http, "request", None)), "provider HTTP capability")

    def _request(self, method, path):
        try:
            code, body = self.http.request(method, path)
            require(type(code) is int and 200 <= code < 300, "provider HTTP failure")
            require(type(body) is bytes, "provider response bytes")
            return code, strict(body)
        except BaseException:
            raise ValueError("provider request or response refused") from None

    def instances(self):
        try:
            code, value = self._request("GET", "/instances/")
            return successful_instance_response(code, value)
        except BaseException:
            raise ValueError("provider instance observation refused") from None

    def credit(self):
        try:
            _, value = self._request("GET", "/users/current/")
            return {"credit": selected_credit(value)}
        except BaseException:
            raise ValueError("provider credit observation refused") from None

    def delete(self, instance):
        require(type(instance) is int and instance == self.instance, "DELETE exact approved instance only")
        try:
            _, value = self._request("DELETE", f"/instances/{instance}/")
            require(type(value) is dict and value.get("success") is True and not any(k in value for k in ("error", "errors")), "DELETE failed")
            return {"success": True}
        except BaseException:
            raise ValueError("provider DELETE unconfirmed; retain claim") from None
