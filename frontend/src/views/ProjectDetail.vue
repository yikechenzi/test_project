<template>
  <div class="project-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>项目详情</h2>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="executeAllTests">
          <el-icon><VideoPlay /></el-icon>
          执行所有测试
        </el-button>
      </div>
    </div>
    
    <div v-loading="loading">
      <!-- Project Info -->
      <el-card class="info-card">
        <template #header>
          <span>项目信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">
            {{ project.name }}
          </el-descriptions-item>
          <el-descriptions-item label="项目ID">
            {{ project.id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="project.is_active ? 'success' : 'danger'">
              {{ project.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(project.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ project.description || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <!-- Statistics -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value">{{ stats.totalCases }}</div>
            <div class="stat-label">测试用例</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card passed">
            <div class="stat-value">{{ stats.passedCases }}</div>
            <div class="stat-label">通过</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card failed">
            <div class="stat-value">{{ stats.failedCases }}</div>
            <div class="stat-label">失败</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card rate">
            <div class="stat-value">{{ stats.passRate }}%</div>
            <div class="stat-label">通过率</div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Test Cases -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>测试用例</span>
            <el-button type="primary" size="small" @click="showAddCaseDialog">
              添加用例
            </el-button>
          </div>
        </template>
        
        <el-table :data="testCases" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="用例名称" />
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
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="executeTestCase(row)">
                执行
              </el-button>
              <el-button type="primary" link @click="viewTestCase(row)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const project = ref<any>({})
const testCases = ref([])
const loading = ref(false)

const stats = reactive({
  totalCases: 0,
  passedCases: 0,
  failedCases: 0,
  passRate: 0
})

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

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchProject = async () => {
  const projectId = route.params.id
  loading.value = true
  
  try {
    const [projectRes, casesRes] = await Promise.all([
      axios.get(`/api/projects/${projectId}`),
      axios.get('/api/test-cases', { params: { project_id: projectId } })
    ])
    
    project.value = projectRes.data
    testCases.value = casesRes.data
    
    // Calculate stats
    stats.totalCases = casesRes.data.length
    // TODO: Calculate passed/failed from executions
    stats.passedCases = 0
    stats.failedCases = 0
    stats.passRate = 0
  } catch (error) {
    ElMessage.error('获取项目详情失败')
  } finally {
    loading.value = false
  }
}

const executeAllTests = async () => {
  try {
    for (const testCase of testCases.value) {
      await axios.post(`/api/test-cases/${(testCase as any).id}/execute`)
    }
    ElMessage.success('所有测试已开始执行')
    router.push('/test-executions')
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const executeTestCase = async (testCase: any) => {
  try {
    await axios.post(`/api/test-cases/${testCase.id}/execute`)
    ElMessage.success('测试已开始执行')
    router.push('/test-executions')
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const viewTestCase = (testCase: any) => {
  router.push(`/test-cases/${testCase.id}`)
}

const showAddCaseDialog = () => {
  router.push('/test-cases')
}

onMounted(() => {
  fetchProject()
})
</script>

<style scoped>
.project-detail {
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

.info-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.stat-card.passed .stat-value {
  color: #67c23a;
}

.stat-card.failed .stat-value {
  color: #f56c6c;
}

.stat-card.rate .stat-value {
  color: #409eff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>