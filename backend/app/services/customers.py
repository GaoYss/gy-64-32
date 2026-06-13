from app.services.base import CrudService


class CustomerService(CrudService):
    collection = "customers"
    status_field = "status"
    status_transitions = {
        "new": {"contacted", "lost"},
        "contacted": {"measured", "lost"},
        "measured": {"quoted", "lost"},
        "quoted": {"signed", "lost"},
        "signed": set(),
        "lost": set(),
    }


customer_service = CustomerService()
