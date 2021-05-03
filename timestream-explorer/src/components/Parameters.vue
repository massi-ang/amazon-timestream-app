<template>
  <div class="md-layout md-gutter">
    <div class="md-layout-item">
      <div class="md-layout md-gutter">
        <div class="md-layout-item">
            <h4>Parameters</h4>   
        </div>
      </div>
      <div class="md-layout-item">
        <div class="md-layout md-gutter">
          <div class="md-layout-item">
            <md-field>
              <label for="sensor">Sensor</label>
              <md-select id="sensor" v-model="sensor">
                <md-option v-for="s in sensors" :key="s" :value="s">{{ s }}</md-option>
              </md-select>
            </md-field>
          </div>
          <div v-if="type != 'simple'" class="md-layout-item">
            <md-field>
              <label for="measure">Measure</label>
              <md-select id="measure" v-model="measure">
                <md-option>temperature</md-option>
                <md-option>humidity</md-option>
                <md-option>pressure</md-option>
                <md-option>battery</md-option>
              </md-select>
            </md-field>
          </div>
          <div class="md-layout-item">
            <md-field>
              <label for="time">Time period</label>
              <md-select id="time" v-model="time">
                <md-option value="10m">10m</md-option>
                <md-option value="1h">1h</md-option>
                <md-option value="3h">3h</md-option>
                <md-option value="24h">24h</md-option>
                <md-option value="3d">3d</md-option>
                <md-option value="7d">7d</md-option>
              </md-select>
            </md-field>
          </div>
          <div class="md-layout-item">
            <md-field>
              <label for="points">Points</label>
              <md-select id="points" v-model="points">
                <md-option v-for="p in points_values" :key="p" :value="p">{{p}}</md-option>
              </md-select>
            </md-field>
          </div>
        </div>
        <div class="md-layout">
          <div class="md-layout-item">
            <md-button class="md-primary md-raised" @click="refresh()">Fetch</md-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['type'],
  data () {
    return {
      measure: 'temperature',
      time: '24h',
      points: 50,
      sensor: 'e0b4e2cfb279',
      sensors: ['e7428453ecb1', 'e16bcf522e77', 'e20e80bc247d', 'cdcdc86198d7', 'c93750a303c0', 'e0b4e2cfb279'],
      points_values: [10, 20, 50, 100, 200]
    }
  },
  methods: {
    refresh () {
      this.$emit('refresh', this.measure, this.time, this.points, this.sensor)
    }
  }
}
</script>
