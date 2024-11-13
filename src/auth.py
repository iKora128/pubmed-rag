from firebase_admin import auth, initialize_app
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Firebase初期化
initialize_app()

security = HTTPBearer()

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: dict = Depends(verify_firebase_token)):
    return token.get('uid')