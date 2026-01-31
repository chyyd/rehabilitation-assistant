/**
 * Preload脚本
 * 暴露安全的API给渲染进程
 */
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  // API调用 - 与Python后端通信
  invoke: async (channel: string, ...args: any[]) => {
    const validChannels = ['api-request', 'health-check']
    if (validChannels.includes(channel)) {
      return ipcRenderer.invoke(channel, ...args)
    }
    return Promise.reject('Invalid channel')
  },

  // 便捷方法：API请求
  apiRequest: async (method: string, url: string, data?: any) => {
    return ipcRenderer.invoke('api-request', { method, url, data })
  },

  // 便捷方法：健康检查
  healthCheck: async () => {
    return ipcRenderer.invoke('health-check')
  }
})
