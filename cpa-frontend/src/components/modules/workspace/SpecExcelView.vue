<!--
  SpecExcelView.vue - Excel文件专用展示和标注组件
  
  功能说明：
  1. 支持在浏览器中展示xlsx/xls格式的Excel文件
  2. 提供可视化标注功能，支持对指定区域添加视觉元素
  3. 支持多种标注样式：边框高亮、背景色标注、文字标注等
  4. 集成文件上传和管理功能
  
  技术特点：
  - 使用xlsx库解析Excel文件
  - 响应式表格展示，支持大量数据
  - 可拖拽和点击选择标注区域
  - 支持标注数据的导入导出
-->

<template>
  <div class="spec-excel-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Excel文件展示与标注</h1>
        <p class="page-description">上传并展示Excel文件，支持对指定区域进行可视化标注</p>
      </div>
      <div class="header-actions">
        <button 
          class="btn btn-primary" 
          @click="openFileDialog"
          :disabled="loading"
        >
          <i class="icon-upload"></i>
          选择Excel文件
        </button>
        <button 
          class="btn btn-secondary" 
          @click="refreshAnomalies"
          :disabled="!hasData"
        >
          <i class="icon-refresh"></i>
          刷新异常检测
        </button>
      </div>
    </div>

    <!-- 文件上传区域 -->
    <div v-if="!hasData" class="upload-area">
      <div 
        class="upload-dropzone"
        :class="{ 'dragover': isDragOver }"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="openFileDialog"
      >
        <div class="upload-content">
          <i class="icon-file-excel upload-icon"></i>
          <h3>拖拽Excel文件到此处或点击选择</h3>
          <p class="upload-tips">支持 .xlsx 和 .xls 格式文件</p>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div v-if="hasData" class="toolbar">
      <div class="toolbar-left">
        <div class="file-info">
          <i class="icon-file-excel"></i>
          <span class="filename">{{ currentFile.name }}</span>
          <span class="file-size">({{ formatFileSize(currentFile.size) }})</span>
        </div>
      </div>
      
      <div class="toolbar-center">
        <div class="sheet-tabs" v-if="sheets.length > 1">
          <button
            v-for="(sheet, index) in sheets"
            :key="sheet.name"
            class="sheet-tab"
            :class="{ active: currentSheetIndex === index }"
            @click="switchSheet(index)"
          >
            {{ sheet.name }}
          </button>
        </div>
      </div>
      
      <div class="toolbar-right">
        <div class="anomaly-info">
          <span class="anomaly-count">
            <i class="icon-warning"></i>
            {{ systemAnomalies.length }} 个异常标记
          </span>
        </div>
      </div>
    </div>

    <!-- Excel表格展示区域 -->
    <div v-if="hasData" class="excel-container">
      <div class="table-wrapper" ref="tableWrapper">
        <table class="excel-table" ref="excelTable">
          <!-- 列标题 -->
          <thead>
            <tr class="column-headers">
              <th class="row-number-header"></th>
              <th
                v-for="(col, colIndex) in columnHeaders"
                :key="colIndex"
                class="column-header"
              >
                {{ col }}
              </th>
            </tr>
          </thead>
          
          <!-- 数据行 -->
          <tbody>
            <tr
              v-for="(row, rowIndex) in currentSheetData"
              :key="rowIndex"
              class="data-row"
            >
              <!-- 行号 -->
              <td class="row-number">{{ rowIndex + 1 }}</td>
              
              <!-- 数据单元格 -->
              <td
                v-for="(cell, colIndex) in row"
                :key="colIndex"
                class="data-cell"
                :class="getCellClasses(rowIndex, colIndex)"
                :style="getCellStyles(rowIndex, colIndex)"
                :data-row="rowIndex"
                :data-col="colIndex"
              >
                {{ formatCellValue(cell) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 系统异常标记面板 -->
    <div v-if="hasData && systemAnomalies.length > 0" class="anomalies-panel">
      <div class="panel-header">
        <h3>异常标记</h3>
        <span class="anomaly-count">{{ systemAnomalies.length }} 个异常</span>
      </div>
      
      <div class="anomalies-list">
        <div
          v-for="(anomaly, index) in systemAnomalies"
          :key="index"
          class="anomaly-item"
        >
          <div class="anomaly-preview">
            <div class="severity-indicator" :class="anomaly.severity"></div>
            <div class="anomaly-info">
              <div class="anomaly-range">
                {{ getAnomalyRangeText(anomaly) }}
              </div>
              <div class="anomaly-type">{{ anomaly.type }}</div>
              <div class="anomaly-description">{{ anomaly.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="icon-spinner"></i>
        <span>正在解析Excel文件...</span>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept=".xlsx,.xls"
      @change="handleFileSelect"
      style="display: none"
    />
  </div>
</template>

<script>
import * as XLSX from 'xlsx'

export default {
  name: 'SpecExcelView',
  props: {
    fileUrl: { type: String, default: '' },
    fileName: { type: String, default: '' }
  },
  
  data() {
    return {
      // 文件相关数据
      currentFile: null,
      hasData: false,
      loading: false,
      
      // Excel数据
      workbook: null,
      sheets: [],
      currentSheetIndex: 0,
      currentSheetData: [],
      columnHeaders: [],
      
      // 拖拽状态
      isDragOver: false,
      
      // 系统异常标记相关
      systemAnomalies: [], // 系统检测到的异常标记
      
      // 选择状态（保留基础功能）
      isSelecting: false,
      selectionStart: null,
      selectionEnd: null,
      currentSelection: null
    }
  },
  
  computed: {
    /**
     * 获取当前工作表数据
     */
    currentSheet() {
      return this.sheets[this.currentSheetIndex]
    }
  },
  
  methods: {
    /**
     * 打开文件选择对话框
     */
    openFileDialog() {
      this.$refs.fileInput.click()
    },
    
    /**
     * 处理文件选择
     */
    async handleFileSelect(event) {
      const files = event.target.files
      if (files && files.length > 0) {
        await this.loadExcelFile(files[0])
      }
      // 清空input值，允许选择同一个文件
      event.target.value = ''
    },
    
    /**
     * 处理拖拽相关事件
     */
    handleDragOver(event) {
      event.preventDefault()
      this.isDragOver = true
    },
    
    handleDragLeave(event) {
      event.preventDefault()
      this.isDragOver = false
    },
    
    async handleDrop(event) {
      event.preventDefault()
      this.isDragOver = false
      
      const files = event.dataTransfer.files
      if (files && files.length > 0) {
        const file = files[0]
        if (this.isExcelFile(file)) {
          await this.loadExcelFile(file)
        } else {
          this.$message?.error('请选择 .xlsx 或 .xls 格式的Excel文件')
        }
      }
    },
    
    /**
     * 检查是否为Excel文件
     */
    isExcelFile(file) {
      const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
      ]
      const validExtensions = ['.xlsx', '.xls']
      
      return validTypes.includes(file.type) || 
             validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
    },
    
    /**
     * 加载并解析Excel文件
     */
    async loadExcelFile(file) {
      this.loading = true
      this.currentFile = file
      
      try {
        const arrayBuffer = await this.readFileAsArrayBuffer(file)
        this.workbook = XLSX.read(arrayBuffer, { type: 'array' })
        
        // 解析所有工作表
        this.parseWorkbook()
        
        // 设置默认显示第一个工作表
        this.currentSheetIndex = 0
        this.switchSheet(0)
        
        this.hasData = true
        // 在工作表解析完成后加载异常配置
        this.loadSystemAnomalies()
        
      } catch (error) {
        console.error('解析Excel文件失败:', error)
        this.$message?.error('解析Excel文件失败，请检查文件格式')
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 将文件读取为ArrayBuffer
     */
    readFileAsArrayBuffer(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = () => reject(new Error('文件读取失败'))
        reader.readAsArrayBuffer(file)
      })
    },
    
    /**
     * 解析工作簿
     */
    parseWorkbook() {
      this.sheets = this.workbook.SheetNames.map(name => ({
        name,
        data: XLSX.utils.sheet_to_json(this.workbook.Sheets[name], {
          header: 1,
          defval: '',
          raw: false
        })
      }))
    },
    
    /**
     * 切换工作表
     */
    switchSheet(index) {
      this.currentSheetIndex = index
      const sheet = this.sheets[index]
      this.currentSheetData = sheet.data
      
      // 生成列标题 A, B, C...
      if (this.currentSheetData.length > 0) {
        const maxCols = Math.max(...this.currentSheetData.map(row => row.length))
        this.columnHeaders = this.generateColumnHeaders(maxCols)
      } else {
        this.columnHeaders = []
      }
      
      // 清除当前选择
      this.clearSelection()
    },
    
    /**
     * 生成列标题 (A, B, C, ... Z, AA, AB, ...)
     */
    generateColumnHeaders(count) {
      const headers = []
      for (let i = 0; i < count; i++) {
        headers.push(this.numberToColumnLetter(i))
      }
      return headers
    },
    
    /**
     * 数字转换为列字母
     */
    numberToColumnLetter(num) {
      let result = ''
      while (num >= 0) {
        result = String.fromCharCode(65 + (num % 26)) + result
        num = Math.floor(num / 26) - 1
        if (num < 0) break
      }
      return result
    },
    
    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    /**
     * 格式化单元格值
     */
    formatCellValue(value) {
      if (value === null || value === undefined || value === '') {
        return ''
      }
      return String(value)
    },
    
    /**
     * 加载系统异常标记配置
     */
    loadSystemAnomalies() {
      // 根据当前文件名加载对应的异常标记配置
      const fileName = this.currentFile?.name
      if (!fileName) return
      
      // 模拟异常配置数据（实际应从服务器或配置文件加载）
      this.systemAnomalies = this.getAnomaliesConfig(fileName)
    },
    
    /**
     * 获取异常配置（模拟数据）
     */
    getAnomaliesConfig(fileName) {
      // 为货币资金文件配置异常标记
      if (fileName.includes('货币资金') || fileName.includes('1010')) {
        // 找到1010-7工作表的索引
        const sheet1010_7_Index = this.sheets.findIndex(sheet => sheet.name === '1010-7')
        const targetSheetIndex = sheet1010_7_Index >= 0 ? sheet1010_7_Index : 0
        
        return [
          {
            type: '数据异常',
            severity: 'high',
            description: '支付公司2024年财产险保费数据异常',
            range: {
              startRow: 14,  // 对应第15行（0-based index）
              endRow: 14,
              startCol: 0,
              endCol: 12     // 整行标记
            },
            sheetIndex: targetSheetIndex
          },
          {
            type: '跨期风险',
            severity: 'medium', 
            description: '期末资金收支可能存在跨期问题',
            range: {
              startRow: 15,
              endRow: 16,
              startCol: 3,   // 内容列
              endCol: 5      // 对应科目列
            },
            sheetIndex: targetSheetIndex
          }
        ]
      }
      return []
    },
    
    /**
     * 刷新异常检测
     */
    refreshAnomalies() {
      this.loadSystemAnomalies()
    },
    
    /**
     * 清除选择
     */
    clearSelection() {
      this.isSelecting = false
      this.selectionStart = null
      this.selectionEnd = null
      this.currentSelection = null
    },
    
    /**
     * 获取单元格CSS类
     */
    getCellClasses(row, col) {
      const classes = []
      
      // 当前选择高亮
      if (this.currentSelection && this.isCellInRange(row, col, this.currentSelection)) {
        classes.push('selecting')
      }
      
      // 系统异常标记样式
      const anomalies = this.getCellAnomalies(row, col)
      if (anomalies.length > 0) {
        const highestSeverity = this.getHighestSeverity(anomalies)
        classes.push(`anomaly-${highestSeverity}`)
        classes.push('system-anomaly')
      }
      
      return classes
    },
    
    /**
     * 获取单元格CSS样式
     */
    getCellStyles(row, col) {
      const styles = {}
      const anomalies = this.getCellAnomalies(row, col)
      
      if (anomalies.length > 0) {
        const highestSeverity = this.getHighestSeverity(anomalies)
        
        // 根据异常等级设置美化的边框样式
        if (highestSeverity === 'high') {
          styles.border = '3px solid #ff4757'
          styles.background = 'linear-gradient(135deg, #fff5f5 0%, #ffecec 100%)'
          styles.boxShadow = '0 0 0 1px rgba(255, 71, 87, 0.2), inset 0 1px 2px rgba(255, 71, 87, 0.1)'
          styles.position = 'relative'
        } else if (highestSeverity === 'medium') {
          styles.border = '3px solid #ffa502'
          styles.background = 'linear-gradient(135deg, #fffaf0 0%, #fff4e6 100%)'
          styles.boxShadow = '0 0 0 1px rgba(255, 165, 2, 0.2), inset 0 1px 2px rgba(255, 165, 2, 0.1)'
          styles.position = 'relative'
        } else if (highestSeverity === 'low') {
          styles.border = '3px solid #ffda79'
          styles.background = 'linear-gradient(135deg, #fffef0 0%, #fffbe6 100%)'
          styles.boxShadow = '0 0 0 1px rgba(255, 218, 121, 0.2), inset 0 1px 2px rgba(255, 218, 121, 0.1)'
          styles.position = 'relative'
        }
        
        styles.boxSizing = 'border-box'
        styles.borderRadius = '3px'
      }
      
      return styles
    },
    
    /**
     * 获取单元格的所有异常标记
     */
    getCellAnomalies(row, col) {
      return this.systemAnomalies.filter(anomaly => 
        anomaly.sheetIndex === this.currentSheetIndex &&
        this.isCellInRange(row, col, anomaly.range)
      )
    },
    
    /**
     * 获取最高异常等级
     */
    getHighestSeverity(anomalies) {
      const severityOrder = { high: 3, medium: 2, low: 1 }
      return anomalies.reduce((highest, current) => {
        return severityOrder[current.severity] > severityOrder[highest] ? current.severity : highest
      }, 'low')
    },
    
    /**
     * 检查单元格是否在指定范围内
     */
    isCellInRange(row, col, range) {
      return row >= range.startRow && row <= range.endRow &&
             col >= range.startCol && col <= range.endCol
    },
    
    
    /**
     * 获取异常范围文本
     */
    getAnomalyRangeText(anomaly) {
      const { startRow, endRow, startCol, endCol } = anomaly.range
      const startCell = `${this.numberToColumnLetter(startCol)}${startRow + 1}`
      
      if (startRow === endRow && startCol === endCol) {
        return startCell
      } else {
        const endCell = `${this.numberToColumnLetter(endCol)}${endRow + 1}`
        return `${startCell}:${endCell}`
      }
    },
    async loadExcelFromUrl(url, name = 'Excel.xlsx') {
      try {
        this.loading = true
        const res = await fetch(url)
        if (!res.ok) throw new Error(`加载失败: ${res.status}`)
        const blob = await res.blob()
        const arrayBuffer = await blob.arrayBuffer()
        this.workbook = XLSX.read(arrayBuffer, { type: 'array' })
        this.parseWorkbook()
        this.currentSheetIndex = 0
        this.switchSheet(0)
        this.hasData = true
        this.currentFile = { name: name || (url.split('/').pop() || 'Excel.xlsx'), size: blob.size }
        this.loadSystemAnomalies()
      } catch (e) {
        console.error('从URL加载Excel失败:', e)
        this.$message?.error('无法加载远程Excel文件')
      } finally {
        this.loading = false
      }
    }
  },
  
  // 组件销毁时清理资源
  beforeUnmount() {
    this.workbook = null
    this.sheets = []
    this.currentSheetData = []
  },
  mounted() {
    if (this.fileUrl) {
      const name = this.fileName || (this.fileUrl.split('/').pop() || 'Excel.xlsx')
      this.loadExcelFromUrl(this.fileUrl, name)
    }
  },
  watch: {
    fileUrl(newVal) {
      if (newVal) {
        const name = this.fileName || (newVal.split('/').pop() || 'Excel.xlsx')
        this.loadExcelFromUrl(newVal, name)
      }
    }
  }
}

</script>

<style scoped>
.spec-excel-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: white;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.page-description {
  margin: 4px 0 0;
  color: #6c757d;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

/* 文件上传区域 */
.upload-area {
  flex: 1;
  padding: 40px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-dropzone {
  width: 100%;
  max-width: 600px;
  height: 300px;
  border: 2px dashed #ced4da;
  border-radius: 12px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-dropzone:hover,
.upload-dropzone.dragover {
  border-color: #007bff;
  background-color: #f8f9ff;
}

.upload-content {
  text-align: center;
  color: #6c757d;
}

.upload-icon {
  font-size: 48px;
  color: #28a745;
  margin-bottom: 16px;
}

.upload-content h3 {
  margin: 0 0 8px;
  color: #495057;
  font-weight: 500;
}

.upload-tips {
  margin: 0;
  font-size: 14px;
  color: #6c757d;
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e9ecef;
  gap: 16px;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #495057;
  font-size: 14px;
}

.filename {
  font-weight: 500;
}

.file-size {
  color: #6c757d;
}

.sheet-tabs {
  display: flex;
  gap: 4px;
}

.sheet-tab {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.sheet-tab:hover {
  background: #e9ecef;
}

.sheet-tab.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.anomaly-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.anomaly-count {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #495057;
  font-size: 14px;
  font-weight: 500;
}

.anomaly-count .icon-warning::before {
  content: "⚠️";
  font-size: 16px;
}

/* Excel表格容器 */
.excel-container {
  flex: 1;
  padding: 16px 24px;
  overflow: hidden;
}

.table-wrapper {
  height: 100%;
  overflow: auto;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
}

.excel-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.column-headers {
  background: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 10;
}

.row-number-header {
  width: 50px;
  min-width: 50px;
  background: #e9ecef;
  border-right: 1px solid #dee2e6;
  border-bottom: 1px solid #dee2e6;
}

.column-header {
  min-width: 80px;
  padding: 8px;
  text-align: center;
  font-weight: 600;
  background: #f8f9fa;
  border-right: 1px solid #dee2e6;
  border-bottom: 1px solid #dee2e6;
  color: #495057;
}

.data-row:nth-child(even) {
  background-color: #fdfdfd;
}

.row-number {
  width: 50px;
  min-width: 50px;
  padding: 6px 8px;
  text-align: center;
  background: #f8f9fa;
  border-right: 1px solid #dee2e6;
  color: #6c757d;
  font-weight: 500;
  position: sticky;
  left: 0;
  z-index: 5;
}

.data-cell {
  padding: 6px 8px;
  border-right: 1px solid #e9ecef;
  border-bottom: 1px solid #e9ecef;
  min-width: 80px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  position: relative;
}

.data-cell:hover {
  background-color: #f8f9ff;
}

.data-cell.selecting {
  background-color: #cce5ff !important;
}

/* 系统异常标记样式 */
.data-cell.system-anomaly {
  position: relative;
  z-index: 2;
  font-weight: 500;
}

/* 高风险异常样式 */
.data-cell.anomaly-high {
  animation: glow-high 2.5s ease-in-out infinite;
}

.data-cell.anomaly-high::before {
  content: "";
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ff4757, #ff3742, #ff5722);
  background-size: 400% 400%;
  border-radius: 4px;
  z-index: -1;
  animation: gradient-shift 3s ease infinite;
  opacity: 0.8;
}

.data-cell.anomaly-high::after {
  content: "⚠️";
  position: absolute;
  top: -8px;
  right: -8px;
  width: 16px;
  height: 16px;
  background: #ff4757;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: white;
  z-index: 3;
  animation: bounce 2s infinite;
}

/* 中风险异常样式 */
.data-cell.anomaly-medium {
  animation: glow-medium 3s ease-in-out infinite;
}

.data-cell.anomaly-medium::before {
  content: "";
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ffa502, #ff9500, #ff8c00);
  background-size: 400% 400%;
  border-radius: 4px;
  z-index: -1;
  animation: gradient-shift 3s ease infinite;
  opacity: 0.6;
}

.data-cell.anomaly-medium::after {
  content: "⚡";
  position: absolute;
  top: -6px;
  right: -6px;
  width: 14px;
  height: 14px;
  background: #ffa502;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8px;
  color: white;
  z-index: 3;
}

/* 低风险异常样式 */
.data-cell.anomaly-low {
  animation: glow-low 3.5s ease-in-out infinite;
}

.data-cell.anomaly-low::before {
  content: "";
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ffda79, #ffd54f, #ffcc02);
  background-size: 400% 400%;
  border-radius: 4px;
  z-index: -1;
  animation: gradient-shift 4s ease infinite;
  opacity: 0.4;
}

/* 动画效果定义 */
@keyframes glow-high {
  0%, 100% { 
    box-shadow: 
      0 0 0 1px rgba(255, 71, 87, 0.3),
      0 0 8px rgba(255, 71, 87, 0.4),
      inset 0 1px 2px rgba(255, 71, 87, 0.1);
  }
  50% { 
    box-shadow: 
      0 0 0 2px rgba(255, 71, 87, 0.5),
      0 0 16px rgba(255, 71, 87, 0.6),
      inset 0 1px 4px rgba(255, 71, 87, 0.2);
  }
}

@keyframes glow-medium {
  0%, 100% { 
    box-shadow: 
      0 0 0 1px rgba(255, 165, 2, 0.3),
      0 0 6px rgba(255, 165, 2, 0.4),
      inset 0 1px 2px rgba(255, 165, 2, 0.1);
  }
  50% { 
    box-shadow: 
      0 0 0 2px rgba(255, 165, 2, 0.5),
      0 0 12px rgba(255, 165, 2, 0.6),
      inset 0 1px 3px rgba(255, 165, 2, 0.2);
  }
}

@keyframes glow-low {
  0%, 100% { 
    box-shadow: 
      0 0 0 1px rgba(255, 218, 121, 0.3),
      0 0 4px rgba(255, 218, 121, 0.4),
      inset 0 1px 2px rgba(255, 218, 121, 0.1);
  }
  50% { 
    box-shadow: 
      0 0 0 2px rgba(255, 218, 121, 0.5),
      0 0 8px rgba(255, 218, 121, 0.6),
      inset 0 1px 3px rgba(255, 218, 121, 0.2);
  }
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-3px); }
  60% { transform: translateY(-2px); }
}

/* 异常标记面板 */
.anomalies-panel {
  width: 320px;
  background: white;
  border-left: 1px solid #dee2e6;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #495057;
}

.annotation-count {
  font-size: 12px;
  color: #6c757d;
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 12px;
}

.anomalies-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.anomaly-item {
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.2s;
  background: #fff;
}

.anomaly-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.anomaly-preview {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.severity-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 2px;
  flex-shrink: 0;
}

.severity-indicator.high {
  background-color: #ff4757;
}

.severity-indicator.medium {
  background-color: #ffa502;
}

.severity-indicator.low {
  background-color: #ffda79;
}

.anomaly-info {
  flex: 1;
}

.anomaly-range {
  font-weight: 600;
  color: #495057;
  font-size: 14px;
  margin-bottom: 4px;
}

.anomaly-type {
  font-size: 12px;
  color: #007bff;
  font-weight: 500;
  margin-bottom: 4px;
}

.anomaly-description {
  font-size: 12px;
  color: #6c757d;
  line-height: 1.4;
}

.btn-icon {
  padding: 4px;
  border: none;
  background: transparent;
  border-radius: 3px;
  cursor: pointer;
  color: #6c757d;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #f8f9fa;
  color: #495057;
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #007bff;
}

.loading-spinner .icon-spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 图标字体 - 简单的替代方案 */
.icon-upload::before { content: "📤"; }
.icon-refresh::before { content: "🔄"; }
.icon-file-excel::before { content: "📊"; }
.icon-warning::before { content: "⚠️"; }
.icon-spinner::before { content: "⭮"; }

/* 响应式设计 */
@media (max-width: 768px) {
  .spec-excel-view {
    flex-direction: column;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .anomalies-panel {
    width: 100%;
    height: 250px;
    border-left: none;
    border-top: 1px solid #dee2e6;
  }
  
  .excel-container {
    padding: 12px;
  }
  
  .table-wrapper {
    border-radius: 4px;
  }
}
</style>