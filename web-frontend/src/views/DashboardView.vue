<template>
  <div class="dashboard-view">
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <div class="card kpi">
          <div class="label">知识图谱实体总数</div>
          <div class="val text-primary">28,450 <span class="unit">个</span></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="card kpi">
          <div class="label">关联拓扑边总数</div>
          <div class="val text-success">142,300 <span class="unit">条</span></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="card kpi">
          <div class="label">临床指南切片数</div>
          <div class="val text-warning">1,050 <span class="unit">篇</span></div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="card kpi">
          <div class="label">高危禁忌规则对</div>
          <div class="val text-danger">520 <span class="unit">组</span></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="14">
        <div class="card">
          <div class="card-title">🚨 高危药物配伍禁忌案例频次排行榜 (Top 5)</div>
          <div ref="contraChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="card">
          <div class="card-title">🏥 各科室高发疾病与用药咨询分布</div>
          <div ref="deptRadarRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="24">
        <div class="card">
          <div class="card-title">📈 7 日全平台问答与图谱检索趋势</div>
          <div ref="lineChartRef" class="chart-container" style="height: 220px;"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getDashboardStats } from '../api/dashboard'

const contraChartRef = ref<HTMLElement>()
const deptRadarRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()

const initCharts = () => {
  if (contraChartRef.value) {
    const cc = echarts.init(contraChartRef.value)
    cc.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '5%', containLabel: true },
      xAxis: { type: 'value', axisLine: { lineStyle: { color: '#8c8c8c' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      yAxis: { type: 'category', data: ['辛伐他汀↔奥美拉唑','卡托普利↔螺内酯','布洛芬↔华法林','左氧氟沙星↔茶碱','阿司匹林↔华法林'], axisLine: { lineStyle: { color: '#8c8c8c' } } },
      series: [{
        type: 'bar',
        data: [320, 410, 780, 890, 1240],
        itemStyle: { color: '#f5222d', borderRadius: [0, 4, 4, 0] }
      }]
    })
  }

  if (deptRadarRef.value) {
    const dr = echarts.init(deptRadarRef.value)
    dr.setOption({
      backgroundColor: 'transparent',
      radar: {
        indicator: [
          { name: '心内科', max: 5000 },
          { name: '呼吸内科', max: 5000 },
          { name: '内分泌科', max: 5000 },
          { name: '消化内科', max: 5000 },
          { name: '神经内科', max: 5000 }
        ],
        axisName: { color: '#c1d1e8' },
        splitArea: { show: false },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      series: [{
        type: 'radar',
        data: [
          { value: [4200, 3800, 3500, 2900, 2400], name: '科室分布', areaStyle: { color: 'rgba(22,119,255,0.2)' }, lineStyle: { color: '#1677ff' } }
        ]
      }]
    })
  }

  if (lineChartRef.value) {
    const lc = echarts.init(lineChartRef.value)
    lc.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['09-10','09-11','09-12','09-13','09-14','09-15'], axisLine: { lineStyle: { color: '#8c8c8c' } } },
      yAxis: { type: 'value', axisLine: { lineStyle: { color: '#8c8c8c' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      series: [
        { name: '问答请求', type: 'line', smooth: true, data: [450, 520, 610, 730, 820, 950], itemStyle: { color: '#1677ff' }, areaStyle: { color: 'rgba(22,119,255,0.1)' } }
      ]
    })
  }
}

onMounted(() => {
  initCharts()
})
</script>

<style scoped lang="scss">
.kpi-row .card.kpi {
  padding: 16px;
  background: #0b1726;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
  .label { font-size: 13px; color: #8c8c8c; margin-bottom: 8px; }
  .val { font-size: 24px; font-weight: bold; .unit { font-size: 13px; font-weight: normal; color: #8c8c8c; } }
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
.text-danger { color: #ff4d4f; }
</style>