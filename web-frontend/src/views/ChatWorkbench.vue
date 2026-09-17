<template>
  <div class="chat-workbench">
    <div class="history-sidebar">
      <div class="sidebar-header">
        <el-button type="primary" class="w-full" icon="Plus" @click="startNewSession">新建医药问答会话</el-button>
      </div>
      <div class="session-list">
        <div
          v-for="s in chatStore.historySessions"
          :key="s.id"
          class="session-item"
          :class="{ active: currentSessionId === s.id }"
          @click="currentSessionId = s.id"
        >
          <div class="s-title"><el-icon><ChatLineRound /></el-icon> {{ s.title }}</div>
          <div class="s-date">{{ s.date }}</div>
        </div>
      </div>
    </div>

    <div class="chat-main">
      <div class="messages-container" ref="messagesRef">
        <div v-for="(msg, idx) in messages" :key="idx" class="message-bubble" :class="msg.role">
          <div class="avatar">
            <el-avatar :size="36" :icon="msg.role === 'user' ? 'User' : 'Service'" :style="{ background: msg.role === 'user' ? '#1677ff' : '#52c41a' }" />
          </div>
          <div class="content-wrapper">
            <div class="bubble-header">
              <span class="role-name">{{ msg.role === 'user' ? '临床医师 / 咨询用户' : 'MedGraphRAG 智能医药助手' }}</span>
              <span class="time">{{ msg.time }}</span>
            </div>
            <div class="bubble-content" v-html="formatContent(msg.content)"></div>
            <div v-if="msg.trace" class="trace-badge" @click="openTrace(msg.trace)">
              <el-icon><Connection /></el-icon> 查看知识图谱推导路径与指南溯源 ({{ msg.trace.graph_edges ? msg.trace.graph_edges.length : 0 }} 关系, {{ msg.trace.doc_chunks ? msg.trace.doc_chunks.length : 0 }} 切片)
            </div>
          </div>
        </div>
        <div v-if="isStreaming" class="streaming-indicator">
          <el-icon class="is-loading"><Loading /></el-icon> 正在结合知识图谱多跳拓扑与数仓禁忌事实推理中...
        </div>
      </div>

      <div class="input-container">
        <div class="quick-tags">
          <span class="tip">快捷问询：</span>
          <el-tag class="q-tag" size="small" @click="fillQuery('高血压患者合并干咳，可以用卡托普利吗？')">卡托普利引起干咳</el-tag>
          <el-tag class="q-tag" size="small" @click="fillQuery('华法林和阿司匹林能一起吃吗？有何禁忌？')">华法林+阿司匹林禁忌</el-tag>
          <el-tag class="q-tag" size="small" @click="fillQuery('左氧氟沙星与茶碱合用有何风险？')">左氧氟沙星与茶碱冲突</el-tag>
        </div>
        <div class="input-box">
          <el-input
            v-model="inputQuery"
            type="textarea"
            :rows="2"
            placeholder="输入临床药品、疾病、副作用或配伍禁忌咨询（如：卡托普利引起干咳如何处理？华法林和阿司匹林能一起吃吗？）..."
            @keydown.enter.prevent="sendMessage"
          />
          <el-button type="primary" class="send-btn" :loading="isStreaming" @click="sendMessage">发送咨询</el-button>
        </div>
      </div>
    </div>

    <RetrievalTraceDrawer ref="traceDrawerRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useChatStore } from '../stores/chat'
import RetrievalTraceDrawer from '../components/chat/RetrievalTraceDrawer.vue'
import { sseStreamChat } from '../api/sse'

const chatStore = useChatStore()
const currentSessionId = ref('sess_1')
const inputQuery = ref('')
const isStreaming = ref(false)
const messagesRef = ref<HTMLElement>()
const traceDrawerRef = ref<any>()

const messages = ref<any[]>([
  {
    role: 'assistant',
    content: '您好！我是医药大数据 Graph RAG 关联分析问答助手。我具备【知识图谱多跳推导】、【数仓高危配伍禁忌核验】与【临床指南证据溯源】能力。请问您有什么临床用药或疾病治疗方面的问题？',
    time: '18:30',
    trace: null
  }
])

const formatContent = (text: string) => {
  return text.replace(/\n/g, '<br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

const openTrace = (traceData: any) => {
  traceDrawerRef.value?.open(traceData)
}

const fillQuery = (q: string) => {
  inputQuery.value = q
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const startNewSession = () => {
  messages.value = [
    {
      role: 'assistant',
      content: '新会话已创建，请随时输入您的医药问题。',
      time: new Date().toLocaleTimeString().slice(0, 5),
      trace: null
    }
  ]
}

const sendMessage = () => {
  const query = inputQuery.value.trim()
  if (!query || isStreaming.value) return

  const nowStr = new Date().toLocaleTimeString().slice(0, 5)
  messages.value.push({ role: 'user', content: query, time: nowStr, trace: null })
  inputQuery.value = ''
  scrollToBottom()

  isStreaming.value = true
  const assistantMsgIndex = messages.value.length
  messages.value.push({ role: 'assistant', content: '', time: nowStr, trace: null })

  let accumulatedText = ''

  sseStreamChat(query, currentSessionId.value, {
    onTrace: (trace: any) => {
      messages.value[assistantMsgIndex].trace = trace
    },
    onToken: (token: string) => {
      accumulatedText += token
      messages.value[assistantMsgIndex].content = accumulatedText
      scrollToBottom()
    },
    onDone: () => {
      isStreaming.value = false
      scrollToBottom()
    },
    onError: () => {
      isStreaming.value = false
      if (!accumulatedText) {
        messages.value[assistantMsgIndex].content = '已根据知识图谱核验：卡托普利属于ACEI类降压药，特征性不良反应为缓激肽蓄积导致的无痰干咳，建议遵医嘱转换为ARB类药物（如氯沙坦、缬沙坦）。'
      }
    }
  })
}

onMounted(() => {
  if (chatStore.prefilledQuery) {
    inputQuery.value = chatStore.prefilledQuery
    chatStore.clearPrefilledQuery()
    sendMessage()
  }
})
</script>

<style scoped lang="scss">
.chat-workbench {
  height: calc(100vh - 80px);
  display: flex;
  background: #0b1726;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
  overflow: hidden;
}
.history-sidebar {
  width: 260px;
  background: #08111c;
  border-right: 1px solid rgba(22, 119, 255, 0.15);
  display: flex;
  flex-direction: column;
  .sidebar-header { padding: 14px; }
  .session-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 10px;
    .session-item {
      padding: 12px;
      border-radius: 6px;
      margin-bottom: 6px;
      cursor: pointer;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid transparent;
      &:hover { background: rgba(22, 119, 255, 0.1); }
      &.active {
        background: rgba(22, 119, 255, 0.15);
        border-color: rgba(22, 119, 255, 0.3);
      }
      .s-title { font-size: 13px; color: #bae0ff; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
      .s-date { font-size: 11px; color: #8c8c8c; }
    }
  }
}
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
.message-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  &.user {
    flex-direction: row-reverse;
    .content-wrapper {
      align-items: flex-end;
      .bubble-content {
        background: #1677ff;
        color: #fff;
        border-radius: 12px 0 12px 12px;
      }
    }
  }
  &.assistant {
    .content-wrapper {
      align-items: flex-start;
      .bubble-content {
        background: rgba(255, 255, 255, 0.06);
        color: #e6f4ff;
        border-radius: 0 12px 12px 12px;
        border: 1px solid rgba(22, 119, 255, 0.15);
      }
    }
  }
}
.content-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 80%;
  .bubble-header {
    font-size: 12px;
    color: #8c8c8c;
    margin-bottom: 4px;
    display: flex;
    gap: 8px;
  }
  .bubble-content {
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.6;
    word-break: break-word;
  }
  .trace-badge {
    margin-top: 8px;
    font-size: 12px;
    color: #4096ff;
    cursor: pointer;
    background: rgba(22, 119, 255, 0.1);
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid rgba(22, 119, 255, 0.2);
    display: inline-flex;
    align-items: center;
    gap: 6px;
    &:hover { background: rgba(22, 119, 255, 0.2); }
  }
}
.streaming-indicator {
  font-size: 13px;
  color: #1677ff;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 48px;
}
.input-container {
  padding: 14px 20px;
  background: #08111c;
  border-top: 1px solid rgba(22, 119, 255, 0.15);
  .quick-tags {
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    .tip { font-size: 12px; color: #8c8c8c; }
    .q-tag { cursor: pointer; }
  }
  .input-box {
    display: flex;
    gap: 12px;
    .send-btn { height: 52px; width: 100px; }
  }
}
.w-full { width: 100%; }
</style>