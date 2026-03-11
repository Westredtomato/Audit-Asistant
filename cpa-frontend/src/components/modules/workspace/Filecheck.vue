<template>
  <div class="filecheck">
    <!-- 生成进度：水平长条布局 -->
    <div v-if="generating" class="progress-horizontal">
      <div class="left-block">
        <div class="progress-title">正在生成复核标准...</div>
      </div>
      <div class="right-block">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="progress-text">{{ progress }}%</div>
      </div>
    </div>

    <!-- 生成完成：长条水平布局，左边文件标题，右边查看按钮 -->
    <div v-else class="filecheck-bar">
      <div class="bar-left">
        <div class="file-icon">📄</div>
        <div class="file-title">复核标准文件</div>
      </div>
      <div class="bar-right">
        <button class="view-btn" @click="openStandard">查看</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onUnmounted, watch } from "vue";
//复核标准生成由父组件通过axios调用后端接口。

export default {
  name: "FileCheck",
  emits: ["add-message", "open-standard", "standard-generated"],
  props: {
    userInput: { type: String, required: true },
    // 当父组件检测到后端已返回复核标准时，置为true以将进度推至100%
    standardReady: { type: Boolean, default: false },
  },
  setup(props, { emit }) {
    const generating = ref(true);
    const generated = ref(false);
    const progress = ref(0);
    const standardData = ref(null);
    let timer = null;

    // 展示简易的伪进度，仅用于视觉占位，父组件完成生成后自行提示并打开侧边栏
    timer = setInterval(() => {
      if (progress.value < 95) {
        progress.value += 5;
      } else {
        // 达到95%后保持进度，等待后端返回标准后再推至100%
        clearInterval(timer);
      }
    }, 1500); //毫秒

    // 监听父组件传入的standardReady，置为true时将进度推到100%，并结束生成状态
    const finalizeProgress = () => {
      if (timer) {
        clearInterval(timer);
      }
      progress.value = 100;
      generating.value = false;
      generated.value = true;
    };

    // 如果初始就已准备好，直接完成
    if (props.standardReady) {
      finalizeProgress();
    }

    watch(
      () => props.standardReady,
      (newVal) => {
        if (newVal) {
          finalizeProgress();
        }
      }
    );

    const openStandard = () => {
      emit("open-standard", { title: "复核标准" });
    };

    // 清理定时器避免内存泄漏
    onUnmounted(() => {
      if (timer) {
        clearInterval(timer);
      }
    });

    return {
      generating,
      generated,
      progress,
      openStandard,
    };
  },
};
</script>

<style scoped>
.filecheck {
  padding: 12px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
/* 水平长条进度样式 */
.progress-horizontal {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}
.left-block {
  display: flex;
  align-items: center;
  gap: 10px;
}
.progress-title {
  font-size: 14px;
  color: #333;
}
.right-block {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 220px;
}
.progress-bar {
  flex: 1;
  height: 8px;
  background: #eee;
  border-radius: 6px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #0b6bcb;
  transition: width 0.2s ease;
}
.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 40px;
  text-align: right;
}

/* 生成完成后的水平长条 */
.filecheck-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  background: #f1fff5;
  border: 1px solid #c9f7d9;
  border-radius: 8px;
}
.bar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.file-icon {
  font-size: 18px;
}
.file-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}
.bar-right {
  display: flex;
  align-items: center;
}
.view-btn {
  background: #00b894;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
}
.view-btn:hover {
  background: #019875;
}
</style>
