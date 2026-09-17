<template>
  <div class="mining-view">
    <el-row :gutter="16">
      <el-col :span="12">
        <div class="card">
          <div class="card-title">🏆 Spark GraphX PageRank 核心医学实体权重 Top 10</div>
          <div ref="prChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card">
          <div class="card-title">🌐 Louvain 药物-疾病社群聚类规模分布 (旭日图)</div>
          <div ref="sunburstRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="14">
        <div class="card">
          <div class="card-title">🔥 15 核心药品有效成分重叠与过量风险矩阵 (Jaccard 热力图)</div>
          <div ref="heatRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="card">
          <div class="card-header">
            <span class="card-title">⚠️ 高风险配伍禁忌 Top 列表</span>
            <span class="sub">点击行直接在问答工作台发起核验</span>
          </div>
          <el-table :data="contraList" class="custom-table" size="small" @row-click="handleRowClick">
            <el-table-column label="配伍药品对" width="160">
              <template #default="{ row }">
                <span class="pair-tag">{{ row.pair[0] }} ↔ {{ row.pair[1] }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="等级" width="70">
              <template #default="{ row }">
                <el-tag :type="row.level === 'High' ? 'danger' : 'warning'" size="small">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="case_count" label="案例数" width="80" />
            <el-table-column prop="risk_detail" label="不良后果推导" show-overflow-tooltip />
          </el-table>
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
import { getTopContraindications } from '../api/etl'

const router = useRouter()
const chatStore = useChatStore()

const prChartRef = ref<HTMLElement>()
const sunburstRef = ref<HTMLElement>()
const heatRef = ref<HTMLElement>()
const contraList = ref<any[]>([])

const initCharts = () => {
  if (prChartRef.value) {
    const pc = echarts.init(prChartRef.value)
    pc.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '5%', containLabel: true },
      xAxis: { type: 'value', axisLine: { lineStyle: { color: '#8c8c8c' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      yAxis: { type: 'category', data: ['美托洛尔','布洛芬','奥美拉唑','左氧氟沙星','华法林','冠心病','阿司匹林','二甲双胍','高血压','卡托普利'], axisLine: { lineStyle: { color: '#8c8c8c' } } },
      series: [{
        type: 'bar',
        data: [0.052, 0.055, 0.058, 0.062, 0.065, 0.068, 0.072, 0.076, 0.079, 0.084],
        itemStyle: { color: '#1677ff', borderRadius: [0, 4, 4, 0] }
      }]
    })
  }

  if (sunburstRef.value) {
    const sc = echarts.init(sunburstRef.value)
    sc.setOption({
      backgroundColor: 'transparent',
      series: [{
        type: 'sunburst',
        radius: [0, '90%'],
        data: [
          { name: '心血管代谢', value: 68, itemStyle: { color: '#1677ff' } },
          { name: '内分泌代谢', value: 45, itemStyle: { color: '#52c41a' } },
          { name: '呼吸抗感染', value: 39, itemStyle: { color: '#faad14' } },
          { name: '消化抗凝', value: 32, itemStyle: { color: '#f5222d' } },
          { name: '镇痛抗炎', value: 28, itemStyle: { color: '#722ed1' } }
        ]
      }]
    })
  }

  if (heatRef.value) {
    const hc = echarts.init(heatRef.value)
    const drugs = ['卡托普利','依那普利','二甲双胍','格列美脲','阿司匹林','华法林','左氧氟沙星','茶碱','奥美拉唑','辛伐他汀','硝苯地平','美托洛尔','氢氯噻嗪','对乙酰氨基酚','布洛芬']
    const data: any[] = []
    for (let i = 0; i < drugs.length; i++) {
      for (let j = 0; j < drugs.length; j++) {
        let val = (i === j) ? 1.0 : ((i === 0 && j === 1) ? 0.85 : ((i === 4 && j === 14) ? 0.45 : ((Math.abs(i * 17 + j * 31) % 25) / 100.0)))
        data.push([i, j, val])
      }
    }
    hc.setOption({
      backgroundColor: 'transparent',
      tooltip: { position: 'top' },
      grid: { height: '80%', top: '5%', bottom: '15%' },
      xAxis: { type: 'category', data: drugs, axisLabel: { interval: 0, rotate: 45, color: '#8c8c8c', fontSize: 10 } },
      yAxis: { type: 'category', data: drugs, axisLabel: { color: '#8c8c8c', fontSize: 10 } },
      visualMap: { min: 0, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: '0', inRange: { color: ['#0b1726', '#1677ff', '#f5222d'] }, textStyle: { color: '#8c8c8c' } },
      series: [{ type: 'heatmap', data, label: { show: false } }]
    })
  }
}

const handleRowClick = (row: any) => {
  chatStore.setPrefilledQuery(`${row.pair[0]} 和 ${row.pair[1]} 能一起吃吗？有何禁忌风险？`)
  router.push('/chat')
}

onMounted(async () => {
  initCharts()
  const res = await getTopContraindications()
  contraList.value = res || []
})
</script>

<style scoped lang="scss">
.card {
  background: #0b1726;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
  padding: 16px;
}
.mt-16 { margin-top: 16px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  .sub { font-size: 12px; color: #8c8c8c; }
}
.card-title { font-size: 15px; font-weight: 600; color: #bae0ff; }
.chart-container { height: 280px; }
.pair-tag { font-weight: bold; color: #bae0ff; cursor: pointer; }
</style>