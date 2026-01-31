/**
 * 简单的事件总线实现
 * 用于跨组件通信
 */
type EventCallback = (...args: any[]) => void

class EventBus {
  private events: Record<string, EventCallback[]> = {}

  /**
   * 监听事件
   */
  on(event: string, callback: EventCallback) {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(callback)
  }

  /**
   * 取消监听
   */
  off(event: string, callback: EventCallback) {
    if (!this.events[event]) return

    const index = this.events[event].indexOf(callback)
    if (index > -1) {
      this.events[event].splice(index, 1)
    }
  }

  /**
   * 触发事件
   */
  emit(event: string, ...args: any[]) {
    if (!this.events[event]) return

    this.events[event].forEach(callback => {
      callback(...args)
    })
  }
}

// 导出单例
export const eventBus = new EventBus()
