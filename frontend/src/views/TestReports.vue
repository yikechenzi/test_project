<template>
  <div class="test-reports">
    <div class="page-header">
      <h2>测试报告</h2>
      <div class="header-actions">
        <el-select v-model="selectedProject" placeholder="选择项目" clearable style="width: 200px">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-button type="primary" @click="generateReport" :disabled="!selectedProject">
          <el-icon><Document /></el-icon>
          生成报告
        </el-button>
      </div>
    </div>
    
    <!-- Reports List -->
    <el-card>
      <el-table :data="reports" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="报告标题" />
        <el-table-column prop="project_id" label="项目ID" width="100" />
        <el-table-column prop="total_tests" label="总用例数" width="100" />
        <el-table-column prop="passed_tests" label="通过" width="80">
          <template #default="{ row }">
            <span style="color: #67c23a">{{ row.passed_tests }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed_tests" label="失败" width="80">
          <template #default="{ row }">
            <span style="color: #f56c6c">{{ row.failed_tests }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.pass_rate"
              :color="row.pass_rate >= 80 ? '#67c23a' : row.pass_rate >= 60 ? '#e6a23c' : '#f56c6c'"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewReport(row)">
              查看详情
            </el-button>
            <el-button type="success" link @click="downloadReport(row)">
              下载
            </el-button>
            <el-button type="danger" link @click="deleteReport(row)">
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
        @size-change="fetchReports"
        @current-change="fetchReports"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- Report Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="报告详情"
      width="90%"
      fullscreen
    >
      <div v-if="selectedReport" class="report-detail">
        <!-- Summary Cards -->
        <el-row :gutter="20" class="summary-row">
          <el-col :span="4">
            <el-card shadow="hover" class="summary-card">
              <div class="summary-value">{{ selectedReport.total_tests }}</div>
              <div class="summary-label">总用例数</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card shadow="hover" class="summary-card passed">
              <div class="summary-value">{{ selectedReport.passed_tests }}</div>
              <div class="summary-label">通过</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card shadow="hover" class="summary-card failed">
              <div class="summary-value">{{ selectedReport.failed_tests }}</div>
              <div class="summary-label">失败</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card shadow="hover" class="summary-card error">
              <div class="summary-value">{{ selectedReport.error_tests }}</div>
              <div class="summary-label">错误</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card shadow="hover" class="summary-card skipped">
              <div class="summary-value">{{ selectedReport.skipped_tests }}</div>
              <div class="summary-label">跳过</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card shadow="hover" class="summary-card rate">
              <div class="summary-value">{{ selectedReport.pass_rate }}%</div>
              <div class="summary-label">通过率</div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- Charts -->
        <el-row :gutter="20" style="margin-top: 20px">
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
                <span>测试详情</span>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="报告标题">
                  {{ selectedReport.title }}
                </el-descriptions-item>
                <el-descriptions-item label="生成时间">
                  {{ formatDate(selectedReport.created_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="开始时间">
                  {{ formatDate(selectedReport.start_time) }}
                </el-descriptions-item>
                <el-descriptions-item label="结束时间">
                  {{ formatDate(selectedReport.end_time) }}
                </el-descriptions-item>
                <el-descriptions-item label="总耗时">
                  {{ selectedReport.duration ? `${selectedReport.duration}秒` : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="描述">
                  {{ selectedReport.description || '-' }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'

const reports = ref([])
const projects = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedReport = ref<any>(null)
const selectedProject = ref<number | null>(null)
const statusChartRef = ref<HTMLElement>()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchReports = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    const response = await axios.get('/api/test-reports', { params })
    reports.value = response.data
    total.value = response.data.length
  } catch (error) {
    ElMessage.error('获取报告列表失败')
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

const generateReport = async () => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要为该项目生成测试报告吗？', '提示', {
      type: 'info'
    })
    
    await axios.post(`/api/test-reports/generate/${selectedProject.value}`)
    ElMessage.success('报告生成成功')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('报告生成失败')
    }
  }
}

const viewReport = async (report: any) => {
  try {
    const response = await axios.get(`/api/test-reports/${report.id}`)
    selectedReport.value = response.data
    detailDialogVisible.value = true
    
    await nextTick()
    initStatusChart()
  } catch (error) {
    ElMessage.error('获取报告详情失败')
  }
}

const initStatusChart = () => {
  if (!statusChartRef.value || !selectedReport.value) return
  
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
          { value: selectedReport.value.passed_tests, name: '通过', itemStyle: { color: '#67c23a' } },
          { value: selectedReport.value.failed_tests, name: '失败', itemStyle: { color: '#f56c6c' } },
          { value: selectedReport.value.error_tests, name: '错误', itemStyle: { color: '#e6a23c' } },
          { value: selectedReport.value.skipped_tests, name: '跳过', itemStyle: { color: '#909399' } }
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

const downloadReport = async (report: any) => {
  try {
    const response = await axios.get(`/api/test-reports/${report.id}/download`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `test-report-${report.id}.html`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const deleteReport = async (report: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该报告吗？', '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/test-reports/${report.id}`)
    ElMessage.success('删除成功')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchProjects()
  fetchReports()
})
</script>

<style scoped>
.test-reports {
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

.report-detail {
  padding: 10px 0;
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