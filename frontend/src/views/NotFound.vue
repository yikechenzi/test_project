<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="goHome">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
}

.content {
  text-align: center;
}

.content h1 {
  font-size: 120px;
  color: #409eff;
  margin: 0;
  line-height: 1;
}

.content h2 {
  font-size: 24px;
  color: #333;
  margin: 20px 0 10px;
}

.content p {
  color: #666;
  margin-bottom: 30px;
}
</style>