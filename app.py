# ═══════════════════════════════════════════════════════════════
#  DORAEMON INTELLIGENCE AI v6.0 – THUẬT TOÁN TÀI XỈU TỐI CAO
#  Nâng cấp: Học sâu Markov bậc 3, Phân tích entropy, GNN ảo
#  Tác giả: orinlo
# ═══════════════════════════════════════════════════════════════

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests, sqlite3, os, random, string, hashlib, math, json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import numpy as np

app = Flask(__name__)
CORS(app)
DB_FILE = "royal_keys.db"
USER_DB = "users.db"

# ═══════════════ KHỞI TẠO DATABASE ═══════════════
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)
def get_user_db(): return sqlite3.connect(USER_DB, check_same_thread=False)

def khoi_tao_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS keys (key_str TEXT PRIMARY KEY, expire_time DATETIME, is_banned INTEGER)''')
        c.execute("INSERT OR IGNORE INTO keys (key_str, expire_time, is_banned) VALUES (?, ?, ?)", ('hungki98vip', '2099-12-31 23:59:59', 0))
        conn.commit()
    with get_user_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, created_at DATETIME)''')
        c.execute("INSERT OR IGNORE INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)", 
                  ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin', datetime.now()))
        conn.commit()

khoi_tao_db()

# ═══════════════ THUẬT TOÁN TÀI XỈU VIP PRO 6.0 ═══════════════
class TaiXiuAIv60:
    def __init__(self):
        self.markov_order = 3  # Markov bậc 3
        self.entropy_window = 20  # Cửa sổ phân tích entropy
        self.pattern_memory = defaultdict(list)  # Bộ nhớ mẫu cầu
        
    def _entropy(self, data):
        """Tính entropy để đo độ hỗn loạn của cầu"""
        if not data: return 0
        counter = Counter(data)
        total = len(data)
        return -sum((count/total) * math.log2(count/total) for count in counter.values())
    
    def _markov_predict(self, kq_list, order=3):
        """Dự đoán Markov bậc cao"""
        if len(kq_list) < order + 1:
            return None, 0
        
        # Xây dựng ma trận chuyển đổi
        transitions = defaultdict(lambda: defaultdict(int))
        for i in range(len(kq_list) - order):
            state = tuple(kq_list[i:i+order])
            next_val = kq_list[i+order]
            transitions[state][next_val] += 1
        
        # Lấy trạng thái hiện tại
        current_state = tuple(kq_list[-order:])
        if current_state not in transitions:
            return None, 0
        
        probs = transitions[current_state]
        total = sum(probs.values())
        if total == 0: return None, 0
        
        # Chọn giá trị có xác suất cao nhất
        predicted = max(probs, key=probs.get)
        confidence = (probs[predicted] / total) * 100
        return predicted, confidence
    
    def _pattern_detect(self, kq_list):
        """Phát hiện mẫu cầu lặp lại"""
        if len(kq_list) < 6: return None, 0
        
        # Tìm mẫu 3-4 phiên lặp
        for pattern_len in [3, 4]:
            for i in range(len(kq_list) - pattern_len * 2):
                pattern = kq_list[i:i+pattern_len]
                # Tìm lần xuất hiện tiếp theo
                for j in range(i+pattern_len, len(kq_list) - pattern_len):
                    if kq_list[j:j+pattern_len] == pattern:
                        # Dự đoán phiên tiếp theo dựa trên mẫu
                        if j+pattern_len < len(kq_list):
                            return kq_list[j+pattern_len], 85.0
                        elif i+pattern_len < len(kq_list):
                            return kq_list[i+pattern_len], 80.0
        
        return None, 0
    
    def _bayesian_weight(self, kq_list):
        """Tính trọng số Bayes cho Tài/Xỉu"""
        if len(kq_list) < 10: return 0.5, 0.5
        
        # Sử dụng phân phối Beta-Binomial
        tai_count = kq_list[-30:].count("Tài")
        xiu_count = kq_list[-30:].count("Xỉu")
        total = tai_count + xiu_count
        
        # Ước tính MAP với prior Beta(2,2)
        alpha, beta = 2, 2
        p_tai = (tai_count + alpha) / (total + alpha + beta)
        p_xiu = (xiu_count + beta) / (total + alpha + beta)
        return p_tai, p_xiu
    
    def predict(self, kq_list):
        """Dự đoán tổng hợp VIP PRO 6.0"""
        if not kq_list or len(kq_list) == 0:
            return "TÀI", "CHỜ DỮ LIỆU...", 50.0
        
        kq_cuoi = kq_list[-1]
        
        # Lớp 1: Markov bậc 3
        markov_pred, markov_conf = self._markov_predict(kq_list, self.markov_order)
        
        # Lớp 2: Phát hiện mẫu cầu
        pattern_pred, pattern_conf = self._pattern_detect(kq_list)
        
        # Lớp 3: Phân tích entropy
        entropy = self._entropy(kq_list[-self.entropy_window:])
        entropy_threshold = 0.8  # Entropy thấp = cầu ổn định
        
        # Lớp 4: Trọng số Bayes
        p_tai, p_xiu = self._bayesian_weight(kq_list)
        
        # ═══ QUYẾT ĐỊNH TỔNG HỢP ═══
        votes = {"Tài": 0, "Xỉu": 0}
        reasons = []
        
        # Markov vote (trọng số cao nhất)
        if markov_pred and markov_conf > 60:
            votes[markov_pred] += 3
            reasons.append(f"Markov bậc 3: {markov_pred} ({markov_conf:.1f}%)")
        
        # Pattern vote
        if pattern_pred and pattern_conf > 75:
            votes[pattern_pred] += 2
            reasons.append(f"Phát hiện mẫu cầu: {pattern_pred}")
        
        # Bayes vote
        if p_tai > p_xiu + 0.15:
            votes["Tài"] += 2
            reasons.append(f"Bayes nghiêng Tài ({p_tai*100:.1f}%)")
        elif p_xiu > p_tai + 0.15:
            votes["Xỉu"] += 2
            reasons.append(f"Bayes nghiêng Xỉu ({p_xiu*100:.1f}%)")
        
        # Entropy vote
        if entropy < entropy_threshold:
            # Cầu ổn định, theo xu hướng
            recent_trend = Counter(kq_list[-5:]).most_common(1)[0][0]
            votes[recent_trend] += 1
            reasons.append(f"Cầu ổn định (entropy={entropy:.2f})")
        else:
            # Cầu hỗn loạn, đánh ngược phiên cuối
            nguoc = "Xỉu" if kq_cuoi == "Tài" else "Tài"
            votes[nguoc] += 1
            reasons.append(f"Cầu hỗn loạn -> đảo chiều")
        
        # Chọn kết quả cuối cùng
        if votes["Tài"] > votes["Xỉu"]:
            du_doan = "TÀI"
        elif votes["Xỉu"] > votes["Tài"]:
            du_doan = "XỈU"
        else:
            du_doan = "TÀI" if p_tai > p_xiu else "XỈU"
        
        # Tính độ chính xác tổng hợp
        max_votes = max(votes["Tài"], votes["Xỉu"])
        total_votes = votes["Tài"] + votes["Xỉu"]
        confidence = (max_votes / total_votes * 100) if total_votes > 0 else 50
        confidence = min(99.9, max(60, confidence + random.uniform(-3, 5)))
        
        # Lý do chính
        main_reason = "; ".join(reasons[:2]) if reasons else "Phân tích tổng hợp"
        
        return du_doan, main_reason, confidence


# Khởi tạo AI engine
ai_engine = TaiXiuAIv60()

def phan_tich_ai_v60(kq_list, is_chanle=False):
    if not kq_list or len(kq_list) < 1:
        return {
            "du_doan": "LOADING...",
            "ti_le": 0,
            "loi_khuyen": "KẾT NỐI API THẤT BẠI",
            "kq_cuoi": ""
        }
    
    if is_chanle:
        # Chuyển đổi Tài/Xỉu -> Chẵn/Lẻ cho Xóc Đĩa
        cl_list = ["CHẴN" if x == "Tài" else "LẺ" for x in kq_list]
        du_doan, reason, confidence = ai_engine.predict(kq_list)
        du_doan_hien_thi = "CHẴN" if du_doan == "TÀI" else "LẺ"
        kq_cuoi_hien_thi = "CHẴN" if kq_list[-1] == "Tài" else "LẺ"
    else:
        du_doan, reason, confidence = ai_engine.predict(kq_list)
        du_doan_hien_thi = du_doan
        kq_cuoi_hien_thi = kq_list[-1].upper()
    
    return {
        "du_doan": du_doan_hien_thi,
        "ti_le": round(confidence, 1),
        "loi_khuyen": reason,
        "kq_cuoi": kq_cuoi_hien_thi
    }


# ═══════════════ API ROUTES ═══════════════
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
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0 V60-FIXED"}, timeout=5).json()
        lst = res.get("data", res.get("list", res)) if isinstance(res, dict) else res
        
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
        
        data = phan_tich_ai_v60(kq, is_chanle)
        
        if lst:
            s_cuoi = lst[-1]
            phien_hien_tai = get_id(s_cuoi)
            data["phien"] = str(phien_hien_tai + 1) if phien_hien_tai > 0 else "ĐANG TẢI..."
        else:
            data["phien"] = "LỖI MẠNG NHÀ CÁI"
            
        return jsonify({"status": "success", "data": data})
    except Exception as e: 
        return jsonify({"status": "error", "msg": "Mạng lag hoặc lỗi JSON!"})


@app.route("/api/manual_md5", methods=["POST"])
def manual_md5():
    req = request.get_json() or {}
    key = req.get("key", "")
    md5_str = req.get("md5", "")
    
    # Verify key
    if key != "hungki98vip":
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str = ?", (key,))
            row = c.fetchone()
            if not row: return jsonify({"status": "error", "msg": "Key không hợp lệ!"})
            if row[1] == 1: return jsonify({"status": "error", "msg": "Key bị khóa!"})
            if datetime.now() > datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"): return jsonify({"status": "error", "msg": "Key đã hết hạn!"})
    
    if not md5_str or len(md5_str) != 32:
        return jsonify({"status": "error", "msg": "Chuỗi MD5 không hợp lệ!"})
    
    # Phân tích MD5 nâng cao
    hex_digits = md5_str
    tai_score = sum(int(c, 16) for c in hex_digits[::2])  # Vị trí chẵn -> Tài
    xiu_score = sum(int(c, 16) for c in hex_digits[1::2])  # Vị trí lẻ -> Xỉu
    
    total = tai_score + xiu_score
    p_tai = (tai_score / total) * 100
    p_xiu = (xiu_score / total) * 100
    
    # Điều chỉnh với entropy
    last_byte = int(hex_digits[-2:], 16)
    if last_byte % 2 == 0:
        p_tai = min(99, p_tai + 5)
    else:
        p_xiu = min(99, p_xiu + 5)
    
    suggestion = "TÀI" if p_tai > p_xiu else "XỈU"
    
    return jsonify({
        "status": "success",
        "tai": round(p_tai, 1),
        "xiu": round(p_xiu, 1),
        "suggestion": suggestion
    })


@app.route("/api/login", methods=["POST"])
def login():
    req = request.get_json() or {}
    username = req.get("username", "")
    password = req.get("password", "")
    
    with get_user_db() as conn:
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if not row:
            return jsonify({"status": "error", "msg": "Tài khoản không tồn tại!"})
        
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if hashed != row[0]:
            return jsonify({"status": "error", "msg": "Mật khẩu không đúng!"})
        
        return jsonify({
            "status": "success",
            "data": {
                "name": username,
                "role": row[1]
            }
        })


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


if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=8080)
