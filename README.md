# ai-tools-collection

AI工具 - 自动化部署

## 文件说明
## 📁 项目文件列表

- `video_agent_simple_fixed.py`
- `test_toutiao_video.py`
- `bot_experience_tester.py`
- `bot_experience_tester_simple.py`
- `trading_signal_simple.py`
- `enhanced_ai_trading_signal.py`
- `enhanced_ai_trading_signal_fixed.py`
- `ai_trading_signal_enhanced.py`
- `project_1_ai_code_assistant_pro.py`
- `project_2_ultra_studio_ai.py`
- `enhanced_digital_products.py`
- `enhanced_projects/data_consulting.py`
- `accelerated_deliverables/ai_code_reviewer.py`
- `accelerated_deliverables/auto_test_framework.py`
- `accelerated_deliverables/system_integration_framework.py`
- `accelerated_deliverables/project_management_dashboard.py`
- `highspeed-projects/ai-data-consulting/enhanced_server.py`
- `highspeed-projects/ai-data-consulting/simple_server.py`
- `skills/autonomous-search/SKILL.md`
- `autonomous_search_skill_plan.md`
- `video_agent_skill/SKILL.md`
- `video_agent_skill/scripts/subtitle_processor.py`
- `video_agent_skill/scripts/video_agent_main.py`
- `video_agent_skill/scripts/video_downloader.py`
- `voice-skill/SKILL.md`
- `voice-skill/scripts/force_transcribe.py`
- `page-agent-skill/scripts/content_analyzer.py`

这是一个自动化生成的GitHub仓库。

## 部署状态
- ✅ 仓库创建完成
- ⚡ 文件准备中
- 🚀 即将推送完整项目

## 联系
- GitHub: [fabio2026-ui](https://github.com/fabio2026-ui)
- Email: fufansong@gmail.com

## 🐳 Docker 部署
## 🧪 测试

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_ai_tools_collection.py

# 运行集成测试
pytest tests/test_integration_ai_tools_collection.py -v
```

### 测试覆盖率

项目使用pytest-cov进行测试覆盖率统计。目标覆盖率:

- **单元测试**: ≥80%
- **集成测试**: ≥70%
- **总体覆盖率**: ≥75%

### 测试类型

1. **单元测试**: 测试单个函数和类
2. **集成测试**: 测试组件之间的交互
3. **端到端测试**: 测试完整工作流程
4. **性能测试**: 测试系统性能
5. **安全测试**: 测试安全漏洞

### 持续集成

GitHub Actions自动运行测试:
- 每次推送到main分支
- 每次拉取请求
- 每天凌晨自动运行

### 测试报告

测试报告可在以下位置查看:
- **GitHub Actions**: 工作流运行详情
- **Codecov**: 代码覆盖率报告
- **测试产物**: HTML覆盖率报告

### 测试最佳实践

- 每个测试应该独立运行
- 使用fixture进行测试数据准备
- 模拟外部依赖
- 测试边界情况和错误场景
- 保持测试快速运行

## 📦 GitHub Container Registry

### 自动构建的容器镜像

每次推送到main分支时，GitHub Actions会自动构建并推送Docker镜像到GitHub Container Registry。

**镜像地址**: `ghcr.io/fabio2026-ui/ai-tools-collection:latest`

### 拉取和使用镜像

```bash
# 拉取最新镜像
docker pull ghcr.io/fabio2026-ui/ai-tools-collection:latest

# 运行容器
docker run -d -p 8080:8000 --name ai-tools-collection ghcr.io/fabio2026-ui/ai-tools-collection:latest

# 使用docker-compose
version: '3.8'
services:
  ai-tools-collection:
    image: ghcr.io/fabio2026-ui/ai-tools-collection:latest
    ports:
      - "8080:8000"
```

### 手动构建和推送

```bash
# 登录到GitHub Container Registry
echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin

# 构建镜像
docker build -t ghcr.io/fabio2026-ui/ai-tools-collection:latest .

# 推送镜像
docker push ghcr.io/fabio2026-ui/ai-tools-collection:latest
```


### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/fabio2026-ui/ai-tools-collection.git
   cd ai-tools-collection
   ```

2. **使用Docker部署**
   ```bash
   # 方法1: 使用部署脚本
   ./deploy.sh
   
   # 方法2: 手动部署
   docker-compose build
   docker-compose up -d
   ```

3. **访问应用**
   - 本地访问: http://localhost:8080
   - 容器状态: `docker ps | grep ai-tools-collection`
   - 查看日志: `docker logs ai-tools-collection`

### 管理命令

```bash
# 停止容器
docker-compose down

# 重启容器
docker-compose restart

# 查看日志
docker-compose logs -f

# 进入容器
docker exec -it ai-tools-collection bash
```

### 生产环境部署

对于生产环境，建议使用:
- **Docker Swarm** 或 **Kubernetes** 进行容器编排
- **Traefik** 或 **Nginx** 作为反向代理
- **Let's Encrypt** 进行SSL证书管理
