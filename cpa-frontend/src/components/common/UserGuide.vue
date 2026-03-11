<template>
  <!-- 用户操作指引组件 - 为首次使用的用户提供分步导览 -->
  <div class="user-guide-overlay" v-if="isVisible">
    <div class="guide-backdrop" @click="closeGuide"></div>
    
    <!-- 指引步骤内容 -->
    <div class="guide-step" 
         :style="stepPosition" 
         v-if="currentStep">
      <div class="guide-content">
        <div class="guide-header">
          <h4>{{ currentStep.title }}</h4>
          <span class="step-counter">{{ currentStepIndex + 1 }} / {{ steps.length }}</span>
        </div>
        
        <div class="guide-body">
          <p>{{ currentStep.description }}</p>
          <div v-if="currentStep.tips" class="guide-tips">
            <h5>💡 小贴士：</h5>
            <ul>
              <li v-for="tip in currentStep.tips" :key="tip">{{ tip }}</li>
            </ul>
          </div>
        </div>
        
        <div class="guide-actions">
          <button v-if="currentStepIndex > 0" 
                  @click="previousStep" 
                  class="btn-secondary">
            上一步
          </button>
          
          <button v-if="currentStepIndex < steps.length - 1" 
                  @click="nextStep" 
                  class="btn-primary">
            下一步
          </button>
          
          <button v-else 
                  @click="finishGuide" 
                  class="btn-primary">
            完成导览
          </button>
          
          <button @click="skipGuide" class="btn-text">跳过导览</button>
        </div>
      </div>
      
      <!-- 指向目标元素的箭头 -->
      <div class="guide-arrow" :class="currentStep.arrowDirection"></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'UserGuide',
  props: {
    // 指引步骤配置
    steps: {
      type: Array,
      required: true,
      default: () => []
    },
    // 是否自动开始
    autoStart: {
      type: Boolean,
      default: false
    },
    // 存储键名（用于记住用户是否已看过指引）
    storageKey: {
      type: String,
      default: 'user-guide-completed'
    }
  },
  emits: ['guide-started', 'guide-completed', 'guide-skipped', 'step-changed'],
  setup(props, { emit }) {
    // ===== 响应式数据 =====
    const isVisible = ref(false)
    const currentStepIndex = ref(0)
    
    // ===== 计算属性 =====
    const currentStep = computed(() => {
      return props.steps[currentStepIndex.value] || null
    })
    
    // 计算指引步骤的位置
    const stepPosition = computed(() => {
      if (!currentStep.value || !currentStep.value.target) {
        return {
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)'
        }
      }
      
      const targetElement = document.querySelector(currentStep.value.target)
      if (!targetElement) {
        return {
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)'
        }
      }
      
      const rect = targetElement.getBoundingClientRect()
      const position = currentStep.value.position || 'bottom'
      
      switch (position) {
        case 'top':
          return {
            top: `${rect.top - 20}px`,
            left: `${rect.left + rect.width / 2}px`,
            transform: 'translate(-50%, -100%)'
          }
        case 'bottom':
          return {
            top: `${rect.bottom + 20}px`,
            left: `${rect.left + rect.width / 2}px`,
            transform: 'translate(-50%, 0)'
          }
        case 'left':
          return {
            top: `${rect.top + rect.height / 2}px`,
            left: `${rect.left - 20}px`,
            transform: 'translate(-100%, -50%)'
          }
        case 'right':
          return {
            top: `${rect.top + rect.height / 2}px`,
            left: `${rect.right + 20}px`,
            transform: 'translate(0, -50%)'
          }
        default:
          return {
            top: `${rect.bottom + 20}px`,
            left: `${rect.left + rect.width / 2}px`,
            transform: 'translate(-50%, 0)'
          }
      }
    })
    
    // ===== 方法 =====
    
    // 开始指引
    const startGuide = () => {
      // 检查用户是否已完成过指引
      if (localStorage.getItem(props.storageKey)) {
        return false
      }
      
      isVisible.value = true
      currentStepIndex.value = 0
      highlightTargetElement()
      emit('guide-started')
      return true
    }
    
    // 下一步
    const nextStep = () => {
      if (currentStepIndex.value < props.steps.length - 1) {
        currentStepIndex.value++
        highlightTargetElement()
        emit('step-changed', currentStepIndex.value)
      }
    }
    
    // 上一步
    const previousStep = () => {
      if (currentStepIndex.value > 0) {
        currentStepIndex.value--
        highlightTargetElement()
        emit('step-changed', currentStepIndex.value)
      }
    }
    
    // 完成指引
    const finishGuide = () => {
      closeGuide()
      localStorage.setItem(props.storageKey, 'true')
      emit('guide-completed')
    }
    
    // 跳过指引
    const skipGuide = () => {
      closeGuide()
      localStorage.setItem(props.storageKey, 'true')
      emit('guide-skipped')
    }
    
    // 关闭指引
    const closeGuide = () => {
      isVisible.value = false
      removeHighlight()
    }
    
    // 高亮目标元素
    const highlightTargetElement = () => {
      // 移除之前的高亮
      removeHighlight()
      
      if (currentStep.value && currentStep.value.target) {
        const targetElement = document.querySelector(currentStep.value.target)
        if (targetElement) {
          targetElement.classList.add('guide-highlight')
          targetElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          })
        }
      }
    }
    
    // 移除高亮
    const removeHighlight = () => {
      const highlightedElements = document.querySelectorAll('.guide-highlight')
      highlightedElements.forEach(el => {
        el.classList.remove('guide-highlight')
      })
    }
    
    // 键盘事件处理
    const handleKeydown = (event) => {
      if (!isVisible.value) return
      
      switch (event.key) {
        case 'Escape':
          closeGuide()
          break
        case 'ArrowRight':
        case 'ArrowDown':
          nextStep()
          break
        case 'ArrowLeft':
        case 'ArrowUp':
          previousStep()
          break
      }
    }
    
    // ===== 生命周期 =====
    onMounted(() => {
      // 添加键盘事件监听
      document.addEventListener('keydown', handleKeydown)
      
      // 自动开始指引
      if (props.autoStart) {
        setTimeout(() => {
          startGuide()
        }, 1000) // 延迟1秒开始，确保页面加载完成
      }
    })
    
    onUnmounted(() => {
      // 移除事件监听
      document.removeEventListener('keydown', handleKeydown)
      removeHighlight()
    })
    
    // ===== 暴露给父组件的方法 =====
    return {
      isVisible,
      currentStepIndex,
      currentStep,
      stepPosition,
      startGuide,
      nextStep,
      previousStep,
      finishGuide,
      skipGuide,
      closeGuide
    }
  }
}
</script>

<style scoped>
/* 指引遮罩层 */
.user-guide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
  pointer-events: none;
}

/* 背景遮罩 */
.guide-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  pointer-events: all;
}

/* 指引步骤容器 */
.guide-step {
  position: absolute;
  max-width: 320px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  pointer-events: all;
  z-index: 10000;
}

/* 指引内容 */
.guide-content {
  padding: 20px;
}

/* 指引头部 */
.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.guide-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.step-counter {
  font-size: 12px;
  color: #7f8c8d;
  background: #ecf0f1;
  padding: 2px 8px;
  border-radius: 12px;
}

/* 指引主体 */
.guide-body {
  margin-bottom: 16px;
}

.guide-body p {
  margin: 0 0 12px 0;
  font-size: 14px;
  line-height: 1.5;
  color: #34495e;
}

/* 小贴士 */
.guide-tips {
  background: #f8f9fa;
  border-left: 3px solid #3498db;
  padding: 12px;
  border-radius: 4px;
}

.guide-tips h5 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #2980b9;
}

.guide-tips ul {
  margin: 0;
  padding-left: 16px;
}

.guide-tips li {
  font-size: 12px;
  color: #5a6c7d;
  margin-bottom: 4px;
}

/* 操作按钮 */
.guide-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-primary {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-text {
  background: none;
  border: none;
  color: #7f8c8d;
  font-size: 12px;
  cursor: pointer;
  margin-left: auto;
}

.btn-text:hover {
  color: #5a6c7d;
}

/* 指向箭头 */
.guide-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border: 8px solid transparent;
}

.guide-arrow.top {
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: white;
}

.guide-arrow.bottom {
  top: -16px;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: white;
}

.guide-arrow.left {
  right: -16px;
  top: 50%;
  transform: translateY(-50%);
  border-left-color: white;
}

.guide-arrow.right {
  left: -16px;
  top: 50%;
  transform: translateY(-50%);
  border-right-color: white;
}
</style>

<style>
/* 全局样式 - 高亮目标元素 */
.guide-highlight {
  position: relative;
  z-index: 9998 !important;
  box-shadow: 0 0 0 4px rgba(52, 152, 219, 0.5) !important;
  border-radius: 4px !important;
  transition: all 0.3s ease !important;
}
</style>