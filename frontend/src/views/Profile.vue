<template>
  <div class="profile">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>
    
    <el-row :gutter="20">
      <!-- User Info -->
      <el-col :span="8">
        <el-card class="user-card">
          <div class="user-avatar">
            <el-avatar :size="80" icon="UserFilled" />
          </div>
          <h3>{{ user.username }}</h3>
          <p class="user-email">{{ user.email }}</p>
          <el-tag :type="user.role === 'admin' ? 'danger' : 'primary'">
            {{ user.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
          
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ stats.projects }}</div>
              <div class="stat-label">参与项目</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.executions }}</div>
              <div class="stat-label">执行次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- Edit Form -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>编辑资料</span>
          </template>
          
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="100px"
          >
            <el-form-item label="用户名">
              <el-input v-model="user.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
            
            <el-form-item label="姓名">
              <el-input v-model="form.full_name" placeholder="请输入姓名" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- Change Password -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>修改密码</span>
          </template>
          
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="passwordForm.currentPassword"
                type="password"
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()

const user = ref<any>({})
const stats = reactive({
  projects: 0,
  executions: 0
})

const updating = ref(false)
const changingPassword = ref(false)

const formRef = ref()
const passwordFormRef = ref()

const form = reactive({
  email: '',
  full_name: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const fetchUserInfo = async () => {
  try {
    const response = await axios.get('/api/auth/me')
    user.value = response.data
    form.email = response.data.email
    form.full_name = response.data.full_name || ''
    
    // Fetch stats
    const [projectsRes, execsRes] = await Promise.all([
      axios.get('/api/projects'),
      axios.get('/api/test-executions')
    ])
    
    stats.projects = projectsRes.data.length
    stats.executions = execsRes.data.length
  } catch (error) {
    console.error('Failed to fetch user info:', error)
  }
}

const updateProfile = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  
  updating.value = true
  
  try {
    await axios.put('/api/auth/me', {
      email: form.email,
      full_name: form.full_name
    })
    
    ElMessage.success('更新成功')
    fetchUserInfo()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    updating.value = false
  }
}

const changePassword = async () => {
  try {
    await passwordFormRef.value?.validate()
  } catch {
    return
  }
  
  changingPassword.value = true
  
  try {
    await axios.post('/api/auth/change-password', null, {
      params: {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword
      }
    })
    
    ElMessage.success('密码修改成功')
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.profile {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.user-card {
  text-align: center;
}

.user-avatar {
  margin-bottom: 15px;
}

.user-card h3 {
  margin: 10px 0 5px;
  color: #333;
}

.user-email {
  color: #666;
  margin-bottom: 15px;
}

.user-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}
</style>