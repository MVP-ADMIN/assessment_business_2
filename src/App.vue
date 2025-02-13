<template>
  <router-view></router-view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isReady = ref(false)

onMounted(() => {
  isReady.value = true
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100%;
}
</style> 