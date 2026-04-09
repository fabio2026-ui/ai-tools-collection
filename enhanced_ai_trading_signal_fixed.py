                        <button class="refresh-btn" onclick="loadSignals()">刷新信号</button>
                    </div>
                    
                    <!-- 性能统计卡片 -->
                    <div class="card">
                        <h2>📊 系统性能</h2>
                        <div id="performanceStats">
                            <!-- 性能统计将通过JavaScript动态加载 -->
                        </div>
                        <button class="refresh-btn" onclick="loadPerformance()">刷新统计</button>
                    </div>
                    
                    <!-- 技术分析卡片 -->
                    <div class="card">
                        <h2>🔍 技术分析</h2>
                        <div id="technicalAnalysis">
                            <p>选择符号进行分析：</p>
                            <select id="symbolSelect" onchange="loadTechnicalAnalysis()">
                                <option value="BTC">BTC - 比特币</option>
                                <option value="ETH">ETH - 以太坊</option>
                                <option value="SOL">SOL - Solana</option>
                                <option value="ADA">ADA - Cardano</option>
                                <option value="AAPL">AAPL - 苹果</option>
                                <option value="TSLA">TSLA - 特斯拉</option>
                                <option value="NVDA">NVDA - 英伟达</option>
                            </select>
                            <div id="analysisResult" style="margin-top: 15px;"></div>
                        </div>
                    </div>
                </div>
                
                <!-- API文档部分 -->
                <div class="api-section">
                    <h2>🔧 API接口</h2>
                    <div class="api-endpoints">
                        <div class="api-endpoint">
                            <span class="endpoint-method method-get">GET</span>
                            <span class="endpoint-path">/api/market_data</span>
                            <p>获取实时市场数据</p>
                        </div>
                        <div class="api-endpoint">
                            <span class="endpoint-method method-get">GET</span>
                            <span class="endpoint-path">/api/signals</span>
                            <p>获取交易信号列表</p>
                        </div>
                        <div class="api-endpoint">
                            <span class="endpoint-method method-get">GET</span>
                            <span class="endpoint-path">/api/analysis/{symbol}</span>
                            <p>获取技术分析</p>
                        </div>
                        <div class="api-endpoint">
                            <span class="endpoint-method method-get">GET</span>
                            <span class="endpoint-path">/api/performance</span>
                            <p>获取系统性能统计</p>
                        </div>
                        <div class="api-endpoint">
                            <span class="endpoint-method method-post">POST</span>
                            <span class="endpoint-path">/api/generate_signal</span>
                            <p>生成新的交易信号</p>
                        </div>
                    </div>
                </div>
                
                <footer>
                    <p>AI交易信号系统 v2.0.0 • 实时数据更新 • 技术支持：小六</p>
                    <p>访问地址：http://localhost:5007 • API文档完整可用</p>
                </footer>
            </div>
            
            <script>
                // 加载市场数据
                async function loadMarketData() {
                    try {
                        const response = await fetch('/api/market_data');
                        const data = await response.json();
                        
                        let html = '';
                        for (const [symbol, info] of Object.entries(data.data)) {
                            const changeClass = info.change_24h >= 0 ? 'positive' : 'negative';
                            const changeSign = info.change_24h >= 0 ? '+' : '';
                            
                            html += `
                                <div class="market-item">
                                    <div class="symbol">${symbol}</div>
                                    <div class="price">$${info.price.toLocaleString()}</div>
                                    <div class="change ${changeClass}">
                                        ${changeSign}${info.change_24h}%
                                    </div>
                                    <div style="font-size: 0.8rem; opacity: 0.7;">
                                        成交量: $${(info.volume / 1000000).toFixed(1)}M
                                    </div>
                                </div>
                            `;
                        }
                        
                        document.getElementById('marketData').innerHTML = html;
                    } catch (error) {
                        console.error('加载市场数据失败:', error);
                        document.getElementById('marketData').innerHTML = 
                            '<p style="color: #f87171;">加载失败，请稍后重试</p>';
                    }
                }
                
                // 加载交易信号
                async function loadSignals() {
                    try {
                        const response = await fetch('/api/signals?limit=5');
                        const data = await response.json();
                        
                        let html = '';
                        data.signals.forEach(signal => {
                            const signalClass = signal.signal.toLowerCase();
                            const signalTypeClass = signalClass;
                            
                            html += `
                                <div class="signal-item ${signalClass}">
                                    <div class="signal-header">
                                        <span class="signal-symbol">${signal.symbol}</span>
                                        <span class="signal-type ${signalTypeClass}">${signal.signal}</span>
                                    </div>
                                    <div class="signal-confidence">
                                        置信度: ${signal.confidence}% • 
                                        价格: $${signal.price} • 
                                        目标: $${signal.target_price}
                                    </div>
                                    <div class="signal-reason">理由: ${signal.reason}</div>
                                </div>
                            `;
                        });
                        
                        document.getElementById('signalsList').innerHTML = html;
                    } catch (error) {
                        console.error('加载交易信号失败:', error);
                        document.getElementById('signalsList').innerHTML = 
                            '<p style="color: #f87171;">加载失败，请稍后重试</p>';
                    }
                }
                
                // 加载性能统计
                async function loadPerformance() {
                    try {
                        const response = await fetch('/api/performance');
                        const data = await response.json();
                        
                        const html = `
                            <div style="font-size: 1.1rem;">
                                <p>📈 总信号数: ${data.total_signals}</p>
                                <p>🟢 活跃信号: ${data.active_signals}</p>
                                <p>✅ 已关闭信号: ${data.closed_signals}</p>
                                <p>🎯 胜率: ${data.win_rate}</p>
                                <p>📊 平均置信度: ${data.average_confidence}%</p>
                                <p>🔥 最活跃符号: ${data.most_active_symbol}</p>
                            </div>
                        `;
                        
                        document.getElementById('performanceStats').innerHTML = html;
                    } catch (error) {
                        console.error('加载性能统计失败:', error);
                        document.getElementById('performanceStats').innerHTML = 
                            '<p style="color: #f87171;">加载失败，请稍后重试</p>';
                    }
                }
                
                // 加载技术分析
                async function loadTechnicalAnalysis() {
                    const symbol = document.getElementById('symbolSelect').value;
                    
                    try {
                        const response = await fetch(`/api/analysis/${symbol}`);
                        const data = await response.json();
                        
                        if (data.error) {
                            document.getElementById('analysisResult').innerHTML = 
                                `<p style="color: #f87171;">错误: ${data.error}</p>`;
                            return;
                        }
                        
                        const indicators = data.technical_indicators;
                        const trendColor = indicators.trend === 'OVERBOUGHT' ? '#f87171' : 
                                          indicators.trend === 'OVERSOLD' ? '#4ade80' : '#fbbf24';
                        
                        const html = `
                            <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px;">
                                <h3 style="margin-bottom: 10px;">${symbol} 技术分析</h3>
                                <p>当前价格: <strong>$${data.price}</strong> (${data.change_24h >= 0 ? '+' : ''}${data.change_24h}%)</p>
                                <p>趋势状态: <strong style="color: ${trendColor}">${indicators.trend}</strong></p>
                                <div style="margin-top: 10px;">
                                    <p>📊 RSI: ${indicators.RSI}</p>
                                    <p>📈 MACD: ${indicators.MACD}</p>
                                    <p>📉 MA20: $${indicators.MA_20}</p>
                                    <p>📉 MA50: $${indicators.MA_50}</p>
                                </div>
                                <div style="margin-top: 15px; padding: 10px; background: rgba(255, 255, 255, 0.15); border-radius: 5px;">
                                    <strong>建议:</strong> ${data.recommendation}
                                </div>
                                <p style="margin-top: 10px; font-size: 0.9rem;">${data.analysis}</p>
                            </div>
                        `;
                        
                        document.getElementById('analysisResult').innerHTML = html;
                    } catch (error) {
                        console.error('加载技术分析失败:', error);
                        document.getElementById('analysisResult').innerHTML = 
                            '<p style="color: #f87171;">加载失败，请稍后重试</p>';
                    }
                }
                
                // 页面加载时初始化数据
                document.addEventListener('DOMContentLoaded', function() {
                    loadMarketData();
                    loadSignals();
                    loadPerformance();
                    loadTechnicalAnalysis();
                    
                    // 每30秒自动刷新市场数据
                    setInterval(loadMarketData, 30000);
                    // 每60秒自动刷新信号
                    setInterval(loadSignals, 60000);
                });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def _send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_error_response(self, code, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        error_data = {
            "error": message,
            "timestamp": datetime.now().isoformat(),
            "code": code
        }
        self.wfile.write(json.dumps(error_data, ensure_ascii=False).encode('utf-8'))

def run_server(port=5007):
    """运行HTTP服务器"""
    handler = EnhancedTradingSignalHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 增强版AI交易信号系统已启动")
        print(f"📊 访问地址: http://localhost:{port}")
        print(f"🔧 API端点:")
        print(f"   GET  /api/market_data      - 市场数据")
        print(f"   GET  /api/signals          - 交易信号")
        print(f"   GET  /api/analysis/{{symbol}} - 技术分析")
        print(f"   GET  /api/performance      - 性能统计")
        print(f"   POST /api/generate_signal  - 生成信号")
        print(f"📈 系统已就绪，开始提供实时交易信号服务...")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()