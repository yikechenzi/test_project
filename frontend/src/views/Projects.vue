<template>
  <div class="projects">
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button v-if="authStore.isAdmin" type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>
    
    <!-- Project List -->
    <el-card>
      <el-table :data="projects" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="company_name" label="所属公司" width="150" />
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewProject(row)">
              查看
            </el-button>
            <el-button v-if="authStore.isAdmin" type="primary" link @click="editProject(row)">
              编辑
            </el-button>
            <el-button v-if="authStore.isAdmin" type="danger" link @click="deleteProject(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑项目' : '新建项目'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        
        <el-form-item v-if="!isEdit" label="所属公司" prop="company_id">
          <el-select v-model="form.company_id" placeholder="请选择公司" style="width: 100%">
            <el-option
              v-for="company in companies"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
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
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const projects = ref([])
const companies = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const editId = ref<number | null>(null)

const formRef = ref()

const form = reactive({
  name: '',
  description: '',
  company_id: null as number | null
})

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  company_id: [
    { required: true, message: '请选择公司', trigger: 'change' }
  ]
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/projects')
    projects.value = response.data
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCompanies = async () => {
  try {
    const response = await axios.get('/api/companies')
    companies.value = response.data
  } catch (error) {
    console.error('Failed to fetch companies:', error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  editId.value = null
  form.name = ''
  form.description = ''
  form.company_id = null
  dialogVisible.value = true
}

const editProject = (project: any) => {
  isEdit.value = true
  editId.value = project.id
  form.name = project.name
  form.description = project.description
  dialogVisible.value = true
}

const viewProject = (project: any) => {
  router.push(`/projects/${project.id}`)
}

const deleteProject = async (project: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该项目吗？', '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/projects/${project.id}`)
    ElMessage.success('删除成功')
    fetchProjects()
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
      await axios.put(`/api/projects/${editId.value}`, {
        name: form.name,
        description: form.description
      })
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/projects', form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchProjects()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchProjects()
  if (authStore.isAdmin) {
    fetchCompanies()
  }
})
</script>

<style scoped>
.projects {
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
</style>