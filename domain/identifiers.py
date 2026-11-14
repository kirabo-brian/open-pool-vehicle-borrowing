from domain.errors import InvalidRequest


def clean_id(value, label):
    """Reject blank or non-string IDs; trim and uppercase the rest."""
    if not isinstance(value, str) or not value.strip():
        raise InvalidRequest(f"{label} must be a non-blank string")
    return value.strip().upper()
