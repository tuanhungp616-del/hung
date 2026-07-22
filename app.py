# ═══════════════════════════════════════════════════════════════
#  DORAEMON AI v12.0 – MINI WIDGET SERVER (Render/VPS)
#  Admin Key: admin123
# ═══════════════════════════════════════════════════════════════

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests, sqlite3, os, random, string, hashlib, math
from datetime import datetime, timedelta
from collections import Counter, defaultdict

app = Flask(__name__)
CORS(app)
DB_FILE = "royal_keys.db"

ADMIN_KEY = "admin123"

def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def khoi_tao_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS keys (
                        key_str TEXT PRIMARY KEY,
                        expire_time DATETIME,
                        is_banned INTEGER
                     )''')
        c.execute("INSERT OR IGNORE INTO keys VALUES (?, '2099-12-31 23:59:59', 0)", (ADMIN_KEY,))
        conn.commit()

khoi_tao_db()

# ═══════════════ AI ENGINE (15 PHIÊN, TOÀN BỘ CẦU) ═══════════════
class UltimateAIDetector:
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
        if count >= 12:
            pred = "Xỉu" if last == "Tài" else "Tài"
            return pred.upper(), 82
        elif count >= 5:
            pred = "Xỉu" if last == "Tài" else "Tài"
            return pred.upper(), 78
        elif count >= 4:
            return last.upper(), 88
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
                conf = 85 + min(length*2, 14)
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
        if (last6[0]==last6[3] and last6[1]==last6[2]==last6[4]==last6[5] and last6[0]!=last6[1]):
            return last6[0].upper(), 88
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

    def markov_predict_v3(self, hist):
        order = 3
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
        return pred.upper(), min(conf + 20, 94.8)

    def predict(self, full_hist):
        hist = self._last_n(full_hist, self.window)
        if len(hist) < 2:
            return "TÀI", "KHÔNG ĐỦ DỮ LIỆU", 50.0

        detectors = [
            ("Cầu 1-1", self.detect_1_1),
            ("Cầu 2-2", self.detect_2_2),
            ("Cầu 1-2/2-1", self.detect_1_2_or_2_1),
            ("Cầu 1-2-3", self.detect_1_2_3),
            ("Bệt", self.detect_bet),
            ("Cầu nghiêng", self.detect_nghieng),
        ]
        best_pred, best_reason, best_conf = None, "", 0
        for name, det in detectors:
            pred, conf = det(hist)
            if pred and conf > best_conf:
                best_pred, best_reason, best_conf = pred, f"{name} ({conf:.1f}%)", conf
                if conf >= 90: break

        m_pred, m_conf = self.markov_predict_v3(hist)
        if best_pred and m_pred:
            if best_pred == m_pred:
                return best_pred, f"{best_reason} + Markov", min(best_conf + 5, 99.5)
            else:
                if best_conf >= m_conf:
                    return best_pred, best_reason, best_conf
                else:
                    return m_pred, f"Markov bậc 3 ({m_conf:.1f}%)", m_conf
        elif best_pred:
            return best_pred, best_reason, best_conf
        elif m_pred:
            return m_pred, f"Markov bậc 3 ({m_conf:.1f}%)", m_conf

        cnt = Counter(hist)
        if cnt["Tài"] > cnt["Xỉu"]:
            pred, reason = "XỈU", "Đảo xu hướng (Tài áp đảo)"
        elif cnt["Xỉu"] > cnt["Tài"]:
            pred, reason = "TÀI", "Đảo xu hướng (Xỉu áp đảo)"
        else:
            pred, reason = random.choice(["TÀI", "XỈU"]), "Ngẫu nhiên"
        conf = max(cnt.values()) / len(hist) * 100
        return pred, reason, min(conf, 80)

ai = UltimateAIDetector(window=15)

last_pred_map = defaultdict(lambda: None)
last_history = defaultdict(lambda: None)

def get_id(item):
    if isinstance(item, dict):
        for k in ['id','phien','sessionId','SessionID']:
            if k in item and str(item[k]).isdigit(): return int(item[k])
    return 0

@app.route("/api/verify_key", methods=["POST"])
def verify_key():
    req = request.get_json() or {}
    k = req.get("key","").strip()
    if not k: return jsonify({"status":"error","msg":"Nhập Key!"})
    if k == ADMIN_KEY:
        return jsonify({"status":"success","role":"admin","expire":"VĨNH VIỄN"})
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str=?",(k,))
        row = c.fetchone()
        if not row: return jsonify({"status":"error","msg":"KEY KHÔNG TỒN TẠI"})
        if row[1]==1: return jsonify({"status":"error","msg":"KEY BỊ KHÓA"})
        if datetime.now() > datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S"):
            return jsonify({"status":"error","msg":"KEY HẾT HẠN"})
        return jsonify({"status":"success","role":"user","expire":row[0]})

@app.route("/api/scan")
def scan():
    tool = request.args.get("tool","")
    mode = request.args.get("mode","tx_md5")
    key  = request.args.get("key","")
    if key != ADMIN_KEY:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT expire_time, is_banned FROM keys WHERE key_str=?",(key,))
            row = c.fetchone()
            if not row: return jsonify({"status":"error","msg":"Key không tồn tại"})
            if row[1]==1: return jsonify({"status":"error","msg":"Key bị khóa"})
            if datetime.now() > datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S"):
                return jsonify({"status":"error","msg":"Key hết hạn"})

    urls = {
        "lc79": {"xoc_dia": "https://wcl.tele68.com/v1/chanlefull/sessions",
                 "tx_md5": "https://wtxmd52.tele68.com/v1/txmd5/sessions",
                 "tx": "https://wtx.tele68.com/v1/tx/sessions"},
        "betvip": {"tx_md5": "https://wtxmd52.macminim6.online/v1/txmd5/sessions",
                   "tx": "https://wtx.macminim6.online/v1/tx/sessions"}
    }
    url = urls.get(tool, {}).get(mode, "")
    if not url: return jsonify({"status":"error","msg":"Sàn không hỗ trợ"})

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
                "last_result": last_history[f"{tool}_{mode}"]
            }
        })
    except Exception as e:
        return jsonify({"status":"error","msg":str(e)})

@app.route("/")
def home():
    return send_file("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
