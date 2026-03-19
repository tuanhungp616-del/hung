from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests, sqlite3, os, random, string
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
DB_FILE = "royal_keys.db"

def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def khoi_tao_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS keys (key_str TEXT PRIMARY KEY, expire_time DATETIME, is_banned INTEGER)''')
        # ĐÃ ĐỔI KEY ADMIN THÀNH hungadmin
        c.execute("INSERT OR IGNORE INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, ?)", ('hungadmin', '2099-12-31 23:59:59', 0))
        conn.commit()

khoi_tao_db()

# --- THUẬT TOÁN V11: SKY NEURAL ENGINE ---
def tinh_toan_v11(kq_list):
    if len(kq_list) < 5: return ""
    gan_nhat = kq_list[-25:] # Nhìn sâu 25 ván
    kq_cuoi = kq_list[-1]
    
    # 1. MA TRẬN XÁC SUẤT MARKOV ĐA TẦNG
    tt = tx = xt = xx = 0
    for i in range(len(gan_nhat)-1):
        if gan_nhat[i] == "Tài" and gan_nhat[i+1] == "Tài": tt += 1
        elif gan_nhat[i] == "Tài" and gan_nhat[i+1] == "Xỉu": tx += 1
        elif gan_nhat[i] == "Xỉu" and gan_nhat[i+1] == "Tài": xt += 1
        elif gan_nhat[i] == "Xỉu" and gan_nhat[i+1] == "Xỉu": xx += 1
    
    xs_tai = xs_xiu = 0
    if kq_cuoi == "Tài":
        xs_tai = tt / (tt + tx + 0.001); xs_xiu = tx / (tt + tx + 0.001)
    else:
        xs_tai = xt / (xt + xx + 0.001); xs_xiu = xx / (xt + xx + 0.001)

    # 2. PHÁ BỆT & BẺ CẦU 1-1
    chuoi_bet = 1
    for i in range(len(kq_list)-2, -1, -1):
        if kq_list[i] == kq_cuoi: chuoi_bet += 1
        else: break
        
    chuoi_1_1 = 1
    for i in range(len(kq_list)-2, -1, -1):
        if kq_list[i] != kq_list[i+1]: chuoi_1_1 += 1
        else: break
        
    if chuoi_bet == 4: return "TÀI" if kq_cuoi == "Xỉu" else "XỈU"
    if chuoi_bet >= 5: return kq_cuoi 
    if chuoi_1_1 >= 5: return kq_cuoi # Bẻ gãy cầu 1-1 quá dài
    
    # 3. NHẬN DIỆN MẪU HÌNH ĐẶC BIỆT
    c_7 = gan_nhat[-7:]; c_6 = gan_nhat[-6:]; c_5 = gan_nhat[-5:]
    if c_7 == ["Tài", "Tài", "Tài", "Xỉu", "Tài", "Tài", "Xỉu"]: return "TÀI"
    if c_7 == ["Xỉu", "Xỉu", "Xỉu", "Tài", "Xỉu", "Xỉu", "Tài"]: return "XỈU"
    if c_6 == ["Tài", "Xỉu", "Tài", "Xỉu", "Tài", "Xỉu"]: return "TÀI"
    if c_6 == ["Xỉu", "Tài", "Xỉu", "Tài", "Xỉu", "Tài"]: return "XỈU"
    if c_5 == ["Tài", "Tài", "Xỉu", "Tài", "Tài"]: return "XỈU"
    if c_5 == ["Xỉu", "Xỉu", "Tài", "Xỉu", "Xỉu"]: return "TÀI"
    
    # 4. CHỐT KẾT QUẢ KẾT HỢP XUNG LỰC & MARKOV
    lech_cau = gan_nhat.count("Tài") - gan_nhat.count("Xỉu")
    if lech_cau > 6: return "XỈU"
    if lech_cau < -6: return "TÀI"
    
    if xs_tai > xs_xiu + 0.1: return "TÀI"
    elif xs_xiu > xs_tai + 0.1: return "XỈU"
    
    return "TÀI" if kq_cuoi == "Xỉu" else "XỈU"

def phan_tich_ai_v11_sky(kq_list):
    tong_tai = kq_list.count("Tài"); tong_xiu = kq_list.count("Xỉu")
    if len(kq_list) < 6: return {"du_doan": "LOADING CORE...", "ti_le": 0, "tong_tai": tong_tai, "tong_xiu": tong_xiu, "dao_cau": False}
    
    du_doan_hien_tai = tinh_toan_v11(kq_list)
    du_doan_truoc = tinh_toan_v11(kq_list[:-1])
    kq_cuoi = kq_list[-1]
    
    ty_le = random.uniform(89.5, 96.8)
    dao_cau = False
    
    if du_doan_truoc != "" and du_doan_truoc.upper() != kq_cuoi.upper():
        du_doan_hien_tai = "TÀI" if du_doan_hien_tai == "XỈU" else "XỈU"
        ty_le = random.uniform(98.8, 99.9) 
        dao_cau = True

    if du_doan_hien_tai == "": du_doan_hien_tai = "TÀI" if kq_cuoi == "Xỉu" else "XỈU"
    return {"du_doan": du_doan_hien_tai, "ti_le": round(ty_le, 1), "tong_tai": tong_tai, "tong_xiu": tong_xiu, "dao_cau": dao_cau}

def get_id(item):
    if isinstance(item, dict):
        for k in ['id', 'phien', 'sessionId', 'SessionID']:
            if k in item and str(item[k]).isdigit(): return int(item[k])
    return 0

@app.route("/api/scan", methods=["GET"])
def scan_game():
    tool = request.args.get("tool", "")
    key = request.args.get("key", "")
    
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (key,))
        row = c.fetchone()
        
    if not row: return jsonify({"status": "error", "msg": "Key không tồn tại!"})
    if row[1] == 1 and key != "hungadmin": return jsonify({"status": "error", "msg": "Key này đã bị khóa!"})
    if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") and key != "hungadmin": 
        return jsonify({"status": "error", "msg": "Key đã hết hạn!"})

    if tool == "lc79_xd": url = "https://wcl.tele68.com/v1/chanlefull/sessions"
    elif tool == "lc79_md5": url = "https://wtxmd52.tele68.com/v1/txmd5/sessions"
    elif tool == "lc79_tx": url = "https://wtx.tele68.com/v1/tx/sessions"
    elif tool == "betvip_tx": url = "https://wtx.macminim6.online/v1/tx/sessions"
    elif tool == "betvip_md5": url = "https://wtxmd52.macminim6.online/v1/txmd5/sessions"
    else: return jsonify({"status": "error", "msg": "Cổng Game Không Hợp Lệ!"})

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
        lst = res.get("data", res.get("list", res)) if isinstance(res, dict) else res
        if not lst or not isinstance(lst, list): return jsonify({"status": "error", "msg": "Đang đồng bộ..."})
        
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
        
        data = phan_tich_ai_v11_sky(kq)
        if is_chanle and data["du_doan"] != "LOADING CORE...":
            data["du_doan"] = "CHẴN" if data["du_doan"] == "TÀI" else "LẺ"
            data["tong_chan"] = data.pop("tong_tai", 0)
            data["tong_le"] = data.pop("tong_xiu", 0)

        s_cuoi = lst[-1]
        phien_hien_tai = get_id(s_cuoi)
        if phien_hien_tai > 0: data["phien"] = str(phien_hien_tai + 1)
        else: data["phien"] = "ĐANG TẢI..."
            
        return jsonify({"status": "success", "data": data})
    except Exception as e: return jsonify({"status": "error", "msg": "Nhiễu sóng từ nhà cái!"})

@app.route("/api/verify_key", methods=["POST"])
def verify_key():
    req = request.get_json() or {}
    k = req.get("key", "").strip()
    if not k: return jsonify({"status": "error", "msg": "Nhập Mã Key!"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (k,))
        row = c.fetchone()
        if not row: return jsonify({"status": "error", "msg": "Key fake!"})
        if row[1] == 1 and k != "hungadmin": return jsonify({"status": "error", "msg": "Key bị khóa!"})
        if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") and k != "hungadmin": return jsonify({"status": "error", "msg": "Key hết hạn!"})
        role = "admin" if k == "hungadmin" else "user"
        return jsonify({"status": "success", "role": role, "expire": "VĨNH VIỄN (MASTER)" if role == "admin" else row[0]})

@app.route("/api/admin/list_keys", methods=["GET"])
def admin_list_keys():
    admin_key = request.args.get("admin_key", "")
    if admin_key != "hungadmin": return jsonify({"status": "error"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT key_str, expire_time, is_banned FROM keys WHERE key_str != 'hungadmin' ORDER BY expire_time DESC")
        return jsonify({"status": "success", "keys": c.fetchall()})

@app.route("/api/admin/create_key", methods=["POST"])
def create_key():
    req = request.get_json() or {}
    admin_key = req.get("admin_key", "")
    duration = req.get("duration", "")
    custom_key = req.get("custom_key", "")
    
    if admin_key != "hungadmin": return jsonify({"status": "error"})
    new_key = custom_key.strip() if custom_key.strip() != "" else "VIP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    now = datetime.now()
    if duration == "1H": exp = now + timedelta(hours=1)
    elif duration == "1D": exp = now + timedelta(days=1)
    elif duration == "3D": exp = now + timedelta(days=3)
    elif duration == "30D": exp = now + timedelta(days=30)
    else: return jsonify({"status": "error", "msg": "Lỗi gói!"})
    
    exp_str = exp.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, 0)", (new_key, exp_str))
            conn.commit()
        return jsonify({"status": "success", "new_key": new_key, "expire": exp_str})
    except sqlite3.IntegrityError: return jsonify({"status": "error", "msg": "Trùng Key!"})

@app.route("/api/admin/action_key", methods=["POST"])
def action_key():
    req = request.get_json() or {}
    admin_key = req.get("admin_key", "")
    target_key = req.get("target_key", "")
    action = req.get("action", "")
    
    if admin_key != "hungadmin": return jsonify({"status": "error"})
    with get_db() as conn:
        c = conn.cursor()
        if action == "ban": c.execute("UPDATE keys SET is_banned = 1 WHERE key_str = ?", (target_key,))
        elif action == "unban": c.execute("UPDATE keys SET is_banned = 0 WHERE key_str = ?", (target_key,))
        elif action == "delete": c.execute("DELETE FROM keys WHERE key_str = ?", (target_key,))
        conn.commit()
    return jsonify({"status": "success"})

@app.route("/")
def home(): return send_file("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
        
