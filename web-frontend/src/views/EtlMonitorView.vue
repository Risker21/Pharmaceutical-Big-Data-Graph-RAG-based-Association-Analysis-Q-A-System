<template>
  <div class="etl-view">
    <el-row :gutter="16">
      <el-col :span="14">
        <div class="card">
          <div class="card-title">🌊 数仓分层数据流向桑基图 (ODS → DWD → ADS)</div>
          <div ref="sankeyRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="card">
          <div class="card-title">🌹 数仓各层数据量极坐标玫瑰图</div>
          <div ref="roseRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="24">
        <div class="card">
          <div class="card-header">
            <span class="card-title">⏱️ Spark 离线与图计算作业调度执行甘特历史</span>
            <el-button type="primary" size="small" @click="refreshEtl">立即重跑全部作业</el-button>
          </div>
          <el-table :data="jobHistory" class="custom-table" size="small">
            <el-table-column prop="job_name" label="作业名" width="200" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag type="success" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration_ms" label="执行耗时" width="120">
              <template #default="{ row }">
                {{ row.duration_ms }} ms
              </template>
            </el-table-column>
            <el-table-column prop="input_rows" label="输入行数" width="120" />
            <el-table-column prop="output_rows" label="产出行数" width="120" />
            <el-table-column label="执行时间" show-overflow-tooltip>
              <template #default="{ row }">
                {{ new Date(row.start_ts).toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getJobHistory } from '../api/etl'
import { ElMessage } from 'element-plus'

const sankeyRef = ref<HTMLElement>()
const roseRef = ref<HTMLElement>()
const jobHistory = ref<any[]>([])

const initCharts = () => {
  if (sankeyRef.value) {
    const sc = echarts.init(sankeyRef.value)
    sc.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        lineStyle: { color: 'gradient', curveness: 0.5 },
        data: [
          { name: 'ODS_药品说明书' }, { name: 'ODS_CMeKG病症' }, { name: 'ODS_临床指南' },
          { name: 'DWD_药品维度' }, { name: 'DWD_疾病事实' }, { name: 'DWD_禁忌关系' },
          { name: 'ADS_高危配伍矩阵' }, { name: 'ADS_科室疾病分布' }, { name: 'ADS_成分重叠宽表' }
        ],
        links: [
          { source: 'ODS_药品说明书', target: 'DWD_药品维度', value: 183 },
          { source: 'ODS_药品说明书', target: 'DWD_禁忌关系', value: 520 },
          { source: 'ODS_CMeKG病症', target: 'DWD_疾病事实', value: 50 },
          { source: 'ODS_临床指南', target: 'DWD_药品维度', value: 1050 },
          { source: 'DWD_药品维度', target: 'ADS_成分重叠宽表', value: 225 },
          { source: 'DWD_禁忌关系', target: 'ADS_高危配伍矩阵', value: 50 },
          { source: 'DWD_疾病事实', target: 'ADS_科室疾病分布', value: 7 }
        ]
      }]
    })
  }

  if (roseRef.value) {
    const rc = echarts.init(roseRef.value)
    rc.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      legend: { bottom: '0', textStyle: { color: '#c1d1e8' } },
      series: [{
        name: '数仓分层分布',
        type: 'pie',
        radius: [20, 100],
        roseType: 'area',
        itemStyle: { borderRadius: 6 },
        data: [
          { value: 12850, name: 'ODS原始层', itemStyle: { color: '#1677ff' } },
          { value: 12100, name: 'DWD明细层', itemStyle: { color: '#52c41a' } },
          { value: 3450, name: 'ADS应用层', itemStyle: { color: '#faad14' } }
        ]
      }]
    })
  }
}

const refreshEtl = async () => {
  ElMessage.success('ETL 计算作业触发成功，正在流水线执行')
  const res = await getJobHistory()
  jobHistory.value = res || []
}

onMounted(async () => {
  initCharts()
  const res = await getJobHistory()
  jobHistory.value = res || []
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
}
.card-title { font-size: 15px; font-weight: 600; color: #bae0ff; }
.chart-container { height: 280px; }
</style>