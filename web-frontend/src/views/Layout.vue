<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon class="logo-icon"><Connection /></el-icon>
        <span class="logo-title">MedGraph RAG</span>
      </div>
      <el-menu
        :default-active="route.path"
        router
        class="menu"
        background-color="#0b1726"
        text-color="#c1d1e8"
        active-text-color="#1677ff"
      >
        <el-menu-item index="/crawler">
          <el-icon><Download /></el-icon>
          <span>数据采集中枢</span>
        </el-menu-item>
        <el-menu-item index="/etl">
          <el-icon><DataAnalysis /></el-icon>
          <span>数仓ETL看板</span>
        </el-menu-item>
        <el-menu-item index="/graph-mining">
          <el-icon><Share /></el-icon>
          <span>图挖掘分析</span>
        </el-menu-item>
        <el-menu-item index="/chat-analysis">
          <el-icon><Histogram /></el-icon>
          <span>问答效果分析</span>
        </el-menu-item>
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>宏观指标大屏</span>
        </el-menu-item>
        <el-menu-item index="/graph">
          <el-icon><Connection /></el-icon>
          <span>知识图谱拓扑</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能问答工作台</span>
        </el-menu-item>
      </el-menu>
      <div class="user-profile">
        <div class="u-info">
          <el-avatar size="small" icon="UserFilled" />
          <span class="u-name">{{ userStore.username }}</span>
        </div>
        <el-button link type="danger" @click="handleLogout">退出</el-button>
      </div>
    </el-aside>
    
    <el-container class="main-container">
      <el-header height="48px" class="header">
        <div class="header-left">
          <span class="page-title">{{ currentTitle }}</span>
        </div>
        <div class="system-health-bar">
          <el-tooltip content="Scrapy 爬虫引擎与采集监控正常运行" placement="bottom">
            <span class="status-pill green">
              <span class="status-dot"></span>
              采集正常
            </span>
          </el-tooltip>
          <el-tooltip content="Spark 数仓分层清洗 ETL 管道就绪" placement="bottom">
            <span class="status-pill green">
              <span class="status-dot"></span>
              ETL就绪
            </span>
          </el-tooltip>
          <el-tooltip content="Neo4j 知识图谱图拓扑服务已连接" placement="bottom">
            <span class="status-pill green">
              <span class="status-dot"></span>
              图谱就绪
            </span>
          </el-tooltip>
          <el-tooltip content="FastAPI Graph RAG 混合检索推理引擎就绪" placement="bottom">
            <span class="status-pill green">
              <span class="status-dot"></span>
              AI引擎就绪
            </span>
          </el-tooltip>
          <el-tooltip content="Redis 滑动窗口限流与二级缓存保护已开启" placement="bottom">
            <span class="status-pill green">
              <span class="status-dot"></span>
              限流防护绿
            </span>
          </el-tooltip>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const titleMap: Record<string, string> = {
  '/crawler': '数据采集中枢 (Scrapy + Kafka)',
  '/etl': '数仓 ETL 管道看板 (ODS → DWD → ADS)',
  '/graph-mining': '图挖掘与关联分析 (PageRank / Louvain / 禁忌)',
  '/chat-analysis': '问答效果与运营分析 (Token / 意图 / 词云)',
  '/dashboard': '宏观医疗大数据指标分析大屏',
  '/graph': '3D 医药知识图谱动态拓扑视窗',
  '/chat': '临床医药 Graph RAG 智能问答工作台'
}

const currentTitle = computed(() => titleMap[route.path] || '医药大数据问答系统')

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
  width: 100vw;
  background-color: #06111c;
  color: #fff;
}
.aside {
  background-color: #0b1726;
  border-right: 1px solid rgba(22, 119, 255, 0.15);
  display: flex;
  flex-direction: column;
}
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 18px;
  border-bottom: 1px solid rgba(22, 119, 255, 0.15);
  .logo-icon {
    font-size: 24px;
    color: #1677ff;
    margin-right: 10px;
  }
  .logo-title {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #fff;
  }
}
.menu {
  flex: 1;
  border-right: none;
}
.user-profile {
  padding: 14px 18px;
  border-top: 1px solid rgba(22, 119, 255, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
  .u-info {
    display: flex;
    align-items: center;
    gap: 8px;
    .u-name {
      font-size: 13px;
      color: #c1d1e8;
    }
  }
}
.header {
  background-color: #091a2d;
  border-bottom: 1px solid rgba(22, 119, 255, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  .page-title {
    font-size: 15px;
    font-weight: 600;
    color: #e6f4ff;
  }
}
.system-health-bar {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
  
  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.25s ease;
    user-select: none;
    
    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      display: inline-block;
    }
    
    &.green {
      background: rgba(82, 196, 26, 0.16);
      color: #73d13d;
      border: 1px solid rgba(82, 196, 26, 0.45);
      
      .status-dot {
        background-color: #52c41a;
        box-shadow: 0 0 8px #52c41a;
      }
      
      &:hover {
        background: rgba(82, 196, 26, 0.28);
        border-color: #52c41a;
        transform: translateY(-1px);
        box-shadow: 0 2px 10px rgba(82, 196, 26, 0.25);
      }
    }
  }
}
.main-content {
  padding: 16px;
  overflow-y: auto;
  background-color: #06111c;
}
</style>
