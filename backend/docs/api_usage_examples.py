"""
复核标准 API 使用示例
演示如何通过 HTTP 请求调用复核标准相关 API
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"


def login():
    """登录获取 token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    print(f"✓ 登录成功，获取 token")
    return token


def example_1_semantic_search(token):
    """示例 1: 语义检索"""
    print("\n" + "="*60)
    print("示例 1: 语义检索复核标准")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 语义检索请求
    search_request = {
        "query": "被审计单位的收入确认时点接近资产负债表日，需要关注截止性问题",
        "top_k": 3,
        "similarity_threshold": 0.6
    }
    
    print(f"\n查询文本: {search_request['query']}")
    
    response = requests.post(
        f"{BASE_URL}/review-standards/search/semantic",
        headers=headers,
        json=search_request
    )
    
    response.raise_for_status()
    result = response.json()
    
    print(f"\n找到 {result['total_found']} 个相似结果:")
    for idx, item in enumerate(result['results'], 1):
        print(f"\n{idx}. {item['title']}")
        print(f"   相似度: {item['similarity_score']:.4f}")
        print(f"   分类: {item['category']}")
        print(f"   标签: {item['tags']}")


def example_2_generate_standard(token):
    """示例 2: AI 生成复核标准"""
    print("\n" + "="*60)
    print("示例 2: AI 生成复核标准")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 生成请求
    generate_request = {
        "audit_conclusion": """经审计，被审计单位2023年度存货账面价值较大，占总资产的40%。
        通过实地盘点发现部分原材料存在积压现象，且有部分产品已过保质期。
        经测试存货跌价准备计提是否充分，发现被审计单位对滞销产品的跌价准备计提不足。
        考虑到存货金额重大且存在减值风险，将存货的计价和分摊认定为重大事项。""",
        "auto_save": False,  # 不自动保存，仅预览
        "title": "存货减值复核标准"
    }
    
    print(f"\n审计结论:")
    print(generate_request['audit_conclusion'])
    print("\n正在生成复核标准（需要 10-30 秒）...")
    
    response = requests.post(
        f"{BASE_URL}/review-standards/generate",
        headers=headers,
        json=generate_request
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 生成成功!")
        print(f"\n标题: {result['generated_title']}")
        print(f"参考标准数: {result['reference_count']}")
        print(f"\n证据分类数量: {len(result['审计证据分类与要求'])}")
        
        # 显示第一个证据分类
        if result['审计证据分类与要求']:
            first = result['审计证据分类与要求'][0]
            for level1, level2_dict in first.items():
                print(f"\n一级分类: {level1}")
                for level2, evidences in level2_dict.items():
                    print(f"  二级分类: {level2} ({len(evidences)} 个证据)")
    else:
        print(f"\n✗ 生成失败: {response.status_code}")
        print(response.text)


def example_3_create_standard(token):
    """示例 3: 创建复核标准"""
    print("\n" + "="*60)
    print("示例 3: 手动创建复核标准")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建请求
    create_request = {
        "title": "货币资金内部控制复核标准",
        "audit_conclusion": "被审计单位的货币资金内部控制存在缺陷，现金管理不规范，需要特别关注。",
        "evidence_classification": [
            {
                "货币资金": {
                    "内部控制": [
                        {
                            "证据内容": "现金盘点表",
                            "质量要求": "证据来源于审计师，需要出纳在场，并由出纳签字确认。"
                        },
                        {
                            "证据内容": "内部控制测试工作底稿",
                            "质量要求": "证据来源于审计师，需要记录测试的样本、测试结果和结论。"
                        }
                    ]
                }
            }
        ],
        "category": "货币资金",
        "tags": "内部控制,现金管理",
        "source": "user_created"
    }
    
    print(f"\n创建标准: {create_request['title']}")
    
    response = requests.post(
        f"{BASE_URL}/review-standards/",
        headers=headers,
        json=create_request
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n✓ 创建成功!")
        print(f"标准ID: {result['id']}")
        print(f"已自动创建向量索引")
        return result['id']
    else:
        print(f"\n✗ 创建失败: {response.status_code}")
        print(response.text)
        return None


def example_4_list_standards(token):
    """示例 4: 获取标准列表"""
    print("\n" + "="*60)
    print("示例 4: 获取复核标准列表")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取列表
    params = {
        "page": 1,
        "page_size": 10,
        "category": "银行存款"  # 按分类筛选
    }
    
    response = requests.get(
        f"{BASE_URL}/review-standards/",
        headers=headers,
        params=params
    )
    
    response.raise_for_status()
    result = response.json()
    
    print(f"\n总数: {result['total']}")
    print(f"当前页: {result['page']}/{(result['total'] + result['page_size'] - 1) // result['page_size']}")
    print(f"\n标准列表:")
    
    for idx, item in enumerate(result['items'], 1):
        print(f"\n{idx}. {item['title']}")
        print(f"   ID: {item['id']}")
        print(f"   分类: {item['category']}")
        print(f"   来源: {item['source']}")
        print(f"   使用次数: {item['usage_count']}")


def example_5_get_statistics(token):
    """示例 5: 获取统计信息"""
    print("\n" + "="*60)
    print("示例 5: 获取统计信息")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/review-standards/stats/overview",
        headers=headers
    )
    
    response.raise_for_status()
    result = response.json()
    
    print(f"\n总标准数: {result['total_standards']}")
    
    print("\n按分类统计:")
    for category, count in result['by_category'].items():
        print(f"  {category}: {count}")
    
    print("\n按来源统计:")
    for source, count in result['by_source'].items():
        print(f"  {source}: {count}")
    
    print("\n最常用标准:")
    for idx, item in enumerate(result['most_used'][:3], 1):
        print(f"  {idx}. {item['title']} (使用 {item['usage_count']} 次)")


def example_6_update_standard(token, standard_id):
    """示例 6: 更新标准"""
    print("\n" + "="*60)
    print("示例 6: 更新复核标准")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 更新请求
    update_request = {
        "tags": "内部控制,现金管理,更新测试"
    }
    
    print(f"\n更新标准 ID {standard_id}")
    
    response = requests.put(
        f"{BASE_URL}/review-standards/{standard_id}",
        headers=headers,
        json=update_request
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 更新成功!")
        print(f"新标签: {result['tags']}")
    else:
        print(f"\n✗ 更新失败: {response.status_code}")


def example_7_delete_standard(token, standard_id):
    """示例 7: 删除标准"""
    print("\n" + "="*60)
    print("示例 7: 删除复核标准")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n删除标准 ID {standard_id}")
    
    response = requests.delete(
        f"{BASE_URL}/review-standards/{standard_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        print(f"\n✓ 删除成功!")
    else:
        print(f"\n✗ 删除失败: {response.status_code}")


def main():
    """主函数"""
    print("="*60)
    print("复核标准 API 使用示例")
    print("="*60)
    print(f"\n基础 URL: {BASE_URL}")
    print(f"用户名: {USERNAME}")
    
    try:
        # 登录
        token = login()
        
        # 示例 1: 语义检索
        example_1_semantic_search(token)
        
        # 示例 2: AI 生成（需要 API Key）
        try:
            example_2_generate_standard(token)
        except Exception as e:
            print(f"\n⚠ 跳过 AI 生成示例: {str(e)}")
        
        # 示例 3: 创建标准
        created_id = example_3_create_standard(token)
        
        # 示例 4: 获取列表
        example_4_list_standards(token)
        
        # 示例 5: 统计信息
        example_5_get_statistics(token)
        
        # 如果创建成功，演示更新和删除
        if created_id:
            # 示例 6: 更新标准
            example_6_update_standard(token, created_id)
            
            # 示例 7: 删除标准
            example_7_delete_standard(token, created_id)
        
        print("\n" + "="*60)
        print("所有示例执行完成!")
        print("="*60)
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ API 请求失败: {str(e)}")
        print("\n请确保:")
        print("1. 后端服务正在运行 (python main.py)")
        print("2. 端口配置正确 (默认 8000)")
        print("3. 用户名密码正确")
    except Exception as e:
        print(f"\n✗ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

