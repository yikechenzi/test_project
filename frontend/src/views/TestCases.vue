<template>
  <div class="test-cases">
    <div class="page-header">
      <h2>测试用例</h2>
      <div class="header-actions">
        <el-select v-model="selectedProject" placeholder="选择项目" clearable style="width: 200px">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
      </div>
    </div>
    
    <!-- Filters -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.testType" placeholder="测试类型" clearable>
            <el-option label="黑盒测试" value="black_box" />
            <el-option label="白盒测试" value="white_box" />
            <el-option label="API测试" value="api" />
            <el-option label="UI测试" value="ui" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.priority" placeholder="优先级" clearable>
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="critical" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="filters.keyword" placeholder="搜索用例名称" clearable />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="fetchTestCases">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- Test Cases List -->
    <el-card>
      <el-table :data="testCases" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" />
        <el-table-column prop="test_type" label="测试类型" width="120">
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
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewTestCase(row)">
              查看
            </el-button>
            <el-button type="success" link @click="executeTestCase(row)">
              执行
            </el-button>
            <el-button type="primary" link @click="editTestCase(row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="deleteTestCase(row)">
              删除
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
        @size-change="fetchTestCases"
        @current-change="fetchTestCases"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑测试用例' : '新建测试用例'"
      width="800px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用例名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入用例名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属项目" prop="project_id">
              <el-select v-model="form.project_id" placeholder="请选择项目" style="width: 100%">
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="测试类型" prop="test_type">
              <el-select v-model="form.test_type" placeholder="请选择测试类型" style="width: 100%">
                <el-option label="黑盒测试" value="black_box" />
                <el-option label="白盒测试" value="white_box" />
                <el-option label="API测试" value="api" />
                <el-option label="UI测试" value="ui" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择优先级" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="请输入用例描述"
          />
        </el-form-item>
        
        <el-form-item label="测试脚本" prop="script_content">
          <el-input
            v-model="form.script_content"
            type="textarea"
            :rows="10"
            placeholder="请输入Python测试脚本"
          />
        </el-form-item>
        
        <el-form-item label="预期结果">
          <el-input
            v-model="form.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入预期结果"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input v-model="form.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const router = useRouter()

const testCases = ref([])
const projects = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const editId = ref<number | null>(null)
const selectedProject = ref<number | null>(null)

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  testType: '',
  priority: '',
  keyword: ''
})

const formRef = ref()

const form = reactive({
  name: '',
  project_id: null as number | null,
  test_type: 'black_box',
  priority: 'medium',
  description: '',
  script_content: '',
  expected_result: '',
  tags: ''
})

const rules = {
  name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' }
  ],
  project_id: [
    { required: true, message: '请选择项目', trigger: 'change' }
  ],
  test_type: [
    { required: true, message: '请选择测试类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  script_content: [
    { required: true, message: '请输入测试脚本', trigger: 'blur' }
  ]
}

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

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchTestCases = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    if (filters.testType) {
      params.test_type = filters.testType
    }
    if (filters.priority) {
      params.priority = filters.priority
    }
    
    const response = await axios.get('/api/test-cases', { params })
    testCases.value = response.data
    total.value = response.data.length
  } catch (error) {
    ElMessage.error('获取测试用例列表失败')
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await axios.get('/api/projects')
    projects.value = response.data
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  }
}

const resetFilters = () => {
  filters.testType = ''
  filters.priority = ''
  filters.keyword = ''
  fetchTestCases()
}

const showCreateDialog = () => {
  isEdit.value = false
  editId.value = null
  form.name = ''
  form.project_id = selectedProject.value
  form.test_type = 'black_box'
  form.priority = 'medium'
  form.description = ''
  form.script_content = ''
  form.expected_result = ''
  form.tags = ''
  dialogVisible.value = true
}

const editTestCase = (testCase: any) => {
  isEdit.value = true
  editId.value = testCase.id
  form.name = testCase.name
  form.project_id = testCase.project_id
  form.test_type = testCase.test_type
  form.priority = testCase.priority
  form.description = testCase.description
  form.script_content = testCase.script_content
  form.expected_result = testCase.expected_result
  form.tags = testCase.tags
  dialogVisible.value = true
}

const viewTestCase = (testCase: any) => {
  router.push(`/test-cases/${testCase.id}`)
}

const executeTestCase = async (testCase: any) => {
  try {
    await ElMessageBox.confirm('确定要执行该测试用例吗？', '提示', {
      type: 'info'
    })
    
    await axios.post(`/api/test-cases/${testCase.id}/execute`)
    ElMessage.success('测试已开始执行')
    router.push('/test-executions')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败')
    }
  }
}

const deleteTestCase = async (testCase: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该测试用例吗？', '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/test-cases/${testCase.id}`)
    ElMessage.success('删除成功')
    fetchTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  
  submitting.value = true
  
  try {
    if (isEdit.value && editId.value) {
      await axios.put(`/api/test-cases/${editId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/test-cases', form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchTestCases()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

watch(selectedProject, () => {
  fetchTestCases()
})

onMounted(() => {
  fetchProjects()
  fetchTestCases()
})
</script>

<style scoped>
.test-cases {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-card {
  margin-bottom: 20px;
}
</style>