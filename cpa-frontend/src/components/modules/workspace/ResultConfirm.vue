<template>
  <!-- 结构化复核结果展示组件 -->
  <div class="result-confirm">
    <!-- 模块头部 -->
    <div class="module-header">
      <div class="module-icon">📊</div>
      <h3>复核结果展示</h3>
      <div class="module-status" :class="reviewResultStore.reviewResult.status">
        {{ getStatusText(reviewResultStore.reviewResult.status) }}
      </div>
      <div class="version-info" v-if="reviewResultStore.reviewResult.version">
        版本: {{ reviewResultStore.reviewResult.version }}
      </div>
      <button class="close-btn" @click="closeModule" title="关闭">✕</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="reviewResultStore.reviewResult.loading" class="loading-container">
      <el-loading text="正在加载复核结果..." />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="reviewResultStore.reviewResult.error" class="error-container">
      <el-alert
        title="加载失败"
        :description="reviewResultStore.reviewResult.error"
        type="error"
        show-icon
        :closable="false"
      >
        <template #default>
          <el-button type="primary" @click="retryLoad">重新加载</el-button>
        </template>
      </el-alert>
    </div>

    <!-- 主要内容区域 -->
    <div v-else-if="reviewResultStore.reviewResult.data" class="module-content">
      <!-- 操作工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button class="text-button" @click="refreshData">
            刷新数据
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button class="text-button success-button" @click="confirmArchive" :loading="archiving">
            {{ archiving ? '正在归档...' : '保存并归档' }}
          </el-button>
        </div>
      </div>

      <!-- 结构化结果展示 - 分层折叠面板 -->
      <el-collapse v-model="activeCollapse" class="result-collapse">


        <!-- 重大事项概述 -->
        <el-collapse-item v-if="reviewData.重大事项概述" name="summary" title="重大事项概述">
          <div class="summary-section">
            <div class="data-row">
              <span class="data-key">概述</span>
              <span class="data-value">{{ reviewData.重大事项概述 }}</span>
            </div>
          </div>
        </el-collapse-item>

        <!-- 审计结论 -->
        <el-collapse-item v-if="reviewData.审计结论" name="conclusion" title="审计结论">
          <div class="conclusion-section">
            <div class="data-row">
              <span class="data-key">结论</span>
              <span class="data-value">{{ reviewData.审计结论 }}</span>
            </div>
          </div>
        </el-collapse-item>

        <!-- 复核结果明细（保持嵌套结构进行渲染） -->
        <el-collapse-item v-if="reviewData.复核结果明细 && reviewData.复核结果明细.length" name="details" title="复核结果明细">
          <div class="details-section">
            <!-- 一级类别组（对象列表） -->
            <div 
              v-for="(group, gIdx) in reviewData.复核结果明细" 
              :key="gIdx" 
              class="detail-group"
            >
              <!-- 顶层类别名称及其子结构（对象：子类别 -> 列表） -->
              <div 
                v-for="(subMap, topName) in group" 
                :key="topName"
                class="detail-card"
              >
                <div class="detail-header">
                  <strong>{{ topName }}</strong>
                </div>
                <!-- 二级子类别：名称 -> 证据项列表 -->
                <div 
                  v-for="(items, subName) in subMap" 
                  :key="topName + '-' + subName"
                  class="detail-content"
                >
                  <div class="data-row">
                    <span class="data-key">子类别</span>
                    <span class="data-value">{{ subName }}</span>
                  </div>

                  <!-- 具体证据项列表 -->
                  <div 
                    v-for="(item, idx) in items" 
                    :key="topName + '-' + subName + '-' + idx"
                    class="detail-item"
                  >
                    <div class="data-row" v-if="item.证据内容">
                      <span class="data-key">证据内容</span>
                      <span class="data-value">{{ item.证据内容 }}</span>
                    </div>

                    <div class="data-row" v-if="item.质量要求">
                      <span class="data-key">质量要求</span>
                      <span class="data-value">{{ item.质量要求 }}</span>
                    </div>



                    <!-- 相关证据与质量评估（数组） -->
                    <div v-if="item.相关证据与质量评估 && item.相关证据与质量评估.length" class="quality-assessment">
                      <span class="data-key">相关证据与质量评估</span>
                      <div class="assessment-list">
                        <div 
                          v-for="(ev, eIdx) in item.相关证据与质量评估" 
                          :key="topName + '-' + subName + '-' + idx + '-ev-' + eIdx"
                          class="assessment-item"
                        >
                          <div class="data-row" v-if="ev.证据">
                            <span class="sub-key">证据</span>
                            <span class="sub-value">{{ ev.证据 }}</span>
                          </div>

                          <div class="location-info" v-if="ev.信息定位">
                            <span class="sub-key">信息定位</span>
                            <el-button 
                              type="primary" 
                              link 
                              class="location-btn"
                              @click="openSpecExcelView(ev.信息定位)"
                            >
                              {{ ev.信息定位 }}
                            </el-button>
                          </div>

                          <div class="assessment-conclusion" v-if="ev.质量评估 && ev.质量评估.结论">
                            <el-tag :type="getAssessmentTagType(ev.质量评估.结论)">
                              {{ ev.质量评估.结论 }}
                            </el-tag>
                          </div>
                          <div class="assessment-reason" v-if="ev.质量评估 && ev.质量评估.理由">
                            <span class="sub-key">理由</span>
                            <span class="sub-value">{{ ev.质量评估.理由 }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-collapse-item>

        <!-- 统计整理概览 -->
        <el-collapse-item name="overview" title="统计整理概览">
          <div class="overview-section">
            <div class="stats-summary">
              <div class="stat-item">
                <span class="stat-label">统计整理</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">证据总数</span>
                <span class="stat-value">{{ reviewData.统计整理.证据总数 }}</span>
              </div>
            </div>
          </div>
        </el-collapse-item>

        <!-- 充分性情况 -->
        <el-collapse-item name="sufficiency" title="充分性情况">
          <div class="sufficiency-section">
            <div class="section-header">
              <h4>充分性情况</h4>
              <el-tag type="warning" v-if="reviewData.统计整理.充分性情况.缺失数量 > 0">
                缺失数量: {{ reviewData.统计整理.充分性情况.缺失数量 }}
              </el-tag>
              <el-tag type="success" v-else>
                无缺失
              </el-tag>
            </div>
            
            <!-- 缺失详情列表 -->
            <div v-if="reviewData.统计整理.充分性情况.缺失详情" class="missing-details">
              <div class="detail-header">
                <strong>缺失详情</strong>
              </div>
              <div 
                v-for="(detail, index) in reviewData.统计整理.充分性情况.缺失详情"
                :key="index"
                class="detail-card"
              >
                <div class="detail-header">
                  <strong>{{ detail.证据内容 }}</strong>
                </div>
                <div class="detail-content">
                  <div class="data-row">
                    <span class="data-key">质量要求</span>
                    <span class="data-value">{{ detail.质量要求 }}</span>
                  </div>
                  <div class="evidence-categories">
                    <span class="data-key">证据类别</span>
                    <div class="category-list">
                      <el-tag 
                        v-for="(category, catIndex) in detail.证据类别"
                        :key="catIndex"
                        size="small"
                        class="category-tag"
                      >
                        {{ category }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-collapse-item>

        <!-- 适当性情况（兼容严谨性字段名） -->
        <el-collapse-item name="appropriateness" title="适当性情况">
          <div class="appropriateness-section">
            <div class="section-header">
              <h4>适当性情况</h4>
              <el-tag type="danger" v-if="appropriatenessStats.count > 0">
                不适当证据数量: {{ appropriatenessStats.count }}
              </el-tag>
              <el-tag type="success" v-else>
                无不适当证据
              </el-tag>
            </div>
            
            <!-- 不适当证据详情 -->
            <div v-if="appropriatenessStats.details && appropriatenessStats.details.length" class="inappropriate-details">
              <div class="detail-header">
                <strong>详情</strong>
              </div>
              <div 
                v-for="(detail, index) in appropriatenessStats.details"
                :key="index"
                class="detail-card inappropriate"
              >
                <div class="detail-header">
                  <strong>{{ detail.证据内容 || detail.证据 || `明细#${index+1}` }}</strong>
                </div>
                
                <div class="detail-content">
                  <!-- 顶层证据（若提供） -->
                  <div class="data-row" v-if="detail.证据">
                    <span class="data-key">证据</span>
                    <span class="data-value">{{ detail.证据 }}</span>
                  </div>

                  <!-- 顶层信息定位（若提供） -->
                  <div class="location-info" v-if="detail.信息定位">
                    <span class="data-key">信息定位</span>
                    <el-button 
                      type="primary" 
                      link 
                      class="location-btn"
                      @click="openSpecExcelView(detail.信息定位)"
                    >
                      {{ detail.信息定位 }}
                    </el-button>
                  </div>

                  <!-- 顶层证据内容与质量要求（若提供） -->
                  <div class="data-row" v-if="detail.证据内容">
                    <span class="data-key">证据内容</span>
                    <span class="data-value">{{ detail.证据内容 }}</span>
                  </div>
                  <div class="data-row" v-if="detail.质量要求">
                    <span class="data-key">质量要求</span>
                    <span class="data-value">{{ detail.质量要求 }}</span>
                  </div>

                  <!-- 相关证据与质量评估（数组） -->
                  <div v-if="detail.相关证据与质量评估 && detail.相关证据与质量评估.length" class="quality-assessment">
                    <span class="data-key">相关证据与质量评估</span>
                    <div class="assessment-list">
                      <div 
                        v-for="(ev, eIdx) in detail.相关证据与质量评估" 
                        :key="index + '-ev-' + eIdx"
                        class="assessment-item"
                      >
                        <div class="data-row" v-if="ev.证据">
                          <span class="sub-key">证据</span>
                          <span class="sub-value">{{ ev.证据 }}</span>
                        </div>

                        <div class="location-info" v-if="ev.信息定位">
                          <span class="sub-key">信息定位</span>
                          <el-button 
                            type="primary" 
                            link 
                            class="location-btn"
                            @click="openSpecExcelView(ev.信息定位)"
                          >
                            {{ ev.信息定位 }}
                          </el-button>
                        </div>

                        <div class="assessment-conclusion" v-if="ev.质量评估 && ev.质量评估.结论">
                          <el-tag :type="getAssessmentTagType(ev.质量评估.结论)">
                            {{ ev.质量评估.结论 }}
                          </el-tag>
                        </div>
                        <div class="assessment-reason" v-if="ev.质量评估 && ev.质量评估.理由">
                          <span class="sub-key">理由</span>
                          <span class="sub-value">{{ ev.质量评估.理由 }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 顶层质量评估（兼容对象或数组） -->
                  <div v-else-if="detail.质量评估" class="quality-assessment">
                    <span class="data-key">质量评估</span>
                    <div class="assessment-list" v-if="Array.isArray(detail.质量评估)">
                      <div 
                        v-for="(assessment, assessIndex) in detail.质量评估"
                        :key="assessIndex"
                        class="assessment-item"
                      >
                        <div class="assessment-conclusion">
                          <el-tag :type="getAssessmentTagType(assessment.结论)">
                            {{ assessment.结论 }}
                          </el-tag>
                        </div>
                        <div class="assessment-reason">
                          <span class="sub-key">理由</span>
                          <span class="sub-value">{{ assessment.理由 }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="assessment-item" v-else>
                      <div class="assessment-conclusion" v-if="detail.质量评估.结论">
                        <el-tag :type="getAssessmentTagType(detail.质量评估.结论)">
                          {{ detail.质量评估.结论 }}
                        </el-tag>
                      </div>
                      <div class="assessment-reason" v-if="detail.质量评估.理由">
                        <span class="sub-key">理由</span>
                        <span class="sub-value">{{ detail.质量评估.理由 }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 证据类别（若后端提供） -->
                  <div class="evidence-categories" v-if="detail.证据类别 && detail.证据类别.length">
                    <span class="data-key">证据类别</span>
                    <div class="category-list">
                      <el-tag 
                        v-for="(category, catIndex) in detail.证据类别"
                        :key="catIndex"
                        size="small"
                        class="category-tag"
                      >
                        {{ category }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-collapse-item>


        <!-- 结论与原因 -->
        <el-collapse-item v-if="reviewData.结论与原因" name="final" title="结论与原因">
          <div class="final-section">
            <div class="data-row" v-if="reviewData.结论与原因.复核结论">
              <span class="data-key">复核结论</span>
              <span class="data-value">{{ reviewData.结论与原因.复核结论 }}</span>
            </div>
            <div class="data-row" v-if="reviewData.结论与原因.业务原因">
              <span class="data-key">业务原因</span>
              <span class="data-value">{{ reviewData.结论与原因.业务原因 }}</span>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>




  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useReviewResultStore } from '@/stores/reviewResult'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  FolderAdd
} from '@element-plus/icons-vue'



export default {
  name: 'ResultConfirm',
  components: {

    Refresh,
    FolderAdd
  },
  props: {
    eventId: {
      type: String,
      required: true
    }
  },
  emits: ['close', 'archived'],
  setup(props, { emit }) {
    // 路由实例
    const router = useRouter()
    // Store实例
    const reviewResultStore = useReviewResultStore()

    // 响应式数据
    const activeCollapse = ref(['overview', 'sufficiency', 'appropriateness'])
    const archiving = ref(false)

    // 监听归档状态
    watch(
      () => reviewResultStore.archiving.isArchiving,
      (newValue) => {
        archiving.value = newValue
      }
    )

    // 计算属性
    const reviewData = computed(() => {
      return reviewResultStore.reviewResult.data || {}
    })

    // 适当性情况映射（仅使用适当性情况字段）
    const appropriatenessStats = computed(() => {
      const stats = reviewData.value?.统计整理 || {}
      const src = stats.适当性情况 || {}
      return {
        count: (src.不适当证据数量 ?? 0),
        details: src.详情 || []
      }
    })

    // 方法定义
    const getStatusText = (status) => {
      const statusMap = {
        'draft': '草稿',
        'archived': '已归档'
      }
      return statusMap[status] || '未知状态'
    }

    const getAssessmentTagType = (conclusion) => {
      const typeMap = {
        '达标': 'success',
        '不达标': 'danger',
        '基本达标': 'warning'
      }
      return typeMap[conclusion] || 'info'
    }



    // 刷新数据
    const refreshData = async () => {
      try {
        await reviewResultStore.loadReviewResult(props.eventId)
        ElMessage.success('数据刷新成功')
      } catch (error) {
        ElMessage.error('数据刷新失败: ' + error.message)
      }
    }

    // 重新加载
    const retryLoad = async () => {
      await refreshData()
    }

    // 确认归档
    const confirmArchive = async () => {
      try {
        archiving.value = true
        const result = await reviewResultStore.saveAndArchive({})
        
        ElMessage.success('复核结果已保存并归档成功！')
        emit('archived', { version: result.version })
      } catch (error) {
        ElMessage.error('归档失败')
      } finally {
        archiving.value = false
      }
    }



    // 关闭模块
    const closeModule = () => {
      emit('close')
    }

    // 打开底稿查看组件（侧边栏信息定位）
    const openSpecExcelView = (locationText) => {
      emit('open-excel-view', { title: '信息定位', location: locationText })
    }

    // 组件挂载时加载数据
    onMounted(async () => {
      try {
        await reviewResultStore.loadReviewResult(props.eventId)
        // loadReviewResult 方法内部已经调用了 loadArchiveVersions()
      } catch (error) {
        console.error('初始化加载失败:', error)
      }
    })



    return {
      // Store
      reviewResultStore,
      
      // 响应式数据
      activeCollapse,
      archiving,
      
      // 计算属性
      reviewData,
      appropriatenessStats,
      
      // 方法
      getStatusText,
      getAssessmentTagType,

      refreshData,
      retryLoad,
      confirmArchive,
      closeModule,
      openSpecExcelView
    }
  }
}
</script>

<style scoped>
/* 主容器样式 */
.result-confirm {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 模块头部样式 */
.module-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0;
}

.module-icon {
  font-size: 20px;
  margin-right: 12px;
}

.module-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  flex: 1;
}

.module-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 12px;
  background: rgba(255, 255, 255, 0.2);
}

.module-status.draft {
  background: rgba(255, 193, 7, 0.2);
}

.module-status.archived {
  background: rgba(40, 167, 69, 0.2);
}

.version-info {
  font-size: 12px;
  margin-right: 12px;
  opacity: 0.9;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 加载和错误状态样式 */
.loading-container,
.error-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* 主要内容区域样式 */
.module-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 工具栏样式 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 6px;
}

.toolbar :deep(.el-button) {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
}

/* 统一按钮样式 */
.toolbar :deep(.text-button),
.toolbar :deep(.success-button) {
  /* 默认状态：白色背景，灰色边框和文字 */
  border: 2px solid #d1d5db;
  background: #ffffff;
  color: #6b7280;
  border-radius: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toolbar :deep(.text-button:hover),
.toolbar :deep(.success-button:hover) {
  /* 悬停状态：蓝色边框和文字，浅蓝色背景 */
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.toolbar :deep(.text-button:active),
.toolbar :deep(.success-button:active) {
  /* 点击状态：深绿色背景和边框 */
  border-color: #059669;
  background: #059669;
  color: #ffffff;
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 折叠面板样式 */
.result-collapse {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.result-collapse :deep(.el-collapse-item__header) {
  background: #f8f9fa;
  font-weight: 600;
  font-size: 16px;
  padding: 0 20px;
}

.result-collapse :deep(.el-collapse-item__content) {
  padding: 20px;
}

/* 概览部分样式 */
.overview-section {
  background: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.stats-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 30px;
}

.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-label {
  font-weight: 500;
  color: #606266;
  font-size: 15px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  margin-left: auto;
}

/* 部分头部样式 */
.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-header h4::before {
  content: '';
  width: 4px;
  height: 16px;
  background: #409eff;
  border-radius: 2px;
}

/* 详情卡片样式 */
.detail-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  background: #fff;
  transition: all 0.3s;
  position: relative;
}

.detail-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.detail-card.inappropriate {
  border-left: 4px solid #67C23A;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.detail-content {
  color: #606266;
  line-height: 1.8;
  font-size: 14px;
}

.detail-content strong {
  color: #303133;
  margin-right: 8px;
}

.detail-content p {
  margin: 8px 0;
}

/* 数据行样式 - 键值对高亮 */
.data-row {
  display: flex;
  align-items: flex-start;
  margin: 12px 0;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 8px;
  border-left: 4px solid #64748b;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.data-row:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateX(3px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.data-key {
  display: inline-block;
  min-width: 85px;
  font-weight: 600;
  color: #475569;
  background: linear-gradient(135deg, #64748b, #475569);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-right: 12px;
  font-size: 14px;
  flex-shrink: 0;
}

.data-value {
  flex: 1;
  color: #334155;
  font-weight: 500;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  border: 1px solid rgba(100, 116, 139, 0.2);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 子级键值对样式 */
.sub-key {
  display: inline-block;
  min-width: 65px;
  font-weight: 500;
  color: #64748b;
  background: linear-gradient(135deg, #64748b, #475569);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-right: 10px;
  font-size: 13px;
}

.sub-value {
  color: #475569;
  font-weight: 400;
  padding: 2px 8px;
  background: rgba(100, 116, 139, 0.08);
  border-radius: 4px;
  border: 1px solid rgba(100, 116, 139, 0.15);
}

/* 位置信息样式 */
.location-info {
  margin: 12px 0;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-left: 4px solid #64748b;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.location-info:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateX(3px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.location-info .data-key {
  color: #475569;
  background: linear-gradient(135deg, #64748b, #475569);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.location-btn {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  padding: 6px 12px;
  height: auto;
  line-height: 1.5;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 6px;
  border: 1px solid rgba(100, 116, 139, 0.25);
  color: #475569 !important;
  transition: all 0.2s ease;
}

.location-btn:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(100, 116, 139, 0.4);
  transform: translateY(-1px);
}

/* 质量评估样式 */
.quality-assessment {
  margin: 12px 0;
  padding: 14px 18px;
  background: linear-gradient(135deg, #fef8f8 0%, #f1f5f9 100%);
  border-left: 4px solid #94a3b8;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.quality-assessment:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  transform: translateX(3px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.quality-assessment .data-key {
  color: #475569;
  background: linear-gradient(135deg, #64748b, #475569);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: block;
  margin-bottom: 10px;
}

.assessment-list {
  margin-top: 10px;
}

.assessment-item {
  margin: 10px 0;
  padding: 14px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.assessment-item:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(148, 163, 184, 0.35);
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.assessment-conclusion {
  margin-bottom: 8px;
}

.assessment-reason {
  font-size: 14px;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

/* 证据类别样式 */
.evidence-categories {
  margin: 12px 0;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-left: 4px solid #64748b;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.evidence-categories:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  transform: translateX(3px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.evidence-categories .data-key {
  color: #475569;
  background: linear-gradient(135deg, #64748b, #475569);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: block;
  margin-bottom: 10px;
}

.category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.category-tag {
  margin: 0;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(100, 116, 139, 0.25);
  transition: all 0.3s ease;
  color: #475569;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.category-tag:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(100, 116, 139, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}



/* 归档对话框样式 */
.archive-content {
  padding: 16px 0;
}

.archive-summary {
  margin-bottom: 20px;
}

.archive-summary h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.archive-summary p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}

/* 版本历史样式 */
.version-history {
  max-height: 400px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .module-content {
    padding: 12px;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 12px;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }
  
  .stats-summary {
    flex-direction: column;
    gap: 12px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>