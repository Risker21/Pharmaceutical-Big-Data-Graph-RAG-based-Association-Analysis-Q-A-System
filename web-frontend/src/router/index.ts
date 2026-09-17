import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '../views/Layout.vue'
import LoginView from '../views/LoginView.vue'
import CrawlerHubView from '../views/CrawlerHubView.vue'
import EtlMonitorView from '../views/EtlMonitorView.vue'
import GraphMiningView from '../views/GraphMiningView.vue'
import ChatAnalysisView from '../views/ChatAnalysisView.vue'
import DashboardView from '../views/DashboardView.vue'
import GraphView from '../views/GraphView.vue'
import ChatWorkbench from '../views/ChatWorkbench.vue'

const routes: Array<RouteRecordRaw> = [
  { path: '/login', name: 'Login', component: LoginView },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      { path: 'crawler', name: 'CrawlerHub', component: CrawlerHubView, meta: { title: '数据采集中枢', icon: 'Download' } },
      { path: 'etl', name: 'EtlMonitor', component: EtlMonitorView, meta: { title: '数仓ETL看板', icon: 'DataAnalysis' } },
      { path: 'graph-mining', name: 'GraphMining', component: GraphMiningView, meta: { title: '图挖掘分析', icon: 'Share' } },
      { path: 'chat-analysis', name: 'ChatAnalysis', component: ChatAnalysisView, meta: { title: '问答效果分析', icon: 'Histogram' } },
      { path: 'dashboard', name: 'Dashboard', component: DashboardView, meta: { title: '宏观指标大屏', icon: 'Odometer' } },
      { path: 'graph', name: 'Graph', component: GraphView, meta: { title: '知识图谱拓扑', icon: 'Connection' } },
      { path: 'chat', name: 'Chat', component: ChatWorkbench, meta: { title: '智能问答工作台', icon: 'ChatDotRound' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    // 自动以演示 admin 身份登录
    localStorage.setItem('token', 'mock_jwt_token_admin')
    localStorage.setItem('username', 'admin')
    localStorage.setItem('roles', JSON.stringify(['ROLE_ADMIN', 'ROLE_USER']))
  }
  next()
})

export default router
