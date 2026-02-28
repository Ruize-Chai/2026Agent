<template>
  <div class="toolbox">
    <div class="toolbox-header">
      <h4>🧩 Node Palette</h4>
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="search-input"
        />
      </div>
    </div>

    <!-- Group: Input -->
    <div class="node-group">
      <div class="group-title">INPUT</div>
      <ul class="node-list">
        <li
          v-for="t in filterNodes(['Start', 'TEXT INPUT', 'NUMBER INPUT'])"
          :key="t"
          :draggable="true"
          @dragstart="onDragStart($event, t)"
          @dragend="onDragEnd"
          class="node-item input-type"
          :title="`Drag to add ${t} node`"
        >
          <span class="icon">📥</span>
          <span class="name">{{ t }}</span>
        </li>
      </ul>
    </div>

    <!-- Group: Process -->
    <div class="node-group">
      <div class="group-title">PROCESS</div>
      <ul class="node-list">
        <li
          v-for="t in filterNodes(['DELAYTIMER', 'IFCONDITION'])"
          :key="t"
          :draggable="true"
          @dragstart="onDragStart($event, t)"
          @dragend="onDragEnd"
          class="node-item process-type"
          :title="`Drag to add ${t} node`"
        >
          <span class="icon">⚙️</span>
          <span class="name">{{ t }}</span>
        </li>
      </ul>
    </div>

    <!-- Group: AI/LLM -->
    <div class="node-group">
      <div class="group-title">AI & LLM</div>
      <ul class="node-list">
        <li
          v-for="t in filterNodes(['LLM_Answer', 'LLM_FileProduction', 'LLM_GenerateWorkflow', 'LLM_Summarize', 'LLM_QA', 'LLM_Translate', 'LLM_CodeGeneration', 'LLM_Conversation'])"
          :key="t"
          :draggable="true"
          @dragstart="onDragStart($event, t)"
          @dragend="onDragEnd"
          class="node-item llm-type"
          :title="`Drag to add ${t} node`"
        >
          <span class="icon">🤖</span>
          <span class="name">{{ t }}</span>
        </li>
      </ul>
    </div>

    <!-- Group: Output -->
    <div class="node-group">
      <div class="group-title">OUTPUT</div>
      <ul class="node-list">
        <li
          v-for="t in filterNodes(['CHATBOX', 'CHECKBOX', 'END'])"
          :key="t"
          :draggable="true"
          @dragstart="onDragStart($event, t)"
          @dragend="onDragEnd"
          class="node-item output-type"
          :title="`Drag to add ${t} node`"
        >
          <span class="icon">📤</span>
          <span class="name">{{ t }}</span>
        </li>
      </ul>
    </div>

    <!-- Dragging indicator -->
    <div v-if="isDragging" class="drag-indicator">
      <span>{{ draggedType }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const allTypes = [
  'Start', 'END',
  'TEXT INPUT', 'NUMBER INPUT',
  'CHATBOX', 'CHECKBOX',
  'DELAYTIMER', 'IFCONDITION',
  'LLM_Answer', 'LLM_FileProduction', 'LLM_GenerateWorkflow',
  'LLM_Summarize', 'LLM_QA', 'LLM_Translate', 'LLM_CodeGeneration', 'LLM_Conversation'
]

const searchQuery = ref('')
const isDragging = ref(false)
const draggedType = ref('')

const filterNodes = (nodeList: string[]) => {
  if (!searchQuery.value) return nodeList
  const query = searchQuery.value.toLowerCase()
  return nodeList.filter(t => t.toLowerCase().includes(query))
}

const visibleTypes = computed(() => {
  if (!searchQuery.value) return allTypes
  const query = searchQuery.value.toLowerCase()
  return allTypes.filter(t => t.toLowerCase().includes(query))
})

function onDragStart(e: DragEvent, t: string) {
  if (!e.dataTransfer) return
  e.dataTransfer.effectAllowed = 'copy'
  e.dataTransfer.setData('application/node-type', t)
  e.dataTransfer.setData('text/plain', t)
  isDragging.value = true
  draggedType.value = t
}

function onDragEnd() {
  isDragging.value = false
  draggedType.value = ''
}
</script>

<style scoped>
.toolbox {
  width: 240px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-right: 1px solid rgba(255, 255, 255, 0.03);
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  position: relative;
}

.toolbox-header {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.02);
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  z-index: 10;
}

.toolbox-header h4 {
  color: var(--text-light);
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.search-box {
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  color: var(--text-light);
  font-size: 12px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-input:focus {
  border-color: rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.05);
}

.node-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.group-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 4px 8px;
  opacity: 0.7;
}

.node-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.node-item {
  padding: 8px 10px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.01));
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  color: var(--text-light);
  font-size: 12px;
  font-weight: 500;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.node-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  transform: translateX(-100%);
  transition: transform 0.3s;
}

.node-item:hover::before {
  transform: translateX(100%);
}

.node-item:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateX(2px);
}

.node-item:active {
  cursor: grabbing;
  transform: translateX(2px) scale(0.98);
}

.node-item.input-type {
  border-color: rgba(0, 212, 255, 0.15);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(0, 212, 255, 0.02));
}

.node-item.input-type:hover {
  border-color: rgba(0, 212, 255, 0.3);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.12), rgba(0, 212, 255, 0.04));
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.2);
}

.node-item.process-type {
  border-color: rgba(245, 158, 11, 0.15);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.02));
}

.node-item.process-type:hover {
  border-color: rgba(245, 158, 11, 0.3);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0.04));
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.2);
}

.node-item.llm-type {
  border-color: rgba(168, 85, 247, 0.15);
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.08), rgba(168, 85, 247, 0.02));
}

.node-item.llm-type:hover {
  border-color: rgba(168, 85, 247, 0.3);
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.12), rgba(168, 85, 247, 0.04));
  box-shadow: 0 0 12px rgba(168, 85, 247, 0.2);
}

.node-item.output-type {
  border-color: rgba(16, 185, 129, 0.15);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.02));
}

.node-item.output-type:hover {
  border-color: rgba(16, 185, 129, 0.3);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(16, 185, 129, 0.04));
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.2);
}

.node-item .icon {
  font-size: 14px;
  flex-shrink: 0;
}

.node-item .name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drag-indicator {
  position: fixed;
  bottom: 20px;
  left: 20px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.9), rgba(0, 212, 255, 0.7));
  border-radius: 8px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
  animation: slide-up 0.3s ease-out;
  z-index: 1000;
  pointer-events: none;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scrollbar */
.toolbox::-webkit-scrollbar {
  width: 6px;
}

.toolbox::-webkit-scrollbar-track {
  background: transparent;
}

.toolbox::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.3);
  border-radius: 3px;
}

.toolbox::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 116, 139, 0.5);
}
</style>
