
class DBError(Exception):
    pass


class MultiRowsError(DBError):
    pass


class MultiColumnsError(DBError):
    pass
