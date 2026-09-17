<template>
  <div class="graph-view">
    <div class="toolbar">
      <el-input v-model="searchKey" placeholder="搜索药品 / 疾病 / 症状实体..." style="width: 280px;" prefix-icon="Search" clearable @change="filterGraph" />
      <div class="filters">
        <el-tag effect="dark" type="primary" class="legend-tag">💊 药品 (Drug)</el-tag>
        <el-tag effect="dark" type="success" class="legend-tag">🏥 疾病 (Disease)</el-tag>
        <el-tag effect="dark" type="warning" class="legend-tag">⚗️ 成分 (Ingredient)</el-tag>
        <el-tag effect="dark" type="danger" class="legend-tag">🤒 症状 (Symptom)</el-tag>
      </div>
      <el-button type="primary" size="small" @click="resetLayout">重置拓扑视窗</el-button>
    </div>
    <div ref="containerRef" class="graph-canvas"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import G6 from '@antv/g6'

const searchKey = ref('')
const containerRef = ref<HTMLElement>()
let graph: any = null

const graphData = {
  nodes: [
    { id: 'd1', label: '卡托普利', type: 'Drug', style: { fill: '#1677ff' }, size: 45 },
    { id: 'd2', label: '依那普利', type: 'Drug', style: { fill: '#1677ff' }, size: 40 },
    { id: 'd3', label: '华法林', type: 'Drug', style: { fill: '#1677ff' }, size: 45 },
    { id: 'd4', label: '阿司匹林', type: 'Drug', style: { fill: '#1677ff' }, size: 45 },
    { id: 'd5', label: '左氧氟沙星', type: 'Drug', style: { fill: '#1677ff' }, size: 40 },
    { id: 'd6', label: '茶碱', type: 'Drug', style: { fill: '#1677ff' }, size: 40 },
    { id: 'd7', label: '二甲双胍', type: 'Drug', style: { fill: '#1677ff' }, size: 45 },
    { id: 'dis1', label: '高血压', type: 'Disease', style: { fill: '#52c41a' }, size: 50 },
    { id: 'dis2', label: '冠心病', type: 'Disease', style: { fill: '#52c41a' }, size: 50 },
    { id: 'dis3', label: '2型糖尿病', type: 'Disease', style: { fill: '#52c41a' }, size: 50 },
    { id: 'dis4', label: '心房颤动', type: 'Disease', style: { fill: '#52c41a' }, size: 45 },
    { id: 'sym1', label: '干咳', type: 'Symptom', style: { fill: '#f5222d' }, size: 35 },
    { id: 'sym2', label: '出血风险', type: 'Symptom', style: { fill: '#f5222d' }, size: 35 },
    { id: 'sym3', label: '心律失常', type: 'Symptom', style: { fill: '#f5222d' }, size: 35 },
    { id: 'ing1', label: '乙酰水杨酸', type: 'Ingredient', style: { fill: '#faad14' }, size: 35 },
    { id: 'ing2', label: '华法林钠', type: 'Ingredient', style: { fill: '#faad14' }, size: 35 }
  ],
  edges: [
    { source: 'd1', target: 'dis1', label: 'TREATS (0.78)' },
    { source: 'd2', target: 'dis1', label: 'TREATS (0.80)' },
    { source: 'd1', target: 'sym1', label: 'ADVERSE (干咳10%~20%)' },
    { source: 'd3', target: 'd4', label: 'INTERACTS_WITH (High 出血)' },
    { source: 'd5', target: 'd6', label: 'INTERACTS_WITH (High 心律失常)' },
    { source: 'd7', target: 'dis3', label: 'TREATS (0.92)' },
    { source: 'd4', target: 'dis2', label: 'TREATS (0.90)' },
    { source: 'd3', target: 'dis4', label: 'TREATS (0.93)' },
    { source: 'd4', target: 'ing1', label: 'CONTAINS' },
    { source: 'd3', target: 'ing2', label: 'CONTAINS' }
  ]
}

const initGraph = () => {
  if (!containerRef.value) return
  const width = containerRef.value.scrollWidth || 1000
  const height = containerRef.value.scrollHeight || 600

  graph = new G6.Graph({
    container: containerRef.value,
    width,
    height,
    layout: {
      type: 'force',
      preventOverlap: true,
      linkDistance: 120,
      nodeStrength: -200
    },
    modes: {
      default: ['drag-canvas', 'zoom-canvas', 'drag-node']
    },
    defaultNode: {
      size: 40,
      labelCfg: {
        style: {
          fill: '#fff',
          fontSize: 12
        }
      }
    },
    defaultEdge: {
      style: {
        stroke: 'rgba(255, 255, 255, 0.25)',
        endArrow: true
      },
      labelCfg: {
        autoRotate: true,
        style: {
          fill: '#8c8c8c',
          fontSize: 10
        }
      }
    }
  })

  graph.data(graphData)
  graph.render()
}

const filterGraph = () => {
  if (!graph) return
  const key = searchKey.value.trim()
  if (!key) {
    graph.data(graphData)
    graph.render()
    return
  }
  const filteredNodes = graphData.nodes.filter((n: any) => n.label.includes(key))
  const nodeIds = new Set(filteredNodes.map((n: any) => n.id))
  const filteredEdges = graphData.edges.filter((e: any) => nodeIds.has(e.source) || nodeIds.has(e.target))
  graph.data({ nodes: filteredNodes, edges: filteredEdges })
  graph.render()
}

const resetLayout = () => {
  if (graph) {
    graph.layout()
  }
}

onMounted(() => {
  initGraph()
})
</script>

<style scoped lang="scss">
.graph-view {
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}
.toolbar {
  padding: 12px 16px;
  background: #0b1726;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  .filters {
    display: flex;
    gap: 8px;
  }
}
.graph-canvas {
  flex: 1;
  background: #06111c;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
}
</style>