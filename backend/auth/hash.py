from passlib.context import CryptContext

Hash = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')

def get_password_hash(password: str): 
    return Hash.hash(password)
def verify_password_hash(plain_password: str, hashed_password: str): 
    return Hash.verify(plain_password, hashed_password)