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
        <div class="chart-header">
          <h3>中证红利/国证A股 242日布林线(±2σ)</h3>
          <button class="info-btn" @click="showModal2 = true">
            <span>说明</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4"/>
              <path d="M12 8h.01"/>
            </svg>
          </button>
        </div>
        <div ref="chart2Ref" class="chart"></div>
      </div>

      <!-- 图表3: 收益差 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>40日收益差：中证红利 - 国证A股 (MA242)</h3>
          <button class="info-btn" @click="showModal3 = true">
            <span>说明</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4"/>
              <path d="M12 8h.01"/>
            </svg>
          </button>
        </div>
        <div ref="chart3Ref" class="chart"></div>
      </div>

      <!-- 图表4: RSI -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>中证红利/国证A股 RSI14(MA242)</h3>
          <button class="info-btn" @click="showModal4 = true">
            <span>说明</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4"/>
              <path d="M12 8h.01"/>
            </svg>
          </button>
        </div>
        <div ref="chart4Ref" class="chart"></div>
      </div>
    </div>

    <!-- 图表2 说明弹窗 -->
    <div v-if="showModal2" class="modal-overlay" @click.self="showModal2 = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>布林线说明</h3>
          <button class="modal-close" @click="showModal2 = false">&times;</button>
        </div>
        <div class="modal-body">
          <h4>计算：</h4>
          <ul>
            <li>比值 = 中证红利全收益 / 国证A股全收益</li>
            <li>中轨 = 比值的242日简单移动平均（MA242）</li>
            <li>上轨 = 中轨 + 2×标准差</li>
            <li>下轨 = 中轨 - 2×标准差</li>
            <li>%B = (当前比值 - 下轨) / (上轨 - 下轨)</li>
            <li>带宽 = (上轨 - 下轨) / 中轨 × 100%</li>
          </ul>
          <h4>作用：</h4>
          <p>判断红利/国证比值处于历史波动区间的什么位置。%B靠近0说明比值接近下轨（红利相对偏弱），靠近1说明比值接近上轨（红利相对偏强）。带宽变宽说明波动加大。</p>
        </div>
      </div>
    </div>

    <!-- 图表3 说明弹窗 -->
    <div v-if="showModal3" class="modal-overlay" @click.self="showModal3 = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>收益差说明</h3>
          <button class="modal-close" @click="showModal3 = false">&times;</button>
        </div>
        <div class="modal-body">
          <h4>计算：</h4>
          <ul>
            <li>40日收益差 = 中证红利40日累计收益率 - 国证A股40日累计收益率</li>
            <li>再叠加一条242日均线（MA242）</li>
          </ul>
          <h4>作用：</h4>
          <p>衡量短期（40日）内红利指数相对国证A股的超额收益方向和幅度。差值为正说明红利短期跑赢，反之跑输。均线方向反映中期趋势。</p>
          <p>过高的时候不要追高，可以静待回落到零轴甚至此前常见的低点时杀入。</p>
        </div>
      </div>
    </div>

    <!-- 图表4 说明弹窗 -->
    <div v-if="showModal4" class="modal-overlay" @click.self="showModal4 = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>RSI说明</h3>
          <button class="modal-close" @click="showModal4 = false">&times;</button>
        </div>
        <div class="modal-body">
          <h4>计算：</h4>
          <ul>
            <li>先算出比值（中证红利/国证A股）</li>
            <li>RSI(14) = 100 - 100/(1+RS)</li>
            <li>RS = 14日内上涨幅度均值 / 14日内下跌幅度均值（绝对值）</li>
            <li>同样叠加242日均线</li>
          </ul>
          <h4>作用：</h4>
          <p>RSI反映比值的动能强弱。RSI&gt;70说明比值处于强势上涨区间（红利相对强势），RSI&lt;30说明比值弱势（红利相对跑输）。和图2结合可以看价格位置+动能方向。</p>
        </div>
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

const showModal2 = ref(false)
const showModal3 = ref(false)
const showModal4 = ref(false)

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

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-header h3 {
  margin-bottom: 0;
}

.info-btn {
  background: transparent;
  border: none;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  color: #888;
  display: flex;
  align-items: center;
  gap: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.info-btn:hover {
  color: #1a3a6b;
  background: rgba(26, 58, 107, 0.08);
}

.info-btn svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 10px;
  max-width: 540px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  line-height: 1;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 16px 20px 20px;
}

.modal-body h4 {
  font-size: 14px;
  color: #1a3a6b;
  margin: 12px 0 6px;
}

.modal-body ul {
  margin: 0 0 8px;
  padding-left: 20px;
}

.modal-body li {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

.modal-body p {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
  margin: 6px 0;
}
</style>
