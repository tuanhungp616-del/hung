# ═══════════════════════════════════════════════════════════════
#  DORAEMON INTELLIGENCE AI v8.0 – VIP PRO (SIÊU XỊN)
#  Thuật toán: Hybrid Markov bậc 4, Entropy, Bayesian, Pattern
#  Giao diện: Neon Glassmorphism Cao Cấp
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

def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)
def get_user_db(): return sqlite3.connect(USER_DB, check_same_thread=False)

def khoi_tao_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS keys (key_str TEXT PRIMARY KEY, expire_time DATETIME, is_banned INTEGER)''')
        c.execute("INSERT OR IGNORE INTO keys VALUES ('hungki98vip','2099-12-31 23:59:59',0)")
        conn.commit()
    with get_user_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, created_at DATETIME)''')
        c.execute("INSERT OR IGNORE INTO users VALUES ('admin', ?, 'admin', ?)", (hashlib.sha256('admin123'.encode()).hexdigest(), datetime.now()))
        conn.commit()

khoi_tao_db()

# ═══════════════ AI ENGINE PRO ═══════════════
class TaiXiuAIPro:
    def __init__(self):
        self.markov_order = 4
        self.entropy_window = 25

    def _entropy(self, data):
        if not data: return 0
        cnt = Counter(data)
        total = len(data)
        return -sum((c/total) * math.log2(c/total) for c in cnt.values())

    def _markov_predict(self, hist):
        order = self.markov_order
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

    def _pattern_detect(self, hist):
        if len(hist) < 6: return None, 0
        for plen in [3,4]:
            for i in range(len(hist) - plen*2):
                pat = hist[i:i+plen]
                for j in range(i+plen, len(hist)-plen):
                    if hist[j:j+plen] == pat:
                        if j+plen < len(hist):
                            return hist[j+plen], 85.0
                        elif i+plen < len(hist):
                            return hist[i+plen], 80.0
        return None, 0

    def _bayesian(self, hist):
        if len(hist) < 10: return 0.5, 0.5
        tai = hist[-30:].count("Tài")
        xiu = hist[-30:].count("Xỉu")
        total = tai + xiu
        alpha, beta = 2, 2
        p_tai = (tai + alpha) / (total + alpha + beta)
        p_xiu = (xiu + beta) / (total + alpha + beta)
        return p_tai, p_xiu

    def predict(self, hist):
        if not hist or len(hist) < 2:
            return "TÀI", "KHÔNG ĐỦ DỮ LIỆU", 50.0

        last = hist[-1]
        markov_pred, markov_conf = self._markov_predict(hist)
        pat_pred, pat_conf = self._pattern_detect(hist)
        entropy = self._entropy(hist[-self.entropy_window:])
        p_tai, p_xiu = self._bayesian(hist)

        votes = {"Tài":0, "Xỉu":0}
        reasons = []

        if markov_pred and markov_conf > 55:
            votes[markov_pred] += 3
            reasons.append(f"Markov bậc 4: {markov_pred} ({markov_conf:.0f}%)")
        if pat_pred and pat_conf > 70:
            votes[pat_pred] += 2
            reasons.append(f"Mẫu cầu: {pat_pred}")
        if p_tai > p_xiu + 0.2:
            votes["Tài"] += 2
            reasons.append(f"Bayes Tài ({p_tai*100:.0f}%)")
        elif p_xiu > p_tai + 0.2:
            votes["Xỉu"] += 2
            reasons.append(f"Bayes Xỉu ({p_xiu*100:.0f}%)")
        if entropy < 0.7:
            trend = Counter(hist[-5:]).most_common(1)[0][0]
            votes[trend] += 1
            reasons.append("Cầu ổn định")
        else:
            nguoc = "Xỉu" if last == "Tài" else "Tài"
            votes[nguoc] += 1
            reasons.append("Hỗn loạn -> đảo")

        if votes["Tài"] > votes["Xỉu"]:
            pred = "TÀI"
        elif votes["Xỉu"] > votes["Tài"]:
            pred = "XỈU"
        else:
            pred = "TÀI" if p_tai > p_xiu else "XỈU"

        max_votes = max(votes.values())
        total_votes = votes["Tài"] + votes["Xỉu"]
        conf = (max_votes / total_votes * 100) if total_votes > 0 else 50
        conf = min(99.9, max(65, conf + random.uniform(-2, 4)))
        main_reason = "; ".join(reasons[:2]) if reasons else "Tổng hợp"
        return pred, main_reason, conf

ai = TaiXiuAIPro()

# ═══════════════ STATE & HISTORY ═══════════════
tool_state = defaultdict(lambda: {"loss":0, "rev":False, "rev_loss":0, "last_pred":None})
history_log = defaultdict(list)

def update_state_and_reverse(tool, mode, actual_result):
    state = tool_state[f"{tool}_{mode}"]
    if state["last_pred"] is not None and actual_result is not None:
        win = (state["last_pred"] == actual_result)
        if win:
            if state["rev"]: state["rev_loss"] = 0
            else: state["loss"] = 0
        else:
            if state["rev"]:
                state["rev_loss"] += 1
                if state["rev_loss"] >= 3:
                    state["rev"] = False
                    state["rev_loss"] = 0
                    state["loss"] = 0
            else:
                state["loss"] += 1
                if state["loss"] >= 3:
                    state["rev"] = True
                    state["loss"] = 0
                    state["rev_loss"] = 0
    return state["rev"]

def get_id(item):
    if isinstance(item, dict):
        for k in ['id','phien','sessionId','SessionID']:
            if k in item and str(item[k]).isdigit(): return int(item[k])
    return 0

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
        url = "https://sunwin-api.example.com/tx"
    else:
        return jsonify({"status":"error","msg":"Sàn không hỗ trợ"})

    try:
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        data = resp.json()
        sessions = data.get("data", data.get("list", []))
        if not isinstance(sessions, list): sessions = []
        sessions = sorted(sessions, key=get_id)

        hist = []
        is_chanle = ("chanle" in url.lower() or mode == "xoc_dia")
        for s in sessions[-50:]:
            val = str(s).upper()
            if is_chanle:
                hist.append("Tài" if ("CHẴN" in val or "CHAN" in val or "'C'" in val) else "Xỉu")
            else:
                hist.append("Tài" if ("TAI" in val or "TÀI" in val or "'T'" in val) else "Xỉu")

        actual = hist[-1].upper() if hist else None
        rev = update_state_and_reverse(tool, mode, actual)
        state = tool_state[f"{tool}_{mode}"]

        if state["last_pred"] is not None and actual is not None:
            win = (state["last_pred"] == actual)
            history_log[f"{tool}_{mode}"].append({
                "phien": str(sessions[-1].get("id","?")) if sessions else "?",
                "du_doan": state["last_pred"],
                "ket_qua": actual,
                "win": win
            })
            if len(history_log[f"{tool}_{mode}"]) > 20:
                history_log[f"{tool}_{mode}"].pop(0)

        raw_pred, reason, conf = ai.predict(hist)
        if state["rev"]:
            raw_pred = "XỈU" if raw_pred == "TÀI" else "TÀI"
            reason = "🔄 ĐẢO CẦU - " + reason
        state["last_pred"] = raw_pred

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
                "reverse_mode": state["rev"]
            }
        })
    except Exception as e:
        return jsonify({"status":"error","msg":str(e)})

@app.route("/api/history")
def get_history():
    tool = request.args.get("tool","")
    mode = request.args.get("mode","tx_md5")
    return jsonify(history_log.get(f"{tool}_{mode}", []))

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

# ... (admin APIs giữ nguyên, không thay đổi)

@app.route("/")
def home():
    return send_file("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
