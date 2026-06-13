from app.services.base import CrudService


class ProjectService(CrudService):
    collection = "projects"
    status_field = "phase"
    status_transitions = {
        "design": {"demolition"},
        "demolition": {"plumbing"},
        "plumbing": {"waterproofing"},
        "waterproofing": {"carpentry"},
        "carpentry": {"finishing"},
        "finishing": {"completed"},
        "completed": set(),
    }


project_service = ProjectService()
