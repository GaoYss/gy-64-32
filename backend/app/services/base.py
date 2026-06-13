from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel

from app.data.store import store


class CrudService:
    collection: str
    status_field: str | None = None
    status_transitions: dict[str, set[str]] | None = None
    relation_fields: dict[str, str] | None = None

    def list(self) -> list[dict]:
        return store.list_items(self.collection)

    def get(self, item_id: int) -> dict | None:
        items = store.list_items(self.collection)
        for item in items:
            if item["id"] == item_id:
                return item
        return None

    def create(self, payload: BaseModel) -> dict:
        data = payload.model_dump(mode="json")
        data = self.before_create(data)
        item = store.add_item(self.collection, data)
        self.after_create(item)
        return item

    def update(self, item_id: int, payload: BaseModel) -> dict:
        update_data = payload.model_dump(exclude_unset=True, mode="json")
        existing = self.get(item_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        update_data = self.before_update(existing, update_data)
        item = store.update_item(self.collection, item_id, update_data)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        self.after_update(item)
        return item

    def before_create(self, data: dict[str, Any]) -> dict[str, Any]:
        self._validate_relations(data)
        if self.status_field and self.status_field in data:
            self._validate_initial_status(data[self.status_field])
        return data

    def after_create(self, item: dict[str, Any]) -> None:
        pass

    def before_update(self, existing: dict[str, Any], update_data: dict[str, Any]) -> dict[str, Any]:
        self._validate_relations(update_data)
        if self.status_field and self.status_field in update_data:
            self._validate_status_transition(existing[self.status_field], update_data[self.status_field])
        return update_data

    def after_update(self, item: dict[str, Any]) -> None:
        pass

    def _validate_relations(self, data: dict[str, Any]) -> None:
        if not self.relation_fields:
            return
        for field_name, target_collection in self.relation_fields.items():
            if field_name in data and data[field_name] is not None:
                self._validate_relation_exists(target_collection, data[field_name], field_name)

    def _validate_relation_exists(self, collection: str, related_id: int, field_name: str) -> None:
        items = store.list_items(collection)
        found = any(item["id"] == related_id for item in items)
        if not found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} {related_id} does not exist",
            )

    def _initial_statuses(self) -> set[str]:
        if not self.status_transitions:
            return set()
        reachable: set[str] = set()
        for next_statuses in self.status_transitions.values():
            reachable.update(next_statuses)
        return set(self.status_transitions.keys()) - reachable

    def _validate_initial_status(self, status_value: str) -> None:
        if not self.status_transitions:
            return
        allowed = self._initial_statuses()
        if not allowed or status_value in allowed:
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status '{status_value}' is not a valid initial status. Available: {sorted(allowed)}",
        )

    def _validate_status_transition(self, old_status: str, new_status: str) -> None:
        if not self.status_transitions:
            return
        if new_status == old_status:
            return
        allowed = self.status_transitions.get(old_status, set())
        if new_status in allowed:
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition '{self.status_field}' from '{old_status}' to '{new_status}'. Allowed: {sorted(allowed) or 'none (terminal status)'}",
        )
