from app.services.base import CrudService


class InspectionService(CrudService):
    collection = "inspections"
    status_field = "result"
    status_transitions = {
        "pending": {"passed", "整改", "failed"},
        "passed": set(),
        "整改": {"passed", "failed"},
        "failed": set(),
    }
    relation_fields = {
        "project_id": "projects",
    }


inspection_service = InspectionService()
