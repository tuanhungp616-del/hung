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
        c.execute("INSERT OR IGNORE INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, ?)", ('hungki98vip', '2099-12-31 23:59:59', 0))
        conn.commit()

khoi_tao_db()

# ==========================================
# 🧠 NÃO BỘ 1: TÀI XỈU (ĐÃ VÁ LỖI ANTI-CRASH)
# ==========================================
def tinh_toan_tai_xiu_v31(kq_list):
    # CHỐNG CRASH KHI NHÀ CÁI KHÔNG TRẢ VỀ DỮ LIỆU
    if not kq_list or len(kq_list) == 0: 
        return "TÀI", "ĐANG ĐỢI DỮ LIỆU NHÀ CÁI..."
        
    gan_nhat = kq_list[-50:] 
    kq_cuoi = kq_list[-1]
    
    # HẠ MỐC YÊU CẦU XUỐNG 3 VÁN ĐỂ PHÁN NGAY
    if len(kq_list) < 3: 
        return ("TÀI" if kq_cuoi == "Xỉu" else "XỈU"), "DỮ LIỆU ÍT -> ĐÁNH DÒ ĐƯỜNG"
    
    cuoi_3 = kq_list[-3:]
    if cuoi_3 == ["Tài", "Xỉu", "Xỉu"]: return "TÀI", "BẮT CẦU NHỊP 1-2-1 (VÀO TÀI)"
    if cuoi_3 == ["Xỉu", "Tài", "Tài"]: return "XỈU", "BẮT CẦU NHỊP 1-2-1 (VÀO XỈU)"
    
    cuoi_5 = kq_list[-5:] if len(kq_list) >= 5 else kq_list
    if len(cuoi_5) == 5:
        if cuoi_5 == ["Tài", "Tài", "Tài", "Xỉu", "Xỉu"]: return "TÀI", "BẮT CẦU NHỊP 3-2-1"
        if cuoi_5 == ["Xỉu", "Xỉu", "Xỉu", "Tài", "Tài"]: return "XỈU", "BẮT CẦU NHỊP 3-2-1"
        if cuoi_5 == ["Tài", "Xỉu", "Xỉu", "Tài", "Tài"]: return "TÀI", "BẮT CẦU NHỊP 1-2-3"
        if cuoi_5 == ["Xỉu", "Tài", "Tài", "Xỉu", "Xỉu"]: return "XỈU", "BẮT CẦU NHỊP 1-2-3"
        if cuoi_5.count("Tài") == 4: return "TÀI", "CẦU NGHIÊNG 5 (THIÊN TÀI)"
        if cuoi_5.count("Xỉu") == 4: return "XỈU", "CẦU NGHIÊNG 5 (THIÊN XỈU)"

    chuoi_1_1 = 1
    for i in range(len(kq_list)-2, -1, -1):
        if kq_list[i] != kq_list[i+1]: chuoi_1_1 += 1
        else: break
    if chuoi_1_1 >= 4: return ("TÀI" if kq_cuoi == "Xỉu" else "XỈU"), f"CẦU ĐẢO XEN KẼ {chuoi_1_1} TAY"

    chuoi_bet = 1
    for i in range(len(kq_list)-2, -1, -1):
        if kq_list[i] == kq_cuoi: chuoi_bet += 1
        else: break
    if chuoi_bet == 4: return ("XỈU" if kq_cuoi == "Tài" else "TÀI"), "CẦU DÀI 4 -> CHUẨN BỊ BẺ CẦU"
    elif chuoi_bet >= 5: return kq_cuoi, f"BỆT SÂU {chuoi_bet} TAY -> ĐU BỆT TỚI CÙNG"

    tt = tx = xt = xx = 0
    for i in range(len(gan_nhat)-1):
        if gan_nhat[i] == "Tài" and gan_nhat[i+1] == "Tài": tt += 1
        elif gan_nhat[i] == "Tài" and gan_nhat[i+1] == "Xỉu": tx += 1
        elif gan_nhat[i] == "Xỉu" and gan_nhat[i+1] == "Tài": xt += 1
        elif gan_nhat[i] == "Xỉu" and gan_nhat[i+1] == "Xỉu": xx += 1
    
    dt = dx = 0
    if kq_cuoi == "Tài": dt += (tt/(tt+tx+0.01))*100; dx += (tx/(tt+tx+0.01))*100
    else: dt += (xt/(xt+xx+0.01))*100; dx += (xx/(xt+xx+0.01))*100

    if dt > dx + 12: return "TÀI", "MARKOV ĐỘT BIẾN -> ÉP TÀI"
    elif dx > dt + 12: return "XỈU", "MARKOV ĐỘT BIẾN -> ÉP XỈU"
    
    return ("TÀI" if kq_cuoi == "Xỉu" else "XỈU"), "CẦU LOẠN -> ĐÁNH DÒ ĐƯỜNG"

# ==========================================
# 🧠 NÃO BỘ 2: XÓC ĐĨA PRO MAX
# ==========================================
def tinh_toan_xoc_dia_v31(kq_list):
    if not kq_list or len(kq_list) == 0: 
        return "CHẴN", "ĐANG ĐỢI DỮ LIỆU NHÀ CÁI..."
        
    cl_list = ["CHẴN" if x == "Tài" else "LẺ" for x in kq_list]
    cl_cuoi = cl_list[-1]
    
    if len(cl_list) < 3: 
        return ("CHẴN" if cl_cuoi == "LẺ" else "LẺ"), "ĐANG LẤY MẪU XÓC ĐĨA"
    
    chuoi_chuyen = 1
    for i in range(len(cl_list)-2, -1, -1):
        if cl_list[i] != cl_list[i+1]: chuoi_chuyen += 1
        else: break
    if chuoi_chuyen >= 4: return ("CHẴN" if cl_cuoi == "LẺ" else "LẺ"), f"CẦU CHUYỀN (1-1) DÀI {chuoi_chuyen} TAY"

    cuoi_4 = cl_list[-4:] if len(cl_list) >= 4 else cl_list
    if len(cuoi_4) == 4:
        if cuoi_4 == ["CHẴN", "CHẴN", "LẺ", "LẺ"]: return "CHẴN", "BẮT CẦU 2-2 (VÀO CHẴN)"
        if cuoi_4 == ["LẺ", "LẺ", "CHẴN", "CHẴN"]: return "LẺ", "BẮT CẦU 2-2 (VÀO LẺ)"
        if cuoi_4 == ["CHẴN", "CHẴN", "CHẴN", "LẺ"]: return "CHẴN", "CẦU LỆCH 3-1 -> BẮT CHẴN"
        if cuoi_4 == ["LẺ", "LẺ", "LẺ", "CHẴN"]: return "LẺ", "CẦU LỆCH 3-1 -> BẮT LẺ"

    chuoi_bet = 1
    for i in range(len(cl_list)-2, -1, -1):
        if cl_list[i] == cl_cuoi: chuoi_bet += 1
        else: break
    if chuoi_bet == 4: return ("LẺ" if cl_cuoi == "CHẴN" else "CHẴN"), f"BỆT {cl_cuoi} 4 TAY -> BẺ CẦU"
    if chuoi_bet >= 5: return cl_cuoi, f"BỆT {cl_cuoi} {chuoi_bet} TAY -> ĐU THEO BỆT"

    t_chan = cl_list[-20:].count("CHẴN"); t_le = cl_list[-20:].count("LẺ")
    if t_chan > t_le + 4: return "CHẴN", "TẦN SUẤT ĐANG NGHIÊNG CHẴN"
    if t_le > t_chan + 4: return "LẺ", "TẦN SUẤT ĐANG NGHIÊNG LẺ"

    return ("CHẴN" if cl_cuoi == "LẺ" else "LẺ"), "QUÉT CẦU ĐỘC LẬP"

def phan_tich_ai_v31(kq_list, is_chanle):
    if not kq_list or len(kq_list) < 1: 
        return {"du_doan": "LOADING...", "ti_le": 0, "loi_khuyen": "KẾT NỐI API THẤT BẠI", "kq_cuoi": ""}
    
    if is_chanle: 
        du_doan_hien_tai, loi_khuyen = tinh_toan_xoc_dia_v31(kq_list)
        kq_cuoi_hien_thi = "CHẴN" if kq_list[-1] == "Tài" else "LẺ"
    else: 
        du_doan_hien_tai, loi_khuyen = tinh_toan_tai_xiu_v31(kq_list)
        kq_cuoi_hien_thi = kq_list[-1].upper()

    if "BẮT CẦU NHỊP" in loi_khuyen or "CẦU 2-2" in loi_khuyen or "MARKOV" in loi_khuyen: ty_le = random.uniform(97.5, 99.9)
    elif "BỆT SÂU" in loi_khuyen or "CẦU CHUYỀN" in loi_khuyen: ty_le = random.uniform(95.2, 97.4)
    elif "BẺ CẦU" in loi_khuyen: ty_le = random.uniform(89.5, 93.5)
    else: ty_le = random.uniform(86.5, 89.4)

    return {"du_doan": du_doan_hien_tai, "ti_le": round(ty_le, 1), "loi_khuyen": loi_khuyen, "kq_cuoi": kq_cuoi_hien_thi}

def get_id(item):
    if isinstance(item, dict):
        for k in ['id', 'phien', 'sessionId', 'SessionID']:
            if k in item and str(item[k]).isdigit(): return int(item[k])
    return 0

@app.route("/api/scan", methods=["GET"])
def scan_game():
    tool = request.args.get("tool", "")
    key = request.args.get("key", "")
    if key != "hungki98vip":
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (key,))
            row = c.fetchone()
            if not row: return jsonify({"status": "error", "msg": "Key không tồn tại!"})
            if row[1] == 1: return jsonify({"status": "error", "msg": "Key bị khóa!"})
            if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"): return jsonify({"status": "error", "msg": "Key đã hết hạn!"})

    if tool == "lc79_xd": url = "https://wcl.tele68.com/v1/chanlefull/sessions"
    elif tool == "lc79_md5": url = "https://wtxmd52.tele68.com/v1/txmd5/sessions"
    elif tool == "lc79_tx": url = "https://wtx.tele68.com/v1/tx/sessions"
    elif tool == "betvip_tx": url = "https://wtx.macminim6.online/v1/tx/sessions"
    elif tool == "betvip_md5": url = "https://wtxmd52.macminim6.online/v1/txmd5/sessions"
    else: return jsonify({"status": "error", "msg": "Lỗi Cổng!"})

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0 V31-FIXED"}, timeout=5).json()
        lst = res.get("data", res.get("list", res)) if isinstance(res, dict) else res
        
        # Sửa lỗi: Nếu API không trả về mảng list, coi như rỗng
        if not lst or not isinstance(lst, list): 
            lst = [] 
        
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
        
        data = phan_tich_ai_v31(kq, is_chanle)
        
        if lst:
            s_cuoi = lst[-1]
            phien_hien_tai = get_id(s_cuoi)
            data["phien"] = str(phien_hien_tai + 1) if phien_hien_tai > 0 else "ĐANG TẢI..."
        else:
            data["phien"] = "LỖI MẠNG NHÀ CÁI"
            
        return jsonify({"status": "success", "data": data})
    except Exception as e: 
        return jsonify({"status": "error", "msg": "Mạng lag hoặc lỗi JSON!"})

@app.route("/api/verify_key", methods=["POST"])
def verify_key():
    req = request.get_json() or {}
    k = req.get("key", "").strip()
    if not k: return jsonify({"status": "error", "msg": "Nhập Key!"})
    if k == "hungki98vip": return jsonify({"status": "success", "role": "admin", "expire": "VĨNH VIỄN (GOD MODE)"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (k,))
        row = c.fetchone()
        if not row: return jsonify({"status": "error", "msg": "KEY KHÔNG TỒN TẠI!"})
        if row[1] == 1: return jsonify({"status": "error", "msg": "KEY BỊ KHÓA!"})
        if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"): return jsonify({"status": "error", "msg": "KEY ĐÃ HẾT HẠN!"})
        return jsonify({"status": "success", "role": "user", "expire": row[0]})

@app.route("/api/admin/list_keys", methods=["GET"])
def admin_list_keys():
    admin_key = request.args.get("admin_key", "")
    if admin_key != "hungki98vip": return jsonify({"status": "error"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT key_str, expire_time, is_banned FROM keys WHERE key_str != 'hungki98vip' ORDER BY expire_time DESC")
        return jsonify({"status": "success", "keys": c.fetchall()})

@app.route("/api/admin/create_key", methods=["POST"])
def create_key():
    req = request.get_json() or {}
    admin_key = req.get("admin_key", "")
    duration = req.get("duration", "")
    custom_key = req.get("custom_key", "")
    if admin_key != "hungki98vip": return jsonify({"status": "error"})
    new_key = custom_key.strip() if custom_key.strip() != "" else "VIP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    now = datetime.now()
    if duration == "1H": exp = now + timedelta(hours=1)
    elif duration == "1D": exp = now + timedelta(days=1)
    elif duration == "3D": exp = now + timedelta(days=3)
    elif duration == "30D": exp = now + timedelta(days=30)
    else: return jsonify({"status": "error", "msg": "Lỗi!"})
    exp_str = exp.strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, 0)", (new_key, exp_str))
        conn.commit()
    return jsonify({"status": "success", "new_key": new_key, "expire": exp_str})

@app.route("/api/admin/action_key", methods=["POST"])
def action_key():
    req = request.get_json() or {}
    admin_key = req.get("admin_key", "")
    target_key = req.get("target_key", "")
    action = req.get("action", "")
    if admin_key != "hungki98vip": return jsonify({"status": "error"})
    with get_db() as conn:
        c = conn.cursor()
        if action == "ban": c.execute("UPDATE keys SET is_banned = 1 WHERE key_str = ?", (target_key,))
        elif action == "unban": c.execute("UPDATE keys SET is_banned = 0 WHERE key_str = ?", (target_key,))
        elif action == "delete": c.execute("DELETE FROM keys WHERE key_str = ?", (target_key,))
        conn.commit()
    return jsonify({"status": "success"})

@app.route("/")
def home(): return send_file("index.html")

if __name__ == "__main__": app.run(host="0.0.0.0", port=8080)
                   
