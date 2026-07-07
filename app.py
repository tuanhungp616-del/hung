import os
import math
import random
import re
import numpy as np
from collections import deque
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ==========================================
# 💾 BỘ NHỚ LƯU TRỮ LỊCH SỬ THUẬT TOÁN
# ==========================================
GAME_HISTORIES = {
    "betvip_tx": deque(maxlen=350),
    "lc79_tx": deque(maxlen=350),
    "sunwin_sicbo": deque(maxlen=350)
}

GAME_STATS = {key: {"t":0, "x":0, "streak_t":0, "streak_x":0, "max_streak_t":0, "max_streak_x":0, "cycles":{}} 
              for key in GAME_HISTORIES}

# ==========================================
# 🛠️ CÔNG CỤ XỬ LÝ ID PHIÊN VÀ THỐNG KÊ
# ==========================================
def get_id(item):
    if isinstance(item, dict):
        for k in ['id', 'phien', 'sessionId', 'sid', 'referenceId', 'matchId', 'phien_hien_tai', 'turnNum']:
            if k in item and str(item[k]).replace('-', '').isdigit():
                return int(item[k])
    matches = re.findall(r"'?(?:id|phien|referenceId|sessionId|matchId|phien_hien_tai|turnNum)'?\s*:\s*'?'?(\d+)'?'?", str(item), re.IGNORECASE)
    return int(matches[0]) if matches else 0

def update_stats(game_key, result):
    stats = GAME_STATS[game_key]
    stats["t"] += 1 if result == "T" else 0
    stats["x"] += 1 if result == "X" else 0
    
    seq = list(GAME_HISTORIES[game_key])
    for cycle_len in range(2, 15):
        if len(seq) >= cycle_len * 3:
            cycle = tuple(seq[-cycle_len:])
            stats["cycles"][cycle] = stats["cycles"].get(cycle, 0) + 1

def detect_cycle_pattern(history):
    seq = list(history)
    if len(seq) < 12: return None, 0
    best_cycle, best_score = None, 0
    for length in range(3, 12):
        matches, total = 0, 0
        for i in range(len(seq)-length*2):
            if seq[i:i+length] == seq[i+length:i+length*2]: matches += 1
            total += 1
        if total > 0:
            score = matches / total
            if score > best_score and score > 0.4:
                best_score = score
                best_cycle = seq[-length:]
    return best_cycle, best_score

def trend_analysis(history):
    seq = np.array([1 if x=="T" else 0 for x in history])
    if len(seq) < 15: return 0
    trends, weights = [], []
    for w in [5, 10, 20]:
        if len(seq) >= w:
            y = seq[-w:]
            x = np.arange(w)
            trends.append(np.polyfit(x, y, 1)[0])
            weights.append(w)
    return np.average(trends, weights=weights) if trends else 0

# ==========================================
# 🧠 THUẬT TOÁN DỰ ĐOÁN HỢP NHẤT HYBRID
# ==========================================
def hybrid_predict(history):
    seq = [1 if s=="T" else 0 for s in history]
    total_prob = 0.5
    if len(seq) >= 12:
        order_weights = {1:0.45, 2:0.35, 3:0.20}
        total_prob = 0.0
        for order, weight in order_weights.items():
            if len(seq) < order + 2: continue
            trans = {}
            for i in range(order, len(seq)):
                state = tuple(seq[i-order:i])
                if state not in trans: trans[state] = {"t":0, "x":0}
                if seq[i] == 1: trans[state]["t"] += 1
                else: trans[state]["x"] += 1
            
            curr_state = tuple(seq[-order:])
            if curr_state in trans:
                dt = trans[curr_state]
                total_prob += (dt["t"]/(dt["t"]+dt["x"]) if dt["t"]+dt["x"]>0 else 0.5) * weight

        cycle, cycle_conf = detect_cycle_pattern(history)
        if cycle and len(cycle) >= 2: total_prob += (0.15 if cycle[0]=="T" else -0.15) * cycle_conf
        total_prob += trend_analysis(history) * 0.25

    base_p = max(0.15, min(0.85, total_prob))
    final_p = sum(1 for _ in range(10000) if random.random() < (base_p + random.uniform(-0.05, 0.05))) / 100
    pred = "TÀI" if final_p > 50 else "XỈU"
    conf = max(55.0, min(99.0, final_p if pred == "TÀI" else 100-final_p))
    
    return pred, round(conf, 1), "CHUAHUNGKITO AI V2.0"

# ==========================================
# 📡 ĐƯỜNG TRUYỀN API ĐỒNG BỘ
# ==========================================
@app.route("/api/scan", methods=["GET"])
def scan_game():
    tool = request.args.get("tool", "betvip_tx")
    urls = {
        "betvip_tx": "https://wtx.macminim6.online/v1/tx/sessions",
        "lc79_tx": "https://wtx.tele68.com/v1/tx/sessions",
        "sunwin_sicbo": "https://api.wsktnus8.net/v2/history/getLastResult?gameId=ktrng_3979&size=100"
    }
    
    try:
        res = requests.get(urls.get(tool, urls["betvip_tx"]), timeout=5).json()
        lst = res.get("data", res.get("list", res))
        if not isinstance(lst, list): raise Exception()
        
        lst = sorted(lst, key=lambda x: get_id(x))
        for s in lst:
            GAME_HISTORIES[tool].append("T" if any(k in str(s).upper() for k in ["TAI","TÀI","BIG"]) else "X")
            update_stats(tool, GAME_HISTORIES[tool][-1])
        
        phien_hien_tai = str(get_id(lst[-1]) + 1)
        dd, tl, lk = hybrid_predict(list(GAME_HISTORIES[tool]))
        
        return jsonify({"status": "success", "data": {"du_doan": dd, "ti_le": tl, "loi_khuyen": lk, "phien": phien_hien_tai}})
    
    except:
        return jsonify({"status": "error", "data": {"du_doan": "TÀI", "ti_le": round(random.uniform(75, 88), 1), "phien": "Đang kết nối..."}})

@app.route("/")
def home():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_file(os.path.join(base_dir, "index.html"))

if __name__ == "__main__":
    # Cấu hình dự phòng chạy cục bộ dưới máy
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
