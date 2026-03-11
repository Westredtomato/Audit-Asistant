import { defineStore } from 'pinia'

export const useMessageStore = defineStore('message', {
  state: () => ({
    messages: [],
    unreadCount: 0,
    loading: false,
    error: null
  }),
  
  getters: {
    getMessages: (state) => state.messages,
    getUnreadCount: (state) => state.unreadCount,
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  },
  
  actions: {
    async fetchMessages() {
      this.loading = true
      this.error = null
      try {
        // 模拟 API 调用
        // const response = await api.getMessages()
        // this.messages = response.data
        
        // 模拟数据
        this.messages = [
          { id: 1, title: '新任务分配', content: '您有一个新的审计任务需要处理', read: false },
          { id: 2, title: '项目进度更新', content: '项目A已完成50%', read: true },
          { id: 3, title: '会议提醒', content: '明天上午10点项目会议', read: false }
        ]
        
        this.unreadCount = this.messages.filter(msg => !msg.read).length
      } catch (error) {
        this.error = error.message
        console.error('获取消息失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    markAsRead(messageId) {
      const message = this.messages.find(msg => msg.id === messageId)
      if (message && !message.read) {
        message.read = true
        this.unreadCount = this.messages.filter(msg => !msg.read).length
      }
    }
  }
})