<template>
  <div class="container">
    <div class="actions">
      <button class="btn-refresh" @click="store.fetchData()" :disabled="store.loading">
        {{ store.loading ? '加载中...' : '刷新数据' }}
      </button>
      <span class="update-time" v-if="store.data">更新: {{ store.data.generated_at }}</span>
    </div>

    <div v-if="store.error" class="error-msg">{{ store.error }}</div>

    <div v-if="store.data" class="charts-grid">
      <!-- 图表1: 收益走势 -->
      <div class="chart-card">
        <h3>中证红利 PK 国证A股 收益走势图</h3>
        <div ref="chart1Ref" class="chart"></div>
      </div>

      <!-- 图表2: 布林线 -->
      <div class="chart-card">
        <h3>中证红利/国证A股 242日布林线(±2σ)</h3>
        <div ref="chart2Ref" class="chart"></div>
      </div>

      <!-- 图表3: 收益差 -->
      <div class="chart-card">
        <h3>40日收益差：中证红利 - 国证A股 (MA242)</h3>
        <div ref="chart3Ref" class="chart"></div>
      </div>

      <!-- 图表4: RSI -->
      <div class="chart-card">
        <h3>中证红利/国证A股 RSI14(MA242)</h3>
        <div ref="chart4Ref" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useHongliStore } from '@/stores/hongli'

const store = useHongliStore()
const chart1Ref = ref(null)
const chart2Ref = ref(null)
const chart3Ref = ref(null)
const chart4Ref = ref(null)

const BLUE = '#1a3a6b'
const RED = '#e63946'
const LIGHT_BLUE = 'rgba(26, 58, 107, 0.1)'

let chart1, chart2, chart3, chart4

function initCharts() {
  if (chart1Ref.value) chart1 = echarts.init(chart1Ref.value)
  if (chart2Ref.value) chart2 = echarts.init(chart2Ref.value)
  if (chart3Ref.value) chart3 = echarts.init(chart3Ref.value)
  if (chart4Ref.value) chart4 = echarts.init(chart4Ref.value)
}

function resizeCharts() {
  chart1?.resize()
  chart2?.resize()
  chart3?.resize()
  chart4?.resize()
}

function renderChart1() {
  if (!chart1 || !store.data) return
  const d = store.data.chart1
  chart1.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['中证红利', '国证A股'], top: 10 },
    grid: { top: 50, bottom: 30, left: 60, right: 20 },
    xAxis: { type: 'category', data: d.dates, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: v => v.toFixed(0) } },
    series: [
      { name: '中证红利', type: 'line', data: d.hongli, smooth: true, color: BLUE },
      { name: '国证A股', type: 'line', data: d.guozheng, smooth: true, color: RED }
    ]
  })
}

function renderChart2() {
  if (!chart2 || !store.data) return
  const d = store.data.chart2
  const last = d.ratio.length - 1
  chart2.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['比值', 'MA242'], top: 10 },
    grid: { top: 50, bottom: 30, left: 60, right: 30 },
    xAxis: { type: 'category', data: d.dates, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: v => v.toFixed(2) } },
    series: [
      { name: '比值', type: 'line', data: d.ratio, smooth: true, color: BLUE },
      { name: 'MA242', type: 'line', data: d.ma242, smooth: true, color: RED, lineStyle: { type: 'dashed' } },
      {
        name: '布林带上轨',
        type: 'line',
        data: d.upper,
        smooth: true,
        lineStyle: { color: 'rgba(26,58,107,0.4)', type: 'dotted', width: 1 },
        symbol: 'none'
      },
      {
        name: '布林带下轨',
        type: 'line',
        data: d.lower,
        smooth: true,
        lineStyle: { color: 'rgba(26,58,107,0.4)', type: 'dotted', width: 1 },
        symbol: 'none'
      }
    ],
    graphic: [{
      type: 'text',
      right: 10,
      top: 15,
      style: {
        text: `比值: ${d.ratio[last]?.toFixed(4) ?? '-'}`,
        fontSize: 11,
        fill: '#666',
        fontFamily: 'sans-serif'
      }
    }]
  }, true)
}

function renderChart3() {
  if (!chart3 || !store.data) return
  const d = store.data.chart3
  const last = d.diff.length - 1
  chart3.setOption({
    tooltip: { trigger: 'axis', formatter: params => {
      let html = params[0].axisValue + '<br/>'
      params.forEach(p => {
        if (p.value !== null) {
          html += p.marker + ' ' + p.seriesName + ': ' + (p.value != null ? p.value.toFixed(2) : '-') + '%'
          html += '<br/>'
        }
      })
      return html
    }},
    legend: { data: ['收益差', 'MA242'], top: 10 },
    grid: { top: 50, bottom: 30, left: 60, right: 30 },
    xAxis: { type: 'category', data: d.dates, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: v => v.toFixed(1) + '%' } },
    series: [
      { name: '收益差', type: 'line', data: d.diff, smooth: true, color: '#333' },
      { name: 'MA242', type: 'line', data: d.diff_ma242, smooth: true, color: RED, lineStyle: { type: 'dashed' } }
    ],
    graphic: [{
      type: 'text',
      right: 10,
      top: 15,
      style: {
        text: `收益差: ${d.diff[last]?.toFixed(2) ?? '-'}%`,
        fontSize: 11,
        fill: '#666',
        fontFamily: 'sans-serif'
      }
    }]
  })
}

function renderChart4() {
  if (!chart4 || !store.data) return
  const d = store.data.chart4
  const last = d.rsi.length - 1
  chart4.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['RSI14', 'MA242'], top: 10 },
    grid: { top: 50, bottom: 30, left: 60, right: 30 },
    xAxis: { type: 'category', data: d.dates, boundaryGap: false },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: v => v.toFixed(0) } },
    series: [
      { name: 'RSI14', type: 'line', data: d.rsi, smooth: true, color: BLUE },
      { name: 'MA242', type: 'line', data: d.rsi_ma242, smooth: true, color: RED, lineStyle: { type: 'dashed' } }
    ],
    graphic: [{
      type: 'text',
      right: 10,
      top: 15,
      style: {
        text: `RSI14: ${d.latest_rsi}`,
        fontSize: 11,
        fill: '#666',
        fontFamily: 'sans-serif'
      }
    }]
  })
}

watch(() => store.data, (newData) => {
  if (!newData) return
  nextTick(() => {
    initCharts()
    resizeCharts()
    renderChart1()
    renderChart2()
    renderChart3()
    renderChart4()
  })
})

onMounted(() => {
  window.addEventListener('resize', resizeCharts)
  store.fetchData()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.btn-refresh {
  background: #1a3a6b;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover {
  background: #2450a0;
}

.btn-refresh:disabled {
  background: #9ab;
  cursor: not-allowed;
}

.update-time {
  font-size: 12px;
  color: #888;
}

.error-msg {
  color: #e63946;
  padding: 12px;
  background: #fff5f5;
  border-radius: 4px;
  margin-bottom: 20px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.chart-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
}

.chart-card h3 {
  font-size: 14px;
  color: #444;
  margin-bottom: 12px;
  font-weight: 500;
}

.chart {
  width: 100%;
  height: 320px;
}
</style>
