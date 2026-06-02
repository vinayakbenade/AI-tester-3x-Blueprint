from typing import Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from loguru import logger
import time
import json


class CircuitBreaker:
    def __init__(self, fail_threshold: int = 5, reset_timeout: int = 60):
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.open = False

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.fail_threshold:
            self.open = True

    def reset(self):
        self.failure_count = 0
        self.open = False
        self.last_failure_time = None

    def allow_request(self) -> bool:
        if not self.open:
            return True
        if self.last_failure_time and (time.time() - self.last_failure_time) > self.reset_timeout:
            self.reset()
            return True
        return False


class BaseClient:
    def __init__(self, session: requests.Session, base_url: str, timeout: int = 30, retries: int = 3, backoff: float = 0.5):
        self.session = session
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.circuit = CircuitBreaker()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        headers = kwargs.get('headers') or {}
        safe_headers = {k: v for k, v in headers.items() if 'authorization' not in k.lower() and 'token' not in k.lower()}
        logger.info("{} {}", method, url)
        logger.debug("headers {}", safe_headers)

    def _handle_response(self, resp: requests.Response) -> Any:
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            self.circuit.record_failure()
            logger.error("http_error {} - {}", resp.status_code, resp.text)
            raise
        try:
            return resp.json()
        except json.JSONDecodeError:
            return resp.text

    def _retry_decorator(self):
        def _retry_on_exception(exc: Exception) -> bool:
            # Retry on connection errors and timeouts, and on server (5xx) HTTP errors.
            if isinstance(exc, requests.exceptions.ConnectionError):
                return True
            if isinstance(exc, requests.exceptions.Timeout):
                return True
            if isinstance(exc, requests.exceptions.HTTPError):
                resp = getattr(exc, 'response', None)
                if resp is not None and 500 <= getattr(resp, 'status_code', 0) < 600:
                    return True
                return False
            return False

        return retry(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff),
            retry=retry_if_exception(_retry_on_exception),
        )

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self.circuit.allow_request():
            raise RuntimeError("circuit open")
        url = self._url(path)
        self._log_request(method, url, **kwargs)

        decorator = self._retry_decorator()

        @decorator
        def _do():
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
            return self._handle_response(resp)

        return _do()
