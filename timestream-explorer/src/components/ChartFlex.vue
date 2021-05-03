<template>
  <div>
    <v-chart :options="option" />
  </div>
</template>

<style scoped>
.echarts {
  height: 100%;
  width: 100%;
}
</style>

<script>
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/line'
import 'echarts/lib/component/dataZoom'
import 'echarts/lib/component/axis'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/title'
import 'echarts/lib/component/tooltip'


export default {
  components: {
    'v-chart': ECharts
  },
  props: ['data'],
  //mixins: [mixins.reactiveProp],
  data () {
    return {
      option: {
        title: {
          text: 'Data',
          subtext: '',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            animation: false
          }
        },
        toolbox: {
          feature: {
            dataZoom: {
              yAxisIndex: 'none'
            },
            restore: {},
            saveAsImage: {}
          }
        },
        axisPointer: {
          link: { xAxisIndex: 'all' }
        },
        // dataZoom: [
        //     {
        //         show: true,
        //         realtime: true,
        //         start: 0,
        //         end: 100,
        //         xAxisIndex: [0]
        //     },
        // ],
        grid: [{
          left: 50,
          right: 50,
          height: '80%'
        }],
        xAxis: [
          {
            type: 'time',
            boundaryGap: false,
            axisLine: {onZero: true},
          }
        ],
        yAxis: [
        {
            name: 'Axis',
            type: 'value',
            axisLine: {onZero: true},
        }
        ],
        series: []
      }
    }
  },
  mounted () {
    this.options = this.option
    this.option.series = this.data
  },
  watch: {
    data () {
      this.option.series = this.data
    }
  }
}
</script>


<style scoped>
.echarts {
  height: 400px;
  width: 100%;
}
</style>