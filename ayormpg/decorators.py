
class DangerousError(Exception):
    pass

def checkparam(func):
    def wrapper(*args,**kw):
        for i in args:
            if "'" in i:
                raise DangerousError('received a illegal character')
            if "and" in i:
                raise DangerousError('received a illegal character')
            if "or" in i:
                raise DangerousError('received a illegal character')
            if "union" in i:
                raise DangerousError('received a illegal character')
            if "-" in i:
                raise DangerousError('received a illegal character')
            if "&" in i:
                raise DangerousError('received a illegal character')
            if "|" in i:
                raise DangerousError('received a illegal character')
            if "*" in i:
                raise DangerousError('received a illegal character')
            if "|" in i:
                raise DangerousError('received a illegal character')
            else:
                pass
        for k,v in kw.items():
            if "'" in v:
                raise DangerousError('received a illegal character')
            if "and" in v:
                raise DangerousError('received a illegal character')
            if "or" in v:
                raise DangerousError('received a illegal character')
            if "union" in v:
                raise DangerousError('received a illegal character')
            if "-" in v:
                raise DangerousError('received a illegal character')
            if "*" in v:
                raise DangerousError('received a illegal character')
            if "|" in v:
                raise DangerousError('received a illegal character')

        return func(*args,**kw)
    return wrapper

