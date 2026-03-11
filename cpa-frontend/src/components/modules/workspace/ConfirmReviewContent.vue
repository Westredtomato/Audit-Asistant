<template>
  <div class="confirm-review-content">
    <div class="content-display">
      {{ showedContent }}
    </div>
    <div class="action-buttons">
      <button class="btn-secondary" @click="handleCancel">
        <span class="btn-text">取消</span>
      </button>
      <button class="btn-primary" @click="handleConfirm">
        <span class="btn-text">确认</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmReviewContent',
  props: {
    showedContent: {
      type: String,
      default: ''
    },
    reviewContent: {
      type: String,
      default: ''
    }
  },
  emits: ['confirm-review-content', 'cancel-review-content'],
  setup(props, { emit }) {
    /**
     * 处理确认操作
     */
    const handleConfirm = () => {
      emit('confirm-review-content', props.reviewContent)
    }
    
    /**
     * 处理取消操作
     */
    const handleCancel = () => {
      emit('cancel-review-content')
    }
    
    return {
      handleConfirm,
      handleCancel
    }
  }
}
</script>

<style scoped>
.confirm-review-content {
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  max-width: 800px;
  margin: 0 auto;
}

.confirm-review-content h3 {
  margin: 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.content-display {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #1a1a1a;
  font-size: 16px;
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 24px;
  font-weight: 500;
}

.content-display strong,
.content-display b {
  color: #2d3748;
  font-weight: 700;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin: 0;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #e1e8ed;
}

.btn-secondary:hover {
  background: #e3f2fd;
  border-color: #667eea;
}

.btn-text {
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .confirm-review-content {
    padding: 16px;
  }
  
  .content-display {
    padding: 16px;
    font-size: 14px;
  }
  
  .action-buttons {
    flex-direction: row;
    width: 100%;
    justify-content: flex-end;
  }
  
  .btn-primary,
  .btn-secondary {
    width: auto;
    justify-content: center;
    padding: 10px 20px;
  }
}
</style>