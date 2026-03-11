<template>
  <div class="document-view">
    <h1>文档管理</h1>
    <p class="description">选择您需要管理的文档类型</p>
    
    <!-- 功能入口列表 -->
    <div class="function-menu">
      <div class="menu-item" @click="navigateToAuditPapers">
        <div class="menu-icon">
          <i class="icon-audit-papers">📋</i>
        </div>
        <div class="menu-content">
          <h3>审计底稿</h3>
          <p>管理和查看审计工作底稿文档</p>
        </div>
        <div class="menu-arrow">→</div>
      </div>
      
      <div class="menu-item" @click="navigateToAuditReport">
        <div class="menu-icon">
          <i class="icon-audit-report">📊</i>
        </div>
        <div class="menu-content">
          <h3>审计报告</h3>
          <p>生成和管理审计报告文档</p>
        </div>
        <div class="menu-arrow">→</div>
      </div>
      
      <div class="menu-item" @click="navigateToFinancialStatements">
        <div class="menu-icon">
          <i class="icon-financial">💰</i>
        </div>
        <div class="menu-content">
          <h3>财务报表</h3>
          <p>查看和分析财务报表数据</p>
        </div>
        <div class="menu-arrow">→</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DocumentView',
  methods: {
    /**
     * 导航到审计底稿页面
     * 点击审计底稿功能入口时触发
     */
    navigateToAuditPapers() {
      this.$router.push('/document/audit-papers')
    },
    
    /**
     * 导航到审计报告页面
     * 点击审计报告功能入口时触发
     */
    navigateToAuditReport() {
      this.$router.push('/document/audit-report')
    },
    
    /**
     * 导航到财务报表页面
     * 点击财务报表功能入口时触发
     */
    navigateToFinancialStatements() {
      this.$router.push('/document/financial-statements')
    }
  }
}
</script>

<style scoped>
/* 文档管理页面主容器样式 */
.document-view {
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

/* 功能菜单容器样式 */
.function-menu {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 菜单项样式 */
.menu-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 菜单项悬停效果 */
.menu-item:hover {
  background: #f8f9fa;
  border-color: #007bff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

/* 菜单图标样式 */
.menu-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f8ff;
  border-radius: 50%;
  margin-right: 20px;
  font-size: 24px;
}

/* 菜单内容区域样式 */
.menu-content {
  flex: 1;
}

/* 菜单标题样式 */
.menu-content h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

/* 菜单描述样式 */
.menu-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

/* 菜单箭头样式 */
.menu-arrow {
  font-size: 20px;
  color: #007bff;
  font-weight: bold;
  margin-left: 20px;
}

/* 响应式设计 - 平板设备 */
@media (max-width: 768px) {
  .document-view {
    padding: 15px;
  }
  
  .menu-item {
    padding: 15px;
  }
  
  .menu-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
    margin-right: 15px;
  }
  
  .menu-content h3 {
    font-size: 16px;
  }
}

/* 响应式设计 - 手机设备 */
@media (max-width: 480px) {
  .document-view {
    padding: 10px;
  }
  
  .menu-item {
    padding: 12px;
  }
  
  .menu-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
    margin-right: 12px;
  }
  
  .menu-content h3 {
    font-size: 15px;
  }
  
  .menu-content p {
    font-size: 13px;
  }
}
</style>