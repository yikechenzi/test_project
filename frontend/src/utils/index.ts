/**
 * Format date string
 */
export const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

/**
 * Format duration in seconds
 */
export const formatDuration = (seconds: number | null | undefined): string => {
  if (!seconds) return '-'
  
  if (seconds < 60) {
    return `${seconds.toFixed(2)}s`
  }
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`
}

/**
 * Get test type label
 */
export const getTestTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    black_box: '黑盒测试',
    white_box: '白盒测试',
    api: 'API测试',
    ui: 'UI测试'
  }
  return labels[type] || type
}

/**
 * Get priority label
 */
export const getPriorityLabel = (priority: string): string => {
  const labels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急'
  }
  return labels[priority] || priority
}

/**
 * Get priority type for el-tag
 */
export const getPriorityType = (priority: string): string => {
  const types: Record<string, string> = {
    low: 'info',
    medium: '',
    high: 'warning',
    critical: 'danger'
  }
  return types[priority] || ''
}

/**
 * Get execution status label
 */
export const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    pending: '待执行',
    running: '执行中',
    passed: '通过',
    failed: '失败',
    error: '错误',
    skipped: '跳过',
    cancelled: '已取消',
    not_executed: '未执行'
  }
  return labels[status] || status
}

/**
 * Get execution status type for el-tag
 */
export const getStatusType = (status: string): string => {
  const types: Record<string, string> = {
    pending: 'info',
    running: 'primary',
    passed: 'success',
    failed: 'danger',
    error: 'warning',
    skipped: 'info',
    cancelled: 'info',
    not_executed: 'info'
  }
  return types[status] || 'info'
}

/**
 * Calculate percentage
 */
export const calculatePercentage = (value: number, total: number): number => {
  if (total === 0) return 0
  return Math.round((value / total) * 100)
}

/**
 * Truncate text
 */
export const truncateText = (text: string, maxLength: number = 100): string => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}