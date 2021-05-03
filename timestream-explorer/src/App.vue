<template>
  <div class="page-container">
    <md-app md-mode="reveal">
      <md-app-toolbar>
        <h2 class="md-title" style="flex:1;">Timestream Explorer</h2>
        <router-link to="/about">About</router-link>
      </md-app-toolbar>

      <md-app-content style="heigth:100%;">
        <router-view />
      </md-app-content>
    </md-app>
  </div>
</template>

<style>
.body {
  font-family: 'Roboto';
}
</style>

<script>
export default {
  data() {
    return {
      menuVisible: false
    }
  }
}
</script>