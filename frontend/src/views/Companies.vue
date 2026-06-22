<template>
  <div class="companies">
    <div class="page-header">
      <h2>公司管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        新建公司
      </el-button>
    </div>
    
    <!-- Companies List -->
    <el-card>
      <el-table :data="companies" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="公司名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
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
            <el-button type="primary" link @click="editCompany(row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="deleteCompany(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑公司' : '新建公司'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="公司名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入公司名称" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入公司描述"
          />
        </el-form-item>
        
        <el-form-item v-if="isEdit" label="状态">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

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
  is_active: true
})

const rules = {
  name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' }
  ]
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchCompanies = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/companies')
    companies.value = response.data
  } catch (error) {
    ElMessage.error('获取公司列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  editId.value = null
  form.name = ''
  form.description = ''
  form.is_active = true
  dialogVisible.value = true
}

const editCompany = (company: any) => {
  isEdit.value = true
  editId.value = company.id
  form.name = company.name
  form.description = company.description
  form.is_active = company.is_active
  dialogVisible.value = true
}

const deleteCompany = async (company: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该公司吗？', '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/companies/${company.id}`)
    ElMessage.success('删除成功')
    fetchCompanies()
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
      await axios.put(`/api/companies/${editId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/companies', form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchCompanies()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCompanies()
})
</script>

<style scoped>
.companies {
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