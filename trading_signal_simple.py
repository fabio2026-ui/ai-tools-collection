#!/usr/bin/env python3
"""
简化版AI交易信号系统 - 端口 5007
"""

import http.server
import socketserver
import json
import time
import random
from datetime import datetime, timedelta
import threading
from urllib.parse import urlparse, parse_qs

class TradingSignalSystem:
    def __init__(self):
        self.signals = []
        self.market_data = {
            "BTC": {"price": 65000, "change": 2.5},
            "ETH": {"price": 3500, "change": 1.8},
            "SOL": {"price": 180, "change": 5.2}
        }
        self._init_signals()
    
    def _init_signals(self):
        for i in range(10):
            symbol = random.choice(list(self.market_data.keys()))
            self.signals.append({
                "id": i+1,
                "symbol": symbol,
                "signal": random.choice(["BUY", "SELL", "HOLD"]),
                "confidence": random.randint(65, 95),
                "price": self.market_data[symbol]["price"],
                "timestamp": datetime.now().isoformat()
            })
    
    def get_market_data(self):
        return {"data": self.market_data, "timestamp": datetime.now().isoformat()}
    
    def get_signals(self):
        return {"signals": self.signals[-5:], "total": len(self.signals)}
    
    def get_analysis(self, symbol):
        if symbol not in self.market_data:
            return {"error": "Symbol not found"}
        return {
            "symbol": symbol,
            "price": self.market_data[symbol]["price"],
            "analysis": f"{symbol}技术分析完成",
            "recommendation": random.choice(["买入", "持有", "卖出"])
        }

class TradingHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.system = TradingSignalSystem()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        path = self.path
        
        if path == "/api/market":
            self._send_json(self.system.get_market_data())
        elif path == "/api/signals":
            self._send_json(self.system.get_signals())
        elif path.startswith("/api/analysis/"):
            symbol = path.split("/")[-1]
            self._send_json(self.system.get_analysis(symbol))
        elif path == "/":
            self._send_html()
        else:
            self.send_error(404, "Not Found")
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_html(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI交易信号系统</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                .card { border: 1px solid #ccc; padding: 20px; margin: 10px; border-radius: 10px; }
                .signal { background: #f0f0f0; padding: 10px; margin: 5px; }
            </style>
        </head>
        <body>
            <h1>🚀 AI交易信号系统</h1>
            <div class="card">
                <h2>市场数据</h2>
                <div id="market"></div>
                <button onclick="loadMarket()">刷新</button>
            </div>
            <div class="card">
                <h2>交易信号</h2>
                <div id="signals"></div>
                <button onclick="loadSignals()">刷新</button>
            </div>
            <script>
                async function loadMarket() {
                    const res = await fetch('/api/market');
                    const data = await res.json();
                    let html = '';
                    for (const [symbol, info] of Object.entries(data.data)) {
                        html += `<p>${symbol}: $${info.price} (${info.change}%)</p>`;
                    }
                    document.getElementById('market').innerHTML = html;
                }
                async function loadSignals() {
                    const res = await fetch('/api/signals');
                    const data = await res.json();
                    let html = '';
                    data.signals.forEach(s => {
                        html += `<div class="signal">
                            <strong>${s.symbol}</strong>: ${s.signal} (${s.confidence}%)
                            <br>价格: $${s.price}
                        </div>`;
                    });
                    document.getElementById('signals').innerHTML = html;
                }
                loadMarket();
                loadSignals();
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

def run(port=5007):
    with socketserver.TCPServer(("", port), TradingHandler) as httpd:
        print(f"AI交易信号系统运行在端口 {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()