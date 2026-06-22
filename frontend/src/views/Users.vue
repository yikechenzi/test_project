<template>
  <div class="users">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>
    
    <!-- Users List -->
    <el-card>
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="full_name" label="姓名" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
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
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editUser(row)">
              编辑
            </el-button>
            <el-button type="warning" link @click="showProjectDialog(row)">
              绑定项目
            </el-button>
            <el-button type="info" link @click="resetPassword(row)">
              重置密码
            </el-button>
            <el-button type="danger" link @click="deleteUser(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- Create/Edit User Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="isEdit"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="所属公司">
          <el-select v-model="form.company_id" placeholder="请选择公司" clearable style="width: 100%">
            <el-option
              v-for="company in companies"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- Project Binding Dialog -->
    <el-dialog
      v-model="projectDialogVisible"
      title="绑定项目"
      width="600px"
    >
      <div v-if="selectedUser" class="project-binding">
        <p>为用户 <strong>{{ selectedUser.username }}</strong> 绑定项目：</p>
        
        <el-transfer
          v-model="selectedProjects"
          :data="allProjects"
          :titles="['可选项目', '已绑定项目']"
          :props="{
            key: 'id',
            label: 'name'
          }"
        />
      </div>
      
      <template #footer>
        <el-button @click="projectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleProjectBinding" :loading="bindingProjects">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const users = ref([])
const companies = ref([])
const allProjects = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const projectDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const bindingProjects = ref(false)
const editId = ref<number | null>(null)
const selectedUser = ref<any>(null)
const selectedProjects = ref<number[]>([])

const formRef = ref()

const form = reactive({
  username: '',
  email: '',
  password: '',
  full_name: '',
  role: 'user',
  company_id: null as number | null,
  is_active: true
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/users')
    users.value = response.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
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

const fetchProjects = async () => {
  try {
    const response = await axios.get('/api/projects')
    allProjects.value = response.data.map((p: any) => ({
      id: p.id,
      name: p.name
    }))
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  editId.value = null
  form.username = ''
  form.email = ''
  form.password = ''
  form.full_name = ''
  form.role = 'user'
  form.company_id = null
  form.is_active = true
  dialogVisible.value = true
}

const editUser = (user: any) => {
  isEdit.value = true
  editId.value = user.id
  form.username = user.username
  form.email = user.email
  form.full_name = user.full_name
  form.role = user.role
  form.company_id = user.company_id
  form.is_active = user.is_active
  dialogVisible.value = true
}

const showProjectDialog = async (user: any) => {
  selectedUser.value = user
  
  try {
    const response = await axios.get(`/api/users/${user.id}/projects`)
    selectedProjects.value = response.data.map((p: any) => p.id)
  } catch (error) {
    selectedProjects.value = []
  }
  
  projectDialogVisible.value = true
}

const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/users/${user.id}`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetPassword = async (user: any) => {
  try {
    const { value: newPassword } = await ElMessageBox.prompt(
      '请输入新密码',
      '重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.{6,}/,
        inputErrorMessage: '密码长度不能少于6位'
      }
    )
    
    await axios.post(`/api/users/${user.id}/reset-password`, null, {
      params: { new_password: newPassword }
    })
    ElMessage.success('密码重置成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('密码重置失败')
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
      await axios.put(`/api/users/${editId.value}`, {
        email: form.email,
        full_name: form.full_name,
        role: form.role,
        company_id: form.company_id,
        is_active: form.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/users', form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchUsers()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleProjectBinding = async () => {
  if (!selectedUser.value) return
  
  bindingProjects.value = true
  
  try {
    // Get current projects
    const currentResponse = await axios.get(`/api/users/${selectedUser.value.id}/projects`)
    const currentProjects = currentResponse.data.map((p: any) => p.id)
    
    // Add new projects
    for (const projectId of selectedProjects.value) {
      if (!currentProjects.includes(projectId)) {
        await axios.post(`/api/users/${selectedUser.value.id}/projects/${projectId}`)
      }
    }
    
    // Remove unselected projects
    for (const projectId of currentProjects) {
      if (!selectedProjects.value.includes(projectId)) {
        await axios.delete(`/api/users/${selectedUser.value.id}/projects/${projectId}`)
      }
    }
    
    ElMessage.success('项目绑定成功')
    projectDialogVisible.value = false
  } catch (error) {
    ElMessage.error('项目绑定失败')
  } finally {
    bindingProjects.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchCompanies()
  fetchProjects()
})
</script>

<style scoped>
.users {
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

.project-binding {
  padding: 10px 0;
}

.project-binding p {
  margin-bottom: 20px;
  color: #333;
}
</style>