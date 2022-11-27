def userwrite_json(id: int, username: str|None = None, email: str|None = None, password: str|None = None, role: str|None = None):
    if not username:
        username = f'user{id}'
    if not email:
        email = f'user{id}@company.com'
    if not password:
        password = 'password'
    if not role:
        role = 'customer'
    if role not in ['customer', 'admin']:
        raise ValueError('Invalid role')
    return {"username":username, "email":email, "password":password, "role":role}