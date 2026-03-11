<template>
  <transition name="slide">
    <div v-if="visible" class="sidebar" :style="{ width: width + 'px', top: top + 'px', height: height + 'px' }">
      <div class="resize-handle" @mousedown="startResize" title="拖拽调整宽度"></div>
      <div class="sidebar-header">
        <div class="title">{{ title || '复核标准' }}</div>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      <div class="sidebar-content">
        <component v-if="component" :is="component" v-bind="componentProps || {}" />
        <!-- 保持原有 JSON / 文本展示逻辑作为回退 -->
        <div v-else-if="isJson" class="json-view" v-html="kvHtml"></div>
        <div v-else class="text-view">{{ content }}</div>
      </div>
    </div>
  </transition>
</template>

<script>
import { computed, ref, onBeforeUnmount, onMounted, watch } from 'vue'
export default {
  name: 'ReviewStandardSidebar',
  emits: ['close'],
  props: {
    visible: { type: Boolean, default: false },
    title: { type: String, default: '复核标准' },
    content: { type: [Object, String], required: false, default: '' },
    component: { type: [Object, Function, String], default: null },
    componentProps: { type: Object, default: () => ({}) },
    initialWidth: { type: Number, default: 420 },
    minWidth: { type: Number, default: 320 },
    maxWidth: { type: Number, default: 800 },
    attachSelector: { type: String, default: '.workbench-view' }
  },
  setup(props) {
    const width = ref(props.initialWidth)
    const top = ref(0)
    const height = ref(window.innerHeight)
    const dragging = ref(false)
    let startX = 0
    let startWidth = props.initialWidth
    const isJson = computed(() => typeof props.content === 'object' && props.content !== null)

    // 递归生成键值分离的HTML结构
    const renderKV = (data) => {
      if (data === null) return '<span class="json-null">null</span>'
      if (Array.isArray(data)) {
        const items = data.map((item) => `<li class="json-item">${renderKV(item)}</li>`).join('')
        return `<ul class="json-list json-array">${items}</ul>`
      }
      if (typeof data === 'object') {
        const items = Object.keys(data).map((key) => {
          const value = data[key]
          const valueHtml = renderKV(value)
          return `<li class="json-item"><span class="json-key">${key}</span><span class="json-sep">:</span> ${valueHtml}</li>`
        }).join('')
        return `<ul class="json-list json-object">${items}</ul>`
      }
      // 基础类型渲染
      if (typeof data === 'string') {
        const escaped = data.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        return `<span class="json-string">"${escaped}"</span>`
      }
      if (typeof data === 'number') {
        return `<span class="json-number">${data}</span>`
      }
      if (typeof data === 'boolean') {
        return `<span class="json-boolean">${data}</span>`
      }
      return `<span>${String(data)}</span>`
    }

    const kvHtml = computed(() => {
      try {
        return renderKV(props.content)
      } catch (e) {
        // 回退到原始字符串展示
        return `<pre>${String(props.content)}</pre>`
      }
    })

    const onDrag = (e) => {
      if (!dragging.value) return
      const delta = startX - e.clientX
      let newWidth = startWidth + delta
      if (newWidth < props.minWidth) newWidth = props.minWidth
      if (newWidth > props.maxWidth) newWidth = props.maxWidth
      width.value = newWidth
    }

    const stopResize = () => {
      if (!dragging.value) return
      dragging.value = false
      document.body.style.userSelect = ''
      document.body.style.cursor = ''
      window.removeEventListener('mousemove', onDrag)
      window.removeEventListener('mouseup', stopResize)
    }

    const startResize = (e) => {
      dragging.value = true
      startX = e.clientX
      startWidth = width.value
      document.body.style.userSelect = 'none'
      document.body.style.cursor = 'col-resize'
      window.addEventListener('mousemove', onDrag)
      window.addEventListener('mouseup', stopResize)
    }

    onBeforeUnmount(() => {
      stopResize()
    })

    // 计算侧边栏的 top 和 height 以贴合工作台区域
    const updateBounds = () => {
      try {
        const el = document.querySelector(props.attachSelector)
        if (!el) return
        const rect = el.getBoundingClientRect()
        top.value = rect.top
        height.value = rect.height
      } catch {}
    }

    onMounted(() => {
      updateBounds()
      window.addEventListener('resize', updateBounds)
      window.addEventListener('scroll', updateBounds, { passive: true })
    })

    watch(() => props.visible, (v) => {
      if (v) {
        // 下一帧更新以避免布局抖动
        requestAnimationFrame(updateBounds)
      }
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', updateBounds)
      window.removeEventListener('scroll', updateBounds)
    })

    return { isJson, kvHtml, width, startResize, top, height }
  }
}
</script>

<style scoped>
.sidebar { position: fixed; top: 0; right: 0; width: 420px; height: 100vh; background: #ffffff; box-shadow: -6px 0 16px rgba(0,0,0,0.08); display: flex; flex-direction: column; z-index: 1999; }
.resize-handle { position: absolute; left: 0; top: 0; width: 6px; height: 100%; cursor: col-resize; }
.resize-handle::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 2px; background: #e9ecef; }
.resize-handle:hover { background: linear-gradient(to right, rgba(11,107,203,0.08), rgba(11,107,203,0)); }
.sidebar-header { position: relative; display: flex; align-items: center; justify-content: center; padding: 12px 16px; border-bottom: 1px solid #eee; }
.title { font-size: 18px; font-weight: 600; color: #1a1a1a; }
.close-btn { position: absolute; right: 12px; top: 6px; border: none; background: transparent; font-size: 24px; cursor: pointer; color: #333; }
.sidebar-content { padding: 12px 16px; overflow: auto; }
.json-view { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 14px; line-height: 1.7; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 12px; }
:deep(.json-list) { list-style: none; margin: 0; padding-left: 14px; }
:deep(.json-item) { margin: 4px 0; }
:deep(.json-key) { color: #0b6bcb; font-weight: 600; margin-right: 6px; }
:deep(.json-sep) { color: #999; margin-right: 6px; }
:deep(.json-string) { color: #2b8a3e; }
:deep(.json-number) { color: #ae3ec9; }
:deep(.json-boolean) { color: #d9480f; }
:deep(.json-null) { color: #495057; font-style: italic; }
:deep(.json-array > .json-item), :deep(.json-object > .json-item) { padding-left: 2px; }
.text-view { font-size: 14px; color: #333; }
.slide-enter-active, .slide-leave-active { transition: transform .2s ease, opacity .2s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(420px); opacity: 0; }
</style>