<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    
    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon size="24"><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.projects }}</div>
              <div class="stat-label">项目数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.testCases }}</div>
              <div class="stat-label">测试用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon size="24"><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.executions }}</div>
              <div class="stat-label">执行次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon size="24"><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.passRate }}%</div>
              <div class="stat-label">通过率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>测试执行趋势</span>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>测试状态分布</span>
          </template>
          <div class="chart-container" ref="statusChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Recent Executions -->
    <el-card class="recent-card">
      <template #header>
        <span>最近执行</span>
      </template>
      <el-table :data="recentExecutions" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="test_case_name" label="测试用例" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? `${row.duration.toFixed(2)}s` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="执行时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()

const stats = reactive({
  projects: 0,
  testCases: 0,
  executions: 0,
  passRate: 0
})

const recentExecutions = ref([])

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    passed: 'success',
    failed: 'danger',
    error: 'warning',
    pending: 'info',
    running: 'primary'
  }
  return types[status] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  const chart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '执行次数',
        type: 'line',
        smooth: true,
        data: [10, 15, 8, 20, 12, 18, 25],
        areaStyle: {
          opacity: 0.3
        },
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  chart.setOption(option)
}

const initStatusChart = () => {
  if (!statusChartRef.value) return
  
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
          { value: 580, name: '通过', itemStyle: { color: '#67c23a' } },
          { value: 120, name: '失败', itemStyle: { color: '#f56c6c' } },
          { value: 50, name: '错误', itemStyle: { color: '#e6a23c' } },
          { value: 30, name: '跳过', itemStyle: { color: '#909399' } }
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

const fetchDashboardData = async () => {
  try {
    // Fetch stats
    const [projectsRes, casesRes, execsRes] = await Promise.all([
      axios.get('/api/projects'),
      axios.get('/api/test-cases'),
      axios.get('/api/test-executions')
    ])
    
    stats.projects = projectsRes.data.length
    stats.testCases = casesRes.data.length
    stats.executions = execsRes.data.length
    
    // Calculate pass rate
    const passed = execsRes.data.filter((e: any) => e.status === 'passed').length
    stats.passRate = stats.executions > 0 
      ? Math.round((passed / stats.executions) * 100) 
      : 0
    
    // Recent executions
    recentExecutions.value = execsRes.data.slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

onMounted(() => {
  fetchDashboardData()
  initTrendChart()
  initStatusChart()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.dashboard h2 {
  margin-bottom: 20px;
  color: #333;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.recent-card {
  margin-bottom: 20px;
}
</style>