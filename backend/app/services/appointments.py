from app.services.base import CrudService


class AppointmentService(CrudService):
    collection = "appointments"
    status_field = "status"
    status_transitions = {
        "scheduled": {"completed", "cancelled"},
        "completed": set(),
        "cancelled": set(),
    }
    relation_fields = {
        "customer_id": "customers",
    }


appointment_service = AppointmentService()
