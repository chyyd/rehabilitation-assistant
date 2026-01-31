import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Main',
    component: () => import('@/views/MainView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
