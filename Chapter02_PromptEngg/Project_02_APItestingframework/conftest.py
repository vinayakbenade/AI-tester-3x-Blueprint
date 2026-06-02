import pytest
import requests
from settings import settings as cfg
from base_client import BaseClient
from pet_service import PetService


@pytest.fixture(scope="session")
def settings():
    return cfg


@pytest.fixture(scope="session")
def session(settings):
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    return s


@pytest.fixture(scope="session")
def base_client(session, settings):
    return BaseClient(session=session, base_url=settings.base_url, timeout=settings.timeout, retries=settings.retries, backoff=settings.backoff_seconds)


@pytest.fixture
def pet_service(base_client):
    return PetService(base_client)


@pytest.fixture
def new_pet_payload():
    return {"id": None, "name": "pytest-pet", "photoUrls": ["http://example.com/pet.jpg"], "status": "available"}
