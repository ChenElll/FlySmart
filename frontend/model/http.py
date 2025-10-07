# frontend/model/http.py
import os, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_BASE = os.getenv("FLYSMART_API", "http://127.0.0.1:8000")
PLANES_URL = f"{API_BASE}/planes"
DEFAULT_TIMEOUT = (3, 7)  # (connect, read) seconds

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3, status_forcelist=(502, 503, 504))
session.mount("http://", HTTPAdapter(max_retries=retry))
session.mount("https://", HTTPAdapter(max_retries=retry))
