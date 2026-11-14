class NotFoundError(LookupError):
    """BR6: a required aggregate or record could not be retrieved."""


class PoolNotFound(NotFoundError):
    pass


class DriverNotFound(NotFoundError):
    pass
