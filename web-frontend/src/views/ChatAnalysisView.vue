<template>
  <div class="analysis-view">
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">问答总会话数</div>
          <div class="val text-primary">{{ stats.total_sessions }}</div>
        </div>
      </el-col>
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">累计提问消息</div>
          <div class="val text-success">{{ stats.total_messages }}</div>
        </div>
      </el-col>
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">消耗总 Token</div>
          <div class="val text-warning">1.72M</div>
        </div>
      </el-col>
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">平均响应时延</div>
          <div class="val text-info">{{ stats.avg_response_ms }} ms</div>
        </div>
      </el-col>
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">二级缓存命中率</div>
          <div class="val text-cyan">{{ (stats.cache_hit_rate * 100).toFixed(1) }}%</div>
        </div>
      </el-col>
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">限流拦截拦截数</div>
          <div class="val text-danger">{{ stats.rate_limit_blocked }}</div>
        </div>
      </el-col>
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">图谱平均跳数</div>
          <div class="val text-primary">{{ stats.avg_hop_count_per_trace }}</div>
        </div>
      </el-col>
      <el-col :span="3">
        <div class="card kpi">
          <div class="label">平均指南引用</div>
          <div class="val text-success">{{ stats.avg_chunks_per_retrieval }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="14">
        <div class="card">
          <div class="card-title">📊 7 日会话与 Token 消耗趋势 (双轴)</div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="card">
          <div class="card-title">🎯 用户医学问诊意图分布</div>
          <div ref="intentPieRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="12">
        <div class="card">
          <div class="card-title">☁️ 热门医学高频提问词云</div>
          <div ref="wordCloudRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card">
          <div class="card-title">⚡ 秒级吞吐与限流拦截防护面积图</div>
          <div ref="qpsChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { getChatFullAnalysis } from '../api/analysis'

const router = useRouter()
const chatStore = useChatStore()

const stats = ref<any>({
  total_sessions: 1280,
  total_messages: 4860,
  avg_response_ms: 680,
  cache_hit_rate: 0.38,
  rate_limit_blocked: 18,
  avg_hop_count_per_trace: 1.85,
  avg_chunks_per_retrieval: 2.6
})

const trendChartRef = ref<HTMLElement>()
const intentPieRef = ref<HTMLElement>()
const wordCloudRef = ref<HTMLElement>()
const qpsChartRef = ref<HTMLElement>()

const initCharts = (data: any) => {
  if (trendChartRef.value) {
    const tc = echarts.init(trendChartRef.value)
    tc.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#c1d1e8' } },
      xAxis: { type: 'category', data: ['09-10','09-11','09-12','09-13','09-14','09-15'], axisLine: { lineStyle: { color: '#8c8c8c' } } },
      yAxis: [
        { type: 'value', name: '会话数', axisLine: { lineStyle: { color: '#8c8c8c' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
        { type: 'value', name: 'Token', axisLine: { lineStyle: { color: '#8c8c8c' } }, splitLine: { show: false } }
      ],
      series: [
        { name: '会话数', type: 'bar', data: [120, 145, 160, 190, 210, 245], itemStyle: { color: '#1677ff' } },
        { name: 'Token用量', type: 'line', yAxisIndex: 1, data: [156000, 182000, 215000, 258000, 290000, 334000], itemStyle: { color: '#52c41a' } }
      ]
    })
  }

  if (intentPieRef.value) {
    const ic = echarts.init(intentPieRef.value)
    ic.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: { borderRadius: 6 },
        data: [
          { value: 1850, name: '配伍禁忌核验', itemStyle: { color: '#1677ff' } },
          { value: 1240, name: '不良反应咨询', itemStyle: { color: '#52c41a' } },
          { value: 980, name: '指南方案推荐', itemStyle: { color: '#faad14' } },
          { value: 520, name: '用法用量核查', itemStyle: { color: '#722ed1' } },
          { value: 270, name: '通用医学问诊', itemStyle: { color: '#13c2c2' } }
        ]
      }]
    })
  }

  if (wordCloudRef.value) {
    const wc = echarts.init(wordCloudRef.value)
    wc.setOption({
      backgroundColor: 'transparent',
      series: [{
        type: 'wordCloud',
        shape: 'circle',
        sizeRange: [14, 38],
        rotationRange: [0, 0],
        textStyle: {
          color: () => {
            const colors = ['#1677ff', '#52c41a', '#faad14', '#13c2c2', '#722ed1', '#bae0ff']
            return colors[Math.floor(Math.random() * colors.length)]
          }
        },
        data: [
          { name: '卡托普利干咳', value: 320 },
          { name: '华法林阿司匹林', value: 290 },
          { name: '左氧氟沙星茶碱', value: 240 },
          { name: '二甲双胍降糖', value: 190 },
          { name: '布洛芬降压药', value: 160 },
          { name: '高血压合并糖尿病', value: 140 },
          { name: '依那普利高钾', value: 120 },
          { name: '辛伐他汀肌痛', value: 110 },
          { name: '硝苯地平水肿', value: 95 }
        ]
      }]
    })
    wc.on('click', (params: any) => {
      chatStore.setPrefilledQuery(params.name)
      router.push('/chat')
    })
  }

  if (qpsChartRef.value) {
    const qc = echarts.init(qpsChartRef.value)
    qc.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['19:20','19:21','19:22','19:23','19:24','19:25','19:26','19:27','19:28','19:29'], axisLine: { lineStyle: { color: '#8c8c8c' } } },
      yAxis: { type: 'value', axisLine: { lineStyle: { color: '#8c8c8c' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      series: [
        { name: '通过 QPS', type: 'line', smooth: true, data: [18, 22, 19, 24, 21, 25, 23, 22, 26, 24], itemStyle: { color: '#1677ff' }, areaStyle: { color: 'rgba(22,119,255,0.1)' } },
        { name: '限流拦截 QPS', type: 'line', smooth: true, data: [2, 0, 1, 0, 3, 0, 1, 0, 2, 0], itemStyle: { color: '#f5222d' }, areaStyle: { color: 'rgba(245,34,45,0.1)' } }
      ]
    })
  }
}

onMounted(async () => {
  const res = await getChatFullAnalysis()
  if (res) {
    stats.value = res
  }
  initCharts(res)
})
</script>

<style scoped lang="scss">
.kpi-row .card.kpi {
  padding: 12px;
  background: #0b1726;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
  .label { font-size: 12px; color: #8c8c8c; margin-bottom: 6px; }
  .val { font-size: 18px; font-weight: bold; }
}
.card {
  background: #0b1726;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
  padding: 16px;
}
.mt-16 { margin-top: 16px; }
.card-title { font-size: 15px; font-weight: 600; color: #bae0ff; margin-bottom: 12px; }
.chart-container { height: 260px; }
.text-primary { color: #1677ff; }
.text-success { color: #52c41a; }
.text-warning { color: #faad14; }
.text-info { color: #13c2c2; }
.text-cyan { color: #2f54eb; }
.text-danger { color: #ff4d4f; }
</style>