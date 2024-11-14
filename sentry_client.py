import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://sentry.io/api/0"
SENTRY_ORG = "mozilla"


class SentryClient:
    """A simple Sentry REST API client."""

    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"
        adapter = HTTPAdapter(max_retries=Retry(status_forcelist=[429, 503]))
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{BASE_URL}/{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def paginated_request(self, path: str, **kwargs):
        url = f"{BASE_URL}/{path}"
        while True:
            response = self.session.request("GET", url, **kwargs)
            response.raise_for_status()
            yield from response.json()
            next = response.links.get("next")
            if not next or next.get("results") != "true":
                break
            url = next["url"]

    def org_members(self):
        yield from self.paginated_request(f"organizations/{SENTRY_ORG}/members/")

    def projects(self):
        yield from self.paginated_request(f"organizations/{SENTRY_ORG}/projects/")

    def issues(self, project_slug: str, query: str, stats_period: str = "14d"):
        path = f"projects/{SENTRY_ORG}/{project_slug}/issues/"
        params = {"query": query, "statsPeriod": stats_period}
        yield from self.paginated_request(path, params=params)

    def team_members(self, team_slug: str):
        yield from self.paginated_request(f"teams/{SENTRY_ORG}/{team_slug}/members/")
