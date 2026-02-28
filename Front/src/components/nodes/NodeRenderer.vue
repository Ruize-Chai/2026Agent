<template>
  <div class="node-wrap" :style="styleObj" @mousedown.stop.prevent="startDrag" @touchstart.stop.prevent="startTouch">
    <button class="create-btn" @click.stop.prevent="onCreate">+</button>
    <button class="delete-btn" @click.stop.prevent="onDelete">🗑️</button>
    <component :is="nodeComponent" :node="node" :state="state" :stateClass="stateClass" @select="onClick" @change="onChildChange" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import StartNode from './StartNode.vue'
import EndNode from './EndNode.vue'
import TextInputNode from './TextInputNode.vue'
import NumberInputNode from './NumberInputNode.vue'
import ChatboxNode from './ChatboxNode.vue'
import CheckboxNode from './CheckboxNode.vue'
import DelayTimerNode from './DelayTimerNode.vue'
import IfConditionNode from './IfConditionNode.vue'
import LLMAnswerNode from './LLMAnswerNode.vue'
import LLMFileProductionNode from './LLMFileProductionNode.vue'
import LLMGenerateWorkflowNode from './LLMGenerateWorkflowNode.vue'
import LLMSummarizeNode from './LLMSummarizeNode.vue'
import LLMQANode from './LLMQANode.vue'
import LLMTranslateNode from './LLMTranslateNode.vue'
import LLMCodeGenerationNode from './LLMCodeGenerationNode.vue'
import LLMConversationNode from './LLMConversationNode.vue'

const props = defineProps<{ node: any; state?: string; style?: any }>()
const emit = defineEmits(['select','moved','create','delete'])

const mapping: Record<string, any> = {
  'Start': StartNode,
  'END': EndNode,
  'TEXT INPUT': TextInputNode,
  'NUMBER INPUT': NumberInputNode,
  'CHATBOX': ChatboxNode,
  'CHECKBOX': CheckboxNode,
  'DELAYTIMER': DelayTimerNode,
  'IFCONDITION': IfConditionNode,
  'LLM_Answer': LLMAnswerNode,
  'LLM_FileProduction': LLMFileProductionNode,
  'LLM_GenerateWorkflow': LLMGenerateWorkflowNode,
  'LLM_Summarize': LLMSummarizeNode,
  'LLM_QA': LLMQANode,
  'LLM_Translate': LLMTranslateNode,
  'LLM_CodeGeneration': LLMCodeGenerationNode,
  'LLM_Conversation': LLMConversationNode,
}

const node = props.node
const pos = ref({ x: node.x || 0, y: node.y || 0 })
const dragging = ref(false)
let start = { x: 0, y: 0, ox: 0, oy: 0 }

const styleObj = computed(() => ({ left: (node.x || pos.value.x) + 'px', top: (node.y || pos.value.y) + 'px', position: 'absolute', cursor: dragging.value ? 'grabbing' : 'grab' }))

// 映射状态到CSS类名
const stateClass = computed(() => {
  const st = (props.state || '').toUpperCase()
  if (['RUNNING', 'ACTIVE'].includes(st)) return 'running'
  if (['TEXT INPUT', 'NUMBER INPUT', 'CHECKBOX'].includes(st)) return 'waiting'
  if (st === 'SUCCESS') return 'success'
  if (st === 'ERROR') return 'error'
  return 'idle'
})

const nodeComponent = computed(() => mapping[node.type] || StartNode)

function onClick(payload?: any) { emit('select', node) }

function onChildChange(updated: any) {
  // child emits change with node; ensure parent knows
  emit('moved', updated || node)
}

function onCreate() {
  emit('create', node)
}

function onDelete() {
  emit('delete', node.id)
}

function startDrag(e: MouseEvent) {
  dragging.value = true
  start.x = e.clientX
  start.y = e.clientY
  start.ox = node.x || 0
  start.oy = node.y || 0
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function onMove(e: MouseEvent) {
  if (!dragging.value) return
  const nx = start.ox + (e.clientX - start.x)
  const ny = start.oy + (e.clientY - start.y)
  pos.value.x = nx
  pos.value.y = ny
  node.x = Math.round(nx)
  node.y = Math.round(ny)
  emit('moved', node)
}

function onUp() {
  if (!dragging.value) return
  dragging.value = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', onUp)
  emit('moved', node)
}

function startTouch(e: TouchEvent) {
  const t = e.touches[0]
  dragging.value = true
  start.x = t.clientX
  start.y = t.clientY
  start.ox = node.x || 0
  start.oy = node.y || 0
  window.addEventListener('touchmove', onTouchMove)
  window.addEventListener('touchend', onTouchEnd)
}

function onTouchMove(e: TouchEvent) {
  if (!dragging.value) return
  const t = e.touches[0]
  const nx = start.ox + (t.clientX - start.x)
  const ny = start.oy + (t.clientY - start.y)
  pos.value.x = nx
  pos.value.y = ny
  node.x = Math.round(nx)
  node.y = Math.round(ny)
  emit('moved', node)
}

function onTouchEnd() {
  dragging.value = false
  window.removeEventListener('touchmove', onTouchMove)
  window.removeEventListener('touchend', onTouchEnd)
  emit('moved', node)
}

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', onUp)
  window.removeEventListener('touchmove', onTouchMove)
  window.removeEventListener('touchend', onTouchEnd)
})
</script>

<style scoped>
.node-wrap { width:160px; height:72px; user-select:none; -webkit-user-select:none }
.create-btn { position:absolute; right:6px; top:6px; width:20px; height:20px; border-radius:4px; border:none; background:rgba(255,255,255,0.06); color:#e6eef8; cursor:pointer }
.create-btn:hover { background:rgba(255,255,255,0.12) }
.delete-btn { position:absolute; right:28px; top:6px; width:20px; height:20px; border-radius:4px; border:none; background:rgba(255,255,255,0.06); color:#e6eef8; cursor:pointer; font-size:12px }
.delete-btn:hover { background:rgba(239,68,68,0.3) }
</style>
