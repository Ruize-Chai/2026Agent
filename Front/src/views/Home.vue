<template>
  <div class="home-root">
    <header class="topbar">
      <div class="left"> <div class="logo">O</div> <el-select v-model="selectedWorkflow" placeholder="Select workflow" style="width:320px" @change="onSelectWorkflow">
        <el-option v-for="w in workflows" :key="w.id" :label="w.name || w.filename" :value="w.id" />
      </el-select></div>
      <div class="right" style="display:flex;gap:8px;align-items:center">
        <div class="llm-indicator" :class="{ ready: llmReady, error: !llmReady }">
          <div class="dot"></div>
          <span>{{ llmReady ? 'LLM Ready' : 'LLM Not Configured' }}</span>
        </div>
        <el-button text @click="openLLMDialog" type="primary" style="font-size:12px">⚙️</el-button>
        <el-button type="primary" @click="saveWorkflow">Save</el-button>
        <el-input class="new-wid-input" size="small" placeholder="id (optional)" v-model="newWorkflowId" clearable style="width:220px" />
        <el-button type="info" @click="createWorkflow">Create</el-button>
        <el-button type="warning" @click="interrupt">Interrupt</el-button>
      </div>

      <!-- LLM Configuration Dialog -->
      <el-dialog title="LLM Configuration" v-model="llmDialogVisible" width="400px">
        <el-form :model="llmConfig" label-position="top">
          <el-form-item label="API Key">
            <el-input v-model="llmConfig.api_key" type="password" placeholder="Enter your OpenAI API key" />
          </el-form-item>
          <el-form-item label="Endpoint (optional)">
            <el-input v-model="llmConfig.endpoint" placeholder="https://api.openai.com/v1" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="llmDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveLLMConfig">Save Config</el-button>
        </template>
      </el-dialog>
    </header>
    <div class="main">
          <NodeToolbox />
          <FlowCanvas ref="canvas" :nodes="nodes" :nodeStates="nodeStates" @add="onAddNode" @select="onSelectNode" @update:nodes="onNodesUpdate" />
      <aside class="rightpanel">
        <Chatbox ref="chat" :initial="chatMessages" :showInput="false" />
        <div v-if="!selectedRunWorkflow" class="node-config-panel">
          <div v-if="selectedNode" class="config-section">
            <h3 style="margin-top:0">Node Configuration</h3>
            <el-form :model="selectedNode" label-width="100px" size="small">
              <el-form-item label="Type">
                <el-input v-model="selectedNode.type" disabled />
              </el-form-item>
              <el-form-item label="Node ID">
                <el-input v-model="selectedNode.id" disabled />
              </el-form-item>

              <!-- Context Slots -->
              <el-form-item label="Context Slots">
                <div style="width:100%">
                  <div v-for="(cs, i) in (selectedNode.params?.context_slot || [])" :key="i" style="display:flex;gap:6px;margin-bottom:8px;align-items:center">
                    <el-input-number v-model="cs.id" :min="1" placeholder="Node ID" style="width:60px" />
                    <el-input v-model="cs.key" placeholder="Key name" style="flex:1" />
                    <el-button type="danger" size="small" @click="removeContextSlot(i)">Remove</el-button>
                  </div>
                  <el-button type="primary" size="small" @click="addContextSlot">+ Add Slot</el-button>
                </div>
              </el-form-item>

              <!-- LLM Parameters (for LLM nodes) -->
              <el-divider v-if="isLLMNode(selectedNode.type)" style="margin:8px 0" />
              <div v-if="isLLMNode(selectedNode.type)">
                <h4 style="margin:8px 0">LLM Parameters</h4>
                <el-form-item label="Key">
                  <el-input v-model="paramConfig.key" placeholder="e.g., answer" />
                </el-form-item>
                <el-form-item label="Model">
                  <el-input v-model="paramConfig.model" placeholder="e.g., gpt-3.5-turbo" />
                </el-form-item>
                <el-form-item label="Max Tokens">
                  <el-input-number v-model="paramConfig.max_tokens" :min="1" placeholder="256" />
                </el-form-item>
                <el-form-item label="Prompt Template">
                  <el-input v-model="paramConfig.prompt_template" type="textarea" :rows="3" placeholder="Use {context} as placeholder" />
                </el-form-item>

                <!-- Special params for specific nodes -->
                <el-form-item v-if="selectedNode.type === 'LLM_Translate'" label="Target Language">
                  <el-input v-model="paramConfig.target_lang" placeholder="e.g., Spanish" />
                </el-form-item>
                <el-form-item v-if="selectedNode.type === 'LLM_CodeGeneration'" label="Language">
                  <el-input v-model="paramConfig.language" placeholder="e.g., Python" />
                </el-form-item>
                <el-form-item v-if="selectedNode.type === 'LLM_FileProduction'" label="File Extension">
                  <el-input v-model="paramConfig.file_ext" placeholder="e.g., txt" />
                </el-form-item>
              </div>
            </el-form>
          </div>
          <div v-else style="padding:12px;text-align:center;color:var(--text-muted)">
            <p>Select a node to configure</p>
          </div>
        </div>
        <div v-else class="run-controls">
          <el-select v-model="selectedRunWorkflow" placeholder="Select workflow to run" style="width:100%;margin-bottom:8px" @change="onRunWorkflowSelect">
            <el-option v-for="w in workflows" :key="w.id" :label="w.name || w.filename" :value="w.id" />
          </el-select>
          <el-button type="success" style="width:100%" @click="startRunWorkflow" :disabled="!selectedRunWorkflow">Run Selected</el-button>
        </div>
        <el-dialog title="Human Intervention" v-model="awaitingInput.open">
          <div v-if="awaitingInput.type === 'TEXT INPUT'">
            <el-form>
              <el-form-item label="Input">
                <el-input v-model="inputModel.text" />
              </el-form-item>
            </el-form>
          </div>
          <div v-else-if="awaitingInput.type === 'NUMBER INPUT'">
            <el-form>
              <el-form-item label="Number">
                <el-input-number v-model="inputModel.number" :controls="true" />
              </el-form-item>
            </el-form>
          </div>
          <div v-else-if="awaitingInput.type === 'CHECKBOX'">
            <el-form>
              <el-form-item label="Options">
                <el-checkbox-group v-model="inputModel.selections">
                  <el-checkbox v-for="(o, i) in awaitingInput.options" :key="i" :label="i">{{ o }}</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-form>
          </div>
          <template #footer>
            <el-button @click="awaitingInput.open = false">Cancel</el-button>
            <el-button type="primary" @click="submitIntervention">Submit</el-button>
          </template>
        </el-dialog>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import * as api from '../api/oriflow'
import NodeToolbox from '../components/NodeToolbox.vue'
import FlowCanvas from '../components/FlowCanvas.vue'
import Chatbox from '../components/Chatbox.vue'

const workflows = ref<Array<any>>([])
const selectedWorkflow = ref<string | null>(null)
const nodes = ref<any[]>([])
const nodeStates = ref<Record<number,string>>({})
const awaitingInput = ref<{ node_id: number | null; type?: string; open: boolean; options?: string[] }>({ node_id: null, type: undefined, open: false, options: [] })
const inputModel = ref<any>({ text: '', number: 0, selections: [] })
const selectedNode = ref<any | null>(null)
const mode = ref<'editor'|'run'>('editor')
const newWorkflowId = ref<string>('')
const chat = ref<any>(null)
const chatMessages = ref([])
const selectedRunWorkflow = ref<string | null>(null)

// Node parameter configuration
const paramConfig = reactive({
  key: 'answer',
  model: 'gpt-3.5-turbo',
  max_tokens: 256,
  prompt_template: '',
  target_lang: 'English',
  language: 'Python',
  file_ext: 'txt'
})

// LLM Configuration
const llmReady = ref(false)
const llmDialogVisible = ref(false)
const llmConfig = reactive({ api_key: '', endpoint: '' })

async function loadWorkflowList() {
  const res = await api.getWorkflowList()
  workflows.value = res?.data || []
}

async function loadLLMConfig() {
  try {
    const res = await api.getLlmConfig()
    const data = res?.data || {}
    llmConfig.api_key = data.api_key || ''
    llmConfig.endpoint = data.endpoint || ''
    llmReady.value = !!(data.api_key && data.api_key.trim())
  } catch (e) {
    llmReady.value = false
  }
}

async function saveLLMConfig() {
  try {
    await api.saveLlmConfig(llmConfig as any)
    await loadLLMConfig()
    llmDialogVisible.value = false
    ;(window as any).$message?.success('LLM config saved')
  } catch (e) {
    ;(window as any).$message?.error('Failed to save LLM config')
  }
}

function openLLMDialog() {
  llmDialogVisible.value = true
}

function onRunWorkflowSelect(id: string) {
  // Clear chat when selecting a new workflow
  chat.value?.clearHistory()
}

function onSelectWorkflow(id: string) {
  // load workflow nodes
  api.getWorkflow(id).then(r => {
    const payload = r.data
    nodes.value = payload.nodes || []
    // reset states
    nodeStates.value = {}
  }).catch(()=>{})
}

function onAddNode(n: any) { nodes.value.push(n) }
function onSelectNode(n: any) {
  selectedNode.value = n
  // Load param_config for this node
  const pc = n.params?.param_config || {}
  Object.assign(paramConfig, {
    key: pc.key || 'answer',
    model: pc.model || 'gpt-3.5-turbo',
    max_tokens: pc.max_tokens || 256,
    prompt_template: pc.prompt_template || '',
    target_lang: pc.target_lang || 'English',
    language: pc.language || 'Python',
    file_ext: pc.file_ext || 'txt'
  })
}
function onNodesUpdate(v: any[]) { nodes.value = v }

function addContextSlot() {
  if (!selectedNode.value) return
  if (!selectedNode.value.params) selectedNode.value.params = {}
  if (!selectedNode.value.params.context_slot) selectedNode.value.params.context_slot = []
  selectedNode.value.params.context_slot.push({ id: Date.now() % 100000, key: '' })
}

function removeContextSlot(index: number) {
  if (!selectedNode.value || !selectedNode.value.params?.context_slot) return
  selectedNode.value.params.context_slot.splice(index, 1)
}

async function runWorkflow() {
  if (!selectedWorkflow.value) { window.alert('请选择 workflow'); return }
  mode.value = 'run'
  chat.value?.clearHistory() // Clear previous messages
  chat.value?.appendSystemMessage(`Workflow "${selectedWorkflow.value}" started`, '▶️ RUN')

  // start SSE run and listen for states
  const gen = api.runWorkflowEvents(selectedWorkflow.value);
  (async () => {
    for await (const ev of gen) {
      // ev is NodeStateListPayload
      for (const s of ev.states) {
        // update UI node state
        nodeStates.value = { ...nodeStates.value, [s.node_id]: s.state }

        // handle chatbox outputs
        if ((s.state || '').toUpperCase() === 'OUTPUT') {
          try {
            const r = await api.getChatboxOutput(selectedWorkflow.value as string, s.node_id)
            const data = r.data as any
            const msg = { role: 'ai', content: data.message, meta: data.meta }
            chat.value?.appendMessage(msg)
          } catch (e) {
            // ignore
          }
        }
        // handle waiting states -> if TEXT INPUT/NUMBER INPUT/CHECKBOX open modal
        if (['TEXT INPUT','NUMBER INPUT','CHECKBOX'].includes((s.state||'').toUpperCase())) {
          const st = (s.state||'').toUpperCase()
          const stateMsg = st === 'TEXT INPUT' ? '📝 INPUT'
                         : st === 'NUMBER INPUT' ? '🔢 NUMBER'
                         : '☑️ SELECT'
          chat.value?.appendSystemMessage(
            `Node #${s.node_id} is awaiting your input`,
            stateMsg
          )
          // prepare dialog
          awaitingInput.value.node_id = s.node_id
          awaitingInput.value.type = st
          awaitingInput.value.open = true
          inputModel.value = { text: '', number: 0, selections: [] }
          if (st === 'CHECKBOX') {
            // fetch options
            try {
              const r = await api.getCheckboxOptions(selectedWorkflow.value as string, s.node_id)
              const data = r.data
              // schema: CheckboxOptionsPayload { node_id, options }
              awaitingInput.value.options = data.options || []
            } catch (e) {
              awaitingInput.value.options = []
            }
          }
        }

        // handle success/error states
        if (s.state === 'SUCCESS') {
          chat.value?.appendSystemMessage(`Node #${s.node_id} completed`, '✅ OK')
        } else if (s.state === 'ERROR') {
          chat.value?.appendSystemMessage(`Node #${s.node_id} failed`, '❌ ERROR')
        }
      }
    }
    // Workflow completed
    chat.value?.appendSystemMessage('Workflow execution completed', '✨ DONE')
  })()
}

async function saveWorkflow() {
  // minimal save: call alter with current nodes
  if (!selectedWorkflow.value) { window.alert('请选择 workflow'); return }
  const payload = { workflow_id: selectedWorkflow.value, entry: nodes.value[0]?.id || 0, nodes: nodes.value }
  await api.alterWorkflow(payload)
  window.alert('saved')
}

async function interrupt() { await api.postInterrupt(); window.alert('interrupt sent') }

async function startRunWorkflow() {
  if (!selectedRunWorkflow.value) { window.alert('Please select a workflow'); return }
  chat.value?.clearHistory()
  chat.value?.appendSystemMessage(`Workflow "${selectedRunWorkflow.value}" started`, '▶️ RUN')

  // start SSE run and listen for states
  const gen = api.runWorkflowEvents(selectedRunWorkflow.value);
  (async () => {
    for await (const ev of gen) {
      // ev is NodeStateListPayload
      for (const s of ev.states) {
        // handle chatbox outputs
        if ((s.state || '').toUpperCase() === 'OUTPUT') {
          try {
            const r = await api.getChatboxOutput(selectedRunWorkflow.value as string, s.node_id)
            const data = r.data as any
            const msg = { role: 'ai', content: data.message, meta: data.meta }
            chat.value?.appendMessage(msg)
          } catch (e) {
            // ignore
          }
        }
        // handle waiting states -> if TEXT INPUT/NUMBER INPUT/CHECKBOX open modal
        if (['TEXT INPUT','NUMBER INPUT','CHECKBOX'].includes((s.state||'').toUpperCase())) {
          const st = (s.state||'').toUpperCase()
          const stateMsg = st === 'TEXT INPUT' ? '📝 INPUT'
                         : st === 'NUMBER INPUT' ? '🔢 NUMBER'
                         : '☑️ SELECT'
          chat.value?.appendSystemMessage(
            `Node #${s.node_id} is awaiting your input`,
            stateMsg
          )
          // prepare dialog
          awaitingInput.value.node_id = s.node_id
          awaitingInput.value.type = st
          awaitingInput.value.open = true
          inputModel.value = { text: '', number: 0, selections: [] }
          if (st === 'CHECKBOX') {
            // fetch options
            try {
              const r = await api.getCheckboxOptions(selectedRunWorkflow.value as string, s.node_id)
              const data = r.data
              // schema: CheckboxOptionsPayload { node_id, options }
              awaitingInput.value.options = data.options || []
            } catch (e) {
              awaitingInput.value.options = []
            }
          }
        }

        // handle success/error states
        if (s.state === 'SUCCESS') {
          chat.value?.appendSystemMessage(`Node #${s.node_id} completed`, '✅ OK')
        } else if (s.state === 'ERROR') {
          chat.value?.appendSystemMessage(`Node #${s.node_id} failed`, '❌ ERROR')
        }
      }
    }
    // Workflow completed
    chat.value?.appendSystemMessage('Workflow execution completed', '✨ DONE')
  })()
}

async function createWorkflow() {
  // minimal create using current nodes; allow user-specified id or generate UUID
  const entry = nodes.value[0]?.id || 0
  const provided = (newWorkflowId.value || '').trim()
  const gen = (typeof crypto !== 'undefined' && (crypto as any).randomUUID) ? (crypto as any).randomUUID() : ('wf-' + Math.random().toString(36).slice(2,9))
  const wid = provided || gen
  const payload: any = { workflow_id: wid, entry, nodes: nodes.value }
  try {
    const r = await api.createWorkflow(payload)
    // backend may return workflow_id; prefer that if present
    const returned = r?.data?.workflow_id || r?.data?.id || wid
    await loadWorkflowList()
    if (returned) selectedWorkflow.value = returned
    newWorkflowId.value = ''
    window.alert('created ' + (returned || ''))
  } catch (e) {
    window.alert('create failed: ' + (e as any).toString())
  }
}

function isLLMNode(nodeType: string): boolean {
  return nodeType?.startsWith('LLM_') || false
}

// Watch paramConfig and sync to selectedNode
watch(paramConfig, (newVal) => {
  if (!selectedNode.value || !isLLMNode(selectedNode.value.type)) return
  if (!selectedNode.value.params) selectedNode.value.params = {}
  selectedNode.value.params.param_config = { ...newVal }
}, { deep: true })

onMounted(()=>{
  loadWorkflowList()
  loadLLMConfig()
})

async function submitIntervention() {
  // Support both editing workflow and running any workflow from right panel
  const wid = selectedRunWorkflow.value || selectedWorkflow.value
  const nid = awaitingInput.value.node_id
  const t = (awaitingInput.value.type || '').toUpperCase()
  if (!wid || nid == null) return
  try {
    if (t === 'TEXT INPUT') {
      await api.postTextInput(wid, nid, inputModel.value.text)
      chat.value?.appendMessage({ role: 'user', content: inputModel.value.text })
    } else if (t === 'NUMBER INPUT') {
      await api.postNumberInput(wid, nid, inputModel.value.number)
      chat.value?.appendMessage({ role: 'user', content: String(inputModel.value.number) })
    } else if (t === 'CHECKBOX') {
      // send selection indices
      const sel = inputModel.value.selections || []
      await api.postCheckboxSelection(wid, nid, sel)
      chat.value?.appendMessage({ role: 'user', content: `Selected ${sel.length} options` })
    }
  } catch (e) {
    window.alert('提交失败: ' + (e as any).toString())
  }
  awaitingInput.value.open = false
}
</script>

<style scoped>
.home-root { height:100vh; display:flex; flex-direction:column; background:#0f172a; color:#e6eef8 }
.topbar { height:64px; display:flex; align-items:center; justify-content:space-between; padding:0 16px; border-bottom:1px solid rgba(255,255,255,0.03) }
.main { display:flex; flex:1 }
.rightpanel { width:400px; border-left:1px solid rgba(255,255,255,0.03); display:flex; flex-direction:column; overflow-y:auto }
.node-config-panel { padding:12px; flex:1; overflow-y:auto }
.config-section { }
.config-section h3 { color:#e6eef8; margin:0 0 12px 0; font-size:14px }
.config-section h4 { color:rgba(230,238,248,0.8); margin:8px 0; font-size:12px }
.run-controls { padding:12px; border-top:1px solid rgba(255,255,255,0.03) }
.mode-toggle { padding:12px }
.props-panel { padding:12px }
.run-panel { padding:0; height:100% }
.logo { width:36px; height:36px; margin-right:8px }

/* LLM Indicator */
.llm-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  background: rgba(100, 116, 139, 0.1);
  border: 1px solid rgba(100, 116, 139, 0.2);
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.llm-indicator.ready {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.llm-indicator.error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.llm-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse-indicator 2s ease-in-out infinite;
}

@keyframes pulse-indicator {
  0%, 100% { opacity: 0.4 }
  50% { opacity: 1 }
}

.llm-indicator.ready .dot {
  background: #34d399;
}

.llm-indicator.error .dot {
  background: #fca5a5;
}

/* Create id input styles */
.new-wid-input .el-input__inner {
  background: rgba(255,255,255,0.03) !important;
  color: #e6eef8 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 8px;
  padding-left: 10px;
  height: 34px;
}
.new-wid-input .el-input__inner::placeholder { color: rgba(230,238,248,0.5); }
.topbar .right { gap: 10px; }
</style>
