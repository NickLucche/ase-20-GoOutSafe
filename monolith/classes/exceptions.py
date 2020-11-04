class GoOutSafeError(Exception):
    pass

class DatabaseError(GoOutSafeError):
    pass

class UserNotInDB(GoOutSafeError):
    pass

class FormValidationError(GoOutSafeError):
    pass