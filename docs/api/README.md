# ai-tools-collection API 文档


## 📚 API 文档

### 基础信息
- **API 版本**: v1.0.0
- **生产环境**: https://api.aitoolscollection.com/v1
- **开发环境**: http://localhost:8000/v1
- **认证方式**: Bearer Token (JWT)

### 快速开始

```bash
# 健康检查
curl -X GET https://api.aitoolscollection.com/v1/health

# 获取API文档
curl -X GET https://api.aitoolscollection.com/v1/docs

# 获取OpenAPI规范
curl -X GET https://api.aitoolscollection.com/v1/openapi.json
```

### API 端点

#### 健康检查
```
GET /health
```
检查API服务状态。

#### API文档
```
GET /docs
```
获取交互式API文档。

#### OpenAPI规范
```
GET /openapi.json
```
获取OpenAPI规范JSON。

### 认证

使用Bearer Token进行认证:

```bash
curl -X GET https://api.aitoolscollection.com/v1/endpoint \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 错误处理

HTTP状态码:
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `500`: 服务器内部错误

### 速率限制

- **免费层**: 100请求/小时
- **专业层**: 1000请求/小时
- **企业层**: 10000请求/小时

### SDK 和客户端库

- **Python**: `pip install ai-tools-collection-sdk`
- **JavaScript**: `npm install ai-tools-collection-client`
- **Go**: `go get github.com/fabio2026-ui/ai-tools-collection-go`

### OpenAPI 规范

完整的OpenAPI规范可在以下位置获取:
- [OpenAPI JSON](https://api.aitoolscollection.com/v1/openapi.json)
- [Swagger UI](https://api.aitoolscollection.com/v1/docs)
- [ReDoc](https://api.aitoolscollection.com/v1/redoc)
