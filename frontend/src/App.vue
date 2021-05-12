<template>
  <div id="app">
    <Main/>
  </div>
</template>

<script>
import M from 'materialize-css'

import Main from './components/Main.vue'

export default {
  name: 'App',
  components: {
    Main
  },
  mounted() {
    M.AutoInit()
  }
}
</script>
