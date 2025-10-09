# frontend/model/http.py
import os, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ------------------------------------------------------------
# API Configuration
# ------------------------------------------------------------
# Base URL for the backend API. Uses an environment variable for flexibility.
# Defaults to localhost if not provided.
API_BASE = os.getenv("FLYSMART_API", "http://127.0.0.1:8000")

# Endpoint for plane-related API calls
PLANES_URL = f"{API_BASE}/planes"

# Default timeout for HTTP requests: (connect_timeout, read_timeout)
DEFAULT_TIMEOUT = (3, 7)

# ------------------------------------------------------------
# Session with retry logic
# ------------------------------------------------------------
# Create a persistent HTTP session to reuse connections efficiently.
session = requests.Session()

# Define retry strategy for transient network errors.
# - total=3 → retry up to 3 times
# - backoff_factor=0.3 → exponential backoff between retries
# - status_forcelist → only retry for specific HTTP errors
retry = Retry(total=3, backoff_factor=0.3, status_forcelist=(502, 503, 504))

# Mount the retry strategy for both HTTP and HTTPS requests.
session.mount("http://", HTTPAdapter(max_retries=retry))
session.mount("https://", HTTPAdapter(max_retries=retry))
