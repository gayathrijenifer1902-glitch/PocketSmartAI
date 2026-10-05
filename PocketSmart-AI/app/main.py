import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .db import init_db, connection
from .auth import hash_password, verify_password, make_token, current_user
from .schemas import RegisterRequest, LoginRequest, HomeRequest, PartyRequest, JewelryRequest
from .recommender import recommend

ROOT = Path(__file__).resolve().parent.parent
@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield

app = FastAPI(title="PocketSmart AI", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
@app.get("/")
def index(): return FileResponse(ROOT / "static" / "index.html")
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/register")
def register(body: RegisterRequest):
    try:
        with connection() as con:
            cur = con.execute("INSERT INTO users(email,name,password_hash) VALUES(?,?,?)", (body.email.lower(), body.name, hash_password(body.password)))
        return {"access_token": make_token(cur.lastrowid), "token_type":"bearer", "user":{"id":cur.lastrowid,"email":body.email,"name":body.name}}
    except Exception as e:
        if "UNIQUE" in str(e): raise HTTPException(409, "An account with that email already exists")
        raise
@app.post("/login")
def login(body: LoginRequest):
    with connection() as con: user = con.execute("SELECT * FROM users WHERE email=?", (body.email.lower(),)).fetchone()
    if not user or not verify_password(body.password, user["password_hash"]): raise HTTPException(401, "Incorrect email or password")
    return {"access_token":make_token(user["id"]),"token_type":"bearer","user":{"id":user["id"],"email":user["email"],"name":user["name"]}}
@app.post("/token")
def token(body: LoginRequest): return login(body)
@app.post("/logout")
def logout(): return {"message":"Remove the bearer token from the client to finish logout."}
def save_and_return(kind, payload, user):
    result = recommend(kind, payload)
    with connection() as con: con.execute("INSERT INTO history(user_id,planner,request_json,response_json) VALUES(?,?,?,?)", (user['id'],kind,json.dumps(payload),json.dumps(result)))
    return result
@app.post("/generate-home")
def generate_home(body: HomeRequest, user=Depends(current_user)): return save_and_return("home", body.model_dump(), user)
@app.post("/generate-party")
def generate_party(body: PartyRequest, user=Depends(current_user)): return save_and_return("party", body.model_dump(), user)
@app.post("/generate-jewelry")
def generate_jewelry(body: JewelryRequest, user=Depends(current_user)): return save_and_return("jewelry", body.model_dump(), user)
@app.post("/generate-jewelry/upload")
async def generate_jewelry_upload(budget: float = Form(...), occasion: str = Form(...), style: str = Form("classic"), outfit_description: str = Form(""), image: UploadFile | None = File(None), user=Depends(current_user)):
    payload = JewelryRequest(budget=budget, occasion=occasion, style=style, outfit_description=outfit_description).model_dump()
    raw = await image.read() if image else None
    result = recommend("jewelry", payload, raw)
    with connection() as con: con.execute("INSERT INTO history(user_id,planner,request_json,response_json) VALUES(?,?,?,?)", (user['id'],"jewelry",json.dumps(payload),json.dumps(result)))
    return result
@app.get("/session-info")
def session_info(user=Depends(current_user)): return {"authenticated":True,"user":user}
@app.get("/session-data")
def session_data(user=Depends(current_user)): return {"user":user,"features":["history","saved planner results"]}
@app.get("/history")
def history(user=Depends(current_user)):
    with connection() as con: rows=con.execute("SELECT id,planner,request_json,response_json,created_at FROM history WHERE user_id=? ORDER BY id DESC",(user['id'],)).fetchall()
    return [{**dict(r),"request":json.loads(r['request_json']),"result":json.loads(r['response_json'])} for r in rows]
@app.get("/recommendations-details/{history_id}")
def details(history_id:int,user=Depends(current_user)):
    with connection() as con: row=con.execute("SELECT * FROM history WHERE id=? AND user_id=?",(history_id,user['id'])).fetchone()
    if not row: raise HTTPException(404,"Recommendation not found")
    return {"id":row['id'],"planner":row['planner'],"request":json.loads(row['request_json']),"result":json.loads(row['response_json'])}
