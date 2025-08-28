import os, requests

class ConnectorGPTForwarder:
    def __init__(self, url: str, auth: str | None):
        self.url = url
        self.auth = auth

    @classmethod
    def from_env(cls):
        url = os.getenv("CONNECTOR_GPT_URL")
        if not url:
            return None
        auth = os.getenv("CONNECTOR_GPT_AUTH")
        return cls(url, auth)

    def forward_summary(self, evt_id: str, row: dict, ersp: dict):
        headers = {"Content-Type": "application/json"}
        if self.auth:
            headers["Authorization"] = self.auth
        payload = {"id": evt_id, "row": row, "ersp": ersp}
        requests.post(self.url, json=payload, headers=headers, timeout=5)
