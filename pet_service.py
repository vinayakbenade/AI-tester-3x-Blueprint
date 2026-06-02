from dataclasses import dataclass
from typing import Optional, Any, Dict, List
from base_client import BaseClient


@dataclass
class Pet:
    id: Optional[int]
    name: str
    photoUrls: List[str]
    status: Optional[str] = None


class PetService:
    def __init__(self, client: BaseClient):
        self.client = client

    def get_pet(self, pet_id: int) -> Any:
        return self.client.request("GET", f"/pet/{pet_id}")

    def create_pet(self, pet: Pet) -> Any:
        payload: Dict[str, Any] = {"id": pet.id, "name": pet.name, "photoUrls": pet.photoUrls}
        if pet.status is not None:
            payload["status"] = pet.status
        return self.client.request("POST", "/pet", json=payload)

    def delete_pet(self, pet_id: int) -> Any:
        return self.client.request("DELETE", f"/pet/{pet_id}")
