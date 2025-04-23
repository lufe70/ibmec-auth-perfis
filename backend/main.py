# main.py
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import httpx
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import urllib.parse
import uuid

# Carregar variáveis de ambiente
load_dotenv()

# Configuração Microsoft OAuth
TENANT_ID = os.getenv("MS_TENANT_ID", "common")
CLIENT_ID = os.getenv("MS_CLIENT_ID", "seu-client-id-aqui")
CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET", "seu-client-secret-aqui") 
REDIRECT_URI = os.getenv("MS_REDIRECT_URI", "http://localhost:8000/auth/callback")
SCOPES = ["User.Read"]
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configuração JWT
SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-para-desenvolvimento")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Inicializar app FastAPI
app = FastAPI(title="Autenticação Microsoft IBMEC")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua por origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funções auxiliares
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def determine_user_role(email):
    # Verificar se é um email do IBMEC
    if not email.lower().endswith("@ibmec.edu.br"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Apenas emails do IBMEC são permitidos",
        )
    
    # Verificar se o email contém "professor"
    if "professor" in email.lower():
        return "professor"
    else:
        return "aluno"

# Rotas
@app.get("/")
async def root():
    return {"message": "API de Autenticação Microsoft para IBMEC"}

@app.get("/auth/login")
async def login():
    # Redireciona para página de login da Microsoft
    state = str(uuid.uuid4())
    
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query", 
        "scope": " ".join(SCOPES),
        "state": state
    }
    
    auth_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    # Processa o retorno da autenticação Microsoft
    # Obter o código de autorização dos parâmetros da query
    params = dict(request.query_params)
    
    if "error" in params:
        return JSONResponse(
            status_code=400,
            content={
                "error": params.get("error"),
                "error_description": params.get("error_description", "Falha na autenticação")
            }
        )
    
    if "code" not in params:
        return JSONResponse(
            status_code=400, 
            content={"error": "Código de autorização não fornecido"}
        )
    
    # Trocar o código por tokens
    async with httpx.AsyncClient() as client:
        token_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": params["code"],
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        response = await client.post(
            f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
            data=token_data
        )
        
        if response.status_code != 200:
            return JSONResponse(
                status_code=400,
                content={"error": f"Falha ao trocar código por tokens: {response.text}"}
            )
        
        tokens = response.json()
        ms_access_token = tokens.get("access_token")
        
        # Obter informações do usuário
        user_response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {ms_access_token}"}
        )
        
        if user_response.status_code != 200:
            return JSONResponse(
                status_code=400,
                content={"error": "Falha ao obter informações do usuário"}
            )
        
        user_data = user_response.json()
        
        # Extrair informações do usuário
        email = user_data.get("userPrincipalName", "")
        username = email.split("@")[0] if "@" in email else email
        display_name = user_data.get("displayName", "")
        
        # Determinar o perfil do usuário com base no email
        role = determine_user_role(email)
        
        # Criar nosso próprio token de acesso com informações do perfil
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": username,
                "email": email,
                "name": display_name,
                "role": role,  # Incluir o perfil no token
            }, 
            expires_delta=access_token_expires
        )
        
        # Redirecionar para o frontend com o token
        redirect_url = f"{FRONTEND_URL}/auth?token={access_token}"
        return RedirectResponse(redirect_url)

@app.get("/me")
async def get_me(request: Request):
    # Retorna informações do usuário autenticado
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "username": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "role": payload.get("role"),  # Incluir o perfil na resposta
            "authenticated": True
        }
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
