import pytest
from pet_service import Pet, PetService
import requests


@pytest.mark.parametrize("payload", [
    {"id": None, "name": "valid-pet", "photoUrls": ["http://x"], "status": "available"},
])
def test_create_and_get_pet(pet_service: PetService, payload):
    pet = Pet(id=payload.get("id"), name=payload["name"], photoUrls=payload["photoUrls"], status=payload.get("status"))
    created = pet_service.create_pet(pet)
    assert isinstance(created, dict)
    pet_id = created.get("id")
    assert pet_id is not None
    fetched = pet_service.get_pet(pet_id)
    assert fetched.get("id") == pet_id
    assert fetched.get("name") == pet.name


@pytest.mark.parametrize("pet_id", [999999999, -1])
def test_get_pet_not_found(pet_service: PetService, pet_id):
    with pytest.raises(requests.HTTPError):
        pet_service.get_pet(pet_id)
