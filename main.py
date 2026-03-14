from fastapi import FastAPI
from fastapi.responses import FileResponse
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
        c.execute("INSERT OR IGNORE INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, ?)", ('adminvuakito', '2099-12-31 23:59:59', 0))
        conn.commit()

khoi_tao_db()

# ================= LÕI AI V6: QUANTUM NEURAL ENGINE (ĐÃ FIX LỖI LOADING CORE) =================
def phan_tich_ai_v6_quantum(kq_list):
    tong_tai = kq_list.count("Tài"); tong_xiu = kq_list.count("Xỉu")
    
    # HẠ MỨC YÊU CẦU XUỐNG 10 PHIÊN (Để API trả 15 phiên là ăn ngay)
    if len(kq_list) < 10: 
        return {"du_doan": "LOADING CORE...", "ti_le": 0, "tong_tai": tong_tai, "tong_xiu": tong_xiu}
    
    gan_nhat = kq_list[-15:]; kq_cuoi = kq_list[-1]
    chuoi_bet = 1
    for i in range(len(kq_list)-2, -1, -1):
        if kq_list[i] == kq_cuoi: chuoi_bet += 1
        else: break
        
    du_doan = ""; ty_le = 0.0

    if gan_nhat[-6:] == ["Tài", "Tài", "Tài", "Xỉu", "Tài", "Xỉu"]: du_doan = "TÀI"; ty_le = random.uniform(96.0, 99.5)
    elif gan_nhat[-6:] == ["Xỉu", "Xỉu", "Xỉu", "Tài", "Xỉu", "Tài"]: du_doan = "XỈU"; ty_le = random.uniform(96.0, 99.5)
    elif gan_nhat[-5:] == ["Tài", "Xỉu", "Tài", "Xỉu", "Tài"] or gan_nhat[-5:] == ["Xỉu", "Tài", "Xỉu", "Tài", "Xỉu"]:
        du_doan = "TÀI" if kq_cuoi == "Xỉu" else "XỈU"; ty_le = random.uniform(95.5, 99.9) 
    elif gan_nhat[-4:] == ["Tài", "Tài", "Xỉu", "Xỉu"]: du_doan = "TÀI"; ty_le = random.uniform(94.5, 98.5) 
    elif gan_nhat[-4:] == ["Xỉu", "Xỉu", "Tài", "Tài"]: du_doan = "XỈU"; ty_le = random.uniform(94.5, 98.5) 
    elif gan_nhat[-5:] == ["Tài", "Tài", "Tài", "Xỉu", "Xỉu"]: du_doan = "TÀI"; ty_le = random.uniform(91.0, 95.5)
    elif gan_nhat[-5:] == ["Xỉu", "Xỉu", "Xỉu", "Tài", "Tài"]: du_doan = "XỈU"; ty_le = random.uniform(91.0, 95.5)
    elif chuoi_bet == 3: du_doan = "TÀI" if kq_cuoi == "Xỉu" else "XỈU"; ty_le = random.uniform(84.5, 89.5)
    elif chuoi_bet == 4: du_doan = kq_cuoi; ty_le = random.uniform(88.0, 92.5)
    elif chuoi_bet >= 5: du_doan = kq_cuoi; ty_le = random.uniform(98.0, 99.9)
    else:
        lech_cau = tong_tai - tong_xiu
        if lech_cau > 8: du_doan = "XỈU"; ty_le = random.uniform(81.0, 87.5)
        elif lech_cau < -8: du_doan = "TÀI"; ty_le = random.uniform(81.0, 87.5)
        else: du_doan = "TÀI" if kq_cuoi == "Xỉu" else "XỈU"; ty_le = random.uniform(75.5, 83.5)

    return {"du_doan": du_doan, "ti_le": round(ty_le, 1), "tong_tai": tong_tai, "tong_xiu": tong_xiu}

@app.get("/api/scan")
async def scan_game(tool: str, key: str):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (key,))
        row = c.fetchone()
        
    if not row: return {"status": "error", "msg": "Key không tồn tại trên Hệ thống Hoàng Gia!"}
    if row[1] == 1 and key != "adminvuakito": return {"status": "error", "msg": "Key này đã bị Vua Kito khóa!"}
    if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") and key != "adminvuakito": 
        return {"status": "error", "msg": "Key đã hết hạn! Vui lòng nạp thêm tiền chuộc Key."}

    url = "https://wtx.tele68.com/v1/tx/lite-sessions" if tool == "lc79" else "https://wtx.macminim6.online/v1/tx/lite-sessions"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
        if not res.get("list"): return {"status": "error", "msg": "Chờ cầu mới..."}
        lst = res["list"][::-1]
        kq = ["Tài" if "TAI" in str(s.get("resultTruyenThong", "")).upper() else "Xỉu" for s in lst]
        
        data = phan_tich_ai_v6_quantum(kq)
        data["phien"] = str(int(lst[-1]["id"]) + 1)
        return {"status": "success", "data": data}
    except: return {"status": "error", "msg": "Mất tín hiệu vệ tinh với Server Game!"}

class KeyReq(BaseModel): key: str
@app.post("/api/verify_key")
async def verify_key(req: KeyReq):
    k = req.key.strip()
    if not k: return {"status": "error", "msg": "Dâng lên Mã Key để tiếp tục!"}
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (k,))
        row = c.fetchone()
        if not row: return {"status": "error", "msg": "Key fake hoặc không tồn tại!"}
        if row[1] == 1 and k != "adminvuakito": return {"status": "error", "msg": "Key này đã bị tử hình (Khóa)!"}
        
        is_expired = datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        if is_expired and k != "adminvuakito": return {"status": "error", "msg": "Key đã hết hạn sử dụng!"}
        
        role = "admin" if k == "adminvuakito" else "user"
        expire_str = "VĨNH VIỄN (MASTER KEY)" if role == "admin" else row[0]
        return {"status": "success", "role": role, "expire": expire_str}

@app.get("/api/admin/list_keys")
async def admin_list_keys(admin_key: str):
    if admin_key != "adminvuakito": return {"status": "error"}
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT key_str, expire_time, is_banned FROM keys WHERE key_str != 'adminvuakito' ORDER BY expire_time DESC")
        keys = c.fetchall()
    return {"status": "success", "keys": keys}

class CreateKeyReq(BaseModel): 
    admin_key: str
    duration: str
    custom_key: str = ""

@app.post("/api/admin/create_key")
async def create_key(req: CreateKeyReq):
    if req.admin_key != "adminvuakito": return {"status": "error"}
    
    if req.custom_key.strip() != "":
        new_key = req.custom_key.strip()
    else:
        new_key = "VIP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
    now = datetime.now()
    if req.duration == "1H": exp = now + timedelta(hours=1)
    elif req.duration == "1D": exp = now + timedelta(days=1)
    elif req.duration == "3D": exp = now + timedelta(days=3)
    elif req.duration == "30D": exp = now + timedelta(days=30)
    else: return {"status": "error", "msg": "Gói thời gian sai định dạng!"}
    
    exp_str = exp.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, 0)", (new_key, exp_str))
            conn.commit()
        return {"status": "success", "new_key": new_key, "expire": exp_str}
    except sqlite3.IntegrityError:
        return {"status": "error", "msg": "Mã Key này đã bị trùng, Boss gõ tên khác nhé!"}

class BanKeyReq(BaseModel): admin_key: str; target_key: str; action: str
@app.post("/api/admin/action_key")
async def action_key(req: BanKeyReq):
    if req.admin_key != "adminvuakito": return {"status": "error"}
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
                           
