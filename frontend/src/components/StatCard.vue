<template>
  <el-card
    class="stat-card"
    :class="type"
    shadow="hover"
    @click="$emit('click')"
  >
    <div class="stat-content">
      <div class="stat-icon" :style="{ backgroundColor: iconColor }">
        <el-icon :size="24">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="stat-info">
        <div class="stat-value">{{ value }}</div>
        <div class="stat-label">{{ label }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps({
  value: {
    type: [Number, String],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'DataAnalysis'
  },
  iconColor: {
    type: String,
    default: '#409eff'
  },
  type: {
    type: String,
    default: ''
  }
})

defineEmits(['click'])
</script>

<style scoped>
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

.stat-card.passed .stat-value {
  color: #67c23a;
}

.stat-card.failed .stat-value {
  color: #f56c6c;
}

.stat-card.error .stat-value {
  color: #e6a23c;
}

.stat-card.rate .stat-value {
  color: #409eff;
}
</style>