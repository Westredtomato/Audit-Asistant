<!-- 
  重大判断管理页面组件
  简化版本：仅保留基本页面结构，后续重新设计功能
-->
<template>
  <div class="major-judgments">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-left">
        <!-- 返回按钮 -->
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回
        </button>
        <h1>重大判断管理</h1>
      </div>
    </div>

    <!-- 页面内容 -->
    <div class="content">
      <div class="placeholder">
        <h2>重大判断功能开发中</h2>
        <p>此页面功能正在重新设计和开发中，敬请期待。</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'MajorJudgments',
  setup() {
    const router = useRouter()
    
    // 返回事件管理主页
    const goBack = () => {
      router.push('/events')
    }
    
    return {
      goBack
    }
  }
}
</script>

<style scoped>
/* 主容器 */
.major-judgments {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

/* 头部左侧 */
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 返回按钮 */
.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #e0e0e0;
}

/* 页面标题 */
.header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

/* 页面内容 */
.content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

/* 占位符 */
.placeholder {
  text-align: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #ddd;
}

.placeholder h2 {
  font-size: 24px;
  color: #666;
  margin: 0 0 16px 0;
}

.placeholder p {
  font-size: 16px;
  color: #888;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .major-judgments {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .placeholder {
    padding: 40px 16px;
  }
  
  .placeholder h2 {
    font-size: 20px;
  }
  
  .placeholder p {
    font-size: 14px;
  }
}
</style>