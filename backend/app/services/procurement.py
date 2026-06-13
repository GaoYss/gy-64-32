from app.services.base import CrudService


class ProcurementService(CrudService):
    collection = "procurements"
    status_field = "status"
    status_transitions = {
        "pending": {"ordered"},
        "ordered": {"delivered"},
        "delivered": {"accepted", "returned"},
        "accepted": set(),
        "returned": set(),
    }
    relation_fields = {
        "project_id": "projects",
    }


procurement_service = ProcurementService()
