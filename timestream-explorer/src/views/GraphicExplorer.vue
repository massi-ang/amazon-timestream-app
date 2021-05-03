<template>
  <div>
    <div class="editor">
      <prism-editor v-model="code" language="sql"></prism-editor>
    </div>
    <md-button class="md-primary" @click="query()">Run</md-button>
    <div>
      <h4>{{queryDataType}}</h4>
      <ul>
        <li v-for="c in columns" :key="c.Name">{{c.Name}} [{{c.Type.ScalarType || 'TIMESERIES' }}]</li>
      </ul>
      <chart-flex v-for="(data, k) in measures" :data="data" :key="k"></chart-flex>
      <md-button class="md-primary" @click="display = !display">Show/Hide</md-button>
      <div v-if="display">{{results}}</div>

      <md-snackbar md-position="center" :md-duration="5000" :md-active.sync="showLoadingTime">
        <span>Loaded in {{loadingTime}}ms</span>
        <md-button class="md-primary" @click="showLoadingTime = false">Hide</md-button>
      </md-snackbar>
      <md-snackbar md-position="center" :md-duration="5000" :md-active.sync="showError">
        <span>{{error}}</span>
        <md-button class="md-primary" @click="showLoadingTime = false">Hide</md-button>
      </md-snackbar>
    </div>
  </div>
</template>

<script>
import "prismjs"
import "prismjs/components/prism-sql"
import "prismjs/themes/prism.css"
import "vue-prism-editor/dist/VuePrismEditor.css"
import PrismEditor from 'vue-prism-editor'
import { Config } from '@/assets/config.js'
import Axios from 'axios'
import ChartFlex from '@/components/ChartFlex.vue'

export default {
  components: {
    PrismEditor,
    ChartFlex
  },
  data () {
    return {
      code: '',
      results: '',
      columns: [],
      measures: {},
      display: false,
      error: '',
      showError: false,
      queryDataType: '',
      loadingTime: 0,
      showLoadingTime: false
    }
  },
  methods: {
    query () {
      this.loadingTime = new Date()
      this.results = ""
      console.log(this.code)
      Axios({ method: 'post', url: `${Config.apiEndpoint}/query`, headers: { 'Content-Type': 'text/plain' }, data: JSON.stringify({ 'code': this.code }) }).then(v => {
        //this.time = v.data.map(v => v.time)
        this.loadingTime = (new Date()) - this.loadingTime
        this.showLoadingTime = true
        this.results = v
        console.log('Columns', v.data.ColumnInfo)
        this.columns = v.data.ColumnInfo
        // Find the main columns returned by the query: time, measure_name and measure_value
        let time_index, measure_index = [], dimension_index = []
        this.measures = {}
        // Obtain the information about the columns present in the result set
        for (var i in v.data.ColumnInfo) {
          switch (v.data.ColumnInfo[i].Type.ScalarType) {
            case 'TIMESTAMP':
              time_index = i
              break
            case 'DOUBLE':
              measure_index.push(i)
              break
            case 'BIGINT':
              measure_index.push(i)
              break
            case 'VARCHAR':
              dimension_index.push(i)
              break
          }
        }

        if (time_index === undefined) { // The results can be time series
          console.log('Timeseries data')
          let data = []
          this.queryDataType = 'Timeseries data'
          let timeseries_idx
          let serie_name


          v.data.ColumnInfo.forEach((v, j) => {
            if (v.Type.TimeSeriesMeasureValueColumnInfo !== undefined) {
              timeseries_idx = j; serie_name = v.Name
            }
          })
          if (timeseries_idx === undefined) {
            console.log('No timeserie data in the result set. Currently not supported')
            this.error = 'No timeserie data in the result set. Currently not supported'
            this.showError = true
            return
          }
          v.data.Rows.forEach((ts_row) => {
            serie_name = '';
            ts_row.Data.forEach((v, i) => { if (i != timeseries_idx) { serie_name += `_${v.ScalarValue}` } })
            let serie = ts_row.Data[timeseries_idx].TimeSeriesValue.map((tsv) => [tsv.Time.replace(' ', 'T').split('.')[0], tsv.Value.ScalarValue])
            data.push({
              data: serie,
              symbolSize: 5,
              type: 'line',
              name: serie_name,
              xAxisIndex: 0,
              yAxisIndex: 0
            })
          })
          this.measures[v.Name] = data
        } else {
          // Tabular data
          this.queryDataType = 'Tabular data'

          // Get all the series in the result set
          // These are the combination of the dimensions and measure_names values 
          // Different measures should be graphed on separate charts.
          let serie_names = [...new Set(v.data.Rows.map((r) => dimension_index.map(i => r.Data[i].ScalarValue).join('_')))]
          console.log(serie_names)
          // Unique names: there is no metadata we can use so let's try some smart way based on names
          // Maybe ML could be more useful- eg comparing data scales (min / max ranges using logarithms)
          let uniqueMeasuresSet = new Set()
          measure_index.forEach(m_i => uniqueMeasuresSet.add(this.columns[m_i].Name.split("_")[0]))
          let uniqueMeasures = [...uniqueMeasuresSet]
          console.log(uniqueMeasuresSet)
          if (uniqueMeasures.length == measure_index.length) {
            uniqueMeasuresSet = new Set()
            measure_index.forEach(m_i => uniqueMeasuresSet.add(this.columns[m_i].Name.split("_")[1]))
            uniqueMeasures = [...uniqueMeasuresSet]
            console.log(uniqueMeasuresSet)
            if (uniqueMeasures.length == measure_index.length) {
              console.log('No common terms, assuming all measures are distinct')
              uniqueMeasures = measure_index.map(m_i => this.columns[m_i].Name)
            }
          } else if (uniqueMeasures === undefined || uniqueMeasures.length < 1) {
            console.log('No common terms, assuming all measures are distinct')
            uniqueMeasures = measure_index.map(m_i => this.columns[m_i].Name)
          }
          console.log(uniqueMeasures)

          // Build the data series for the charts from the results
          uniqueMeasures.forEach(measure => {
            let data = []
            measure_index.forEach(m_i => {
              console.log(this.columns[m_i].Name)
              let measure_name = this.columns[m_i].Name.match(new RegExp(measure, 'i')) ? measure : undefined
              console.log(measure_name)
              if (measure_name === undefined) {
                return
              }
              
              serie_names.forEach(m => { // For each timeserie (combination of dimensions and measure name)
                console.log(`Adding serie for mesure column n ${m_i} ${this.columns[m_i].Name} and serie ${m}`)
                let serie = v.data.Rows.filter(h => { // Filter the data rows
                  let name = dimension_index.map(i => h.Data[i].ScalarValue).join('_')
                  return m == name
                }).map((r) => { // Get the data points in a compatible format
                  let t = r.Data[time_index].ScalarValue.replace(' ', 'T').split('.')[0];
                  return [t, r.Data[m_i].ScalarValue]
                })

                data.push({
                  data: serie,
                  symbolSize: 5,
                  type: 'line',
                  name: m + '_' + this.columns[m_i].Name,
                  xAxisIndex: 0,
                  yAxisIndex: 0
                })
              })
              
            })
            this.$set(this.measures, measure, data)
          })
        }
        //console.log()
      }).catch((err) => {
        console.log(err)
        this.error = `${err}\n${err.response.data.error}`
        this.showError = true
      })
    }
  }
}
</script>

<style scoped>
.editor {
  height: 300px;
}
</style>