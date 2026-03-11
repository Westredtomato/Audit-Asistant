<template>
  <div class="financial-statements">
    <h1>财务报表</h1>
    <p class="description">财务报表查看与分析功能正在开发中...</p>
    
    <!-- 功能占位区域 -->
    <div class="placeholder-content">
      <div class="placeholder-icon">💰</div>
      <h3>功能开发中</h3>
      <p>此页面将用于查看和分析财务报表数据</p>
      <ul class="feature-list">
        <li>财务报表导入与解析</li>
        <li>报表数据可视化</li>
        <li>财务指标分析</li>
        <li>报表对比与趋势分析</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FinancialStatements',
  /**
   * 财务报表组件
   * 用于查看和分析财务报表数据
   * 当前为占位页面，待后续开发具体功能
   */
  data() {
    return {
      // 组件数据将在后续开发中添加
    }
  },
  methods: {
    // 组件方法将在后续开发中添加
  }
}
</script>

<style scoped>
/* 财务报表页面主容器样式 */
.financial-statements {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面描述文字样式 */
.description {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

/* 占位内容区域样式 */
.placeholder-content {
  text-align: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #dee2e6;
}

/* 占位图标样式 */
.placeholder-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.6;
}

/* 占位标题样式 */
.placeholder-content h3 {
  color: #495057;
  margin-bottom: 15px;
  font-size: 24px;
}

/* 占位描述样式 */
.placeholder-content p {
  color: #6c757d;
  margin-bottom: 25px;
  font-size: 16px;
}

/* 功能列表样式 */
.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: inline-block;
  text-align: left;
}

/* 功能列表项样式 */
.feature-list li {
  color: #495057;
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
  font-size: 14px;
}

/* 功能列表项前缀图标 */
.feature-list li::before {
  content: '•';
  color: #ffc107;
  position: absolute;
  left: 0;
  font-weight: bold;
}

/* 响应式设计 - 平板设备 */
@media (max-width: 768px) {
  .financial-statements {
    padding: 15px;
  }
  
  .placeholder-content {
    padding: 40px 15px;
  }
  
  .placeholder-icon {
    font-size: 48px;
  }
  
  .placeholder-content h3 {
    font-size: 20px;
  }
}

/* 响应式设计 - 手机设备 */
@media (max-width: 480px) {
  .financial-statements {
    padding: 10px;
  }
  
  .placeholder-content {
    padding: 30px 10px;
  }
  
  .placeholder-icon {
    font-size: 40px;
  }
  
  .placeholder-content h3 {
    font-size: 18px;
  }
  
  .placeholder-content p {
    font-size: 14px;
  }
}
</style>