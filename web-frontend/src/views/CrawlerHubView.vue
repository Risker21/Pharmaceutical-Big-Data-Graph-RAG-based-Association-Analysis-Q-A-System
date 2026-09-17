<template>
  <div class="crawler-view">
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="4">
        <div class="card kpi">
          <div class="label">今日采集量</div>
          <div class="val text-primary">{{ stats.today_total }} <span class="unit">条</span></div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="card kpi">
          <div class="label">历史累计采集</div>
          <div class="val text-success">{{ stats.history_total }} <span class="unit">条</span></div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="card kpi">
          <div class="label">当前平均采集速率</div>
          <div class="val text-warning">110 <span class="unit">条/分</span></div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="card kpi">
          <div class="label">Kafka Topic 积压 Lag</div>
          <div class="val text-info">{{ stats.kafka_topic_lag }} <span class="unit">条</span></div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="card kpi">
          <div class="label">就绪爬虫 Worker</div>
          <div class="val text-cyan">{{ stats.active_crawlers }} <span class="unit">个</span></div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="card kpi">
          <div class="label">数据源整体健康度</div>
          <div class="val text-success">99.2 <span class="unit">分</span></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="14">
        <div class="card chart-card">
          <div class="card-title">📈 实时数据采集吞吐趋势 (条/分钟)</div>
          <div ref="rateChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="card chart-card">
          <div class="card-title">🧬 医药数据源占比与健康评分</div>
          <div ref="sourcePieRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="10">
        <div class="card">
          <div class="card-header">
            <span class="card-title">⚡ 爬虫任务调度控制台</span>
            <el-button type="primary" size="small" @click="triggerAll">一键生成全量样本</el-button>
          </div>
          <el-table :data="spiders" class="custom-table" size="small">
            <el-table-column prop="spider_name" label="爬虫任务" />
            <el-table-column prop="total_items" label="采集行数" width="90" />
            <el-table-column prop="health_score" label="健康度" width="80">
              <template #default="{ row }">
                <el-tag type="success" size="small">{{ row.health_score }}%</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="triggerSpider(row.spider_name)">立即触发</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="14">
        <div class="card">
          <div class="card-header">
            <span class="card-title">📋 ODS 原始数据即时预览</span>
            <el-radio-group v-model="activeTab" size="small" @change="fetchOds">
              <el-radio-button label="drug">药品说明书</el-radio-button>
              <el-radio-button label="disease">CMeKG病症</el-radio-button>
              <el-radio-button label="guideline">临床指南</el-radio-button>
            </el-radio-group>
          </div>
          <el-table :data="odsRows" class="custom-table" size="small" height="240">
            <el-table-column v-if="activeTab === 'drug'" prop="name" label="药品通用名" width="120" />
            <el-table-column v-if="activeTab === 'drug'" prop="approval_no" label="批准文号" width="150" />
            <el-table-column v-if="activeTab === 'drug'" prop="adverse_reaction" label="不良反应" show-overflow-tooltip />

            <el-table-column v-if="activeTab === 'disease'" prop="name" label="疾病名" width="140" />
            <el-table-column v-if="activeTab === 'disease'" prop="icd_code" label="ICD编码" width="110" />
            <el-table-column v-if="activeTab === 'disease'" prop="department" label="就诊科室" />

            <el-table-column v-if="activeTab === 'guideline'" prop="source" label="指南来源" width="180" />
            <el-table-column v-if="activeTab === 'guideline'" prop="content" label="切片内容" show-overflow-tooltip />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getCrawlerStats, getCrawlerSources, getOdsPreview, triggerSpiderRun, triggerAllGenerators } from '../api/crawler'
import { ElMessage } from 'element-plus'

const stats = ref<any>({ today_total: 1300, history_total: 24500, kafka_topic_lag: 12, active_crawlers: 3 })
const spiders = ref<any[]>([])
const odsRows = ref<any[]>([])
const activeTab = ref('drug')

const rateChartRef = ref<HTMLElement>()
const sourcePieRef = ref<HTMLElement>()

const initCharts = () => {
  if (rateChartRef.value) {
    const rateChart = echarts.init(rateChartRef.value)
    rateChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
      xAxis: { type: 'category', data: ['19:20','19:21','19:22','19:23','19:24','19:25','19:26','19:27','19:28','19:29'], axisLine: { lineStyle: { color: '#8c8c8c' } } },
      yAxis: { type: 'value', axisLine: { lineStyle: { color: '#8c8c8c' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      series: [
        { name: '药品说明书', type: 'line', smooth: true, data: [25, 32, 28, 40, 36, 45, 38, 42, 50, 48], itemStyle: { color: '#1677ff' }, areaStyle: { color: 'rgba(22,119,255,0.1)' } },
        { name: 'CMeKG病种', type: 'line', smooth: true, data: [12, 15, 14, 18, 16, 22, 19, 21, 24, 23], itemStyle: { color: '#52c41a' } },
        { name: '临床指南', type: 'line', smooth: true, data: [50, 58, 54, 65, 62, 75, 68, 72, 80, 78], itemStyle: { color: '#faad14' } }
      ]
    })
  }

  if (sourcePieRef.value) {
    const sourcePie = echarts.init(sourcePieRef.value)
    sourcePie.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      legend: { bottom: '0', textStyle: { color: '#c1d1e8' } },
      series: [{
        name: '数据源占比',
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#0b1726', borderWidth: 2 },
        label: { show: false },
        data: [
          { value: 1050, name: '中华医学会指南', itemStyle: { color: '#1677ff' } },
          { value: 200, name: 'NMPA 药品说明书', itemStyle: { color: '#52c41a' } },
          { value: 50, name: 'CMeKG 医药知识图谱', itemStyle: { color: '#faad14' } }
        ]
      }]
    })
  }
}

const fetchOds = async () => {
  const res = await getOdsPreview(activeTab.value as any)
  odsRows.value = Array.isArray(res) ? res : ((res as any).rows || [])
}

const triggerSpider = async (name: string) => {
  await triggerSpiderRun(name)
  ElMessage.success(`爬虫 [${name}] 已触发执行`)
}

const triggerAll = async () => {
  await triggerAllGenerators()
  ElMessage.success('全量医药数据样本已刷新生成')
  fetchOds()
}

onMounted(async () => {
  initCharts()
  const st = await getCrawlerStats()
  stats.value = st
  spiders.value = st.spiders || []
  fetchOds()
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
.mt-16 { margin-top: 16px; }
.card {
  background: #0b1726;
  border: 1px solid rgba(22, 119, 255, 0.15);
  border-radius: 8px;
  padding: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.card-title { font-size: 15px; font-weight: 600; color: #bae0ff; }
.chart-container { height: 260px; }
.text-primary { color: #1677ff; }
.text-success { color: #52c41a; }
.text-warning { color: #faad14; }
.text-info { color: #13c2c2; }
.text-cyan { color: #2f54eb; }
</style>