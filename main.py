from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "matches.json"

# ⬇️ Change these credentials to whatever you want
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ipl2026"

sessions = set()

def load():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_logged_in(request: Request):
    token = request.cookies.get("session")
    return token in sessions

# ✅ ServiceNow calls this — no auth needed
@app.get("/matches")
def get_all():
    return load()

@app.get("/matches/{match_no}")
def get_one(match_no: int):
    for m in load():
        if m["match_no"] == match_no:
            return m
    raise HTTPException(status_code=404, detail="Match not found")

@app.post("/matches")
def add_match(request: Request, match: dict):
    if not is_logged_in(request):
        raise HTTPException(status_code=403, detail="Not authorized")
    data = load()
    data.append(match)
    save(data)
    return {"status": "added"}

@app.put("/matches/{match_no}")
def update_match(request: Request, match_no: int, updated: dict):
    if not is_logged_in(request):
        raise HTTPException(status_code=403, detail="Not authorized")
    data = load()
    for i, m in enumerate(data):
        if m["match_no"] == match_no:
            data[i] = updated
            save(data)
            return {"status": "updated"}
    raise HTTPException(status_code=404, detail="Match not found")

@app.delete("/matches/{match_no}")
def delete_match(request: Request, match_no: int):
    if not is_logged_in(request):
        raise HTTPException(status_code=403, detail="Not authorized")
    data = load()
    data = [m for m in data if m["match_no"] != match_no]
    save(data)
    return {"status": "deleted"}

# 🔐 Login page
@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("templates/login.html", encoding="utf-8") as f:
        return f.read()

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        import uuid
        token = str(uuid.uuid4())
        sessions.add(token)
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie("session", token)
        return response
    return RedirectResponse(url="/login?error=1", status_code=302)

@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("session")
    sessions.discard(token)
    return RedirectResponse(url="/login", status_code=302)

# 🔐 Protected admin page
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()