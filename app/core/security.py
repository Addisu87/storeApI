# Security-related logic (JWT, OAuth, hashing)

# Security
from fastapi.security import OAuth2PasswordBearer


# Security, Authentication and Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
