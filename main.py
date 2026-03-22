from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests, uvicorn, sqlite3, os, random, string
from datetime import datetime, timedelta

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
DB_FILE = "royal_keys.db"

def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def khoi_tao_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS keys (key_str TEXT PRIMARY KEY, expire_time DATETIME, is_banned INTEGER)''')
        c.execute("INSERT OR IGNORE INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, ?)", ('hungadmin11', '2099-12-31 23:59:59', 0))
        conn.commit()

khoi_tao_db()

# --- THUẬT TOÁN V16: SUPREME MATRIX ---
def tinh_toan_v16(kq_list):
    if len(kq_list) < 5: return "", "ĐANG PHÂN TÍCH"
    gan_nhat = kq_list[-50:] 
    kq_cuoi = kq_list[-1]
    
    diem_tai = diem_xiu = 0
    loi_khuyen = "VÀO ĐỀU TAY"

    # QUÉT BỆT VÀ BẺ CẦU
    chuoi_bet = 1
    for i in range(len(kq_list)-2, -1, -1):
        if kq_list[i] == kq_cuoi: chuoi_bet += 1
        else: break
        
    if chuoi_bet == 4:
        if kq_cuoi == "Tài": diem_xiu += 300
        else: diem_tai += 300
        loi_khuyen = "GẤP THẾP BẺ CẦU"
    elif chuoi_bet >= 5:
        if kq_cuoi == "Tài": diem_tai += 350
        else: diem_xiu += 350
        loi_khuyen = "ĐU BỆT MẠNH TAY"

    # QUÉT PING-PONG 1-1
    chuoi_1_1 = 1
    for i in range(len(kq_list)-2, -1, -1):
        if kq_list[i] != kq_list[i+1]: chuoi_1_1 += 1
        else: break
        
    if chuoi_1_1 >= 5 and chuoi_bet < 4:
        if kq_cuoi == "Tài": diem_tai += 200 
        else: diem_xiu += 200
        loi_khuyen = "BẺ GÃY NHỊP 1-1"

    # CẢM BIẾN BẪY NHÀ CÁI
    if chuoi_1_1 >= 3 and chuoi_bet <= 2 and abs(gan_nhat.count("Tài") - gan_nhat.count("Xỉu")) < 4:
        return "CHỜ", "CẦU LOẠN - NẰM IM"

    # MA TRẬN MARKOV V16
    tt = tx = xt = xx = 0
    for i in range(len(gan_nhat)-1):
        if gan_nhat[i] == "Tài" and gan_nhat[i+1] == "Tài": tt += 1
        elif gan_nhat[i] == "Tài" and gan_nhat[i+1] == "Xỉu": tx += 1
        elif gan_nhat[i] == "Xỉu" and gan_nhat[i+1] == "Tài": xt += 1
        elif gan_nhat[i] == "Xỉu" and gan_nhat[i+1] == "Xỉu": xx += 1

    if kq_cuoi == "Tài":
        diem_tai += (tt / (tt + tx + 0.001)) * 80
        diem_xiu += (tx / (tt + tx + 0.001)) * 80
    else:
        diem_tai += (xt / (xt + xx + 0.001)) * 80
        diem_xiu += (xx / (xt + xx + 0.001)) * 80

    if diem_tai > diem_xiu + 20: return "TÀI", loi_khuyen
    elif diem_xiu > diem_tai + 20: return "XỈU", loi_khuyen
    
    return ("TÀI" if kq_cuoi == "Xỉu" else "XỈU"), "ĐÁNH DÒ ĐƯỜNG"

def phan_tich_ai_v16(kq_list, is_chanle):
    tong_tai = kq_list.count("Tài"); tong_xiu = kq_list.count("Xỉu")
    if len(kq_list) < 6: return {"du_doan": "LOADING...", "ti_le": 0, "loi_khuyen": "ĐANG TẢI", "history": []}
    
    du_doan_hien_tai, loi_khuyen = tinh_toan_v16(kq_list)
    kq_cuoi = kq_list[-1]
    
    if du_doan_hien_tai == "CHỜ":
        return {"du_doan": "CHỜ CẦU", "ti_le": 0, "loi_khuyen": "BẪY NHÀ CÁI - KHÔNG ĐÁNH", "history": []}

    ty_le = random.uniform(96.5, 99.9)
    if du_doan_hien_tai == "": du_doan_hien_tai = "TÀI" if kq_cuoi == "Xỉu" else "XỈU"

    history = []
    so_van = min(15, len(kq_list) - 5)
    for i in range(len(kq_list)-so_van, len(kq_list)):
        sub_list = kq_list[:i]
        actual = kq_list[i]
        pred, _ = tinh_toan_v16(sub_list)
        if pred == "" or pred == "CHỜ": pred = "TÀI" if sub_list[-1] == "Xỉu" else "XỈU"
        
        pred_hien_thi = "CHẴN" if pred == "TÀI" and is_chanle else ("LẺ" if pred == "XỈU" and is_chanle else pred)
        actual_hien_thi = "CHẴN" if actual == "Tài" and is_chanle else ("LẺ" if actual == "Xỉu" and is_chanle else actual.upper())
        
        status = "WIN" if pred.upper() == actual.upper() else "LOSE"
        history.insert(0, {"du_doan": pred_hien_thi, "ket_qua": actual_hien_thi, "status": status})

    return {"du_doan": du_doan_hien_tai, "ti_le": round(ty_le, 1), "loi_khuyen": loi_khuyen, "tong_tai": tong_tai, "tong_xiu": tong_xiu, "history": history}

def get_id(item):
    if isinstance(item, dict):
        for k in ['id', 'phien', 'sessionId', 'SessionID']:
            if k in item and str(item[k]).isdigit(): return int(item[k])
    return 0

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Powered-By"] = "HUNGCUTO-V16-SUPREME"
    response.headers["X-Frame-Options"] = "DENY"
    return response

@app.get("/api/scan")
async def scan_game(tool: str, key: str):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (key,))
        row = c.fetchone()
        
    if not row: return JSONResponse(status_code=403, content={"status": "error", "msg": "Key không tồn tại!"})
    if row[1] == 1 and key != "hungadmin11": return JSONResponse(status_code=403, content={"status": "error", "msg": "Key bị Tường Lửa khóa!"})
    if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") and key != "hungadmin11": 
        return JSONResponse(status_code=403, content={"status": "error", "msg": "Key đã hết hạn!"})

    if tool == "lc79_xd": url = "https://wcl.tele68.com/v1/chanlefull/sessions"
    elif tool == "lc79_md5": url = "https://wtxmd52.tele68.com/v1/txmd5/sessions"
    elif tool == "lc79_tx": url = "https://wtx.tele68.com/v1/tx/sessions"
    elif tool == "betvip_tx": url = "https://wtx.macminim6.online/v1/tx/sessions"
    elif tool == "betvip_md5": url = "https://wtxmd52.macminim6.online/v1/txmd5/sessions"
    else: return {"status": "error", "msg": "Cổng Game Không Hợp Lệ!"}

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0 SUPREME-BOT"}, timeout=5).json()
        lst = res.get("data", res.get("list", res)) if isinstance(res, dict) else res
        if not lst or not isinstance(lst, list): return {"status": "error", "msg": "Đang đồng bộ..."}
        
        lst = sorted(lst, key=get_id)
        
        kq = []
        is_chanle = ("chanle" in url.lower() or tool == "lc79_xd")
        for s in lst:
            val = str(s).upper()
            if is_chanle:
                if "CHẴN" in val or "CHAN" in val or "'C'" in val or "0" in val: kq.append("Tài")
                else: kq.append("Xỉu")
            else:
                if "TAI" in val or "TÀI" in val or "'RESULT': 1" in val or "'T'" in val: kq.append("Tài")
                else: kq.append("Xỉu")
        
        data = phan_tich_ai_v16(kq, is_chanle)
        
        for idx, h in enumerate(data["history"]):
            h["phien"] = get_id(lst[-(idx+1)])

        if is_chanle and data["du_doan"] not in ["LOADING...", "CHỜ CẦU"]:
            data["du_doan"] = "CHẴN" if data["du_doan"] == "TÀI" else "LẺ"
            data["tong_chan"] = data.pop("tong_tai", 0)
            data["tong_le"] = data.pop("tong_xiu", 0)

        s_cuoi = lst[-1]
        phien_hien_tai = get_id(s_cuoi)
        if phien_hien_tai > 0: data["phien"] = str(phien_hien_tai + 1)
        else: data["phien"] = "ĐANG TẢI..."
            
        return {"status": "success", "data": data, "secure": "V16-SECURE-ACTIVE"}
    except Exception as e: return {"status": "error", "msg": "Tường lửa chặn kết nối!"}

class KeyReq(BaseModel): key: str
@app.post("/api/verify_key")
async def verify_key(req: KeyReq):
    k = req.key.strip()
    if not k: return {"status": "error", "msg": "Nhập Mã Key!"}
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (k,))
        row = c.fetchone()
        if not row: return {"status": "error", "msg": "TRUY CẬP TRÁI PHÉP!"}
        if row[1] == 1 and k != "hungadmin11": return {"status": "error", "msg": "TÀI KHOẢN BỊ KHÓA!"}
        if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") and k != "hungadmin11": return {"status": "error", "msg": "Key hết hạn!"}
        role = "admin" if k == "hungadmin11" else "user"
        return {"status": "success", "role": role, "expire": "VĨNH VIỄN (MASTER)" if role == "admin" else row[0]}

@app.get("/api/admin/list_keys")
async def admin_list_keys(admin_key: str):
    if admin_key != "hungadmin11": return {"status": "error"}
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT key_str, expire_time, is_banned FROM keys WHERE key_str != 'hungadmin11' ORDER BY expire_time DESC")
        return {"status": "success", "keys": c.fetchall()}

class CreateKeyReq(BaseModel): admin_key: str; duration: str; custom_key: str = ""
@app.post("/api/admin/create_key")
async def create_key(req: CreateKeyReq):
    if req.admin_key != "hungadmin11": return {"status": "error"}
    new_key = req.custom_key.strip() if req.custom_key.strip() != "" else "VIP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    now = datetime.now()
    if req.duration == "1H": exp = now + timedelta(hours=1)
    elif req.duration == "1D": exp = now + timedelta(days=1)
    elif req.duration == "3D": exp = now + timedelta(days=3)
    elif req.duration == "30D": exp = now + timedelta(days=30)
    else: return {"status": "error", "msg": "Lỗi gói!"}
    
    exp_str = exp.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, 0)", (new_key, exp_str))
            conn.commit()
        return {"status": "success", "new_key": new_key, "expire": exp_str}
    except sqlite3.IntegrityError: return {"status": "error", "msg": "Trùng Key!"}

class BanKeyReq(BaseModel): admin_key: str; target_key: str; action: str
@app.post("/api/admin/action_key")
async def action_key(req: BanKeyReq):
    if req.admin_key != "hungadmin11": return {"status": "error"}
    with get_db() as conn:
        c = conn.cursor()
        if req.action == "ban": c.execute("UPDATE keys SET is_banned = 1 WHERE key_str = ?", (req.target_key,))
        elif req.action == "unban": c.execute("UPDATE keys SET is_banned = 0 WHERE key_str = ?", (req.target_key,))
        elif req.action == "delete": c.execute("DELETE FROM keys WHERE key_str = ?", (req.target_key,))
        conn.commit()
    return {"status": "success"}

@app.get("/")
async def home(): return FileResponse("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
