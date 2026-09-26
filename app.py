print(">>> 正在啟動 Masterful Studio 伺服器...")

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'masterful-studio-secret'
# 改用 threading 模式，避免 Python 3.14 卡住問題
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

counts = [0] * 9   # 索引0~8 对应 Zone 1~9

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Masterful Studio - Counter</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body {
            width: 100vw; min-height: 100vh;
            background-color: #0a0a0a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow-y: scroll;
            scrollbar-width: none; -ms-overflow-style: none;
        }
        body::-webkit-scrollbar { display: none; }
        .container {
            width: 100vw; min-height: 100vh;
            display: flex; flex-direction: column; text-align: center;
        }
        h1 {
            color: #fff; font-weight: 300; letter-spacing: 3px;
            font-size: 2.5rem; padding: 20px 0 10px 0; margin: 0;
            background: #0a0a0a; border-bottom: 2px solid #333;
        }
        .grid {
            flex: 0 0 100vh;  /* 關鍵修改：高度設為 100vh，直接將按鈕推到螢幕外 */
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: repeat(3, 1fr);
            gap: 0; background: #0a0a0a; min-height: 500px;
        }
        .card {
            background: #1e1e1e;
            display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            border: 2px solid #3a3a3a; padding: 10px;
            transition: background 0.15s;
        }
        .card:hover { background: #2e2e2e; }
        .card .label {
            color: #aaa; font-size: 2rem; text-transform: uppercase;
            letter-spacing: 3px; margin-bottom: 5px;
        }
        .card .num {
            color: #fff; font-size: 7rem; font-weight: 700;
            line-height: 1; transition: color 0.2s;
        }
        .card .num.pop { color: #4fc3f7; }
        /* 底部按鈕區域 */
        .footer {
            flex-shrink: 0; display: flex; justify-content: center;
            gap: 20px; padding: 50px 0 80px 0; /* 增加上下內距，滑到底時更好看 */
            background: #0a0a0a; border-top: 2px solid #333;
        }
        .btn {
            background: #2a2a2a; border: 1px solid #555; color: #ccc;
            padding: 12px 36px; border-radius: 40px; font-size: 1.2rem;
            cursor: pointer; letter-spacing: 1px;
        }
        .btn:hover { background: #3a3a3a; color: #fff; }
        .btn-reset {
            background: #3a1a1a; border-color: #662222; color: #ff8888;
        }
        .btn-reset:hover { background: #552222; }
        @media (max-width: 600px) {
            h1 { font-size: 1.8rem; }
            .grid { flex: 0 0 100vh; min-height: 400px; } /* 移動端同樣設為 100vh */
            .card .label { font-size: 1.4rem; }
            .card .num { font-size: 4.5rem; }
            .btn { padding: 8px 20px; font-size: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Masterful Studio</h1>
        <div class="grid">
            <!-- 第一行：Zone 3, 2, 1 -->
            <div class="card"><div class="label">Zone 3</div><div class="num" id="c2">0</div></div>
            <div class="card"><div class="label">Zone 2</div><div class="num" id="c1">0</div></div>
            <div class="card"><div class="label">Zone 1</div><div class="num" id="c0">0</div></div>
            <!-- 第二行：Zone 6, 5, 4 -->
            <div class="card"><div class="label">Zone 6</div><div class="num" id="c5">0</div></div>
            <div class="card"><div class="label">Zone 5</div><div class="num" id="c4">0</div></div>
            <div class="card"><div class="label">Zone 4</div><div class="num" id="c3">0</div></div>
            <!-- 第三行：Zone 9, 8, 7 -->
            <div class="card"><div class="label">Zone 9</div><div class="num" id="c8">0</div></div>
            <div class="card"><div class="label">Zone 8</div><div class="num" id="c7">0</div></div>
            <div class="card"><div class="label">Zone 7</div><div class="num" id="c6">0</div></div>
        </div>
        <div class="footer">
            <button class="btn" onclick="fetchAll()">⟳ Refresh All</button>
            <button class="btn btn-reset" onclick="resetAll()">✕ Reset All</button>
        </div>
    </div>

    <script>
        var socket = io();

        socket.on('update_counts', function(data) {
            for (var i = 0; i < 9; i++) updateDisplay(i, data[i]);
        });
        
        socket.on('connect', function() { socket.emit('request_update'); });

        function updateDisplay(index, value) {
            var el = document.getElementById('c' + index);
            if (el) {
                el.innerText = value;
                el.classList.remove('pop');
                void el.offsetWidth;
                el.classList.add('pop');
            }
        }

        function fetchAll() { socket.emit('request_update'); }

        function resetAll() {
            fetch('/reset_all', { method: 'POST' });
        }

        window.onload = function() { socket.emit('request_update'); };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/report/<int:device_id>')
def report(device_id):
    if 1 <= device_id <= 9:
        counts[device_id - 1] += 1
        print(f"Zone {device_id} 按下，目前：{counts[device_id - 1]}")
        socketio.emit('update_counts', counts)
        return f"OK - Zone {device_id} Count: {counts[device_id - 1]}"
    return "Invalid ID", 400

@app.route('/reset_device/<int:device_id>', methods=['POST'])
def reset_device(device_id):
    if 1 <= device_id <= 9:
        counts[device_id - 1] = 0
        print(f"Zone {device_id} 已重置")
        socketio.emit('update_counts', counts)
        return "OK"
    return "Invalid ID", 400

@app.route('/get_count/<int:device_id>')
def get_count(device_id):
    if 1 <= device_id <= 9:
        return jsonify({'count': counts[device_id - 1]})
    return jsonify({'error': 'Invalid ID'}), 400

@app.route('/reset_all', methods=['POST'])
def reset_all():
    global counts
    counts = [0] * 9
    print("所有計數器已歸零")
    socketio.emit('update_counts', counts)
    return "OK"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('update_counts', counts)

@socketio.on('request_update')
def handle_request_update():
    socketio.emit('update_counts', counts)

if __name__ == '__main__':
    print(">>> 伺服器準備就緒，請打開瀏覽器訪問 http://127.0.0.1:5000")
    print(">>> 若要停止伺服器，請按 Ctrl + C")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
