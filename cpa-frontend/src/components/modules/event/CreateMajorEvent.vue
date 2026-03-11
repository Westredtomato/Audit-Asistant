<!--
  重大事项创建组件
  - 提供两种创建方式：直接创建和基于模板创建
  - 支持复杂的表单结构，包括重大事项概述、审计目标、审计证据标准
  - 集成表单验证、草稿保存、创建向导等功能
  - 与状态管理系统深度集成，实现数据的持久化和同步
-->
<template>
  <div class="create-major-event">
    <!-- 主表单界面 -->
    <div v-if="currentStep === 'form'" class="form-container">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M19 12H5M12 19L5 12L12 5"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            返回
          </button>
          <h1>创建重大事项</h1>
        </div>
        <div class="header-actions">
          <button
            class="mode-select-btn"
            @click="showModeSelectionModal = true"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 5V19M5 12H19"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            选择创建方式
          </button>
        </div>
      </div>

      <!-- 模板选择界面 -->
      <div v-if="currentStep === 'selectTemplate'" class="template-selection">
        <div class="header">
          <div class="header-left">
            <button class="back-btn" @click="backToModeSelection">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M19 12H5M12 19L5 12L12 5"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              返回
            </button>
            <h1>选择模板</h1>
          </div>
        </div>

        <div class="template-container">
          <div v-if="templatesLoading" class="loading">加载模板中...</div>
          <div v-else-if="templates.length === 0" class="no-templates">
            <p>暂无可用模板</p>
            <button @click="selectCreationMode('direct')" class="btn-primary">
              直接创建
            </button>
          </div>
          <div v-else class="template-list">
            <div
              v-for="template in templates"
              :key="template.id"
              class="template-item"
              @click="selectTemplate(template)"
            >
              <h4>{{ template.name }}</h4>
              <p>{{ template.description }}</p>
              <div class="template-meta">
                <span>创建时间: {{ formatDate(template.createdAt) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 表单操作按钮 -->
      <div class="form-actions">
        <button class="draft-btn" @click="saveDraft" :disabled="loading">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path
              d="M19 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H16L21 8V19C21 20.1 20.1 21 19 21Z"
              stroke="currentColor"
              stroke-width="2"
            />
            <path d="M17 21V13H7V21" stroke="currentColor" stroke-width="2" />
            <path d="M7 3V8H15" stroke="currentColor" stroke-width="2" />
          </svg>
          保存草稿
        </button>
      </div>

      <!-- 表单容器 -->
      <div class="form-container">
        <form @submit.prevent="handleSubmit" class="event-form">
          <!-- 重大事项概述 -->
          <div class="form-section">
            <h3>重大事项概述 <span class="required">*</span></h3>
            <div class="form-group">
              <label>事项核心内容描述</label>
              <textarea
                v-model="form.title"
                placeholder="请输入重大事项的核心内容描述（必填）"
                rows="4"
                required
                class="form-control"
              ></textarea>
              <div v-if="errors.title" class="error-message">
                {{ errors.title }}
              </div>
            </div>
          </div>

          <!-- 审计目标 -->
          <div class="form-section">
            <h3>审计目标</h3>
            <div class="form-group">
              <label>审计目标描述</label>
              <textarea
                v-model="form.auditObjectives"
                placeholder="请输入审计目标的具体描述"
                rows="3"
                class="form-control"
              ></textarea>
            </div>
          </div>

          <!-- 审计证据标准 -->
          <div class="form-section">
            <h3>审计证据标准</h3>
            <div class="evidence-standards-container">
              <!-- 情况选择 -->
              <div class="situation-tabs">
                <button
                  v-for="(situation, key) in availableSituations"
                  :key="key"
                  type="button"
                  class="situation-tab"
                  :class="{ active: currentSituation === key }"
                  @click="switchSituation(key)"
                >
                  {{ situation.name }}
                </button>
              </div>

              <!-- 当前情况的内容 -->
              <div v-if="currentSituationData" class="situation-content">
                <!-- 审计结论 -->
                <div class="form-group">
                  <label>审计结论</label>
                  <textarea
                    v-model="currentSituationData.auditConclusion"
                    placeholder="请输入该情况下的审计结论"
                    rows="3"
                    class="form-control"
                  ></textarea>
                </div>

                <!-- 审计证据分类 -->
                <div class="evidence-categories">
                  <h4>审计证据分类与要求</h4>
                  <div
                    v-for="(
                      category, categoryIndex
                    ) in currentSituationData.evidenceCategories"
                    :key="categoryIndex"
                    class="evidence-category"
                  >
                    <div class="category-header">
                      <input
                        v-model="category.name"
                        type="text"
                        placeholder="请输入证据分类名称（如：风险评估及计划工作底稿）"
                        class="category-name-input form-control"
                      />
                      <button
                        type="button"
                        class="remove-category-btn"
                        @click="removeEvidenceCategory(categoryIndex)"
                      >
                        删除分类
                      </button>
                    </div>

                    <!-- 二级分类 -->
                    <div
                      v-for="(
                        subcategory, subcategoryIndex
                      ) in category.subcategories"
                      :key="subcategoryIndex"
                      class="evidence-subcategory"
                    >
                      <div class="subcategory-header">
                        <input
                          v-model="subcategory.name"
                          type="text"
                          placeholder="请输入二级分类名称（如：了解被审计单位及其环境）"
                          class="subcategory-name-input form-control"
                        />
                        <button
                          type="button"
                          class="remove-subcategory-btn"
                          @click="
                            removeSubcategory(categoryIndex, subcategoryIndex)
                          "
                        >
                          删除二级分类
                        </button>
                      </div>

                      <!-- 证据条目 -->
                      <div class="evidence-items">
                        <div
                          v-for="(item, itemIndex) in subcategory.items"
                          :key="itemIndex"
                          class="evidence-item"
                        >
                          <div class="form-group">
                            <label>证据内容描述</label>
                            <input
                              v-model="item.content"
                              placeholder="请输入具体证据内容描述"
                              class="form-control"
                            />
                          </div>
                          <div class="form-group">
                            <label>质量要求说明</label>
                            <textarea
                              v-model="item.qualityRequirement"
                              placeholder="请输入对应的质量要求说明"
                              rows="3"
                              class="form-control"
                            ></textarea>
                          </div>
                          <button
                            type="button"
                            class="remove-item-btn"
                            @click="
                              removeEvidenceItem(
                                categoryIndex,
                                subcategoryIndex,
                                itemIndex
                              )
                            "
                          >
                            删除条目
                          </button>
                        </div>
                        <button
                          type="button"
                          class="add-item-btn"
                          @click="
                            addEvidenceItem(categoryIndex, subcategoryIndex)
                          "
                        >
                          + 添加证据条目
                        </button>
                      </div>
                    </div>

                    <button
                      type="button"
                      class="add-subcategory-btn"
                      @click="addSubcategory(categoryIndex)"
                    >
                      + 添加二级分类
                    </button>
                  </div>
                  <button
                    type="button"
                    class="add-category-btn"
                    @click="addEvidenceCategory"
                  >
                    + 添加证据分类
                  </button>
                </div>

                <!-- 充分、适当评判标准 -->
                <div class="form-group">
                  <label>充分、适当评判标准</label>
                  <textarea
                    v-model="currentSituationData.adequacyCriteria"
                    placeholder="请输入充分、适当评判标准（如：若审计记录中覆盖所有证据，且均达到设定质量要求时，则认为审计结论的审计证据充分、适当）"
                    rows="3"
                    class="form-control"
                  ></textarea>
                </div>

                <!-- 标准制定依据 -->
                <div class="form-group">
                  <label>标准制定依据</label>
                  <div
                    v-for="(basis, basisIndex) in form.evidenceStandards
                      .standardBasis"
                    :key="basisIndex"
                    class="standard-basis-item"
                  >
                    <div class="basis-row">
                      <div class="basis-field">
                        <label>条文</label>
                        <input
                          v-model="basis.clause"
                          type="text"
                          placeholder="请输入相关条文"
                          class="form-control"
                        />
                      </div>
                      <div class="basis-field">
                        <label>内容</label>
                        <textarea
                          v-model="basis.content"
                          placeholder="请输入条文内容"
                          rows="2"
                          class="form-control"
                        ></textarea>
                      </div>
                    </div>
                    <div class="basis-row">
                      <div class="basis-field full-width">
                        <label>应用</label>
                        <textarea
                          v-model="basis.application"
                          placeholder="请输入应用说明（如：被审计单位属于持续审计情况，属于……类型企业，根据……适用）"
                          rows="2"
                          class="form-control"
                        ></textarea>
                      </div>
                      <button
                        type="button"
                        class="remove-basis-btn"
                        @click="removeStandardBasis(basisIndex)"
                      >
                        删除
                      </button>
                    </div>
                  </div>

                  <button
                    type="button"
                    class="add-basis-btn"
                    @click="addStandardBasis"
                  >
                    + 添加标准制定依据
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 表单操作按钮 -->
          <div class="form-actions">
            <button
              type="button"
              class="btn-secondary"
              @click="saveDraft"
              :disabled="loading"
            >
              保存草稿
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              {{ loading ? "保存中..." : "保存" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 创建方式选择模态框 -->
    <div
      v-if="showModeSelectionModal"
      class="modal-overlay"
      @click="showModeSelectionModal = false"
    >
      <div class="modal-content mode-selection-modal" @click.stop>
        <div class="modal-header">
          <h2>选择创建方式</h2>
          <button class="close-btn" @click="showModeSelectionModal = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M18 6L6 18M6 6L18 18"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="creation-modes">
            <!-- 直接创建选项 -->
            <div class="creation-mode" @click="selectCreationMode('direct')">
              <div class="mode-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M12 2L2 7L12 12L22 7L12 2Z"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M2 17L12 22L22 17"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M2 12L12 17L22 12"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <h3>直接创建</h3>
              <p>从空白表单开始创建重大事项，手动填写所有必填字段和可选字段</p>
            </div>

            <!-- 模板创建选项 -->
            <div class="creation-mode" @click="selectCreationMode('template')">
              <div class="mode-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M14 2V8H20"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <h3>由模板创建</h3>
              <p>基于预设模板快速创建重大事项，可修改模板内容（功能开发中）</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存成功确认对话框 -->
    <div
      v-if="showSaveConfirmDialog"
      class="modal-overlay"
      @click="handleDialogClose"
    >
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>保存成功</h2>
          <button class="close-btn" @click="handleDialogClose">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M18 6L6 18M6 6L18 18"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p>重大事项已成功保存到重大事项列表中。</p>
          <p>是否执行复核？</p>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="returnToList">否</button>
          <button class="btn-primary" @click="startReview">是</button>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      <p>{{ error }}</p>
      <button @click="clearError">关闭</button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useEventStore } from "@/stores/event";

export default {
  name: "CreateMajorEvent",
  setup() {
    const router = useRouter();
    const eventStore = useEventStore();

    // 响应式数据
    const currentStep = ref("form"); // form, selectTemplate
    const showModeSelectionModal = ref(false);
    const selectedCreationMode = ref(""); // direct, template
    const selectedTemplate = ref(null);
    const templates = ref([]);
    const templatesLoading = ref(false);
    const loading = ref(false);
    const error = ref("");
    const errors = reactive({});
    const showSaveConfirmDialog = ref(false);
    const savedEventId = ref("");

    // 表单数据 - 基于重大事项内容与复核设置.json结构
    const form = reactive({
      title: "", // 重大事项概述
      auditObjectives: "", // 审计目标
      evidenceStandards: {
        situation1: {
          auditConclusion: "", // 审计结论
          evidenceCategories: [], // 审计证据分类与要求
          adequacyCriteria: "", // 充分、适当评判标准
        },
        situation2: {
          auditConclusion: "", // 审计结论
          evidenceCategories: [], // 审计证据分类与要求
          adequacyCriteria: "", // 充分、适当评判标准
        },
        standardBasis: [], // 标准制定依据
      },
    });

    // 当前选中的情况
    const currentSituation = ref("situation1");

    // 可用情况
    const availableSituations = {
      situation1: { name: "情况一" },
      situation2: { name: "情况二" },
    };

    // 计算属性
    const currentSituationData = computed(() => {
      return form.evidenceStandards[currentSituation.value];
    });

    // 方法
    const goBack = () => {
      router.go(-1);
    };

    const selectCreationMode = async (mode) => {
      selectedCreationMode.value = mode;
      showModeSelectionModal.value = false;
      if (mode === "direct") {
        initializeDirectForm();
      } else if (mode === "template") {
        currentStep.value = "selectTemplate";
        await loadTemplates();
      }
    };

    const backToModeSelection = () => {
      currentStep.value = "form";
      selectedCreationMode.value = "";
      selectedTemplate.value = null;
    };

    const backToPreviousStep = () => {
      if (selectedCreationMode.value === "template") {
        currentStep.value = "selectTemplate";
      } else {
        currentStep.value = "form";
      }
    };

    const loadTemplates = async () => {
      try {
        templatesLoading.value = true;
        await eventStore.fetchMajorEventTemplates();
        templates.value = eventStore.majorEventTemplates;
      } catch (err) {
        error.value = "加载模板失败";
        console.error("Error loading templates:", err);
      } finally {
        templatesLoading.value = false;
      }
    };

    const selectTemplate = (template) => {
      selectedTemplate.value = template;
      currentStep.value = "form";
      initializeFormFromTemplate(template);
    };

    const initializeDirectForm = () => {
      // 初始化空白表单 - 提供默认的证据分类结构
      form.evidenceStandards.situation1.evidenceCategories = [
        {
          name: "风险评估及计划工作底稿",
          subcategories: [
            {
              name: "了解被审计单位及其环境",
              items: [],
            },
            {
              name: "了解财务业绩衡量",
              items: [],
            },
            {
              name: "本年度财务报表",
              items: [],
            },
          ],
        },
        {
          name: "控制测试工作底稿",
          subcategories: [
            {
              name: "了解和评价被审计单位风险评估过程",
              items: [],
            },
          ],
        },
      ];
      form.evidenceStandards.standardBasis = [
        {
          clause: "",
          content: "",
          application: "",
        },
      ];
    };

    const initializeFormFromTemplate = (template) => {
      // 从模板初始化表单
      if (template.template) {
        form.title = template.template.title || "";
        form.auditObjectives = template.template.auditObjectives || "";
        // TODO: 根据模板数据初始化审计证据标准
      }
    };

    const switchSituation = (situationKey) => {
      currentSituation.value = situationKey;
    };

    const addEvidenceCategory = () => {
      currentSituationData.value.evidenceCategories.push({
        name: "",
        subcategories: [
          {
            name: "",
            items: [],
          },
        ],
      });
    };

    const removeEvidenceCategory = (categoryIndex) => {
      currentSituationData.value.evidenceCategories.splice(categoryIndex, 1);
    };

    const addSubcategory = (categoryIndex) => {
      currentSituationData.value.evidenceCategories[
        categoryIndex
      ].subcategories.push({
        name: "",
        items: [],
      });
    };

    const removeSubcategory = (categoryIndex, subcategoryIndex) => {
      currentSituationData.value.evidenceCategories[
        categoryIndex
      ].subcategories.splice(subcategoryIndex, 1);
    };

    const addEvidenceItem = (categoryIndex, subcategoryIndex) => {
      currentSituationData.value.evidenceCategories[
        categoryIndex
      ].subcategories[subcategoryIndex].items.push({
        content: "",
        qualityRequirement: "",
      });
    };

    const removeEvidenceItem = (categoryIndex, subcategoryIndex, itemIndex) => {
      currentSituationData.value.evidenceCategories[
        categoryIndex
      ].subcategories[subcategoryIndex].items.splice(itemIndex, 1);
    };

    const addStandardBasis = () => {
      form.evidenceStandards.standardBasis.push({
        clause: "",
        content: "",
        application: "",
      });
    };

    const removeStandardBasis = (index) => {
      form.evidenceStandards.standardBasis.splice(index, 1);
    };

    const validateForm = () => {
      const newErrors = {};

      // 只验证最基本的必填字段
      // 验证重大事项概述
      if (!form.title.trim()) {
        newErrors.title = "重大事项概述不能为空";
        return false;
      }

      console.log("基本验证通过，重大事项概述已填写");

      Object.assign(errors, newErrors);
      return true;
    };

    const saveDraft = async () => {
      try {
        loading.value = true;

        // 检查网络连接状态
        if (!navigator.onLine) {
          error.value = "网络连接已断开，草稿将保存到本地";
        }

        // 验证必要字段
        if (!form.title.trim()) {
          error.value = "重大事项概述不能为空，无法保存草稿";
          return;
        }

        const draftData = {
          title: form.title,
          description: form.title, // 使用title作为description
          auditObjectives: form.auditObjectives,
          auditEvidenceStandards: form.evidenceStandards,
          isDraft: true,
          lastModified: new Date().toISOString(),
          draftId: `draft_${Date.now()}`, // 生成唯一草稿ID
        };

        await eventStore.saveMajorEventDraft(draftData);

        // 同时保存到localStorage作为备份
        localStorage.setItem("majorEventDraft", JSON.stringify(draftData));

        // 显示成功提示
        alert("草稿保存成功");

        // 自动保存提示
        setTimeout(() => {
          if (!error.value) {
            console.log("系统将每5分钟自动保存草稿");
          }
        }, 2000);
      } catch (err) {
        console.error("Error saving draft:", err);

        // 根据错误类型提供不同的处理建议
        if (
          err.message &&
          (err.message.includes("network") || err.message.includes("fetch"))
        ) {
          error.value = "网络连接异常，请检查网络后重试";
        } else if (
          err.message &&
          (err.message.includes("storage") || err.message.includes("quota"))
        ) {
          error.value = "本地存储空间不足，请清理浏览器缓存后重试";
        } else if (err.message && err.message.includes("validation")) {
          error.value = "数据验证失败，请检查表单内容后重试";
        } else {
          error.value = "保存草稿失败，请稍后重试";
        }

        // 提供重试选项
        if (confirm("草稿保存失败，是否立即重试？")) {
          setTimeout(() => saveDraft(), 1000); // 延迟1秒后重试
        }
      } finally {
        loading.value = false;
      }
    };

    const handleSubmit = async () => {
      console.log("handleSubmit 方法被调用");
      try {
        loading.value = true;
        clearError();

        // 检查网络连接
        if (!navigator.onLine) {
          error.value = "网络连接已断开，请检查网络连接后重试";
          return;
        }

        // 1. 表单验证
        console.log("开始表单验证");
        const isValid = validateForm();
        console.log("表单验证结果:", isValid);
        if (!isValid) {
          console.log("表单验证失败，停止提交");
          return;
        }

        // 检查内容完整性
        if (!form.title.trim() || form.title.length < 10) {
          error.value =
            "重大事项概述内容过于简单，请补充必要信息（至少10个字符）";
          return;
        }

        // 检查是否包含敏感信息（简单示例）
        const sensitiveKeywords = ["密码", "账号", "身份证", "银行卡"];
        const hasSensitiveInfo = sensitiveKeywords.some(
          (keyword) =>
            form.title.includes(keyword) ||
            form.auditObjectives.includes(keyword)
        );

        if (hasSensitiveInfo) {
          const confirmed = confirm("检测到可能包含敏感信息，确认继续保存吗？");
          if (!confirmed) {
            return;
          }
        }

        // 2. 验证重大事项内容
        const validationResult = await eventStore.validateMajorEvent({
          title: form.title,
          description: form.title,
          auditObjectives: form.auditObjectives,
        });

        if (!validationResult.isValid) {
          error.value = `内容验证失败: ${validationResult.errors.join(", ")}`;
          return;
        }

        // 3. 检查审计依据符合性
        const complianceCheck = await eventStore.checkAuditComplianceAsync({
          title: form.title,
          auditObjectives: form.auditObjectives,
          evidenceStandards: form.evidenceStandards,
        });

        if (!complianceCheck.isCompliant) {
          error.value = `审计依据合规性检查失败: ${complianceCheck.warnings.join(
            ", "
          )}`;
          return;
        }

        // 4. 创建重大事项
        const eventData = {
          title: form.title,
          description: form.title,
          auditObjectives: form.auditObjectives,
          auditEvidenceStandards: form.evidenceStandards,
        };

        const newEvent = await eventStore.createMajorEvent(eventData);
        savedEventId.value = newEvent.id;
        showSaveConfirmDialog.value = true;

        // 清除localStorage中的草稿数据
        localStorage.removeItem("majorEventDraft");

        // 停止自动保存
        stopAutoSave();
      } catch (err) {
        console.error("Error creating major event:", err);

        // 根据错误类型提供具体的错误信息和解决建议
        if (err.message && err.message.includes("network")) {
          error.value = "网络连接异常，请检查网络连接或稍后再试";
        } else if (err.message && err.message.includes("timeout")) {
          error.value = "请求超时，服务器响应缓慢，请稍后重试";
        } else if (err.message && err.message.includes("database")) {
          error.value = "数据库连接失败，请联系系统管理员或稍后重试";
        } else if (err.message && err.message.includes("validation")) {
          error.value = "数据验证失败，请检查表单内容是否完整和正确";
        } else if (err.message && err.message.includes("permission")) {
          error.value = "权限不足，请联系系统管理员获取相应权限";
        } else {
          error.value = err.message || "创建重大事项时发生未知错误，请稍后重试";
        }

        // 提供重试选项
        setTimeout(() => {
          if (confirm("保存失败，是否重试？")) {
            handleSubmit();
          }
        }, 2000);
      } finally {
        loading.value = false;
      }
    };

    const startReview = () => {
      showSaveConfirmDialog.value = false;
      // 用户希望立即开始复核刚创建的重大事项
      // 检查是否从工作台跳转而来
      const returnToWorkbench = sessionStorage.getItem("returnToWorkbench");

      if (returnToWorkbench === "true") {
        // 清除sessionStorage标记
        sessionStorage.removeItem("returnToWorkbench");
        sessionStorage.removeItem("createMode");

        // 是，跳转回工作台并启动复核流程
        router.push({
          name: "Workbench",
          query: {
            action: "start-review",
            eventId: savedEventId.value,
          },
        });
      } else {
        // 不是（从重大事项而来），跳转到工作台并启动
        router.push({
          name: "Workbench",
          query: {
            action: "start-review",
            eventId: savedEventId.value,
          },
        });
      }
    };

    const returnToList = () => {
      showSaveConfirmDialog.value = false;
      // 用户不希望立即开始复核刚创建的重大事项
      // 检查是否从工作台跳转而来
      const returnToWorkbench = sessionStorage.getItem("returnToWorkbench");

      if (returnToWorkbench === "true") {
        // 清除sessionStorage标记
        sessionStorage.removeItem("returnToWorkbench");
        sessionStorage.removeItem("createMode");

        // 是，跳转回工作台，显示取消复核消息
        router.push({
          name: "Workbench",
          query: {
            action: "cancel-review",
            eventId: savedEventId.value,
          },
        });
      } else {
        // 否，返回重大事项列表
        router.push({
          name: "MajorEventsList",
          query: {
            refresh: "true",
          },
        });
      }
    };

    // 处理对话框关闭事件（点击关闭按钮或遮罩层）
    const handleDialogClose = () => {
      // 关闭对话框时的行为与点击"否"按钮相同
      returnToList();
    };

    const clearError = () => {
      error.value = "";
      Object.keys(errors).forEach((key) => {
        delete errors[key];
      });
    };

    const formatDate = (dateString) => {
      if (!dateString) return "";
      return new Date(dateString).toLocaleDateString("zh-CN");
    };

    // 自动保存草稿功能
    let autoSaveTimer = null;

    const startAutoSave = () => {
      // 清除现有定时器
      if (autoSaveTimer) {
        clearInterval(autoSaveTimer);
      }

      // 设置5分钟自动保存
      autoSaveTimer = setInterval(async () => {
        // 只有在表单有内容且不在加载状态时才自动保存
        if (form.title.trim() && !loading.value) {
          try {
            await saveDraft();
            console.log("自动保存草稿成功");
          } catch (error) {
            console.warn("自动保存草稿失败:", error);
          }
        }
      }, 5 * 60 * 1000); // 5分钟
    };

    const stopAutoSave = () => {
      if (autoSaveTimer) {
        clearInterval(autoSaveTimer);
        autoSaveTimer = null;
      }
    };

    // 监听表单变化，开始自动保存
    watch(
      () => form.title,
      (newTitle) => {
        if (newTitle.trim()) {
          startAutoSave();
        } else {
          stopAutoSave();
        }
      }
    );

    // 页面卸载时清理定时器
    onUnmounted(() => {
      stopAutoSave();
    });

    // 生命周期钩子
    onMounted(() => {
      // 初始化数据
      eventStore.initializeData();

      // 默认显示创建方式选择模态框
      showModeSelectionModal.value = true;

      // 检查是否有未保存的草稿
      const savedDraft = localStorage.getItem("majorEventDraft");
      if (savedDraft) {
        try {
          const draftData = JSON.parse(savedDraft);
          const confirmed = confirm("检测到未保存的草稿，是否恢复？");
          if (confirmed) {
            Object.assign(form, draftData);
            console.log("草稿已恢复");
          } else {
            localStorage.removeItem("majorEventDraft");
          }
        } catch (error) {
          console.error("恢复草稿失败:", error);
          localStorage.removeItem("majorEventDraft");
        }
      }
    });

    return {
      // 响应式数据
      currentStep,
      showModeSelectionModal,
      selectedCreationMode,
      selectedTemplate,
      templates,
      templatesLoading,
      loading,
      error,
      errors,
      showSaveConfirmDialog,
      form,
      currentSituation,
      availableSituations,

      // 计算属性
      currentSituationData,

      // 方法
      goBack,
      selectCreationMode,
      backToModeSelection,
      backToPreviousStep,
      selectTemplate,
      switchSituation,
      addEvidenceCategory,
      removeEvidenceCategory,
      addSubcategory,
      removeSubcategory,
      addEvidenceItem,
      removeEvidenceItem,
      addStandardBasis,
      removeStandardBasis,
      saveDraft,
      handleSubmit,
      startReview,
      returnToList,
      handleDialogClose,
      clearError,
      formatDate,
    };
  },
};
</script>

<style scoped>
.create-major-event {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: #f0f0f0;
  color: #333;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.mode-select-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-select-btn:hover {
  background: #0056b3;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.draft-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.draft-btn:hover:not(:disabled) {
  background-color: #e9ecef;
}

.draft-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 创建方式选择模态框 */
.mode-selection-modal {
  max-width: 800px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.creation-modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.creation-mode {
  background: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.creation-mode:hover {
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
  transform: translateY(-2px);
}

.mode-icon {
  margin-bottom: 1rem;
  color: #007bff;
}

.creation-mode h3 {
  margin: 1rem 0;
  color: #333;
}

.creation-mode p {
  color: #666;
  line-height: 1.5;
}

/* 模板选择界面 */
.template-container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 2rem;
}

.loading,
.no-templates {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.template-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.template-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.template-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.15);
}

.template-item h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.template-item p {
  color: #666;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.template-meta {
  font-size: 0.875rem;
  color: #999;
}

/* 表单创建界面 */
.form-container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 2rem;
}

.event-form {
  background: white;
  border-radius: 8px;
  padding: 2rem;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.25rem;
}

.required {
  color: #dc3545;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* 审计证据标准 */
.evidence-standards-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.situation-tabs {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.situation-tab {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
}

.situation-tab.active {
  background: white;
  color: #007bff;
  border-bottom: 2px solid #007bff;
}

.situation-content {
  padding: 1.5rem;
}

.evidence-categories {
  margin-top: 1.5rem;
}

.evidence-categories h4 {
  margin: 0 0 1rem 0;
  color: #333;
}

.evidence-category {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 1rem;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.category-header h5 {
  margin: 0;
  color: #333;
}

.category-name-input {
  flex: 1;
  margin-right: 12px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
}

.remove-category-btn {
  padding: 0.25rem 0.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

/* 二级分类样式 */
.evidence-subcategory {
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  background: #ffffff;
  margin-left: 16px;
}

.subcategory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.subcategory-name-input {
  flex: 1;
  margin-right: 12px;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.remove-subcategory-btn {
  background: #ffa502;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
}

.remove-subcategory-btn:hover {
  background: #ff9500;
}

.add-subcategory-btn {
  background: #3742fa;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-top: 8px;
}

.add-subcategory-btn:hover {
  background: #2f3542;
}

.evidence-items {
  padding: 1rem;
}

.evidence-item {
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
  position: relative;
}

.remove-item-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem 0.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
}

.add-item-btn,
.add-category-btn {
  padding: 0.5rem 1rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.add-category-btn {
  margin-top: 1rem;
}

/* 标准制定依据样式 */
.standard-basis-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: #fafafa;
}

.basis-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  align-items: flex-start;
}

.basis-field {
  flex: 1;
}

.basis-field.full-width {
  flex: 2;
}

.basis-field label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: #333;
  font-size: 0.875rem;
}

.remove-basis-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  white-space: nowrap;
  align-self: flex-end;
}

.remove-basis-btn:hover {
  background: #c82333;
}

.add-basis-btn {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.add-basis-btn:hover {
  background: #138496;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 模态框通用样式 */
.modal-overlay {
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

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #666;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-body {
  margin-bottom: 1.5rem;
  color: #666;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* 错误提示 */
.error-banner {
  position: fixed;
  top: 1rem;
  right: 1rem;
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 1001;
}

.error-banner button {
  background: none;
  border: none;
  color: #721c24;
  cursor: pointer;
  font-weight: bold;
}
</style>
