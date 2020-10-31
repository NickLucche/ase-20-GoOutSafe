class GoOutSafeError(Exception):
    pass

class DatabaseError(GoOutSafeError):
    pass

class FormValidationError(GoOutSafeError):
    pass