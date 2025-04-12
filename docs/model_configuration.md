# AI模型配置指南

本文档提供了如何在`cnetCompSpy`项目中配置不同AI模型提供商的详细指南。

## 配置文件

AI模型的配置位于`config.yaml`文件的`ai_analyzer`部分。以下是基本配置项：

```yaml
ai_analyzer:
  model: "模型名称"             # 使用的AI模型名称
  max_tokens: 4000              # 生成内容的最大令牌数
  temperature: 0.8              # 温度参数，控制响应的随机性
  api_key: "您的API密钥"        # API密钥
  api_base: "API端点URL"        # API基础URL
  system_prompt: "系统提示词"    # 系统提示词
```

## 常见AI模型提供商配置示例

### 1. OpenAI

```yaml
ai_analyzer:
  model: "gpt-4-turbo"
  api_key: "sk-your-openai-api-key"
  api_base: "https://api.openai.com/v1"
```

### 2. 阿里云通义千问

```yaml
ai_analyzer:
  model: "qwen-max"
  api_key: "your-aliyun-api-key"
  api_base: "https://dashscope.aliyuncs.com/v1"
```

### 3. Azure OpenAI

对于Azure OpenAI，需要提供您的资源名称和部署名称：

```yaml
ai_analyzer:
  model: "your-deployment-name"
  api_key: "your-azure-api-key"
  api_base: "https://your-resource-name.openai.azure.com/openai/deployments/your-deployment-name"
```

### 4. 百度文心一言

```yaml
ai_analyzer:
  model: "ernie-bot-4"
  api_key: "your-baidu-api-key"
  api_base: "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop"
```

### 5. 讯飞星火

```yaml
ai_analyzer:
  model: "spark-3.5"
  api_key: "your-xfyun-api-key"
  api_base: "https://spark-api.xf-yun.com/v1"
```

## 使用模拟模式

如果您不想使用实际的AI模型API，可以将`api_key`和`api_base`留空，系统将自动使用模拟模式：

```yaml
ai_analyzer:
  model: "mock"
  api_key: ""
  api_base: ""
```

## 验证配置

配置完成后，您可以运行以下命令来验证配置是否正确：

```bash
python -m src.main --mode analyze
```

如果配置正确，您将看到日志中显示"初始化AI模型"和"已识别API提供商"等信息。

## 故障排除

1. **API密钥错误**: 如果您看到"API调用失败"的错误，请检查您的API密钥是否正确。

2. **API端点错误**: 如果您看到"API调用异常"的错误，请检查您的API端点URL是否正确。

3. **响应格式错误**: 如果您看到"解析模型响应失败"的错误，可能是因为模型提供商的响应格式发生了变化，请联系开发者更新代码。

4. **模拟模式**: 如果您未提供API密钥或API端点，系统将自动使用模拟模式，这将返回预设的响应而不是实际调用AI模型。 