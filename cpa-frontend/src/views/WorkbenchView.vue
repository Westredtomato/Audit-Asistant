<template>
  <!-- 工作台主页面 - CPA智能助手的核心交互界面 -->
  <div class="workbench-view">
    <!-- 智能体助手对话界面 - 主要的用户交互区域 -->
    <div class="chat-interface">
      <!-- 智能体头部信息 - 显示助手状态和当前项目信息 -->
      <div class="ai-header">
        <div class="ai-avatar">🤖</div>
        <div class="ai-info">
          <h3>CPA智能助手</h3>
          <!-- 实时显示智能体当前状态：准备就绪/思考中/处理中/等待中 -->
          <p class="ai-status">{{ agentStatus }}</p>
        </div>
        <div class="project-info">
          <!-- 显示当前项目名称，从projectStore获取 -->
          <span class="project-name">{{ currentProject?.name || '审计项目' }}</span>
          <!-- 项目状态指示器，支持不同状态的样式 -->
          <span class="project-status" :class="currentProject?.status">{{ getStatusText(currentProject?.status) }}</span>
        </div>
      </div>
      
      <!-- 对话消息区域 - 显示用户与智能体的交互历史 -->
      <div class="chat-messages" ref="messagesContainer">
        <div class="message-item" 
             v-for="message in chatMessages" 
             :key="message.id"
             :class="message.type">
          <div class="message-avatar">
            {{ message.type === 'ai' ? '🤖' : '👤' }}
          </div>
          <div class="message-content">
            <!-- 普通文本消息 - 简单的文本对话 -->
            <div v-if="!message.component" class="message-text">{{ message.content }}</div>
            <!-- 功能组件消息 - 嵌入式功能模块（如设置、上传、分析等） -->
            <div v-else class="message-component">
              <div class="component-header">
                <span class="component-title">{{ message.title }}</span>
                <button class="close-component-btn" @click="closeComponent(message.id)">✕</button>
              </div>
              <!-- 动态组件渲染 - 根据message.component动态加载对应的功能模块 -->
              <component 
                :is="message.component"
                v-bind="message.props || {}"
                @close="() => closeComponent(message.id)"
                @module-completed="(data) => onModuleCompleted(message.id, data)"
                @settings-updated="onSettingsUpdated"
                @files-uploaded="(files) => onFilesUploaded(message.id, files)"
                @timeout-reviewed="onTimeoutReviewed"
                @result-confirmed="onResultConfirmed"
                @result-adjusted="onResultAdjusted"
                @draft-saved="onDraftSaved"
                @review-started="onReviewStarted"
                @event-created="onEventCreated"
                @add-message="onAddMessage"
                @confirm-review-content="onConfirmReviewContent"
                @cancel-review-content="onCancelReviewContent"
                @open-standard="onOpenStandard"
                @open-excel-view="onOpenExcel"
              />
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>
      
      <!-- 功能快捷按钮 - 审计复核工作流的主要入口点 -->
      <div class="quick-actions">
        <!-- 默认复核设置 - 配置项目级别的复核参数和规则 -->
        <button class="action-btn" @click="showDefaultSettings" title="默认复核设置">
          <span class="btn-icon">⚙️</span>
          <span class="btn-text">默认复核设置</span>
        </button>
        <!-- 执行复核 - 选择未复核的重大事项或创建新事项开始复核流程 -->
        <button class="action-btn" @click="executeReview" title="执行复核">
          <span class="btn-icon">🚀</span>
          <span class="btn-text">执行复核</span>
        </button>
        <!-- 补充底稿 - 补充复核所需的底稿文件，支持智能识别和批量上传 -->
        <button class="action-btn" @click="showSupplementDialog" title="补充底稿">
          <span class="btn-icon">📄</span>
          <span class="btn-text">补充底稿</span>
        </button>
        <!-- 超时回溯 - 查看和分析复核过程中的超时处理记录 -->
        <button class="action-btn" @click="showTimeoutReview" title="超时回溯">
          <span class="btn-icon">⏰</span>
          <span class="btn-text">超时回溯</span>
        </button>
        <!-- 复核进度 - 查看当前复核流程的实时进度和状态 -->
        <button class="action-btn" @click="showReviewProgress" title="复核进度" :disabled="reviewStatus === 'idle'">
          <span class="btn-icon">📈</span>
          <span class="btn-text">复核进度</span>
        </button>
        <!-- 结果确认 - 确认分析结果并生成最终报告 -->
        <button class="action-btn" @click="showResultConfirm" title="结果确认">
          <span class="btn-icon">✅</span>
          <span class="btn-text">结果确认</span>
        </button>
      </div>
      
      <!-- 底部对话输入框 -->
      <div class="chat-input-area">
        <div class="input-container">
          <input 
            v-model="userInput" 
            type="text" 
            class="chat-input" 
            placeholder="请输入您的问题或指令..."
            @keyup.enter="sendMessage"
            :disabled="isProcessing"
          />
          <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim() || isProcessing">
            {{ isProcessing ? '⏳' : '📤' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 用户指引组件 -->
    <UserGuide 
      ref="userGuideRef"
      :steps="guideSteps"
    />
    
    <!-- 网络错误提示 -->
    <div v-if="showNetworkError" class="network-error-alert">
      <div class="alert-content">
        <div class="alert-icon">⚠️</div>
        <div class="alert-text">
          <h4>网络连接异常</h4>
          <p>网络请求失败，已重试 {{ networkRetryCount }} 次。请检查网络连接后重试。</p>
        </div>
        <div class="alert-actions">
          <button class="btn-primary" @click="retryNetworkRequest">重试请求</button>
          <button class="btn-secondary" @click="showNetworkError = false">忽略</button>
        </div>
      </div>
    </div>
    
    <!-- 逻辑矛盾警告 -->
    <div v-if="showLogicWarning" class="logic-warning-alert">
      <div class="alert-content">
        <div class="alert-icon">⚠️</div>
        <div class="alert-text">
          <h4>逻辑一致性警告</h4>
          <p>{{ logicWarningMessage }}</p>
        </div>
        <div class="alert-actions">
          <button class="btn-secondary" @click="showLogicWarning = false">知道了</button>
        </div>
      </div>
    </div>

  </div>
  <!-- 复核标准侧边栏 -->
  <ReviewStandardSidebar 
    :visible="sidebarVisible" 
    :title="sidebarTitle" 
    :content="sidebarContent" 
    :component="sidebarComponent"
    :componentProps="sidebarComponentProps"
    @close="sidebarVisible = false" 
  />
</template>

<script>
// Vue 3 Composition API 核心功能
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'

// Pinia 状态管理 - 各个业务模块的数据存储
import { useProjectStore } from '@/stores/project'     // 项目管理：当前项目信息、项目列表
import { useDocumentStore } from '@/stores/document'   // 文档管理：文件上传、存储、检索
import { useEventStore } from '@/stores/event'         // 事件管理：操作日志、事件记录
import { useMessageStore } from '@/stores/message'     // 消息管理：聊天记录、通知消息
import { useWorkspaceStore } from '@/stores/workspace' // 工作区管理：复核流程、智能体状态、文件请求

// 导入axios库发送HTTP请求，与后端交互
import axios from 'axios';

// 导入工作流程模块组件 - 审计复核的核心功能模块
import DefaultReviewSettings from '@/components/modules/workspace/DefaultReviewSettings.vue' // 默认复核设置
import ExecuteReview from '@/components/modules/workspace/ExecuteReview.vue'                 // 执行复核
import SupplementDocuments from '@/components/modules/workspace/SupplementDocuments.vue'     // 补充底稿
import TimeoutReview from '@/components/modules/workspace/TimeoutReview.vue'                 // 超时回溯
import ReviewProgress from '@/components/modules/workspace/ReviewProgress.vue'               // 复核进度
import ResultConfirm from '@/components/modules/workspace/ResultConfirm.vue'                 // 结果确认
import ConfirmReviewContent from '@/components/modules/workspace/ConfirmReviewContent.vue'   // 复核内容确认
import ReviewStandardSidebar from '@/components/modules/workspace/ReviewSidebar.vue'         // 复核标准侧边栏
import Filecheck from '@/components/modules/workspace/Filecheck.vue'                         // 文件入口消息（复核标准生成入口）
import SpecExcelView from '@/components/modules/workspace/SpecExcelView.vue'                 // Excel视图（信息定位）

// 导入用户体验组件
import UserGuide from '@/components/common/UserGuide.vue'                                   // 用户操作指引

export default {
  name: 'WorkbenchView',
  components: {
    DefaultReviewSettings,
    ExecuteReview,
    SupplementDocuments,
    TimeoutReview,
    ReviewProgress,
    ResultConfirm,
    ConfirmReviewContent,
    UserGuide,
    ReviewStandardSidebar,
    Filecheck
  },
  setup() {
    // ===== 状态管理初始化 =====
    // 各个业务模块的状态管理实例
    const route = useRoute()
    const projectStore = useProjectStore()     // 项目相关状态
    const documentStore = useDocumentStore()   // 文档相关状态
    const eventStore = useEventStore()         // 事件相关状态
    const messageStore = useMessageStore()     // 消息相关状态
    const workspaceStore = useWorkspaceStore() // 工作区相关状态（核心）
    
    // ===== 组件本地响应式数据 =====
    const userInput = ref('')                  // 用户输入的消息内容
    const isProcessing = ref(false)            // 智能体是否正在处理中
    const messagesContainer = ref(null)        // 消息容器DOM引用，用于滚动控制
    const waitingTimer = ref(null)             // 文件等待超时定时器
    const filecheckMessageId = ref(null)       // Filecheck组件消息ID（用于进度条控制）
    
    // ===== 用户体验相关数据 =====
    const userGuideRef = ref(null)             // 用户指引组件引用
    const showNetworkError = ref(false)        // 网络错误提示
    const networkRetryCount = ref(0)           // 网络重试次数
    const showLogicWarning = ref(false)        // 逻辑矛盾警告
    const logicWarningMessage = ref('')        // 逻辑矛盾警告信息
    
    // ===== 复核标准侧边栏状态 =====
    const sidebarVisible = ref(false)
    const sidebarTitle = ref('复核标准')
    const sidebarContent = ref('')
    const sidebarComponent = ref(null)
    const sidebarComponentProps = ref({})
    
    // ===== 用户指引步骤配置 =====
    const guideSteps = ref([
      {
        target: '.ai-header',
        title: '欢迎使用CPA智能助手',
        description: '这里显示智能助手的当前状态和项目信息。您可以随时查看助手是否正在工作。',
        position: 'bottom',
        arrowDirection: 'top',
        tips: ['绿色状态表示助手准备就绪', '红色状态表示助手正在处理任务']
      },
      {
        target: '.quick-actions',
        title: '功能快捷按钮',
        description: '这些是审计复核工作的主要功能入口。建议按顺序使用：设置→执行→进度→确认。',
        position: 'top',
        arrowDirection: 'bottom',
        tips: ['首次使用建议先配置默认设置', '可以随时查看复核进度', '完成后记得确认结果']
      },
      {
        target: '.chat-input-area',
        title: '智能对话',
        description: '您可以直接与智能助手对话，询问问题或请求帮助。支持自然语言交互。',
        position: 'top',
        arrowDirection: 'bottom',
        tips: ['支持语音输入和文字输入', '可以询问审计相关问题', '助手会根据上下文提供建议']
      }
    ])
    
    // ===== 聊天消息数据（统一事实源） =====
    // 改为从 store 读取，统一管理并持久化
    const chatMessages = computed(() => workspaceStore.getChatMessages)
    // 从统一消息中派生最近一次复核标准
    // 最近一次复核标准：优先从 Filecheck 组件的持久化 props 中读取
    const latestStandardFromMessages = computed(() => {
      const msgs = workspaceStore.getChatMessages || []
      // 仅从最新的 Filecheck 组件消息中提取标准
      const filecheckMsg = [...msgs]
        .reverse()
        .find(m => m.component === 'Filecheck' && m?.props && m.props.standard)
      return filecheckMsg?.props?.standard || null
    })
    
    // ===== 计算属性 - 从各个store获取响应式数据 =====
    const currentProject = computed(() => projectStore.currentProject)         // 当前项目信息
    const reviewProcess = computed(() => workspaceStore.getReviewProcess)      // 复核流程状态
    const reviewStatus = computed(() => workspaceStore.getReviewStatus)        // 复核状态：idle/confirming/analyzing/paused/completed/error
    const reviewStages = computed(() => workspaceStore.getReviewStages)        // 复核阶段列表
    const currentStage = computed(() => workspaceStore.getCurrentStage)        // 当前复核阶段
    const fileRequest = computed(() => workspaceStore.getFileRequest)          // 文件请求状态
    const agentStatus = computed(() => workspaceStore.getAgentStatus)          // 智能体当前状态
    const currentTask = computed(() => workspaceStore.getCurrentTask)          // 智能体当前任务
    const isWaitingForFiles = computed(() => workspaceStore.isWaitingForFiles) // 是否等待文件
    const requestedFiles = computed(() => workspaceStore.getRequestedFiles)    // 请求的文件列表
    const warningLogs = computed(() => workspaceStore.getWarningLogsData)          // 警告日志
    
    // ===== 工具函数 =====
    // 获取项目状态的中文显示文本
    const getStatusText = (status) => {
      const statusMap = {
        'active': '进行中',
        'completed': '已完成', 
        'paused': '已暂停',
        'archived': '已归档'
      }
      return statusMap[status] || '未知'
    }
    
    // 格式化时间
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 添加消息（统一走 store）
    const addMessage = (type, content, isvaluable, options = {}) => {
      workspaceStore.addChatMessage({
        role: type === 'user' ? 'user' : 'ai',
        type,
        content,
        isvaluable,
        ...options
      })
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    // 添加组件消息（统一走 store）
    const addComponentMessage = (title, component) => {
      const id = Date.now() + Math.random()
      const payload = { id, role: 'ai', type: 'ai', title }
      if (typeof component === 'string') {
        payload.component = component
      } else if (typeof component === 'object' && component !== null) {
        const comp = component.component
        payload.props = component.props
        if (typeof comp === 'string') {
          payload.component = comp
        } else if (comp && typeof comp === 'object') {
          const name = comp.name
          // 统一将对象组件转换为注册键字符串，避免持久化失败
          if (name === 'FileCheck') {
            payload.component = 'Filecheck'
          } else if (typeof name === 'string' && name.length > 0) {
            payload.component = name
          } else {
            // 无法识别时不设置component，避免渲染报错
            payload.component = null
          }
        } else {
          payload.component = null
        }
      }
      workspaceStore.addChatMessage(payload)
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
      return id
    }
    
    // 处理确认复核内容事件
    const onConfirmReviewContent = (content) => {
      try {
        const query = typeof content === 'string'
          ? content
          : (content?.reviewContent || content?.content || '')

        // 更新复核状态为分析中
        workspaceStore.setReviewStatus('analyzing')
        // 标记系统正在处理，禁用用户输入
        isProcessing.value = true

        ensureWorkspaceProjectContext()
        workspaceStore.startSession({ projectId: currentProject.value?.id || 'default', functionalArea: 'workbench' })

        // 1. AI发出消息：正在生成复核标准
        addMessage('ai', '正在生成复核标准...', false)

        // 2. AI发出组件消息（文件入口消息）：显示生成进度与“查看”入口
        // 初始standardReady为false，等待后端返回标准后推至100%
        const createdId = addComponentMessage('文件入口消息', {
          component: 'Filecheck',
          props: {
            userInput: query || '复核内容',
            standardReady: false
          }
        })
        filecheckMessageId.value = createdId
        // 记录待回填的 Filecheck 消息 ID 与请求负载（用于刷新后恢复）
        workspaceStore.setPendingStandard(createdId, {
          status: reviewStatus.value || 'idle',
          type: 'ai',
          content: query
        })

        // 并行请求后端生成/检索复核标准（统一由store action调用）
        workspaceStore.fetchStandards({
          status: reviewStatus.value || 'idle',
          type: 'ai',
          content: query
        }).then(async (result) => {
          // 保存复核标准供查看（已由store推送至chatMessages）
          const data = result?.data
          const standard = data?.审计证据标准 || data || null
          
          // 标准生成成功后，自动启动复核流程
          if (standard) {
            // Store 的 fetchStandards 已负责回填与持久化，视图层仅提示
            // 提示生成完成（在发出组件消息后延迟1秒）
            setTimeout(() => {
              addMessage('ai', '✅ 复核标准生成完成！正在启动复核流程...', false)
              addMessage('ai', '🔍 复核流程已启动，正在分析复核内容...', false)
            }, 1000)
            const reviewData = buildReviewDataFromStandard(query, standard)

            // 延迟5秒再调用复核执行接口，给用户时间查看文件
            setTimeout(async () => {
              try {
                // 调用复核执行接口
                const reviewResponse = await workspaceStore.executeReview(reviewData)
                
                // 处理后端响应，启动复核流程
                handleBackendResponse(reviewResponse.data)
                
              } catch (reviewError) {
                console.error('启动复核流程失败:', reviewError)
                addMessage('ai', '❌ 启动复核流程失败，请稍后重试。', false)
              }
            }, 5000)
          }
          
          // 处理完成，允许用户继续输入
          isProcessing.value = false
        }).catch((error) => {
          // 网络错误提示与逻辑警告
          showNetworkError.value = true
          networkRetryCount.value += 1
          logicWarningMessage.value = '生成复核标准失败，请稍后重试。'
          showLogicWarning.value = true
          console.error('生成复核标准失败:', error)
          // 处理结束，恢复输入
          isProcessing.value = false
        })
      } catch (e) {
        console.error('确认复核内容处理异常:', e)
        isProcessing.value = false
      }
    }
    const buildReviewDataFromStandard = (query, standard) => {
      return {
        重大事项概述: query || '复核内容',
        审计目标: '根据审计证据标准进行复核分析',
        审计证据标准: {
          审计结论: standard?.审计结论 || '',
          审计证据分类与要求: Array.isArray(standard?.审计证据分类与要求) && (standard?.审计证据分类与要求 || []).length > 0
            ? standard.审计证据分类与要求
            : [{ "默认分类": { "默认子分类": [{ "证据内容": "", "质量要求": "" }] } }],
          充分_适当评判标准: standard?.充分_适当评判标准 || '审计证据应当充分、适当，能够支持审计结论'
        }
      }
    }
    const buildReviewDataFromEvent = (event) => {
      const normalized = buildEvidenceStandardsFromEvent(event)
      return {
        重大事项概述: event.description || '',
        审计目标: event.auditObjectives || '',
        审计证据标准: normalized
      }
    }

    // 处理 Filecheck 的“查看”事件，打开复核标准侧边栏
    const onOpenStandard = ({ title } = {}) => {
      sidebarTitle.value = title || '复核标准'
      sidebarContent.value = latestStandardFromMessages.value || '暂无标准数据'
      sidebarComponent.value = null
      sidebarComponentProps.value = {}
      sidebarVisible.value = true
    }
    
    const onOpenExcel = async ({ title, location } = {}) => {
      try {
        sidebarTitle.value = title || '信息定位'
        const files = await workspaceStore.getAvailableFiles()
        const excel = (files || []).find(f => (f.name || '').toLowerCase().match(/\.xlsx$|\.xls$/))
        sidebarComponent.value = SpecExcelView
        sidebarComponentProps.value = excel ? { fileUrl: excel.url, fileName: excel.name } : {}
        sidebarContent.value = ''
        sidebarVisible.value = true
      } catch (e) {
        console.error('打开信息定位侧边栏失败:', e)
        sidebarComponent.value = SpecExcelView
        sidebarComponentProps.value = {}
        sidebarTitle.value = title || '信息定位'
        sidebarContent.value = ''
        sidebarVisible.value = true
      }
    }

    // 处理取消复核内容事件
    const onCancelReviewContent = () => {
      // 清空所有chatMessage内容并恢复为初始状态
      workspaceStore.resetChatMessages()
      workspaceStore.setReviewStatus('idle');
    
    }
    
    // ===== 消息处理逻辑 =====
    // 发送并显示用户消息
    const sendMessage = async () => {
      // 输入验证：空消息或正在处理中时不允许发送
      if (!userInput.value.trim() || isProcessing.value) return
      
      // 获取用户输入内容并清空输入框
      const message = userInput.value.trim()
      userInput.value = ''
      
      // 不在视图层推送用户消息，交由store在/chat中统一处理
      
      // 设置智能体处理状态
      isProcessing.value = true
      
      await responseUserMessage(reviewStatus.value, 'user', message)
    }
    
    // 调用后端API获取并处理智能体响应
    const responseUserMessage = async (status, type, content) => {
      try {
        if (status === "idle") {
          // 交由store：记录用户输入并打包上下文后再请求/chat
          const response = await workspaceStore.chat(status, content);
          
          // 接收响应，消息的数据模式为{"用户意图":"","是否完整":bool,"内容":""}，并分类别处理
          const { "用户意图": userIntent, "是否完整": isComplete, "内容": messageContent } = response.data;
          
          if (userIntent === "执行复核") {
            if (isComplete) {
              // 将内容传入ConfirmReviewContent组件，并调用addComponentMessage方法展示"内容"
              
              // 更新reviewStatus为confirming
              workspaceStore.setReviewStatus('confirming');
              
              const reviewMessage = `📝好的，我已经明晰您想要复核的内容。以下是我的总结：${messageContent}\n\n🎯请您确定是否执行复核`
              addComponentMessage('确认待复核内容', {
                component: 'ConfirmReviewContent',
                props: {
                  showedContent: reviewMessage,
                  reviewContent: messageContent
                }
              });
              isProcessing.value = false;
            } else {
              // 调用addMessage显示"内容"
              addMessage('ai', messageContent, true);
              isProcessing.value = false;
            }
          } else if (userIntent === "未明确") {
            // 调用addMessage显示"内容"
            addMessage('ai', messageContent, true);
            isProcessing.value = false;
          }
        } else if (status === "analyzing" || status === "paused") {
          // 在分析/暂停流程中，视图层需要显式记录用户消息
          workspaceStore.addChatMessage({ role: 'user', type: 'user', content, isvaluable: true })

          // 构造符合ResponseData格式的数据结构
          const responseData = {
            response_type: "help_response",
            data: {
              res_case: "y", // 默认用户提供帮助
              data: content // 用户输入的帮助内容
            }
          };
          
          // 恢复为进行中状态，进入智能体继续处理
          workspaceStore.resumeReviewProcess();
          
          // 统一由store action调用 /continue_review
          const response = await workspaceStore.continueReview(responseData);
          
          // 处理后端响应
          handleBackendResponse(response.data);
          isProcessing.value = false;
        }
      } catch (error) {
        console.error('处理响应时出错:', error);
        addMessage('ai', '处理您的请求时出现错误，请稍后重试。', true);
        isProcessing.value = false;
      }
    }

    
    // 快捷操作方法 - 显示默认复核设置界面
    const showDefaultSettings = () => {
      // 检查是否有复核流程正在运行，如果有则拒绝设置请求
      if (workspaceStore.reviewProcess.status === 'running') {
        addMessage('ai', '⚠️ 复核流程正在进行中，无法修改默认设置。请等待当前流程完成后再试。', true)
        return
      }
      
      addMessage('ai', '让我们配置智能体交互超时处理策略，这将影响后续所有复核流程的超时处理方式。', true)
      addComponentMessage('默认复核设置', 'DefaultReviewSettings')
    }
    
    // 执行复核 - 显示ExecuteReview组件，让用户选择未复核事项或创建新事项
    const executeReview = () => {
      addMessage('ai', '准备执行复核流程。您可以选择已创建但未复核的重大事项开始复核，或创建新的重大事项。', true)
      addComponentMessage('执行复核', 'ExecuteReview')
    }
    
    // 处理复核启动事件 - 当用户从ExecuteReview组件启动复核时触发
    const onReviewStarted = async (data) => {
      try {
        const { event, reviewId } = data
        
        // 记录复核启动事件到活动日志
        console.log('复核启动事件:', {
          type: 'review_started',
          message: `开始复核重大事项: ${event.title}`,
          data: {
            eventId: event.id,
            reviewId: reviewId,
            eventTitle: event.title
          },
          timestamp: new Date().toISOString()
        })
        
        // 更新工作区状态
        await workspaceStore.setCurrentReviewEvent(event)
        workspaceStore.startSession({ projectId: currentProject.value?.id || 'default', functionalArea: 'workbench', eventId: event.id })
        
        const reviewData = buildReviewDataFromEvent(event);
        
        const response = await workspaceStore.executeReview(reviewData);
        
        // 处理后端响应，参数已重命名为engineResponseData
        handleBackendResponse(response.data);
        
        addMessage('ai', `✅ 已开始复核重大事项「${event.title}」，复核ID: ${reviewId}。我将引导您完成整个复核过程。`, true)
        
        // 启动智能体复核流程
        setTimeout(() => {
          addMessage('ai', '正在分析事项内容和相关底稿，准备生成复核计划...', true)
        }, 1000)
        
      } catch (error) {
        console.error('处理复核启动失败:', error)
        addMessage('ai', '❌ 启动复核流程时发生错误，请稍后重试。', true)
      }
    }
    
    // 处理后端响应的通用函数
    const handleBackendResponse = (engineResponseData) => {
      const { response_type, data } = engineResponseData;
      
      switch (response_type) {
        case 'upload_file_requirement':
          // 处理文件上传请求：使用统一方法生成正确的请求对象并触发后续流程
          {
            const fileTypes = Array.isArray(data.filename_list) ? data.filename_list : []
            // 暂停复核流程，等待用户提供文件
            workspaceStore.reviewProcess.status = 'paused'
            workspaceStore.agent.status = 'waiting'
            // 其内部会更新agent状态、请求标记，并在watcher中触发文件请求对话框
            workspaceStore.requestFiles(fileTypes, '复核引擎请求所需文件')
            // 聊天区的提示与组件插入由文件请求监听器统一处理
          }
          break;
          
        case 'help_requirement':
          // 处理帮助请求
          workspaceStore.agent.status = 'waiting';
          workspaceStore.agent.currentTask = '等待用户提供帮助';
          workspaceStore.reviewProcess.status = 'paused'; // 等待用户输入阶段统一为 paused
          addMessage('ai', `💡 智能体在复核过程中需要帮助：\n\n📍 当前阶段： ${data.stage}\n\n❓ 需要帮助： ${data.request}\n\n📝 原因说明： ${data.reason}\n\n请在下方输入您的回复，我会根据您的指导继续复核流程。`, true);
          break;
          
        case 'review_result':
          // 处理复核结果
          workspaceStore.reviewProcess.status = 'completed';
          workspaceStore.reviewProcess.isActive = false;
          workspaceStore.reviewProcess.progress = 100;
          workspaceStore.agent.status = 'ready';
          workspaceStore.agent.currentTask = null;

          // 将后端复核结果保存到本地存储
          try {
            const eventId = workspaceStore.reviewProcess.currentEventId;
            const payload = {
              data: data || {},
              review_config: engineResponseData.review_config || {}
            };
            // 使用workspaceStore的保存方法持久化，ResultConfirm会在加载时合并此数据
            workspaceStore.saveReviewResult(eventId, payload);
          } catch (e) {
            console.warn('保存复核结果失败（将继续展示结果确认界面）:', e);
          }

          addMessage('ai', '✅ 复核流程已完成！正在准备结果确认...', true);
          
          // 显示结果确认组件
          setTimeout(() => {
            addMessage('ai', '请查看复核结果详情，您可以对结果进行调整、重新生成或直接确认归档。', true);
            showResultConfirm();
          }, 1000);
          break;
          
        default:
          console.warn('未知的响应类型:', response_type);
      }
    }

    // 确保工作区上下文与当前项目一致（用于localStorage项目隔离键）
    const ensureWorkspaceProjectContext = () => {
      try {
        const projId = currentProject.value?.id || 'default'
        const ws = workspaceStore.getCurrentWorkspace
        if (!ws || ws?.id !== projId) {
          workspaceStore.setCurrentWorkspace({ id: projId, name: `项目工作区-${projId}` })
        }
        workspaceStore.setProjectId(projId)
      } catch (e) {
        console.warn('设置工作区项目上下文失败，使用默认：', e)
        workspaceStore.setCurrentWorkspace({ id: 'default', name: '默认工作区' })
        workspaceStore.setProjectId('default')
      }
    }

    // 将事件的证据标准统一为中文键并保证最小有效结构
    const buildEvidenceStandardsFromEvent = (createdEvent) => {
      try {
        const es = createdEvent?.evidenceStandards
        if (es && (es.审计结论 !== undefined || es.审计证据分类与要求 !== undefined || es.充分_适当评判标准 !== undefined)) {
          return {
            审计结论: es.审计结论 || '',
            审计证据分类与要求: Array.isArray(es.审计证据分类与要求) && es.审计证据分类与要求.length > 0
              ? es.审计证据分类与要求
              : [{ "默认分类": { "默认子分类": [{ "证据内容": "", "质量要求": "" }] } }],
            充分_适当评判标准: es.充分_适当评判标准 || ''
          }
        }

        const aes = createdEvent?.auditEvidenceStandards
        const adequacy = aes?.adequacyCriteria || ''
        const conclusion = aes?.situation1?.auditConclusion || ''
        const classificationFallback = [{ "默认分类": { "默认子分类": [{ "证据内容": "", "质量要求": "" }] } }]
        return {
          审计结论: conclusion,
          审计证据分类与要求: classificationFallback,
          充分_适当评判标准: adequacy || '审计证据应当充分、适当，能够支持审计结论'
        }
      } catch (e) {
        console.error('规范化证据标准失败:', e)
        return {
          审计结论: '',
          审计证据分类与要求: [{ "默认分类": { "默认子分类": [{ "证据内容": "", "质量要求": "" }] } }],
          充分_适当评判标准: ''
        }
      }
    }

    // 规范化事件对象到工作区使用的结构与状态
    const normalizeEventForWorkspace = (createdEvent, projectId) => {
      return {
        id: createdEvent.id,
        title: createdEvent.title,
        description: createdEvent.description || '',
        auditObjectives: createdEvent.auditObjectives || '',
        evidenceStandards: buildEvidenceStandardsFromEvent(createdEvent),
        status: 'unreviewed',
        projectId: projectId,
        createdAt: createdEvent.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    }

    // 同步新创建的事项到项目隔离的存储: majorEvents_<projectId>
    const syncCreatedEventToWorkspace = (createdEvent) => {
      try {
        // 优先使用工作区ID，确保与workspace.js读取一致
        const workspaceProjectId = (workspaceStore.getCurrentWorkspace?.id) || (workspaceStore.currentWorkspace?.id) || (currentProject.value?.id) || 'default'
        const key = `majorEvents_${workspaceProjectId}`
        const raw = localStorage.getItem(key)
        const list = raw ? JSON.parse(raw) : []
        const normalized = normalizeEventForWorkspace(createdEvent, workspaceProjectId)
        const idx = list.findIndex(e => e.id === normalized.id)
        if (idx >= 0) {
          list[idx] = { ...list[idx], ...normalized }
        } else {
          list.push(normalized)
        }
        localStorage.setItem(key, JSON.stringify(list))
        console.log('已同步事项到工作区存储:', { key, normalized })
        
        // 若项目ID与工作区ID不同，则同时写入项目键，避免跨模块读取不一致
        const projectId = currentProject.value?.id
        if (projectId && projectId !== workspaceProjectId) {
          const projectKey = `majorEvents_${projectId}`
          const rawProject = localStorage.getItem(projectKey)
          const listProject = rawProject ? JSON.parse(rawProject) : []
          const idx2 = listProject.findIndex(e => e.id === normalized.id)
          const normalizedForProject = normalizeEventForWorkspace(createdEvent, projectId)
          if (idx2 >= 0) {
            listProject[idx2] = { ...listProject[idx2], ...normalizedForProject }
          } else {
            listProject.push(normalizedForProject)
          }
          localStorage.setItem(projectKey, JSON.stringify(listProject))
          console.log('兼容写入项目存储键:', { projectKey, normalizedForProject })
        }
      } catch (e) {
        console.error('同步事项到工作区失败:', e)
      }
    }

    // 将ArrayBuffer转换为Base64字符串（用于bytes字段）
    const arrayBufferToBase64 = (buffer) => {
      let binary = ''
      const bytes = new Uint8Array(buffer)
      const len = bytes.byteLength
      for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i])
      }
      return btoa(binary)
    }

    // 处理文件上传完成事件（携带组件消息ID，便于成功后关闭组件）
     const onFilesUploaded = async (messageId, files) => {
       console.log('files-uploaded payload', files)
       console.log('文件已上传:', files)
      
      // 显示用户上传文件的消息（使用真实上传的文件名）
      const fileList = files
        .map(f => `• ${f?.file?.name || f?.originalFile?.name || f?.name || f?.originalName || '未知文件'}`)
        .join('\n')
      addMessage('user', `已补充以下文件：\n\n${fileList}`, true)
      
       // 显示系统确认消息
       addMessage('ai', '✅ 文件上传成功！正在继续复核流程...', true);
      
       try {
         // 构造发送给后端的数据，符合ResponseData类型要求
         // 将文件信息转换为WorkPaperFile格式，并填充content为Base64字符串
         const successfulFiles = files.filter(f => f.success)

         const workPaperFiles = []
         for (const item of successfulFiles) {
           const filename = item?.file?.name || item?.name || item?.originalName || '未知文件'
           let base64Content = ''
           let size = item?.file?.size || 0

           try {
             if (item.originalFile) {
               // 优先使用原始File对象
               const buf = await item.originalFile.arrayBuffer()
               base64Content = arrayBufferToBase64(buf)
               size = item.originalFile.size || size
             } else if (item?.file?.url) {
               // 从服务器URL下载并编码（统一使用axios）
               const res = await axios.get(item.file.url, { responseType: 'arraybuffer' })
               const buf = res.data
               base64Content = arrayBufferToBase64(buf)
               size = size || (buf?.byteLength || 0)
             } else {
               // 无法获取内容，记录警告但继续流程
               console.warn('无法获取文件内容用于继续复核：', item)
             }
           } catch (e) {
             console.error('编码文件为Base64失败：', e)
           }

           workPaperFiles.push({
             filename,
             content: base64Content,
             size
           })
         }
         
         const continueData = {
           response_type: "upload_file_response",
           data: workPaperFiles
         };
        
         // 调用/workspace/continue_review接口继续复核流程
         console.log('posting to /workspace/continue_review', continueData)
         const response = await workspaceStore.continueReview(continueData);
         handleBackendResponse(response.data);

         // 仅在复核继续成功后关闭补充底稿组件
         onModuleCompleted(messageId, 'supplement-documents')
        
       } catch (error) {
         console.error('继续复核流程时出错:', error);
         addMessage('ai', '❌ 继续复核流程时出现错误，请稍后重试。', true);
       }
     }
    
    // 处理事项创建事件 - 当用户从ExecuteReview组件跳转到创建页面时触发
    const onEventCreated = (data) => {
      const { mode } = data
      const modeText = mode === 'direct' ? '直接创建' : '模板创建'
      
      // 记录事项创建事件到活动日志
      console.log('事项创建事件:', {
        type: 'event_creation_started',
        message: `用户选择${modeText}重大事项`,
        data: { mode },
        timestamp: new Date().toISOString()
      })
      
      // 获取刚创建的事项详情
      const createdEvent = eventStore.getMajorEventById(eventId)
      if (createdEvent) {
        // 显示事项详情
        const eventDetails = `🎉 重大事项创建成功！

📋 事项详情：

📝 重大事项概述：
${createdEvent.description || '暂无概述'}

🎯 审计目标：
${createdEvent.auditObjectives || '暂无审计目标'}

⚡ 正在启动复核流程...`
                  addMessage('ai', eventDetails, true)
      }
      
      addMessage('ai', `您选择了${modeText}重大事项，正在跳转到创建页面...`, true)
    }
    
    const showSupplementDialog = () => {
      addMessage('ai', '⚠️ 复核需要补充文件，请上传相关底稿文件以继续复核流程。', true)
      addComponentMessage('补充底稿', 'SupplementDocuments')
    }
    
    const showTimeoutReview = () => {
      addMessage('ai', '开始超时回溯分析，查看复核过程中的超时处理记录。', true)
      addComponentMessage('超时回溯', 'TimeoutReview')
    }
    
    // 显示复核进度 - 查看当前复核流程的实时进度
    const showReviewProgress = () => {
      if (reviewStatus.value === 'idle') {
        addMessage('ai', '当前没有进行中的复核流程。请先点击"执行复核"开始复核。', true)
        return
      }
      addMessage('ai', '正在显示复核进度详情...', true)
      addComponentMessage('复核进度', 'ReviewProgress')
    }
    
    // 结果确认 - 自动进入结果确认阶段，无需手动触发
    const showResultConfirm = () => {
      // 检查是否有复核结果数据可供确认
      if (reviewStatus.value === 'idle') {
        addMessage('ai', '当前没有可确认的复核结果。请先完成复核流程。', true)
        return
      }
      
      // 检查复核是否已完成
      if (reviewStatus.value !== 'completed') {
        addMessage('ai', '复核流程尚未完成，请等待分析完成后再进行结果确认。', true)
        return
      }
      
      addMessage('ai', '正在加载复核结果数据，准备进入结果确认阶段...', true)
      addComponentMessage('结果确认', {
        component: 'ResultConfirm',
        props: {
          eventId: workspaceStore.reviewProcess.currentEventId
        }
      })
    }
    
    // 关闭组件
    const closeComponent = (messageId) => {
      workspaceStore.removeChatMessageById(messageId)
      addMessage('ai', '已关闭当前功能，您可以继续与我对话或选择其他功能。', true)
    }
    
    // 模块事件处理
    const onModuleCompleted = (messageId, data) => {
      const msg = (workspaceStore.chatMessages || []).find(m => m.id === messageId)
      const moduleName = msg?.title
      workspaceStore.removeChatMessageById(messageId)
      if (moduleName && moduleName !== '补充底稿') {
        addMessage('ai', `${moduleName}已完成，您可以继续其他操作。`, true)
      }
    }
    
    // 处理默认复核设置更新事件 - 当用户保存设置后触发
    const onSettingsUpdated = async (settings) => {
      try {
        console.log('智能体交互超时策略设置已更新:', settings)
        
        // 验证设置参数的合法性（预留验证逻辑位置）
        // TODO: 添加设置参数验证逻辑
        
        // 保存设置到数据库（通过workspace store）
        await workspaceStore.saveDefaultReviewSettings(settings)
        
        // 通知其他模块设置已更新
        await workspaceStore.onDefaultReviewSettingsUpdated(settings)
        
        // 记录设置变更历史
        await workspaceStore.addSettingsHistory({
          settings: settings,
          timestamp: new Date().toISOString(),
          action: 'update',
          description: '用户更新智能体交互超时处理策略'
        })
        
        // 记录设置更新事件到活动日志
        console.log('设置更新事件:', {
          type: 'settings_updated',
          message: '默认复核设置已更新',
          data: {
            timeout: settings.timeout,
            scenarios: Object.keys(settings.timeout.scenarios || {}),
            protection: settings.timeout.protection
          },
          timestamp: new Date().toISOString()
        })
        
        // 重置超时计数器，清除历史超时记录
        await workspaceStore.resetTimeoutCounter()
        
        addMessage('ai', '✅ 默认复核设置已更新！新的智能体交互超时策略将应用于该项目后续的所有复核流程。', true)
        
      } catch (error) {
        console.error('处理设置更新失败:', error)
        
        // 记录错误日志
        await workspaceStore.logWarning({
          type: 'settings_error',
          message: '设置更新失败',
          details: error.message,
          timestamp: new Date().toISOString()
        })
        
        addMessage('ai', '❌ 设置更新失败，请检查网络连接或稍后重试。如问题持续，请联系技术支持。', true)
      }
    }
    
    const onTimeoutReviewed = (data) => {
      console.log('超时回溯完成:', data)
      addMessage('ai', `超时回溯分析完成，已生成处理建议。`, true)
    }
    
    // 结果确认完成事件处理 - 用户完成结果确认和归档操作
    const onResultConfirmed = (confirmation) => {
      console.log('结果已确认:', confirmation)
      const { version, archiveId, adjustmentCount } = confirmation
      
      let message = `✅ 复核结果已确认并成功归档！`
      if (version) message += ` 版本号：${version}`
      if (archiveId) message += ` 归档ID：${archiveId}`
      if (adjustmentCount > 0) message += ` 包含${adjustmentCount}次调整记录`
      
      addMessage('ai', message, true)
      addMessage('ai', '复核工作已全部完成，您可以在项目管理中查看归档记录。感谢您的使用！', true)
    }
    
    // 结果调整事件处理 - 用户对复核结果进行调整时触发
    const onResultAdjusted = (adjustmentData) => {
      console.log('结果已调整:', adjustmentData)
      const { type, description, affectedSections } = adjustmentData
      
      if (type === 'regeneration') {
        addMessage('ai', `正在重新生成${affectedSections?.length || 0}个模块的复核结果...`, true)
      } else if (type === 'guided_adjustment') {
        addMessage('ai', `正在根据您的指导"${description}"调整复核结果...`, true)
      }
    }
    
    // 草稿保存事件处理 - 用户保存调整草稿时触发
    const onDraftSaved = (draftData) => {
      console.log('草稿已保存:', draftData)
      addMessage('ai', '✅ 当前调整已自动保存为草稿，您可以随时继续编辑。', true)
    }
    
    // 添加消息事件处理 - 子组件请求添加消息时触发
    const onAddMessage = (messageData) => {
      addMessage(messageData.type, messageData.content, true)
    }
    
    // ===== 文件请求处理逻辑 =====
    // 处理智能体的文件请求 - 当复核流程需要额外文件时触发
    const handleFileRequest = (requestedFiles) => {
      // 仅处理需要用户手动提供的文件
      const pendingFiles = requestedFiles.filter(f => f.status === 'pending')

      if (pendingFiles.length > 0) {
        const pendingTypes = pendingFiles.map(f => f.type).join('、')
        addMessage('ai', `复核过程中需要额外的底稿文件：${pendingTypes}。请选择相应文件或上传新文件。`, true)
        // 插入补充底稿组件，引导用户上传或选择文件
        addComponentMessage('补充底稿', 'SupplementDocuments')
      }
    }
    
    // 启动文件等待倒计时 - 给用户一定时间提供文件
    const startWaitingCountdown = () => {
      const waitTime = workspaceStore.fileRequest.defaultWaitTime / 1000  // 转换为秒
      let remainingTime = waitTime
      
      // 递归更新倒计时显示
      const updateCountdown = () => {
        if (remainingTime > 0 && isWaitingForFiles.value) {
          addMessage('ai', `等待文件提供中... 剩余时间：${remainingTime}秒`, true)
          remainingTime--
          waitingTimer.value = setTimeout(updateCountdown, 1000)
        } else if (remainingTime <= 0) {
          // 等待超时，使用现有文件继续
          addMessage('ai', '等待超时，将使用现有文件继续复核流程。', true)
        }
      }
      
      updateCountdown()
    }
    
    // 提供请求的文件 - 用户选择文件后调用
    const provideFile = (fileId, fileInfo) => {
      // 通知workspace store文件已提供
      workspaceStore.provideRequestedFile(fileId, fileInfo)
      addMessage('ai', `已接收文件：${fileInfo.name}，继续复核流程。`, true)
      
      // 清除等待计时器
      if (waitingTimer.value) {
        clearTimeout(waitingTimer.value)
        waitingTimer.value = null
      }
    }
    
    // 跳过请求的文件 - 用户选择不提供某个文件
    const skipFile = (fileId, reason = '') => {
      // 通知workspace store跳过该文件
      workspaceStore.skipRequestedFile(fileId, reason)
      addMessage('ai', `已跳过文件，将使用现有文件继续复核。${reason ? '原因：' + reason : ''}`, true)
    }
    
    // 使用现有文件继续 - 用户选择不提供任何额外文件
    const continueWithoutFiles = () => {
      // 清理文件请求并恢复复核流程（后端驱动）
      workspaceStore.clearFileRequest()
      workspaceStore.resumeReviewProcess()
      addMessage('ai', '继续使用现有文件进行复核。', true)
      
      // 清除等待计时器
      if (waitingTimer.value) {
        clearTimeout(waitingTimer.value)
        waitingTimer.value = null
      }
    }
    
    // ===== 异常处理方法 =====
    // 网络错误处理 - 显示友好的错误提示并提供重试功能
    const handleNetworkError = (error) => {
      console.error('网络请求失败:', error)
      showNetworkError.value = true
      networkRetryCount.value++
      
      // 添加错误消息到聊天记录
      chatMessages.value.push({
        id: Date.now(),
        status: reviewStatus,        
        type: 'system',
        content: `网络连接异常，请检查网络状态。这是第${networkRetryCount.value}次重试。`,
        isvaluable: false,
        timestamp: new Date(),
        isError: true
      })
    }
    
    // 重试网络请求
    const retryNetworkRequest = async () => {
      showNetworkError.value = false
      try {
        // 这里可以重新执行失败的请求
        ElMessage.success('正在重试请求...')
      } catch (error) {
        handleNetworkError(error)
      }
    }
    
    // 启动用户指引
    const startUserGuide = () => {
      if (userGuideRef.value) {
        userGuideRef.value.startGuide()
      }
    }
    
    // ===== 计算属性 - 文件等待进度 =====
    // 计算文件等待的进度百分比 - 用于显示等待进度条
    const progressPercentage = computed(() => {
      if (!isWaitingForFiles.value) return 0
      
      // 计算已等待时间
      const elapsed = Date.now() - (workspaceStore.fileRequest.waitStartTime || Date.now())
      const total = workspaceStore.fileRequest.defaultWaitTime
      
      // 返回0-100之间的百分比
      return Math.max(0, Math.min(100, (elapsed / total) * 100))
    })
    
    // ===== 生命周期钩子 =====
    // 组件挂载时的初始化逻辑 - 设置监听器和加载初始数据
    onMounted(async () => {
      try {
        workspaceStore.setFunctionalArea('workbench')
        const latest = workspaceStore.getLatestSession?.()
        if (latest && latest.projectId) {
          workspaceStore.setProjectId(latest.projectId)
        }
        // 并行加载各个模块的初始数据
        await Promise.all([
          documentStore.fetchDocuments?.(),   // 加载已上传的文档列表
          eventStore.fetchEvents?.(),         // 加载操作事件历史
          messageStore.fetchMessages?.()      // 加载历史消息记录
        ])

        // 规范化刷新后持久化的组件消息，避免对象组件导致渲染失败
        try {
          const msgs = workspaceStore.chatMessages || []
          msgs.forEach(m => {
            if (m && m.title === '文件入口消息') {
              if (!m.component || typeof m.component !== 'string') {
                m.component = 'Filecheck'
              }
              if (!m.props) {
                m.props = { userInput: '复核内容', standardReady: false }
              }
            }
          })
        } catch (_) {}

        // 刷新恢复：如存在待回填的标准消息，则自动回填并推进进度
        const recoverResult = await workspaceStore.recoverStandardIfPending()
        if (recoverResult?.success && (recoverResult.data?.审计证据标准 || recoverResult.data)) {
          const standard = recoverResult.data?.审计证据标准 || recoverResult.data
          const queryText = recoverResult.request?.content || '复核内容'

          // 提示生成完成与复核启动
          setTimeout(() => {
            addMessage('ai', '✅ 复核标准生成完成！正在启动复核流程...', false)
            addMessage('ai', '🔍 复核流程已启动，正在分析复核内容...', false)
          }, 1000)

          const reviewData = buildReviewDataFromStandard(queryText, standard)

          setTimeout(async () => {
            try {
              const reviewResponse = await workspaceStore.executeReview(reviewData)
              handleBackendResponse(reviewResponse.data)
            } catch (reviewError) {
              console.error('启动复核流程失败(恢复后):', reviewError)
              addMessage('ai', '❌ 启动复核流程失败，请稍后重试。', false)
            }
          }, 5000)
        }

        // 处理从CreateMajorEvent返回的查询参数
        const action = route.query.action
        const eventId = route.query.eventId
        
        if (action === 'start-review' && eventId) {
          // 从创建页面返回并启动复核
          try {
            // 确保工作区上下文与当前项目一致
            ensureWorkspaceProjectContext()
            workspaceStore.startSession({ projectId: currentProject.value?.id || 'default', functionalArea: 'workbench', eventId })
            // 刷新事项数据以获取最新创建的事项
            await eventStore.fetchMajorEvents?.()
            
            // 获取刚创建的事项详情
            const createdEvent = eventStore.getMajorEventById(eventId)
            if (createdEvent) {
              // 显示事项详情
              const eventDetails = `🎉 重大事项创建成功！

📋 事项详情：

📝 重大事项概述：
${createdEvent.description || '暂无概述'}

🎯 审计目标：
${createdEvent.auditObjectives || '暂无审计目标'}

⚡ 正在启动复核流程...`
              addMessage('ai', eventDetails)

              // 将新创建的事项同步到工作区项目隔离存储并规范化
              syncCreatedEventToWorkspace(createdEvent)
            } else {
              addMessage('ai', `✅ 重大事项创建成功！正在启动复核流程...`)
            }
            
            await workspaceStore.setCurrentReviewEvent({ id: eventId })
            
            // 启动复核流程
            const result = await workspaceStore.startMajorEventReview(eventId)
            if (result.success) {
              addMessage('ai', `🔍 复核流程已启动，正在分析重大事项`)
              
              // 处理后端返回的响应数据（兼容不同返回字段）
              const engineResp = (result?.data?.engineResponse) || (result?.data?.backendResponse) || result?.data
              if (engineResp) {
                handleBackendResponse(engineResp)
              } else {
                // 如果没有结构化响应，提示并记录
                console.warn('复核已启动，但未收到结构化响应数据', result)
                addMessage('ai', 'ℹ️ 复核已启动，等待引擎返回下一步指引...')
              }
            } else {
              addMessage('ai', `❌ 复核启动失败：${result.message}`)
            }
          } catch (error) {
            console.error('启动复核失败:', error)
            addMessage('ai', '❌ 复核启动失败，请稍后重试。')
          }
        } else if (action === 'cancel-review') {
          // 从创建页面返回但取消复核
          try {
            // 确保工作区上下文与当前项目一致
            ensureWorkspaceProjectContext()
            // 刷新事项数据以获取最新创建的事项
            await eventStore.fetchMajorEvents?.()
            
            // 获取刚创建的事项详情
            if (eventId) {
              const createdEvent = eventStore.getMajorEventById(eventId)
              if (createdEvent) {
                // 显示事项详情
                const eventDetails = `🎉 **重大事项创建成功！**

📋 **事项详情：**

📝 **重大事项概述：**
${createdEvent.description || '暂无概述'}

🎯 **审计目标：**
${createdEvent.auditObjectives || '暂无审计目标'}

⏸️ 已取消复核，您可以稍后在事项管理中进行复核。`
                  addMessage('ai', eventDetails)

                  // 即便取消复核，也同步到工作区项目隔离存储，方便后续复核
                  syncCreatedEventToWorkspace(createdEvent)
              } else {
                addMessage('ai', '✅ 重大事项创建成功！已取消复核，您可以稍后在事项管理中进行复核。')
              }
            } else {
              addMessage('ai', '✅ 重大事项创建成功！已取消复核，您可以稍后在事项管理中进行复核。')
            }
          } catch (error) {
            console.error('获取事项详情失败:', error)
            addMessage('ai', '✅ 重大事项创建成功！已取消复核，您可以稍后在事项管理中进行复核。')
          }
        }
        
        // ===== 响应式监听器设置 =====
        // 监听文件请求状态变化 - 当复核流程需要额外文件时触发
        watch(
          () => workspaceStore.fileRequest.requestedFiles,
          (newFiles, oldFiles) => {
            // 检查是否有新的文件请求（从无到有）
            if (newFiles.length > 0 && (!oldFiles || oldFiles.length === 0)) {
              handleFileRequest(newFiles)
            }
          },
          { deep: true }  // 深度监听数组内对象的变化
        )
        
        // 监听警告日志变化（仅显示错误和警告信息）
        watch(
          () => workspaceStore.fileRequest.warningLogs,
          (newLogs, oldLogs) => {
            // 检查是否有新增的日志条目
            if (newLogs.length > (oldLogs?.length || 0)) {
              const latestLog = newLogs[newLogs.length - 1]
              // 显示警告或错误信息给用户
              addMessage('ai', `⚠️ ${latestLog.message}`)
            }
          },
          { deep: true }  // 深度监听数组变化
        )
        
        // 监听复核流程状态变化（移除completed状态的重复提示，保留暂停/恢复提示）
        watch(
          () => workspaceStore.reviewProcess.status,
          (newStatus, oldStatus) => {
            if (newStatus === 'paused' && oldStatus === 'running') {
              addMessage('ai', '⏸️ 复核流程已暂停，等待用户操作。')
            } else if (newStatus === 'running' && oldStatus === 'paused') {
              addMessage('ai', '▶️ 复核流程已恢复，继续处理中...')
            }
          }
        )
        
      } catch (error) {
        console.error('初始化数据失败:', error)
      }
      
      // 检查是否为首次使用，如果是则启动用户指引
      const isFirstTime = localStorage.getItem('cpa_first_time_user')
      if (!isFirstTime) {
        setTimeout(() => {
          startUserGuide()
          localStorage.setItem('cpa_first_time_user', 'false')
        }, 1000) // 延迟1秒启动指引，确保页面完全加载
      }
      
      // 监听复核结束事件
      const handleReviewCompleted = (event) => {
        const { version } = event.detail
        addMessage('ai', `✅ 复核结果已确认并成功归档！版本号：${version}`)
        addMessage('ai', '复核工作已全部完成，您可以在项目管理中查看归档记录。感谢您的使用！')
      }
      
      window.addEventListener('reviewCompleted', handleReviewCompleted)
      
      // 组件卸载时移除事件监听器
      onUnmounted(() => {
        window.removeEventListener('reviewCompleted', handleReviewCompleted)
      })
    })
    
    // ===== 返回组件接口 =====
    // 将所有响应式数据、计算属性和方法暴露给模板使用
    return {
      // ===== 响应式数据 =====
      currentProject,               // 当前项目信息（计算属性）
      agentStatus,                  // 智能体状态（计算属性）
      userInput,                    // 用户输入内容
      isProcessing,                 // 智能体处理状态
      chatMessages,                 // 聊天消息列表
      messagesContainer,            // 消息容器DOM引用
      isWaitingForFiles,            // 是否等待文件（计算属性）
      requestedFiles,               // 请求的文件列表（计算属性）
      progressPercentage,           // 文件等待进度百分比（计算属性）
      
      // ===== 工具方法 =====
      getStatusText,                // 获取项目状态文本
      formatTime,                   // 格式化时间显示
      
      // ===== 消息处理方法 =====
      sendMessage,                  // 发送用户消息
      addComponentMessage,          // 添加组件消息
      
      // ===== 快捷操作方法 =====
      showDefaultSettings,          // 显示默认复核设置
      executeReview,                // 执行复核流程
      showSupplementDialog,         // 显示补充底稿对话框
      showTimeoutReview,            // 显示超时回溯界面
      showReviewProgress,           // 显示复核进度界面
      reviewStatus,                 // 复核状态
      reviewStages,                 // 复核阶段列表
      currentStage,                 // 当前复核阶段
      showResultConfirm,            // 显示结果确认界面
      closeComponent,               // 关闭功能组件
      
      // ===== 模块事件处理方法 =====
      onModuleCompleted,            // 模块完成事件处理
      onSettingsUpdated,            // 设置更新事件处理
      onFilesUploaded,              // 文件上传事件处理
      onTimeoutReviewed,            // 超时回溯事件处理
      onResultConfirmed,            // 结果确认事件处理
      onResultAdjusted,             // 结果调整事件处理
      onDraftSaved,                 // 草稿保存事件处理
      onReviewStarted,              // 复核启动事件处理
      onEventCreated,               // 事项创建事件处理
      onAddMessage,                 // 添加消息事件处理
      
      // ===== ConfirmReviewContent事件处理方法 =====
      onConfirmReviewContent,   // 确认复核内容事件处理
      onCancelReviewContent,    // 取消复核内容事件处理
      onOpenStandard,           // 打开复核标准侧边栏
      onOpenExcel,              // 打开信息定位侧边栏（Excel）
      
      // ===== 文件请求处理方法 =====
      provideFile,                  // 提供请求的文件
      skipFile,                     // 跳过请求的文件
      continueWithoutFiles,         // 不提供文件继续流程
      
      // ===== 用户体验相关 =====
      userGuideRef,                 // 用户指引组件引用
      guideSteps,                   // 用户指引步骤配置
      showNetworkError,             // 网络错误提示状态
      networkRetryCount,            // 网络重试次数
      showLogicWarning,             // 逻辑矛盾警告状态
      logicWarningMessage,          // 逻辑矛盾警告信息
      // ===== 复核标准侧边栏 =====
      sidebarVisible,              // 复核标准侧边栏可见性
      sidebarTitle,                // 复核标准侧边栏标题
      sidebarContent,              // 复核标准侧边栏内容
      sidebarComponent,            // 侧边栏动态组件
      sidebarComponentProps,       // 侧边栏动态组件属性
      startUserGuide,               // 启动用户指引
      handleNetworkError,           // 处理网络错误
      retryNetworkRequest,          // 重试网络请求
    }
  }
}
</script>

<style scoped>
.workbench-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

/* 对话界面容器 */
.chat-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  margin: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* AI头部信息 */
.ai-header {
  background: rgba(102, 126, 234, 0.08);
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
  color: #4a5568;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 60px;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
  flex-shrink: 0;
}

.ai-info {
  flex: 1;
  min-width: 0;
}

.ai-info h3 {
  margin: 0 0 2px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.ai-status {
  margin: 0;
  font-size: 12px;
  color: #718096;
  opacity: 0.8;
}

.project-info {
  text-align: right;
  flex-shrink: 0;
}

.project-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 3px;
  color: #4a5568;
}

.project-status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.project-status.active {
  background: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #4caf50;
}

.project-status.completed {
  background: #e3f2fd;
  color: #1565c0;
  border: 1px solid #2196f3;
}

.project-status.pending {
  background: #fff3e0;
  color: #ef6c00;
  border: 1px solid #ff9800;
}

.project-status.paused {
  background: #fce4ec;
  color: #c2185b;
  border: 1px solid #e91e63;
}

/* 对话消息区域 */
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: calc(100vh - 400px);
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-item.ai .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-item.user .message-avatar {
  background: #e3f2fd;
  color: #1976d2;
}

.message-content {
  max-width: 70%;
  background: #f5f5f5;
  border-radius: 18px;
  padding: 12px 16px;
  position: relative;
  white-space: pre-wrap;
}

.message-item.ai .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-item.user .message-content {
  background: #e3f2fd;
  color: #1976d2;
}

.message-text {
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  margin: 0;
}

/* 功能快捷按钮 */
.quick-actions {
  padding: 15px 20px;
  border-top: 1px solid #e1e8ed;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-start;
}

.action-btn {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  color: #333;
  min-width: auto;
  white-space: nowrap;
}

.action-btn:hover {
  border-color: #667eea;
  background: #f8f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.btn-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.btn-text {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.2;
}

/* 对话输入框 */
.chat-input-area {
  padding: 20px;
  border-top: 1px solid #e1e8ed;
  background: #f8f9fa;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e1e8ed;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s ease;
}

.chat-input:focus {
  border-color: #667eea;
}

.chat-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

/* 组件消息样式 */
.message-component {
  width: 100%;
  max-width: none;
}

.component-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px 8px 0 0;
  margin-bottom: 12px;
}

.component-title {
  font-weight: 600;
  font-size: 14px;
}

.close-component-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-component-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 调整组件消息的内容样式 */
.message-item.ai .message-content:has(.message-component) {
  max-width: 90%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 18px;
  padding: 0;
  overflow: hidden;
}

.message-item.ai .message-component {
  padding: 16px;
  background: white;
  color: #333;
  border-radius: 0 0 18px 18px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-interface {
    margin: 10px;
  }
  
  .ai-header {
    padding: 10px 12px;
    gap: 10px;
    min-height: 50px;
  }
  
  .ai-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .ai-info h3 {
    font-size: 14px;
  }
  
  .ai-status {
    font-size: 11px;
  }
  
  .project-name {
    font-size: 13px;
  }
  
  .project-status {
    font-size: 10px;
    padding: 2px 6px;
  }
  
  .chat-messages {
    padding: 15px;
    max-height: calc(100vh - 450px);
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .quick-actions {
    padding: 12px 15px;
    gap: 6px;
  }
  
  .action-btn {
    padding: 6px 10px;
  }
  
  .btn-icon {
    font-size: 14px;
  }
  
  .btn-text {
    font-size: 12px;
  }
  
  .chat-input-area {
    padding: 15px;
  }
}
/* 文件请求对话框样式 */
.file-request-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.file-request-dialog {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.dialog-content {
  padding: 20px;
}

.requested-files-list {
  list-style: none;
  padding: 0;
  margin: 15px 0;
}

.requested-file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 10px;
  background: #f9f9f9;
}

.file-type {
  font-weight: bold;
  color: #2196F3;
  margin-right: 10px;
}

.file-description {
  flex: 1;
  color: #666;
  margin-right: 15px;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.waiting-info {
  margin-top: 20px;
  padding: 15px;
  background: #f0f8ff;
  border-radius: 6px;
  border-left: 4px solid #2196F3;
}

.countdown-text {
  margin: 0 0 10px 0;
  color: #333;
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2196F3, #21CBF3);
  transition: width 0.3s ease;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #f9f9f9;
}

.btn-primary {
  background: #2196F3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-primary:hover {
  background: #1976D2;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

/* 异常处理UI样式 */
.network-error-alert,
.logic-warning-alert {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slideInRight 0.3s ease-out;
}

.network-error-alert {
  border-left: 4px solid #dc3545;
}

.logic-warning-alert {
  border-left: 4px solid #ffc107;
}

.alert-content {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  gap: 12px;
}

.alert-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.alert-text {
  flex: 1;
}

.alert-text h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #333;
}

.alert-text p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.alert-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.alert-actions .btn-primary,
.alert-actions .btn-secondary {
  padding: 6px 12px;
  font-size: 12px;
  min-width: 60px;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>