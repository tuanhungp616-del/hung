# ═══════════════════════════════════════════════════════════════
#  DORAEMON INTELLIGENCE AI v10.0 – FULL PACKAGE
#  app.py – Server Flask triển khai trên Render/VPS
#  Tích hợp AdvancedCauDetector, khung giờ vàng, lịch sử 1 phiên
# ═══════════════════════════════════════════════════════════════

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests, sqlite3, os, random, string, hashlib, math, json
from datetime import datetime, timedelta
from collections import Counter, defaultdict

app = Flask(__name__)
CORS(app)
DB_FILE = "royal_keys.db"
USER_DB = "users.db"

# ─── Database helpers ────────────────────────────────────
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)
def get_user_db(): return sqlite3.connect(USER_DB, check_same_thread=False)

def khoi_tao_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS keys (
                        key_str TEXT PRIMARY KEY,
                        expire_time DATETIME,
                        is_banned INTEGER
                     )''')
        c.execute("INSERT OR IGNORE INTO keys VALUES ('hungki98vip','2099-12-31 23:59:59',0)")
        conn.commit()
    with get_user_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT,
                        role TEXT,
                        created_at DATETIME
                     )''')
        c.execute("INSERT OR IGNORE INTO users VALUES ('admin', ?, 'admin', ?)",
                  (hashlib.sha256('admin123'.encode()).hexdigest(), datetime.now()))
        conn.commit()

khoi_tao_db()

# ═══════════════ ADVANCED CẦU DETECTOR (15 PHIÊN) ═══════════════
class AdvancedCauDetector:
    def __init__(self, window=15):
        self.window = window

    def _last_n(self, hist, n):
        return hist[-n:] if len(hist) >= n else hist

    def detect_bet(self, hist):
        if len(hist) < 4: return None, 0
        last = hist[-1]
        count = 1
        for i in range(len(hist)-2, -1, -1):
            if hist[i] == last: count += 1
            else: break
        if count >= 12:      # Bệt rồng
            pred = "Xỉu" if last == "Tài" else "Tài"
            return pred.upper(), 75
        elif count >= 5:
            pred = "Xỉu" if last == "Tài" else "Tài"
            return pred.upper(), 80
        elif count >= 4:
            pred = "Xỉu" if last == "Tài" else "Tài"
            return pred.upper(), 70
        return None, 0

    def detect_1_1(self, hist):
        if len(hist) < 4: return None, 0
        last4 = hist[-4:]
        if last4[0] != last4[1] and last4[1] != last4[2] and last4[2] != last4[3]:
            length = 1
            for i in range(len(hist)-2, -1, -1):
                if hist[i] != hist[i+1]: length += 1
                else: break
            if length >= 4:
                pred = "Xỉu" if hist[-1] == "Tài" else "Tài"
                conf = min(85 + length*2, 99)
                return pred.upper(), conf
        return None, 0

    def detect_2_2(self, hist):
        if len(hist) < 6: return None, 0
        last6 = hist[-6:]
        if (last6[0]==last6[1] and last6[2]==last6[3] and last6[4]==last6[5] and
            last6[0]!=last6[2] and last6[2]!=last6[4]):
            cur = last6[4]
            pred = "Xỉu" if cur == "Tài" else "Tài"
            return pred.upper(), 90
        return None, 0

    def detect_1_2_or_2_1(self, hist):
        if len(hist) < 6: return None, 0
        last6 = hist[-6:]
        # Mẫu 1-2-1-2: a,b,b,a,b,b
        if (last6[0]==last6[3] and last6[1]==last6[2]==last6[4]==last6[5] and last6[0]!=last6[1]):
            return last6[0].upper(), 88
        # Mẫu 2-1-2-1: a,a,b,a,a,b
        if (last6[0]==last6[1]==last6[3]==last6[4] and last6[2]==last6[5] and last6[0]!=last6[2]):
            return last6[0].upper(), 88
        return None, 0

    def detect_1_2_3(self, hist):
        if len(hist) < 6: return None, 0
        groups = []
        i = len(hist)-1
        while i >= 0 and len(groups) < 3:
            cur = hist[i]
            cnt = 1
            while i-1 >= 0 and hist[i-1] == cur:
                cnt += 1
                i -= 1
            groups.append((cur, cnt))
            i -= 1
        if len(groups) == 3:
            sizes = [g[1] for g in groups]
            if sizes == [3, 2, 1] or sizes == [1, 2, 3]:
                pred = "Xỉu" if groups[0][0] == "Tài" else "Tài"
                return pred.upper(), 82
        return None, 0

    def detect_nghieng(self, hist):
        if len(hist) < 10: return None, 0
        cnt = Counter(hist)
        total = len(hist)
        p_tai = cnt["Tài"] / total
        p_xiu = cnt["Xỉu"] / total
        if p_tai >= 0.7:
            return "XỈU", 65 + int(p_tai*20)
        elif p_xiu >= 0.7:
            return "TÀI", 65 + int(p_xiu*20)
        return None, 0

    def detect_doi_xung(self, hist):
        if len(hist) < 7: return None, 0
        last7 = hist[-7:]
        if (last7[0]==last7[6] and last7[1]==last7[5] and last7[2]==last7[4] and
            last7[0]!=last7[1] and last7[1]!=last7[2]):
            pred = "Xỉu" if hist[-1] == "Tài" else "Tài"
            return pred.upper(), 70
        return None, 0

    def detect_3_3(self, hist):
        if len(hist) < 9: return None, 0
        last9 = hist[-9:]
        if (last9[0]==last9[1]==last9[2] and last9[3]==last9[4]==last9[5] and
            last9[6]==last9[7]==last9[8] and last9[0]!=last9[3] and last9[3]!=last9[6]):
            cur_triple = last9[6]
            pred = "Xỉu" if cur_triple == "Tài" else "Tài"
            return pred.upper(), 88
        return None, 0

    def markov_predict(self, hist):
        order = 2
        if len(hist) < order + 1: return None, 0
        trans = defaultdict(lambda: defaultdict(int))
        for i in range(len(hist) - order):
            state = tuple(hist[i:i+order])
            nxt = hist[i+order]
            trans[state][nxt] += 1
        cur = tuple(hist[-order:])
        if cur not in trans: return None, 0
        probs = trans[cur]
        total = sum(probs.values())
        if total == 0: return None, 0
        pred = max(probs, key=probs.get)
        conf = (probs[pred] / total) * 100
        return pred, conf

    def predict(self, full_hist):
        hist = self._last_n(full_hist, self.window)
        if len(hist) < 2:
            return "TÀI", "KHÔNG ĐỦ DỮ LIỆU", 50.0

        detectors = [
            ("Cầu 1-1", self.detect_1_1),
            ("Cầu 2-2", self.detect_2_2),
            ("Cầu 1-2/2-1", self.detect_1_2_or_2_1),
            ("Cầu 1-2-3", self.detect_1_2_3),
            ("Cầu bệt", self.detect_bet),
            ("Cầu 3-3", self.detect_3_3),
            ("Cầu nghiêng", self.detect_nghieng),
            ("Cầu đối xứng", self.detect_doi_xung),
        ]

        best_pred, best_reason, best_conf = None, "", 0
        for name, detector in detectors:
            pred, conf = detector(hist)
            if pred and conf > best_conf:
                best_pred, best_reason, best_conf = pred, f"{name} ({conf}%)", conf
                if conf >= 90: break

        if best_pred and best_conf >= 65:
            return best_pred, best_reason, best_conf

        m_pred, m_conf = self.markov_predict(hist)
        if m_pred and m_conf > 50:
            return m_pred.upper(), f"Markov ({m_conf:.0f}%)", m_conf

        cnt = Counter(hist)
        if cnt["Tài"] > cnt["Xỉu"]:
            pred, reason = "XỈU", "Đảo xu hướng (nghiêng Tài)"
        elif cnt["Xỉu"] > cnt["Tài"]:
            pred, reason = "TÀI", "Đảo xu hướng (nghiêng Xỉu)"
        else:
            pred, reason = random.choice(["TÀI","XỈU"]), "Ngẫu nhiên"
        conf = max(cnt.values()) / len(hist) * 100 if len(hist) > 0 else 50
        return pred, reason, min(conf, 75)

ai = AdvancedCauDetector(window=15)

# ─── State & history (1 phiên) ──────────────────────────
last_pred_map = defaultdict(lambda: None)
last_history = defaultdict(lambda: None)

def get_id(item):
    if isinstance(item, dict):
        for k in ['id','phien','sessionId','SessionID']:
            if k in item and str(item[k]).isdigit(): return int(item[k])
    return 0

# ─── Khung giờ vàng ─────────────────────────────────────
def get_golden_hours():
    now = datetime.now()
    hour = now.hour
    if 11 <= hour < 13:
        return {"khung_gio": "11:00 - 13:00", "danh_gia": "Cực kỳ dễ nổ", "color": "#ffd740"}
    elif 20 <= hour < 22:
        return {"khung_gio": "20:00 - 22:00", "danh_gia": "Dễ nổ lớn", "color": "#ffd740"}
    elif hour >= 23 or hour < 1:
        return {"khung_gio": "23:00 - 01:00", "danh_gia": "Tỷ lệ nổ cao", "color": "#ffd740"}
    elif 6 <= hour < 9:
        return {"khung_gio": "06:00 - 09:00", "danh_gia": "Có thể nổ", "color": "#ff9800"}
    elif 17 <= hour < 20:
        return {"khung_gio": "17:00 - 20:00", "danh_gia": "Tạm ổn", "color": "#ff9800"}
    else:
        return {"khung_gio": "Các giờ khác", "danh_gia": "Bình thường", "color": "#9e9e9e"}

# ═══════════════ ROUTES ═══════════════════════════════════════
@app.route("/api/golden_hours")
def golden_hours():
    return jsonify({"status":"success", "data": get_golden_hours()})

@app.route("/api/scan")
def scan():
    tool = request.args.get("tool","")
    mode = request.args.get("mode","tx_md5")
    key  = request.args.get("key","")
    if key != "hungki98vip":
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str=?",(key,))
            row = c.fetchone()
            if not row: return jsonify({"status":"error","msg":"Key không tồn tại"})
            if row[1]==1: return jsonify({"status":"error","msg":"Key bị khóa"})
            if datetime.now() > datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S"):
                return jsonify({"status":"error","msg":"Key hết hạn"})

    if tool == "lc79":
        url = "https://wcl.tele68.com/v1/chanlefull/sessions" if mode=="xoc_dia" else "https://wtx.tele68.com/v1/tx/sessions"
    elif tool == "betvip":
        url = "https://wtx.macminim6.online/v1/tx/sessions"
    elif tool == "sunwin":
        url = "https://sunwin-api.example.com/tx"  # placeholder
    else:
        return jsonify({"status":"error","msg":"Sàn không hỗ trợ"})

    try:
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = resp.json()
        sessions = data.get("data", data.get("list", []))
        if not isinstance(sessions, list): sessions = []
        sessions = sorted(sessions, key=get_id)

        full_hist = []
        is_chanle = ("chanle" in url.lower() or mode == "xoc_dia")
        for s in sessions[-50:]:
            val = str(s).upper()
            if is_chanle:
                full_hist.append("Tài" if ("CHẴN" in val or "CHAN" in val or "'C'" in val) else "Xỉu")
            else:
                full_hist.append("Tài" if ("TAI" in val or "TÀI" in val or "'T'" in val) else "Xỉu")

        actual = full_hist[-1].upper() if full_hist else None
        prev_pred = last_pred_map[f"{tool}_{mode}"]
        if prev_pred and actual:
            win = (prev_pred == actual)
            last_history[f"{tool}_{mode}"] = {
                "phien": str(sessions[-1].get("id","?")) if sessions else "?",
                "du_doan": prev_pred,
                "ket_qua": actual,
                "win": win
            }

        raw_pred, reason, conf = ai.predict(full_hist)
        last_pred_map[f"{tool}_{mode}"] = raw_pred

        du_doan_hien_thi = raw_pred
        kq_cuoi_hien_thi = actual if actual else ""
        if is_chanle:
            du_doan_hien_thi = "CHẴN" if raw_pred == "TÀI" else "LẺ"
            kq_cuoi_hien_thi = "CHẴN" if actual == "TÀI" else "LẺ"

        next_phien = "0"
        if sessions:
            pid = get_id(sessions[-1])
            next_phien = str(pid + 1) if pid > 0 else "ĐANG TẢI..."

        return jsonify({
            "status":"success",
            "data":{
                "du_doan": du_doan_hien_thi,
                "ti_le": round(conf,1),
                "phien": next_phien,
                "loi_khuyen": reason,
                "kq_cuoi": kq_cuoi_hien_thi,
                "reverse_mode": False,
                "last_result": last_history[f"{tool}_{mode}"]
            }
        })
    except Exception as e:
        return jsonify({"status":"error","msg":str(e)})

@app.route("/api/history")
def get_history():
    tool = request.args.get("tool","")
    mode = request.args.get("mode","tx_md5")
    his = last_history.get(f"{tool}_{mode}", None)
    return jsonify(his if his else {})

@app.route("/api/login", methods=["POST"])
def login():
    req = request.get_json() or {}
    user = req.get("username","")
    pwd = req.get("password","")
    with get_user_db() as conn:
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE username=?",(user,))
        row = c.fetchone()
        if not row: return jsonify({"status":"error","msg":"Tài khoản không tồn tại"})
        if hashlib.sha256(pwd.encode()).hexdigest() != row[0]:
            return jsonify({"status":"error","msg":"Mật khẩu không đúng"})
        return jsonify({"status":"success","data":{"name":user,"role":row[1]}})

# Admin APIs giữ lại (có thể giản lược nếu không cần)
@app.route("/api/verify_key", methods=["POST"])
def verify_key():
    req = request.get_json() or {}
    k = req.get("key","").strip()
    if not k: return jsonify({"status":"error","msg":"Nhập Key!"})
    if k == "hungki98vip": return jsonify({"status":"success","role":"admin","expire":"VĨNH VIỄN"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str=?",(k,))
        row = c.fetchone()
        if not row: return jsonify({"status":"error","msg":"KEY KHÔNG TỒN TẠI"})
        if row[1]==1: return jsonify({"status":"error","msg":"KEY BỊ KHÓA"})
        if datetime.now() > datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S"):
            return jsonify({"status":"error","msg":"KEY HẾT HẠN"})
        return jsonify({"status":"success","role":"user","expire":row[0]})

@app.route("/api/admin/list_keys")
def admin_list_keys():
    key = request.args.get("admin_key","")
    if key != "hungki98vip": return jsonify({"status":"error"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT key_str, expire_time, is_banned FROM keys WHERE key_str!='hungki98vip' ORDER BY expire_time DESC")
        return jsonify({"status":"success","keys":c.fetchall()})

@app.route("/api/admin/create_key", methods=["POST"])
def create_key():
    req = request.get_json() or {}
    admin_key = req.get("admin_key","")
    duration = req.get("duration","")
    custom = req.get("custom_key","")
    if admin_key != "hungki98vip": return jsonify({"status":"error"})
    new_key = custom.strip() if custom.strip() else "VIP-"+''.join(random.choices(string.ascii_uppercase+string.digits,k=6))
    now = datetime.now()
    if duration == "1H": exp = now + timedelta(hours=1)
    elif duration == "1D": exp = now + timedelta(days=1)
    elif duration == "3D": exp = now + timedelta(days=3)
    elif duration == "30D": exp = now + timedelta(days=30)
    else: return jsonify({"status":"error","msg":"Thời gian không hợp lệ"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO keys VALUES (?, ?, 0)", (new_key, exp.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    return jsonify({"status":"success","new_key":new_key,"expire":exp.strftime("%Y-%m-%d %H:%M:%S")})

@app.route("/api/admin/action_key", methods=["POST"])
def action_key():
    req = request.get_json() or {}
    admin_key = req.get("admin_key","")
    target = req.get("target_key","")
    action = req.get("action","")
    if admin_key != "hungki98vip": return jsonify({"status":"error"})
    with get_db() as conn:
        c = conn.cursor()
        if action == "ban": c.execute("UPDATE keys SET is_banned=1 WHERE key_str=?",(target,))
        elif action == "unban": c.execute("UPDATE keys SET is_banned=0 WHERE key_str=?",(target,))
        elif action == "delete": c.execute("DELETE FROM keys WHERE key_str=?",(target,))
        conn.commit()
    return jsonify({"status":"success"})

@app.route("/")
def home():
    return send_file("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
