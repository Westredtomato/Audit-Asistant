<template>
  <div class="auto-save-draft">
    <!-- 自动保存状态指示器 -->
    <div class="save-indicator" :class="saveStatus">
      <div class="indicator-content">
        <div class="save-icon">
          <span v-if="saveStatus === 'saving'">💾</span>
          <span v-else-if="saveStatus === 'saved'">✅</span>
          <span v-else-if="saveStatus === 'error'">❌</span>
          <span v-else>📝</span>
        </div>
        <div class="save-text">
          <span v-if="saveStatus === 'saving'">正在保存...</span>
          <span v-else-if="saveStatus === 'saved'">已保存 {{ formatTime(lastSaveTime) }}</span>
          <span v-else-if="saveStatus === 'error'">保存失败</span>
          <span v-else>未保存</span>
        </div>
      </div>
      
      <!-- 手动保存按钮 -->
      <button 
        v-if="saveStatus !== 'saving'"
        @click="manualSave"
        class="manual-save-btn"
        :disabled="saveStatus === 'saved' && !hasUnsavedChanges"
      >
        立即保存
      </button>
    </div>
    
    <!-- 草稿历史记录 -->
    <div v-if="showHistory" class="draft-history">
      <div class="history-header">
        <h4>草稿历史</h4>
        <button @click="showHistory = false" class="close-history">×</button>
      </div>
      
      <div class="history-list">
        <div 
          v-for="draft in draftHistory" 
          :key="draft.id"
          class="history-item"
          @click="loadDraft(draft)"
        >
          <div class="draft-info">
            <div class="draft-title">{{ draft.title || '未命名草稿' }}</div>
            <div class="draft-time">{{ formatTime(draft.saveTime) }}</div>
          </div>
          <div class="draft-actions">
            <button @click.stop="deleteDraft(draft.id)" class="delete-btn">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'AutoSaveDraft',
  props: {
    // 要保存的数据
    data: {
      type: Object,
      required: true
    },
    // 保存间隔（毫秒）
    saveInterval: {
      type: Number,
      default: 30000 // 30秒
    },
    // 草稿标识符
    draftKey: {
      type: String,
      required: true
    },
    // 是否启用自动保存
    autoSave: {
      type: Boolean,
      default: true
    }
  },
  emits: ['draft-saved', 'draft-loaded', 'save-error'],
  setup(props, { emit }) {
    // ===== 响应式数据 =====
    const saveStatus = ref('idle') // idle, saving, saved, error
    const lastSaveTime = ref(null)
    const hasUnsavedChanges = ref(false)
    const showHistory = ref(false)
    const draftHistory = ref([])
    const autoSaveTimer = ref(null)
    const lastDataSnapshot = ref(null)
    
    // ===== 计算属性 =====
    const storageKey = computed(() => `draft_${props.draftKey}`)
    const historyKey = computed(() => `draft_history_${props.draftKey}`)
    
    // ===== 工具方法 =====
    // 格式化时间显示
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const now = new Date()
      const time = new Date(timestamp)
      const diff = now - time
      
      if (diff < 60000) { // 1分钟内
        return '刚刚'
      } else if (diff < 3600000) { // 1小时内
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) { // 24小时内
        return `${Math.floor(diff / 3600000)}小时前`
      } else {
        return time.toLocaleDateString() + ' ' + time.toLocaleTimeString()
      }
    }
    
    // 检查数据是否有变化
    const hasDataChanged = () => {
      const currentData = JSON.stringify(props.data)
      const lastData = lastDataSnapshot.value
      return currentData !== lastData
    }
    
    // ===== 保存相关方法 =====
    // 保存草稿到本地存储
    const saveDraft = async () => {
      if (saveStatus.value === 'saving') return
      
      try {
        saveStatus.value = 'saving'
        
        const draftData = {
          id: Date.now(),
          data: props.data,
          saveTime: new Date().toISOString(),
          title: generateDraftTitle(props.data),
          version: '1.0'
        }
        
        // 保存到本地存储
        localStorage.setItem(storageKey.value, JSON.stringify(draftData))
        
        // 更新历史记录
        updateDraftHistory(draftData)
        
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 500))
        
        saveStatus.value = 'saved'
        lastSaveTime.value = draftData.saveTime
        hasUnsavedChanges.value = false
        lastDataSnapshot.value = JSON.stringify(props.data)
        
        emit('draft-saved', draftData)
        
      } catch (error) {
        console.error('保存草稿失败:', error)
        saveStatus.value = 'error'
        emit('save-error', error)
        ElMessage.error('草稿保存失败，请稍后重试')
      }
    }
    
    // 手动保存
    const manualSave = () => {
      saveDraft()
    }
    
    // 生成草稿标题
    const generateDraftTitle = (data) => {
      if (data.projectName) {
        return `${data.projectName} - 复核草稿`
      } else if (data.eventName) {
        return `${data.eventName} - 事项草稿`
      } else {
        return `工作草稿 - ${new Date().toLocaleString()}`
      }
    }
    
    // 更新草稿历史记录
    const updateDraftHistory = (draftData) => {
      let history = []
      try {
        const stored = localStorage.getItem(historyKey.value)
        if (stored) {
          history = JSON.parse(stored)
        }
      } catch (error) {
        console.error('读取草稿历史失败:', error)
      }
      
      // 添加新草稿到历史记录
      history.unshift(draftData)
      
      // 限制历史记录数量（最多保留10个）
      if (history.length > 10) {
        history = history.slice(0, 10)
      }
      
      localStorage.setItem(historyKey.value, JSON.stringify(history))
      draftHistory.value = history
    }
    
    // ===== 加载相关方法 =====
    // 加载草稿
    const loadDraft = (draft) => {
      try {
        emit('draft-loaded', draft.data)
        ElMessage.success('草稿加载成功')
        showHistory.value = false
      } catch (error) {
        console.error('加载草稿失败:', error)
        ElMessage.error('草稿加载失败')
      }
    }
    
    // 删除草稿
    const deleteDraft = (draftId) => {
      try {
        const history = draftHistory.value.filter(draft => draft.id !== draftId)
        localStorage.setItem(historyKey.value, JSON.stringify(history))
        draftHistory.value = history
        ElMessage.success('草稿删除成功')
      } catch (error) {
        console.error('删除草稿失败:', error)
        ElMessage.error('草稿删除失败')
      }
    }
    
    // 加载草稿历史
    const loadDraftHistory = () => {
      try {
        const stored = localStorage.getItem(historyKey.value)
        if (stored) {
          draftHistory.value = JSON.parse(stored)
        }
      } catch (error) {
        console.error('加载草稿历史失败:', error)
      }
    }
    
    // ===== 自动保存逻辑 =====
    const startAutoSave = () => {
      if (!props.autoSave) return
      
      autoSaveTimer.value = setInterval(() => {
        if (hasDataChanged()) {
          hasUnsavedChanges.value = true
          saveDraft()
        }
      }, props.saveInterval)
    }
    
    const stopAutoSave = () => {
      if (autoSaveTimer.value) {
        clearInterval(autoSaveTimer.value)
        autoSaveTimer.value = null
      }
    }
    
    // ===== 监听器 =====
    // 监听数据变化
    watch(
      () => props.data,
      () => {
        if (hasDataChanged()) {
          hasUnsavedChanges.value = true
          saveStatus.value = 'idle'
        }
      },
      { deep: true }
    )
    
    // 监听自动保存开关
    watch(
      () => props.autoSave,
      (newValue) => {
        if (newValue) {
          startAutoSave()
        } else {
          stopAutoSave()
        }
      }
    )
    
    // ===== 生命周期 =====
    onMounted(() => {
      loadDraftHistory()
      lastDataSnapshot.value = JSON.stringify(props.data)
      startAutoSave()
    })
    
    onUnmounted(() => {
      stopAutoSave()
    })
    
    // ===== 暴露给模板 =====
    return {
      saveStatus,
      lastSaveTime,
      hasUnsavedChanges,
      showHistory,
      draftHistory,
      formatTime,
      manualSave,
      loadDraft,
      deleteDraft
    }
  }
}
</script>

<style scoped>
.auto-save-draft {
  position: relative;
}

.save-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  font-size: 12px;
  transition: all 0.3s ease;
}

.save-indicator.saving {
  background: #fff3cd;
  border-color: #ffc107;
}

.save-indicator.saved {
  background: #d4edda;
  border-color: #28a745;
}

.save-indicator.error {
  background: #f8d7da;
  border-color: #dc3545;
}

.indicator-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.save-icon {
  font-size: 14px;
}

.save-text {
  color: #666;
  font-size: 12px;
}

.manual-save-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.2s;
}

.manual-save-btn:hover {
  background: #0056b3;
}

.manual-save-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.draft-history {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.history-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.close-history {
  background: none;
  border: none;
  font-size: 18px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f3f4;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: #f8f9fa;
}

.draft-info {
  flex: 1;
}

.draft-title {
  font-size: 13px;
  color: #333;
  margin-bottom: 4px;
}

.draft-time {
  font-size: 11px;
  color: #666;
}

.draft-actions {
  display: flex;
  gap: 8px;
}

.delete-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.2s;
}

.delete-btn:hover {
  background: #c82333;
}
</style>