class ApplicationError(Exception):
    pass

class DuplicateApplicationError(ApplicationError):
    pass

class InvalidApplicationStateError(ApplicationError):
    pass