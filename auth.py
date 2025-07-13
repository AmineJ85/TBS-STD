from functools import wraps
from flask import redirect, session

def login_required(f): 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('student'):
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function