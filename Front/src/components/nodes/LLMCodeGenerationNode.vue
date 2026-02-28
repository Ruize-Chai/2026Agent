<template>
  <div class="node-box" :class="stateClass">
    <div class="node-label">LLM Code Generation</div>
    <div style="font-size:10px;opacity:0.7">#{{ node.id }}</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ node: any; state?: string; stateClass?: string }>()
</script>

<style scoped>
.node-box { cursor:pointer }
</style>
