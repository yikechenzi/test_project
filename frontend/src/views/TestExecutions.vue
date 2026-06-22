<template>
  <div class="test-executions">
    <div class="page-header">
      <h2>测试执行</h2>
    </div>
    
    <!-- Filters -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.status" placeholder="执行状态" clearable>
            <el-option label="待执行" value="pending" />
            <el-option label="执行中" value="running" />
            <el-option label="通过" value="passed" />
            <el-option label="失败" value="failed" />
            <el-option label="错误" value="error" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="fetchExecutions">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- Executions List -->
    <el-card>
      <el-table :data="executions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="test_case_id" label="测试用例ID" width="120" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="120">
          <template #default="{ row }">
            {{ row.duration ? `${row.duration.toFixed(2)}s` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewExecution(row)">
              详情
            </el-button>
            <el-button
              v-if="row.status === 'pending' || row.status === 'running'"
              type="danger"
              link
              @click="cancelExecution(row)"
            >
              取消
            </el-button>
            <el-button
              v-if="row.screenshot_path"
              type="success"
              link
              @click="viewScreenshot(row)"
            >
              截图
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- Pagination -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchExecutions"
        @current-change="fetchExecutions"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- Execution Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="执行详情"
      width="800px"
    >
      <div v-if="selectedExecution" class="execution-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行ID">
            {{ selectedExecution.id }}
          </el-descriptions-item>
          <el-descriptions-item label="测试用例ID">
            {{ selectedExecution.test_case_id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedExecution.status)">
              {{ getStatusLabel(selectedExecution.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">
            {{ selectedExecution.duration ? `${selectedExecution.duration.toFixed(2)}s` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDate(selectedExecution.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatDate(selectedExecution.end_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="浏览器环境" :span="2">
            {{ selectedExecution.environment || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedExecution.logs" class="logs-section">
          <h4>执行日志</h4>
          <pre class="logs-content">{{ selectedExecution.logs }}</pre>
        </div>
        
        <div v-if="selectedExecution.error_message" class="error-section">
          <h4>错误信息</h4>
          <pre class="error-content">{{ selectedExecution.error_message }}</pre>
        </div>
      </div>
    </el-dialog>
    
    <!-- Screenshot Dialog -->
    <el-dialog
      v-model="screenshotDialogVisible"
      title="测试截图"
      width="800px"
    >
      <div v-if="selectedScreenshot" class="screenshot-container">
        <img :src="selectedScreenshot" alt="Test Screenshot" style="width: 100%" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const executions = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const screenshotDialogVisible = ref(false)
const selectedExecution = ref<any>(null)
const selectedScreenshot = ref('')

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  status: '',
  dateRange: null as any
})

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待执行',
    running: '执行中',
    passed: '通过',
    failed: '失败',
    error: '错误',
    skipped: '跳过',
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
    skipped: 'info',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchExecutions = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (filters.status) {
      params.status = filters.status
    }
    
    const response = await axios.get('/api/test-executions', { params })
    executions.value = response.data
    total.value = response.data.length
  } catch (error) {
    ElMessage.error('获取执行列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.status = ''
  filters.dateRange = null
  fetchExecutions()
}

const viewExecution = async (execution: any) => {
  try {
    const response = await axios.get(`/api/test-executions/${execution.id}`)
    selectedExecution.value = response.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取执行详情失败')
  }
}

const cancelExecution = async (execution: any) => {
  try {
    await ElMessageBox.confirm('确定要取消该执行吗？', '提示', {
      type: 'warning'
    })
    
    await axios.post(`/api/test-executions/${execution.id}/cancel`)
    ElMessage.success('已取消执行')
    fetchExecutions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const viewScreenshot = (execution: any) => {
  selectedScreenshot.value = `/api/test-executions/${execution.id}/screenshot`
  screenshotDialogVisible.value = true
}

onMounted(() => {
  fetchExecutions()
})
</script>

<style scoped>
.test-executions {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.filter-card {
  margin-bottom: 20px;
}

.execution-detail {
  padding: 10px 0;
}

.logs-section,
.error-section {
  margin-top: 20px;
}

.logs-section h4,
.error-section h4 {
  margin-bottom: 10px;
  color: #333;
}

.logs-content,
.error-content {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

.error-content {
  color: #f56c6c;
}

.screenshot-container {
  text-align: center;
}
</style>