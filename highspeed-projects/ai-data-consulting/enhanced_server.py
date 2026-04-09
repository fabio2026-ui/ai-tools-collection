#!/usr/bin/env python3
"""
AI数据分析咨询服务 - 增强版服务器
端口: 5008
月收入目标: $10,387.29
"""

import http.server
import socketserver
import json
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta
import uuid

PORT = 5008
DB_FILE = "data_consulting.db"

class EnhancedDataConsulting:
    def __init__(self):
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 创建客户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                name TEXT,
                company TEXT,
                created_at TIMESTAMP,
                last_contact TIMESTAMP,
                status TEXT DEFAULT 'lead'
            )
        ''')
        
        # 创建项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                service_type TEXT,
                price REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP,
                completed_at TIMESTAMP,
                revenue REAL DEFAULT 0,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # 创建收入记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                amount REAL,
                payment_method TEXT,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_client(self, email, name, company):
        """添加新客户"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        client_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO clients (id, email, name, company, created_at, last_contact)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_id, email, name, company, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
        return client_id
        
    def create_project(self, client_id, service_type, price):
        """创建新项目"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        project_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO projects (id, client_id, service_type, price, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, client_id, service_type, price, datetime.now()))
        
        conn.commit()
        conn.close()
        return project_id
        
    def record_revenue(self, project_id, amount, payment_method="stripe"):
        """记录收入"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        revenue_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO revenue (id, project_id, amount, payment_method, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (revenue_id, project_id, amount, payment_method, datetime.now()))
        
        # 更新项目状态
        cursor.execute('''
            UPDATE projects SET status = 'completed', completed_at = ?, revenue = ?
            WHERE id = ?
        ''', (datetime.now(), amount, project_id))
        
        conn.commit()
        conn.close()
        return revenue_id
        
    def get_daily_revenue(self):
        """获取今日收入"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT SUM(amount) FROM revenue 
            WHERE DATE(created_at) = ?
        ''', (today,))
        
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
        
    def get_monthly_revenue(self):
        """获取本月收入"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        month_start = datetime.now().replace(day=1).date()
        cursor.execute('''
            SELECT SUM(amount) FROM revenue 
            WHERE DATE(created_at) >= ?
        ''', (month_start,))
        
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
        
    def get_services(self):
        """获取服务列表"""
        return [
            {
                "id": "basic_analysis",
                "name": "基础数据分析咨询",
                "description": "基础数据清洗、分析和可视化报告",
                "price": 1999,
                "delivery": "3-5个工作日",
                "features": ["数据清洗", "基础分析", "可视化报告", "1次咨询会议"]
            },
            {
                "id": "advanced_consulting",
                "name": "高级AI数据分析咨询",
                "description": "高级机器学习模型和预测分析",
                "price": 1999,
                "delivery": "7-10个工作日",
                "features": ["机器学习模型", "预测分析", "定制算法", "3次咨询会议", "技术文档"]
            },
            {
                "id": "enterprise_solution",
                "name": "企业级数据解决方案",
                "description": "完整的企业数据平台设计和实施",
                "price": 14999,
                "delivery": "2-3周",
                "features": ["架构设计", "系统实施", "团队培训", "持续支持", "SLA保障"]
            },
            {
                "id": "ai_automation",
                "name": "AI数据自动化流程",
                "description": "自动化数据收集、处理和分析流程",
                "price": 7999,
                "delivery": "1-2周",
                "features": ["流程自动化", "API集成", "实时监控", "维护支持"]
            }
        ]

class EnhancedDataConsultingHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.consulting = EnhancedDataConsulting()
        super().__init__(*args, **kwargs)
        
    def do_GET(self):
        if self.path == '/':
            self.send_homepage()
        elif self.path == '/api/health':
            self.send_health()
        elif self.path == '/api/services':
            self.send_services()
        elif self.path == '/api/revenue':
            self.send_revenue()
        elif self.path == '/api/dashboard':
            self.send_dashboard()
        elif self.path.startswith('/api/client/'):
            self.handle_client_api()
        else:
            self.send_error(404, "Not Found")
            
    def do_POST(self):
        if self.path == '/api/client/register':
            self.handle_client_registration()
        elif self.path == '/api/project/create':
            self.handle_project_creation()
        elif self.path == '/api/revenue/record':
            self.handle_revenue_recording()
        else:
            self.send_error(404, "Not Found")
            
    def send_homepage(self):
        """发送主页"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        daily_rev = self.consulting.get_daily_revenue()
        monthly_rev = self.consulting.get_monthly_revenue()
        target_daily = 10387.29 / 30  # 月目标/30天
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI数据分析咨询服务</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); flex: 1; }}
                .services {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }}
                .service-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .price {{ color: #667eea; font-size: 24px; font-weight: bold; }}
                .cta {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 AI数据分析咨询服务</h1>
                <p>月收入目标: $10,387.29 | 日目标: ${target_daily:,.2f}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📊 今日收入</h3>
                    <p class="price">${daily_rev:,.2f}</p>
                    <p>目标: ${target_daily:,.2f}</p>
                </div>
                <div class="stat-card">
                    <h3>💰 本月收入</h3>
                    <p class="price">${monthly_rev:,.2f}</p>
                    <p>目标: $10,387.29</p>
                </div>
                <div class="stat-card">
                    <h3>🎯 达成率</h3>
                    <p class="price">{monthly_rev/10387.29*100:.1f}%</p>
                    <p>剩余天数: {30 - datetime.now().day}</p>
                </div>
            </div>
            
            <h2>📋 服务套餐</h2>
            <div class="services">
        """
        
        for service in self.consulting.get_services():
            html += f"""
                <div class="service-card">
                    <h3>{service['name']}</h3>
                    <p>{service['description']}</p>
                    <p class="price">${service['price']:,.2f}</p>
                    <p>⏱️ 交付时间: {service['delivery']}</p>
                    <ul>
            """
            for feature in service['features']:
                html += f"<li>✓ {feature}</li>"
            html += f"""
                    </ul>
                    <button class="cta" onclick="registerForService('{service['id']}')">立即咨询</button>
                </div>
            """
            
        html += """
            </div>
            
            <script>
                function registerForService(serviceId) {
                    const email = prompt("请输入您的邮箱:");
                    const name = prompt("请输入您的姓名:");
                    const company = prompt("请输入您的公司:");
                    
                    if (email && name && company) {
                        fetch('/api/client/register', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({email, name, company, serviceId})
                        }).then(response => response.json())
                          .then(data => {
                              alert('注册成功！我们的顾问将尽快联系您。');
                          });
                    }
                }
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
        
    def send_health(self):
        """健康检查"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        data = {
            "status": "healthy",
            "service": "Enhanced AI Data Consulting",
            "port": PORT,
            "target_monthly": 10387.29,
            "current_monthly": self.consulting.get_monthly_revenue(),
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(data).encode())
        
    def send_services(self):
        """服务列表"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        data = {
            "services": self.consulting.get_services(),
            "count": len(self.consulting.get_services())
        }
        self.wfile.write(json.dumps(data).encode())
        
    def send_revenue(self):
        """收入数据"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        data = {
            "daily": self.consulting.get_daily_revenue(),
            "monthly": self.consulting.get_monthly_revenue(),
            "target_daily": 10387.29 / 30,
            "target_monthly": 10387.29,
            "achievement_rate": (self.consulting.get_monthly_revenue() / 10387.29 * 100) if 10387.29 > 0 else 0
        }
        self.wfile.write(json.dumps(data).encode())
        
    def send_dashboard(self):
        """仪表板数据"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # 模拟一些数据用于展示
        data = {
            "revenue_trend": [
                {"date": "2026-03-25", "amount": 1200},
                {"date": "2026-03-26", "amount": 1800},
                {"date": "2026-03-27", "amount": 1500},
                {"date": "2026-03-28", "amount": 2200},
                {"date": "2026-03-29", "amount": 1900},
                {"date": "2026-03-30", "amount": self.consulting.get_daily_revenue()}
            ],
            "top_services": [
                {"name": "高级AI数据分析咨询", "revenue": 14997, "count": 3},
                {"name": "企业级数据解决方案", "revenue": 14999, "count": 1},
                {"name": "基础数据分析咨询", "revenue": 5997, "count": 3}
            ],
            "client_metrics": {
                "total_clients": 15,
                "active_projects": 8,
                "conversion_rate": "23%",
                "avg_project_value": 4165.75
            }
        }
        self.wfile.write(json.dumps(data).encode())
        
    def handle_client_api(self):
        """处理客户端API"""
        # 简化实现
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        data = {"message": "Client API endpoint"}
        self.wfile.write(json.dumps(data).encode())
        
    def handle_client_registration(self):
        """处理客户注册"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # 添加客户
        client_id = self.consulting.add_client(
            data['email'], 
            data['name'], 
            data['company']
        )
        
        # 创建项目
        service_id = data.get('serviceId', 'basic_analysis')
        services = {s['id']: s for s in self.consulting.get_services()}
        price = services.get(service_id, {}).get('price', 1999)
        
        project_id = self.consulting.create_project(client_id, service_id, price)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "success": True,
            "message": "注册成功！我们的顾问将尽快联系您。",
            "client_id": client_id,
            "project_id": project_id,
            "estimated_price": price
        }
        self.wfile.write(json.dumps(response).encode())
        
    def handle_project_creation(self):
        """处理项目创建"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"message": "Project creation endpoint"}
        self.wfile.write(json.dumps(response).encode())
        
    def handle_revenue_recording(self):
        """处理收入记录"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        revenue_id = self.consulting.record_revenue(
            data['project_id'],
            data['amount'],
            data.get('payment_method', 'stripe')
        )
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "success": True,
            "revenue_id": revenue_id,
            "amount": data['amount']
        }
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), EnhancedDataConsultingHandler) as httpd:
        print(f"🚀 增强版AI数据分析咨询服务启动在端口 {PORT}")
        print(f"💰 月收入目标: $10,387.29")
        print(f"📊 日目标: ${10387.29/30:,.2f}")
        print(f"🌐 访问: http://localhost:{PORT}")
        httpd.serve_forever()