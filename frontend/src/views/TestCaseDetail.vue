<template>
  <div class="test-case-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>测试用例详情</h2>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="executeTestCase">
          <el-icon><VideoPlay /></el-icon>
          执行测试
        </el-button>
        <el-button type="primary" @click="editTestCase">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
      </div>
    </div>
    
    <div v-loading="loading">
      <!-- Test Case Info -->
      <el-card class="info-card">
        <template #header>
          <span>基本信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例名称">
            {{ testCase.name }}
          </el-descriptions-item>
          <el-descriptions-item label="用例ID">
            {{ testCase.id }}
          </el-descriptions-item>
          <el-descriptions-item label="测试类型">
            <el-tag>{{ getTestTypeLabel(testCase.test_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(testCase.priority)">
              {{ getPriorityLabel(testCase.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="testCase.is_active ? 'success' : 'danger'">
              {{ testCase.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(testCase.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ testCase.description || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="标签" :span="2">
            <el-tag v-for="tag in tags" :key="tag" style="margin-right: 5px">
              {{ tag }}
            </el-tag>
            <span v-if="tags.length === 0">-</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <!-- Test Script -->
      <el-card class="script-card">
        <template #header>
          <span>测试脚本</span>
        </template>
        <pre class="script-content">{{ testCase.script_content }}</pre>
      </el-card>
      
      <!-- Expected Result -->
      <el-card v-if="testCase.expected_result" class="result-card">
        <template #header>
          <span>预期结果</span>
        </template>
        <pre class="result-content">{{ testCase.expected_result }}</pre>
      </el-card>
      
      <!-- Execution History -->
      <el-card>
        <template #header>
          <span>执行历史</span>
        </template>
        <el-table :data="executions" stripe>
          <el-table-column prop="id" label="执行ID" width="100" />
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
          <el-table-column prop="created_at" label="执行时间" />
          <el-table-column prop="error_message" label="错误信息" show-overflow-tooltip />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const testCase = ref<any>({})
const executions = ref([])
const loading = ref(false)

const tags = computed(() => {
  if (!testCase.value.tags) return []
  return testCase.value.tags.split(',').map((t: string) => t.trim()).filter(Boolean)
})

const getTestTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    black_box: '黑盒测试',
    white_box: '白盒测试',
    api: 'API测试',
    ui: 'UI测试'
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
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchTestCase = async () => {
  const caseId = route.params.id
  loading.value = true
  
  try {
    const [caseRes, execsRes] = await Promise.all([
      axios.get(`/api/test-cases/${caseId}`),
      axios.get('/api/test-executions', { params: { test_case_id: caseId } })
    ])
    
    testCase.value = caseRes.data
    executions.value = execsRes.data
  } catch (error) {
    ElMessage.error('获取测试用例详情失败')
  } finally {
    loading.value = false
  }
}

const executeTestCase = async () => {
  try {
    await axios.post(`/api/test-cases/${testCase.value.id}/execute`)
    ElMessage.success('测试已开始执行')
    fetchTestCase()
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const editTestCase = () => {
  router.push('/test-cases')
}

onMounted(() => {
  fetchTestCase()
})
</script>

<style scoped>
.test-case-detail {
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

.info-card,
.script-card,
.result-card {
  margin-bottom: 20px;
}

.script-content,
.result-content {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>