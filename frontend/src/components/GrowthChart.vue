<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  records: { type: Array, default: () => [] }
})

let chart
const chartElement = ref(null)

function buildOptions() {
  const dates = props.records.map((record) => record.date)
  return {
    color: ['#4f8c8b', '#b9734f'],
    grid: { left: 42, right: 20, top: 28, bottom: 36 },
    tooltip: { trigger: 'axis' },
    legend: {
      bottom: 0,
      textStyle: { color: '#17211b' }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(23,33,27,.25)' } },
      axisLabel: { color: 'rgba(23,33,27,.62)' }
    },
    yAxis: [
      {
        type: 'value',
        name: 'g',
        axisLabel: { color: 'rgba(23,33,27,.62)' },
        splitLine: { lineStyle: { color: 'rgba(23,33,27,.08)' } }
      },
      {
        type: 'value',
        name: 'cm',
        axisLabel: { color: 'rgba(23,33,27,.62)' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '体重',
        type: 'line',
        smooth: true,
        connectNulls: true,
        data: props.records.map((record) => record.weight),
        symbolSize: 8
      },
      {
        name: '体长',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        connectNulls: true,
        data: props.records.map((record) => record.length),
        symbolSize: 8
      }
    ]
  }
}

function renderChart() {
  if (!chartElement.value) return
  if (!chart) {
    chart = echarts.init(chartElement.value)
  }
  chart.setOption(buildOptions())
}

function resizeChart() {
  chart?.resize()
}

onMounted(async () => {
  await nextTick()
  renderChart()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
})

watch(() => props.records, renderChart, { deep: true })
</script>

<template>
  <div ref="chartElement" class="h-72 w-full"></div>
</template>
