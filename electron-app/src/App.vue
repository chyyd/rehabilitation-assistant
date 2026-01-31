<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { provide } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { usePatientStore } from '@/stores/patient'

// 提供全局状态
provide('patientStore', usePatientStore())
</script>

<style>
/* 全局样式 - iOS风格 */
:root {
  --ios-blue: #007AFF;
  --ios-green: #34C759;
  --ios-orange: #FF9500;
  --ios-red: #FF3B30;
  --ios-gray: #F2F2F7;
  --ios-border: #E5E5EA;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100vw;
  height: 100vh;
  background-color: var(--ios-gray);
  overflow: hidden;
}
</style>
