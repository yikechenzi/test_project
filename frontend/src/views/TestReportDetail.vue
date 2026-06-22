<template>
  <div class="test-report-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>测试报告详情</h2>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="downloadReport">
          <el-icon><Download /></el-icon>
          下载报告
        </el-button>
      </div>
    </div>
    
    <div v-loading="loading">
      <!-- Summary Cards -->
      <el-row :gutter="20" class="summary-row">
        <el-col :span="4">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-value">{{ report.total_tests }}</div>
            <div class="summary-label">总用例数</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card shadow="hover" class="summary-card passed">
            <div class="summary-value">{{ report.passed_tests }}</div>
            <div class="summary-label">通过</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card shadow="hover" class="summary-card failed">
            <div class="summary-value">{{ report.failed_tests }}</div>
            <div class="summary-label">失败</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card shadow="hover" class="summary-card error">
            <div class="summary-value">{{ report.error_tests }}</div>
            <div class="summary-label">错误</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card shadow="hover" class="summary-card skipped">
            <div class="summary-value">{{ report.skipped_tests }}</div>
            <div class="summary-label">跳过</div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card shadow="hover" class="summary-card rate">
            <div class="summary-value">{{ report.pass_rate }}%</div>
            <div class="summary-label">通过率</div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Charts -->
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>测试状态分布</span>
            </template>
            <div class="chart-container" ref="statusChartRef"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>报告信息</span>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="报告标题">
                {{ report.title }}
              </el-descriptions-item>
              <el-descriptions-item label="报告ID">
                {{ report.id }}
              </el-descriptions-item>
              <el-descriptions-item label="生成时间">
                {{ formatDate(report.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="总耗时">
                {{ report.duration ? `${report.duration}秒` : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDate(report.start_time) }}
              </el-descriptions-item>
              <el-descriptions-item label="结束时间">
                {{ formatDate(report.end_time) }}
              </el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">
                {{ report.description || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Test Details -->
      <el-card>
        <template #header>
          <span>测试详情</span>
        </template>
        <el-table :data="details" stripe>
          <el-table-column prop="test_case_id" label="用例ID" width="100" />
          <el-table-column prop="test_case_name" label="用例名称" />
          <el-table-column prop="test_type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag>{{ getTestTypeLabel(row.test_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)">
                {{ getPriorityLabel(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="latest_status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.latest_status)">
                {{ getStatusLabel(row.latest_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="execution_count" label="执行次数" width="100" />
          <el-table-column prop="last_executed" label="最后执行时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.last_executed) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const report = ref<any>({})
const details = ref([])
const loading = ref(false)
const statusChartRef = ref<HTMLElement>()

const getTestTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    black_box: '黑盒',
    white_box: '白盒',
    api: 'API',
    ui: 'UI'
  }
  return labels[type] || type
}

const getPriorityLabel = (priority: string) => {
  const labels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急'
  }
  return labels[priority] || priority
}

const getPriorityType = (priority: string) => {
  const types: Record<string, string> = {
    low: 'info',
    medium: '',
    high: 'warning',
    critical: 'danger'
  }
  return types[priority] || ''
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待执行',
    running: '执行中',
    passed: '通过',
    failed: '失败',
    error: '错误',
    not_executed: '未执行',
    cancelled: '已取消'
  }
  return labels[status] || status
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'info',
    running: 'primary',
    passed: 'success',
    failed: 'danger',
    error: 'warning',
    not_executed: 'info',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const initStatusChart = () => {
  if (!statusChartRef.value || !report.value) return
  
  const chart = echarts.init(statusChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '测试状态',
        type: 'pie',
        radius: '50%',
        data: [
          { value: report.value.passed_tests, name: '通过', itemStyle: { color: '#67c23a' } },
          { value: report.value.failed_tests, name: '失败', itemStyle: { color: '#f56c6c' } },
          { value: report.value.error_tests, name: '错误', itemStyle: { color: '#e6a23c' } },
          { value: report.value.skipped_tests, name: '跳过', itemStyle: { color: '#909399' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  chart.setOption(option)
}

const fetchReport = async () => {
  const reportId = route.params.id
  loading.value = true
  
  try {
    const response = await axios.get(`/api/test-reports/${reportId}/details`)
    report.value = response.data.report
    details.value = response.data.details
    
    await nextTick()
    initStatusChart()
  } catch (error) {
    ElMessage.error('获取报告详情失败')
  } finally {
    loading.value = false
  }
}

const downloadReport = async () => {
  try {
    const response = await axios.get(`/api/test-reports/${report.value.id}/download`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `test-report-${report.value.id}.html`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

onMounted(() => {
  fetchReport()
})
</script>

<style scoped>
.test-report-detail {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.summary-row {
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.summary-card:hover {
  transform: translateY(-5px);
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.summary-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.summary-card.passed .summary-value {
  color: #67c23a;
}

.summary-card.failed .summary-value {
  color: #f56c6c;
}

.summary-card.error .summary-value {
  color: #e6a23c;
}

.summary-card.skipped .summary-value {
  color: #909399;
}

.summary-card.rate .summary-value {
  color: #409eff;
}

.chart-container {
  height: 300px;
}
</style>