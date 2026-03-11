import { defineStore } from 'pinia'

/**
 * 基础设置数据管理store
 * 负责管理项目基础配置数据，包括企业基本信息、企业属性信息、审计依据方案
 * 使用localStorage模拟数据库操作，预留实际API调用接口
 */
export const useBaseSettingStore = defineStore('baseSetting', {
  state: () => ({
    // 加载状态管理
    loading: false,
    error: null,
    
    // 企业基本信息
    companyBasicInfo: {
      companyName: '', // 企业名称（只读）
      companyAliases: [] // 企业简称列表（支持CRUD）
    },
    
    // 企业属性信息（所有字段只读）
    companyAttributes: {
      financialYear: '', // 财务报表年份
      isDomestic: null, // 是否为境内企业
      companySize: '', // 企业规模
      industry: '', // 所属行业
      listingStatus: '', // 上市情况
      listingLocation: '', // 上市地点（如果已上市）
      isStateOwned: null // 是否为国有企业
    },
    
    // 审计依据方案（所有字段只读）
    auditBasisScheme: {
      schemeId: '', // 方案标识
      applicableCompanyType: '', // 适用企业类型说明
      accountingStandards: [], // 会计准则列表
      auditingStandards: [], // 审计准则列表
      basicLaws: [], // 基础法律列表
      specialRegulations: [], // 专项法规列表
      basicRegulatoryStandards: [], // 基础监管规范列表
      specialRegulatoryStandards: [] // 专项监管规范列表
    }
  }),
  
  getters: {
    /**
     * 获取企业简称数量
     */
    aliasCount: (state) => state.companyBasicInfo.companyAliases.length,
    
    /**
     * 检查是否有数据加载错误
     */
    hasError: (state) => !!state.error,
    
    /**
     * 获取上市状态显示文本
     */
    listingStatusText: (state) => {
      const status = state.companyAttributes.listingStatus
      const location = state.companyAttributes.listingLocation
      if (status === '已上市' && location) {
        return `${status}（${location}）`
      }
      return status
    }
  },
  
  actions: {
    /**
     * 从后端获取基础设置数据
     * TODO: 替换为实际的API调用
     */
    async fetchBaseSettingData() {
      this.loading = true
      this.error = null
      
      try {
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // TODO: 替换为实际的API调用
        // const response = await api.get('/api/base-setting')
        // const data = response.data
        
        // 从localStorage获取模拟数据
        const data = this.getLocalStorageData()
        
        // 更新state数据
        this.companyBasicInfo = data.companyBasicInfo
        this.companyAttributes = data.companyAttributes
        this.auditBasisScheme = data.auditBasisScheme
        
      } catch (error) {
        this.error = '获取基础设置数据失败，请检查网络连接或稍后再试'
        console.error('获取基础设置数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 添加企业简称
     * @param {string} alias - 新的企业简称
     */
    async addCompanyAlias(alias) {
      if (!alias || !alias.trim()) {
        throw new Error('企业简称不能为空')
      }
      
      // 检查简称唯一性
      if (this.companyBasicInfo.companyAliases.includes(alias.trim())) {
        throw new Error('该企业简称已存在')
      }
      
      try {
        // TODO: 替换为实际的API调用
        // await api.post('/api/company-alias', { alias: alias.trim() })
        
        // 更新本地数据
        this.companyBasicInfo.companyAliases.push(alias.trim())
        this.saveToLocalStorage()
        
      } catch (error) {
        console.error('添加企业简称失败:', error)
        throw new Error('添加企业简称失败，请稍后再试')
      }
    },
    
    /**
     * 更新企业简称
     * @param {number} index - 简称索引
     * @param {string} newAlias - 新的简称
     */
    async updateCompanyAlias(index, newAlias) {
      if (!newAlias || !newAlias.trim()) {
        throw new Error('企业简称不能为空')
      }
      
      const trimmedAlias = newAlias.trim()
      const aliases = this.companyBasicInfo.companyAliases
      
      // 检查简称唯一性（排除当前编辑的项）
      if (aliases.some((alias, i) => i !== index && alias === trimmedAlias)) {
        throw new Error('该企业简称已存在')
      }
      
      try {
        // TODO: 替换为实际的API调用
        // await api.put(`/api/company-alias/${index}`, { alias: trimmedAlias })
        
        // 更新本地数据
        this.companyBasicInfo.companyAliases[index] = trimmedAlias
        this.saveToLocalStorage()
        
      } catch (error) {
        console.error('更新企业简称失败:', error)
        throw new Error('更新企业简称失败，请稍后再试')
      }
    },
    
    /**
     * 删除企业简称
     * @param {number} index - 简称索引
     */
    async deleteCompanyAlias(index) {
      try {
        // TODO: 替换为实际的API调用
        // await api.delete(`/api/company-alias/${index}`)
        
        // 更新本地数据
        this.companyBasicInfo.companyAliases.splice(index, 1)
        this.saveToLocalStorage()
        
      } catch (error) {
        console.error('删除企业简称失败:', error)
        throw new Error('删除企业简称失败，请稍后再试')
      }
    },
    
    /**
     * 获取条文详细信息
     * @param {string} type - 条文类型
     * @param {string} itemId - 条文ID
     */
    async getRegulationDetail(type, itemId) {
      try {
        // TODO: 替换为实际的API调用
        // const response = await api.get(`/api/regulation-detail/${type}/${itemId}`)
        // return response.data
        
        // 模拟返回条文详细信息
        return {
          id: itemId,
          name: '示例条文名称',
          issuer: '示例发文机构',
          issueDate: '2023-01-01',
          content: '这是示例条文的具体内容，实际使用时应从后端API获取真实数据。'
        }
      } catch (error) {
        console.error('获取条文详情失败:', error)
        throw new Error('获取条文详情失败，请稍后再试')
      }
    },
    
    /**
     * 重新加载数据
     */
    async reloadData() {
      await this.fetchBaseSettingData()
    },
    
    /**
     * 清除错误状态
     */
    clearError() {
      this.error = null
    },
    
    /**
     * 从localStorage获取模拟数据
     * @private
     */
    getLocalStorageData() {
      const defaultData = {
        companyBasicInfo: {
          companyName: '示例企业有限公司',
          companyAliases: ['示例企业', '示例公司']
        },
        companyAttributes: {
          financialYear: '2023',
          isDomestic: true,
          companySize: '大型',
          industry: '制造业',
          listingStatus: '已上市',
          listingLocation: '上海证券交易所',
          isStateOwned: false
        },
        auditBasisScheme: {
          schemeId: 'SCHEME_001',
          applicableCompanyType: '适用于大型制造业上市公司',
          accountingStandards: [
            { id: 'AS001', name: '企业会计准则第1号——存货' },
            { id: 'AS002', name: '企业会计准则第2号——长期股权投资' }
          ],
          auditingStandards: [
            { id: 'AUS001', name: '中国注册会计师审计准则第1101号——注册会计师的总体目标' },
            { id: 'AUS002', name: '中国注册会计师审计准则第1121号——对财务报表审计实施的质量控制' }
          ],
          basicLaws: [
            { id: 'LAW001', name: '中华人民共和国公司法' },
            { id: 'LAW002', name: '中华人民共和国证券法' }
          ],
          specialRegulations: [
            { id: 'REG001', name: '上市公司信息披露管理办法' },
            { id: 'REG002', name: '企业内部控制基本规范' }
          ],
          basicRegulatoryStandards: [
            { id: 'BRS001', name: '企业内部控制应用指引第1号——组织架构' },
            { id: 'BRS002', name: '企业内部控制应用指引第2号——发展战略' }
          ],
          specialRegulatoryStandards: [
            { id: 'SRS001', name: '上市公司治理准则' },
            { id: 'SRS002', name: '企业国有资产监督管理暂行条例' }
          ]
        }
      }
      
      const stored = localStorage.getItem('baseSettingData')
      return stored ? JSON.parse(stored) : defaultData
    },
    
    /**
     * 保存数据到localStorage
     * @private
     */
    saveToLocalStorage() {
      const data = {
        companyBasicInfo: this.companyBasicInfo,
        companyAttributes: this.companyAttributes,
        auditBasisScheme: this.auditBasisScheme
      }
      localStorage.setItem('baseSettingData', JSON.stringify(data))
    }
  }
})