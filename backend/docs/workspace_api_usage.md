# Workspace API 使用说明

## 1. 获取审计证据标准 - `/api/v1/workspace/standards`

### 端点信息
- **URL**: `POST /api/v1/workspace/standards`
- **认证**: 需要Bearer Token
- **功能**: 根据用户请求检索或生成审计证据标准

### 请求格式

```json
{
  "status": "初始化",
  "type": "语义检索",
  "content": "货币资金审计"
}
```

#### 参数说明
- `status` (string): 当前系统状态（如：初始化、复核中等）
- `type` (string): 检索类型，支持以下值：
  - `"语义检索"`: 根据审计结论内容进行语义匹配
  - `"分类检索"`: 根据分类标签进行检索
  - `"AI生成"`: 使用AI生成新的审计证据标准
- `content` (string): 检索内容（审计结论或关键词）

### 响应格式

```json
{
  "审计证据标准": {
    "审计结论": "经核查，被审计单位共开立12个银行结算账户...",
    "审计证据分类与要求": [
      {
        "银行存款": {
          "完整性": [
            {
              "证据内容": "银行存款余额调节表",
              "质量要求": "证据来源于被审计单位，形式为经复核人签字的底稿..."
            }
          ],
          "存在": [
            {
              "证据内容": "银行对账单",
              "质量要求": "证据来源于银行，形式为加盖银行印章的原件..."
            }
          ]
        }
      }
    ]
  }
}
```

### 使用示例

#### 示例 1: 语义检索
```python
import requests

url = "http://127.0.0.1:8000/api/v1/workspace/standards"
headers = {
    "Authorization": "Bearer YOUR_TOKEN_HERE",
    "Content-Type": "application/json"
}
data = {
    "status": "初始化",
    "type": "语义检索",
    "content": "银行账户数量过多，存在休眠账户"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### 示例 2: 分类检索
```python
data = {
    "status": "初始化",
    "type": "分类检索",
    "content": "货币资金"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### 示例 3: AI生成
```python
data = {
    "status": "初始化",
    "type": "AI生成",
    "content": "公司存在大量关联方交易，交易价格公允性存疑"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## 2. 执行复核 - `/api/v1/workspace/execute_review`

### 端点信息
- **URL**: `POST /api/v1/workspace/execute_review`
- **认证**: 需要Bearer Token
- **功能**: 开始执行审计复核流程

### 请求格式

```json
{
  "重大事项概述": "被审计单位银行账户数量异常，开立了12个银行结算账户",
  "审计目标": "核实银行账户的完整性、存在性和控制权归属",
  "审计证据标准": {
    "审计结论": "经核查，被审计单位共开立12个银行结算账户...",
    "审计证据分类与要求": [
      {
        "银行存款": {
          "完整性": [
            {
              "证据内容": "银行存款余额调节表",
              "质量要求": "证据来源于被审计单位，形式为经复核人签字的底稿..."
            }
          ]
        }
      }
    ],
    "充分适当评判标准": "审计证据应当充分、适当，能够支持审计结论"
  }
}
```

#### 参数说明
- `重大事项概述` (string): 描述被审计单位面临的重大事项或情况
- `审计目标` (string): 审计师需要达成的具体审计目标
- `审计证据标准` (object): 包含审计结论和证据要求的复合结构
  - `审计结论` (string): 基于审计证据得出的结论
  - `审计证据分类与要求` (array): 按类别组织的审计证据及其质量要求
  - `充分适当评判标准` (string): 用于评估审计证据是否充分和适当的评判标准

### 响应格式

响应类型由 `response_type` 字段决定，可能的值：
- `"upload_file_requirement"`: 需要上传文件
- `"help_requirement"`: 需要人工帮助
- `"review_result"`: 复核完成，返回结果

#### 响应类型 1: upload_file_requirement
```json
{
  "response_type": "upload_file_requirement",
  "data": {
    "filename_list": ["银行存款", "应收账款"],
    "review_config": {
      "MAX_TRIES": 3,
      "WAIT_TIMES": {
        "file_loading": 10,
        "replying": 20
      }
    }
  },
  "review_config": {
    "MAX_TRIES": 3,
    "WAIT_TIMES": {
      "file_loading": 10,
      "replying": 20
    }
  }
}
```

#### 响应类型 2: help_requirement
```json
{
  "response_type": "help_requirement",
  "data": {
    "stage": "证据分析阶段",
    "request": "无法判断证据的充分性",
    "reason": "底稿中缺少关键信息"
  },
  "review_config": {
    "MAX_TRIES": 3,
    "WAIT_TIMES": {
      "file_loading": 10,
      "replying": 20
    }
  }
}
```

#### 响应类型 3: review_result
```json
{
  "response_type": "review_result",
  "data": {
    "重大事项概述": "被审计单位银行账户数量异常...",
    "审计结论": "经核查，被审计单位共开立12个银行结算账户...",
    "复核结果明细": [...],
    "统计整理": {
      "证据总数": 10,
      "充分性情况": {
        "缺失数量": 2,
        "缺失详情": [...]
      },
      "适当性情况": {
        "不适当证据数量": 3,
        "详情": [...]
      }
    },
    "结论与原因": {
      "复核结论": "审计证据总体充分...",
      "业务原因": "部分证据来源不够可靠..."
    }
  },
  "review_config": {
    "MAX_TRIES": 3,
    "WAIT_TIMES": {
      "file_loading": 10,
      "replying": 20
    }
  }
}
```

### 使用示例

```python
import requests

url = "http://127.0.0.1:8000/api/v1/workspace/execute_review"
headers = {
    "Authorization": "Bearer YOUR_TOKEN_HERE",
    "Content-Type": "application/json"
}

# 第一步：先获取审计证据标准
standards_url = "http://127.0.0.1:8000/api/v1/workspace/standards"
standards_data = {
    "status": "初始化",
    "type": "语义检索",
    "content": "银行账户数量异常"
}
standards_response = requests.post(standards_url, json=standards_data, headers=headers)
standard = standards_response.json()["审计证据标准"]

# 第二步：执行复核
review_data = {
    "重大事项概述": "被审计单位银行账户数量异常，开立了12个银行结算账户",
    "审计目标": "核实银行账户的完整性、存在性和控制权归属",
    "审计证据标准": {
        "审计结论": standard["审计结论"],
        "审计证据分类与要求": standard["审计证据分类与要求"],
        "充分适当评判标准": "审计证据应当充分、适当，能够支持审计结论"
    }
}

response = requests.post(url, json=review_data, headers=headers)
result = response.json()

print(f"响应类型: {result['response_type']}")
print(f"响应数据: {result['data']}")
```

---

## 完整工作流程示例

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"
TOKEN = "YOUR_TOKEN_HERE"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 步骤 1: 获取审计证据标准
print("步骤 1: 获取审计证据标准...")
standards_response = requests.post(
    f"{BASE_URL}/workspace/standards",
    json={
        "status": "初始化",
        "type": "语义检索",
        "content": "银行账户数量异常，存在多个休眠账户"
    },
    headers=headers
)
standard = standards_response.json()["审计证据标准"]
print(f"✓ 获取到审计结论: {standard['审计结论'][:50]}...")

# 步骤 2: 开始执行复核
print("\n步骤 2: 执行复核...")
review_response = requests.post(
    f"{BASE_URL}/workspace/execute_review",
    json={
        "重大事项概述": "被审计单位银行账户数量异常",
        "审计目标": "核实银行账户的完整性和控制权",
        "审计证据标准": {
            "审计结论": standard["审计结论"],
            "审计证据分类与要求": standard["审计证据分类与要求"],
            "充分适当评判标准": "审计证据应当充分、适当"
        }
    },
    headers=headers
)

result = review_response.json()
response_type = result["response_type"]

if response_type == "upload_file_requirement":
    print(f"✓ 需要上传文件: {result['data']['filename_list']}")
    # 处理文件上传...
    
elif response_type == "help_requirement":
    print(f"✓ 需要人工帮助: {result['data']['request']}")
    # 提供人工帮助...
    
elif response_type == "review_result":
    print(f"✓ 复核完成!")
    print(f"  证据总数: {result['data']['统计整理']['证据总数']}")
    print(f"  缺失数量: {result['data']['统计整理']['充分性情况']['缺失数量']}")
    print(f"  复核结论: {result['data']['结论与原因']['复核结论']}")
```

---

## 注意事项

1. **认证**: 所有请求都需要在Header中包含有效的Bearer Token
2. **数据库**: 审计证据标准存储在 `backend/infrastructure/data/cpa_assistant.db`
3. **API Key**: 使用AI生成功能需要配置阿里云API Key（在 `system_config_service.py` 中）
4. **向量检索**: 语义检索功能需要事先生成向量索引
5. **文件格式**: 审计证据分类与要求使用嵌套的字典和列表结构

## 错误处理

### 常见错误
- `401 Unauthorized`: Token无效或过期
- `404 Not Found`: 分类检索时未找到对应标准
- `400 Bad Request`: 不支持的检索类型
- `500 Internal Server Error`: 服务器内部错误（如API Key未配置）

### 错误响应示例
```json
{
  "detail": "未找到分类为 '货币资金' 的审计证据标准"
}
```
