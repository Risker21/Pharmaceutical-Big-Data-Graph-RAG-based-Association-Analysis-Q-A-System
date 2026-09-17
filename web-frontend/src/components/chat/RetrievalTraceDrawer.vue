<template>
  <el-drawer
    v-model="visible"
    title="医药知识图谱与指南溯源详情"
    size="520px"
    class="trace-drawer"
    :with-header="true"
  >
    <div v-if="trace" class="trace-body">
      <div class="sec">
        <h4><el-icon><PriceTag /></el-icon> 识别医学实体</h4>
        <div class="tags">
          <el-tag v-for="e in trace.entities" :key="e" type="primary" effect="dark" size="small">{{ e }}</el-tag>
          <span v-if="!trace.entities || !trace.entities.length" class="empty">未识别到特定实体</span>
        </div>
      </div>

      <div class="sec">
        <h4><el-icon><Connection /></el-icon> 知识图谱拓扑推导路径 (1~2 跳)</h4>
        <el-timeline v-if="trace.graph_edges && trace.graph_edges.length">
          <el-timeline-item
            v-for="(edge, idx) in trace.graph_edges"
            :key="idx"
            type="primary"
            color="#1677ff"
            hollow
          >
            <div class="edge-box">
              <span class="node from">{{ edge.from || edge.from_node }}</span>
              <span class="rel">--[{{ edge.rel }}]--></span>
              <span class="node to">{{ edge.to || edge.to_node }}</span>
            </div>
          </el-timeline-item>
        </el-timeline>
        <div v-else class="empty">无图谱特定路径关联</div>
      </div>

      <div class="sec" v-if="trace.contraindications && trace.contraindications.length">
        <h4><el-icon><Warning /></el-icon> 数仓高危配伍禁忌阻断核验</h4>
        <div v-for="(c, i) in trace.contraindications" :key="i" class="contra-card">
          <div class="lvl-tag" :class="c.level ? c.level.toLowerCase() : 'high'">{{ c.level }} 级高危警告</div>
          <div class="contra-text">{{ c.risk || c.risk_detail }}</div>
        </div>
      </div>

      <div class="sec">
        <h4><el-icon><Document /></el-icon> 临床指南与文献切片引用</h4>
        <div v-for="(chunk, i) in trace.doc_chunks" :key="i" class="chunk-card">
          <div class="chunk-header">文献切片 #{{ i + 1 }}</div>
          <div class="chunk-content">{{ chunk }}</div>
        </div>
        <div v-if="!trace.doc_chunks || !trace.doc_chunks.length" class="empty">未检索到具体文献切片</div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const trace = ref<any>(null)

const open = (traceData: any) => {
  trace.value = traceData
  visible.value = true
}

defineExpose({ open })
</script>

<style scoped lang="scss">
.trace-body {
  padding: 10px;
  color: #e6f4ff;
}
.sec {
  margin-bottom: 24px;
  h4 {
    font-size: 14px;
    margin-bottom: 12px;
    color: #4096ff;
    display: flex;
    align-items: center;
    gap: 6px;
  }
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.edge-box {
  background: rgba(22, 119, 255, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  border-left: 3px solid #1677ff;
  .node {
    font-weight: bold;
    color: #bae0ff;
  }
  .rel {
    margin: 0 6px;
    color: #8c8c8c;
  }
}
.contra-card {
  background: rgba(255, 77, 79, 0.1);
  border: 1px solid rgba(255, 77, 79, 0.3);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  .lvl-tag {
    font-weight: bold;
    color: #ff4d4f;
    font-size: 12px;
    margin-bottom: 4px;
  }
  .contra-text {
    font-size: 13px;
    line-height: 1.5;
    color: #fff1f0;
  }
}
.chunk-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  .chunk-header {
    font-size: 12px;
    color: #1677ff;
    margin-bottom: 6px;
  }
  .chunk-content {
    font-size: 13px;
    line-height: 1.6;
    color: #d9d9d9;
  }
}
.empty {
  font-size: 13px;
  color: #8c8c8c;
}
</style>