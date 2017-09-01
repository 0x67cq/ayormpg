
class DangerousError(Exception):
    pass

def checkparam(func):
    def wrapper(*args,**kw):
        print('*************start check')
        for i in args:
            if isinstance(i,str):
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
            if isinstance(v, str):
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
        print('*****************end check')
        return func(*args,**kw)
    return wrapper

