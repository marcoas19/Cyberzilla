<script setup>
import { computed, ref } from 'vue'

const phase = ref('idle')
const busy = ref(false)
const error = ref('')
const result = ref(null)
const scannedAt = ref(null)
const connection = ref('Not checked')
const scenario = ref('suspicious')
const activity = ref([])
const apiBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

const states = {
  idle: { image: 'godzilla-detect.gif', title: 'Ready when you are', description: 'Choose a sample scenario or paste your own events to begin.', label: 'Ready' },
  scanning: { image: 'gigan-scan.gif', title: 'Analyzing events', description: 'Gigan is checking the submitted events with the detection API.', label: 'Scanning' },
  detected: { image: 'godzilla-detect.gif', title: 'Suspicious activity found', description: 'Review the findings below. You can also explore a simulated response.', label: 'Review needed' },
  clean: { image: 'godzilla-detect.gif', title: 'No rule matches found', description: 'These events did not trigger the detector. This is not a full security assessment.', label: 'Scan complete' },
  responding: { image: 'godzilla-atomic.gif', title: 'Simulating containment', description: 'Godzilla demonstrates the response stage. No IP addresses are being blocked.', label: 'Simulation' },
  healing: { image: 'mothra-heal.gif', title: 'Simulating recovery', description: 'Mothra illustrates recovery. No files or malware are being removed.', label: 'Simulation' },
  contained: { image: 'destoroyah-peace.gif', title: 'Response demo complete', description: 'Destoroyah has surrendered. The original scan findings remain available for review.', label: 'Demo complete' },
}
const current = computed(() => states[phase.value])
const threats = computed(() => Array.isArray(result.value?.threats) ? result.value.threats : [])
const threatCount = computed(() => result.value?.threats_detected ?? threats.value.length)
const severityRank = { UNKNOWN: 0, INFO: 1, LOW: 2, MEDIUM: 3, HIGH: 4, CRITICAL: 5 }
const highestSeverity = computed(() => {
  if (!result.value) return '—'
  if (!threatCount.value) return 'None'
  return threats.value.reduce((highest, threat) => {
    const level = String(threat.severity || 'UNKNOWN').toUpperCase()
    return (severityRank[level] || 0) > (severityRank[highest] || 0) ? level : highest
  }, 'UNKNOWN')
})
const eventCount = computed(() => {
  try { const events = JSON.parse(eventsText.value); return Array.isArray(events) ? events.length : null }
  catch { return null }
})
const lastScan = computed(() => scannedAt.value ? scannedAt.value.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'No scans yet')

function makeEvents(suspicious) {
  const start = Date.now() - 60000
  return Array.from({ length: 6 }, (_, index) => ({
    timestamp: new Date(start + index * 8000).toISOString(),
    source_ip: suspicious ? '192.0.2.10' : `192.0.2.${index + 20}`,
    username: 'demo-user',
    event_type: suspicious && index < 5 ? 'login_failed' : 'login_success',
  }))
}
const eventsText = ref(JSON.stringify(makeEvents(true), null, 2))

function loadScenario(value) {
  if (busy.value) return
  scenario.value = value
  eventsText.value = JSON.stringify(makeEvents(value === 'suspicious'), null, 2)
  error.value = ''
}
function log(message) {
  activity.value.unshift({ message, time: new Date().toLocaleTimeString() })
  activity.value = activity.value.slice(0, 8)
}
function severityClass(value) {
  const level = String(value || '').toLowerCase()
  return ['critical', 'high', 'medium', 'low'].includes(level) ? level : 'neutral'
}
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms))

async function scan() {
  if (busy.value) return
  error.value = ''
  let events
  try {
    events = JSON.parse(eventsText.value)
    if (!Array.isArray(events) || !events.length) throw new Error('Enter a non-empty JSON array of events.')
    if (events.some(event => !event || typeof event !== 'object' || !event.timestamp || !event.source_ip || !event.event_type)) {
      throw new Error('Every event needs timestamp, source_ip, and event_type.')
    }
  } catch (err) { error.value = `Check your event data: ${err.message}`; return }

  busy.value = true
  result.value = null
  scannedAt.value = null
  phase.value = 'scanning'
  log(`Scan started · ${events.length} events submitted`)
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 15000)
  try {
    const response = await fetch(`${apiBase}/api/scan`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ events }), signal: controller.signal,
    })
    const body = await response.text()
    if (!response.ok) {
      connection.value = 'Server reached'
      throw new Error(`Scan failed (${response.status}). ${body.slice(0, 350)}`)
    }
    let data
    try { data = JSON.parse(body) }
    catch { throw new Error('The server returned an unexpected response. Check the API connection.') }
    if (!data || typeof data !== 'object' || (typeof data.threats_detected !== 'number' && !Array.isArray(data.threats))) {
      throw new Error('The response is missing the expected scan findings.')
    }
    result.value = data
    scannedAt.value = new Date()
    connection.value = 'Verified by scan'
    phase.value = threatCount.value > 0 ? 'detected' : 'clean'
    log(`Scan complete · ${threatCount.value} threat${threatCount.value === 1 ? '' : 's'} detected`)
  } catch (err) {
    error.value = err.name === 'AbortError'
      ? 'The scan timed out. Check that FastAPI is running and try again.'
      : err.message === 'Failed to fetch'
        ? 'Unable to reach the API. Keep FastAPI running and check the Vite proxy.'
        : err.message
    if (err.name === 'AbortError' || err.message === 'Failed to fetch') connection.value = 'Connection failed'
    phase.value = 'idle'
    log('Scan failed · no result available')
  } finally { clearTimeout(timeout); busy.value = false }
}

async function simulateResponse() {
  if (busy.value || !['detected', 'contained'].includes(phase.value)) return
  busy.value = true
  try {
    phase.value = 'responding'; log('Simulation · containment stage started')
    await wait(2400)
    phase.value = 'healing'; log('Simulation · recovery stage started')
    await wait(2600)
    phase.value = 'contained'; log('Simulation complete · no system changes made')
  } finally { busy.value = false }
}

function downloadReport() {
  if (!result.value) return
  const blob = new Blob([JSON.stringify(result.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url; link.download = 'cyberzilla-scan-report.json'; link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="#overview" aria-label="Cyberzilla overview">
        <span class="brand-mark" aria-hidden="true">CZ</span>
        <span><strong>Cyberzilla</strong><small>Atomic Defense System</small></span>
      </a>
      <span class="portfolio-tag">Security portfolio</span>
    </header>

    <main id="overview" :aria-busy="busy">
      <div class="page-heading">
        <div><span class="eyebrow">SECURITY WORKSPACE</span><h1>Understand the signal.<br /><span>Respond with confidence.</span></h1>
          <p>Analyze login events and turn suspicious activity into clear findings.</p></div>
        <div class="connection"><span class="status-dot" :class="{ verified: connection === 'Verified by scan' }"></span><div><strong>Detection API</strong><small>{{ connection }}</small></div></div>
      </div>

      <section class="metrics" aria-label="Latest scan summary">
        <article class="metric"><span>Events analyzed</span><strong>{{ result?.total_events ?? '—' }}</strong><small>Latest submitted scan</small></article>
        <article class="metric"><span>Threats detected</span><strong :class="{ 'warning-text': result && threatCount > 0 }">{{ result ? threatCount : '—' }}</strong><small>Matches from the detection API</small></article>
        <article class="metric"><span>Highest severity</span><strong class="severity-value" :class="severityClass(highestSeverity)">{{ highestSeverity }}</strong><small>Based on returned findings</small></article>
        <article class="metric"><span>Last scan</span><strong class="time-value">{{ lastScan }}</strong><small>Current session · local time</small></article>
      </section>

      <div class="workspace">
        <div class="main-column">
          <section class="panel input-panel" aria-labelledby="input-title">
            <div class="panel-heading"><div><h2 id="input-title">Run a security scan</h2><p>Start with a sample or bring your own event data.</p></div><span class="step-tag">01 / INPUT</span></div>
            <div class="scenario-grid">
              <button class="scenario" :class="{ selected: scenario === 'suspicious' }" :disabled="busy" @click="loadScenario('suspicious')"><span class="scenario-symbol suspicious" aria-hidden="true">!</span><strong>Suspicious logins</strong><small>Five failed attempts from one IP.</small><span class="choice-label">{{ scenario === 'suspicious' ? 'Selected' : 'Load sample' }}</span></button>
              <button class="scenario" :class="{ selected: scenario === 'clean' }" :disabled="busy" @click="loadScenario('clean')"><span class="scenario-symbol clean" aria-hidden="true">✓</span><strong>Normal activity</strong><small>Successful logins from different IPs.</small><span class="choice-label">{{ scenario === 'clean' ? 'Selected' : 'Load sample' }}</span></button>
            </div>
            <details class="advanced"><summary>Advanced input <span>Edit event JSON</span></summary><div class="editor"><label for="events">Security events</label><p>Required fields: timestamp, source_ip, and event_type.</p><textarea id="events" v-model="eventsText" :disabled="busy" spellcheck="false" rows="12" @input="scenario = 'custom'"></textarea></div></details>
            <div class="scan-action"><span>{{ eventCount === null ? 'Invalid JSON' : `${eventCount} events ready` }}</span><button class="primary" :disabled="busy" @click="scan"><span v-if="phase === 'scanning'" class="spinner" aria-hidden="true"></span>{{ phase === 'scanning' ? 'Scanning…' : busy ? 'Simulation running…' : 'Start scan' }}<span v-if="!busy" aria-hidden="true">↗</span></button></div>
            <div v-if="error" class="error" role="alert"><strong>Scan could not complete</strong><p>{{ error }}</p></div>
          </section>

          <section class="panel findings-panel" aria-labelledby="findings-title">
            <div class="panel-heading"><div><h2 id="findings-title">Scan findings</h2><p>Review the latest result before deciding what to do next.</p></div><button v-if="result" class="text-button" @click="downloadReport">Export JSON ↓</button></div>
            <div v-if="!result" class="empty-state"><span class="empty-icon" aria-hidden="true">⌕</span><h3>{{ phase === 'scanning' ? 'Analysis in progress' : 'Your findings will appear here' }}</h3><p>{{ phase === 'scanning' ? 'Waiting for the detection API to return results.' : 'Choose a scenario above, then select Start scan.' }}</p></div>
            <template v-else>
              <div class="result-banner" :class="{ flagged: threatCount > 0 }"><span class="status-dot" :class="{ verified: !threatCount }"></span><strong>{{ threatCount > 0 ? `${threatCount} threat${threatCount === 1 ? '' : 's'} detected` : 'No threats detected by this rule' }}</strong><span>{{ result.status || 'SCAN COMPLETED' }}</span></div>
              <div v-if="threats.length" class="table-scroll"><table><thead><tr><th>Finding</th><th>Source IP</th><th>Severity</th><th>Attempts</th></tr></thead><tbody><tr v-for="(threat, index) in threats" :key="index"><td><strong>{{ threat.rule_name || threat.name || threat.title || 'Detected threat' }}</strong><small>{{ threat.rule_id || threat.id || 'Detection rule' }}</small></td><td class="mono">{{ threat.source_ip || '—' }}</td><td><span class="severity-pill" :class="severityClass(threat.severity)">{{ threat.severity || 'Unknown' }}</span></td><td>{{ threat.attempts ?? '—' }}</td></tr></tbody></table></div>
              <p v-else class="no-findings">{{ threatCount ? 'The API reported threats without individual finding details. See the full result below.' : 'No repeated failed-login pattern was found in the submitted events.' }}</p>
              <details class="raw-result"><summary>View full API result</summary><pre>{{ JSON.stringify(result, null, 2) }}</pre></details>
            </template>
          </section>
        </div>

        <aside class="side-column">
          <section class="panel defense-panel" aria-labelledby="defense-title">
            <div class="panel-heading"><h2 id="defense-title">Defense activity</h2><span class="live-tag">{{ current.label }}</span></div>
            <div class="mascot-stage"><img :key="phase" :src="`/mascots/${current.image}`" :alt="current.title" /></div>
            <div class="state-copy" aria-live="polite"><h3>{{ current.title }}</h3><p>{{ current.description }}</p></div>
            <div class="workflow" aria-label="Security workflow"><span :class="{ active: ['idle', 'scanning'].includes(phase) }">Scan</span><i aria-hidden="true">→</i><span :class="{ active: ['detected', 'clean'].includes(phase) }">Review</span><i aria-hidden="true">→</i><span :class="{ active: ['responding', 'healing', 'contained'].includes(phase) }">Simulate</span></div>
            <div class="response-box"><div><strong>Response demonstration</strong><span class="simulation-tag">SIMULATION</span></div><p>Explore containment and recovery. This demo does not block IPs or remove malware.</p><button class="secondary" :disabled="busy || !['detected', 'contained'].includes(phase)" @click="simulateResponse">{{ phase === 'contained' ? 'Replay response demo' : 'Simulate response' }}</button></div>
          </section>
          <section class="panel activity-panel"><div class="panel-heading"><h2>Session activity</h2><span class="step-tag">LIVE LOG</span></div><p v-if="!activity.length" class="quiet">No activity yet. Your scan history for this session will appear here.</p><ol v-else class="activity-list" aria-live="polite"><li v-for="(item, index) in activity" :key="`${item.time}-${index}`"><span class="log-dot" aria-hidden="true"></span><div><p>{{ item.message }}</p><time>{{ item.time }}</time></div></li></ol></section>
          <section class="rule-note"><span class="eyebrow">WHAT THIS DETECTOR DOES</span><h3>A focused view of login activity</h3><p>Cyberzilla looks for repeated failed logins from the same source IP. Findings come from FastAPI; the kaiju illustrate each stage.</p></section>
        </aside>
      </div>
      <footer><span>Cyberzilla <span class="footer-dot">/</span> Built by Marco Aguilar</span><span>Detection API · Visual response demo</span></footer>
    </main>
  </div>
</template>

<style scoped>
:global(*) { box-sizing: border-box; }
:global(body) { margin: 0; background: #0b1120; color: #edf3fa; font-family: Inter, 'Segoe UI', Arial, sans-serif; -webkit-font-smoothing: antialiased; }
:global(#app) { max-width: none; margin: 0; padding: 0; text-align: left; }
button, textarea { font: inherit; }
button { cursor: pointer; transition: border-color .15s, background .15s; }
button:disabled { opacity: .5; cursor: not-allowed; }
button:focus-visible, a:focus-visible, summary:focus-visible, textarea:focus-visible { outline: 3px solid #67dce8; outline-offset: 4px; }
a { color: inherit; }
.topbar { min-height: 86px; display: flex; justify-content: space-between; align-items: center; padding: 18px max(24px, calc((100vw - 1280px) / 2)); border-bottom: 1px solid #253047; background: #0f1728; }
.brand { display: flex; gap: 12px; align-items: center; text-decoration: none; }
.brand-mark { display: grid; place-items: center; width: 42px; height: 42px; border: 1px solid #418b9d; border-radius: 12px; color: #86e8e9; background: #173142; font-size: 15px; font-weight: 800; letter-spacing: -1px; }
.brand strong { display: block; font-size: 19px; letter-spacing: -.5px; }
.brand small { display: block; color: #a5b4c8; font-size: 11px; margin-top: 3px; }
.portfolio-tag { color: #a5b4c8; font-size: 12px; border: 1px solid #334159; padding: 7px 12px; border-radius: 30px; }
main { max-width: 1328px; margin: auto; padding: 40px 24px 20px; }
.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 30px; }
.eyebrow { font-size: 10px; font-weight: 700; letter-spacing: 1.8px; color: #7ddbe4; }
h1 { font-size: clamp(28px, 3vw, 39px); line-height: 1.2; letter-spacing: -1.4px; font-weight: 650; margin: 12px 0; }
h1 span { color: #9aaec5; }
p { line-height: 1.6; }
.page-heading p { color: #a5b4c8; font-size: 13px; margin: 0; }
.connection { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border: 1px solid #2a3850; border-radius: 10px; flex-shrink: 0; }
.connection strong { font-size: 12px; display: block; }
.connection small { display: block; margin-top: 4px; font-size: 11px; color: #a5b4c8; }
.status-dot { width: 7px; height: 7px; display: inline-block; background: #a3b0c2; border-radius: 50%; flex-shrink: 0; }
.status-dot.verified { background: #79deb6; }
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 24px; }
.metric { border: 1px solid #29364c; border-radius: 12px; padding: 20px; background: #111b2d; }
.metric > span { display: block; font-size: 12px; color: #b1bed0; }
.metric > strong { display: block; font-size: 33px; font-weight: 600; letter-spacing: -1px; margin: 11px 0; }
.metric > strong.severity-value, .metric > strong.time-value { font-size: 23px; line-height: 40px; }
.metric small { color: #9aaec5; font-size: 10px; }
.warning-text { color: #ffc38a; }
.workspace { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 24px; align-items: start; }
.main-column, .side-column { display: flex; flex-direction: column; gap: 22px; min-width: 0; }
.panel { border: 1px solid #2a3750; border-radius: 14px; background: #111b2d; overflow: hidden; }
.input-panel, .defense-panel, .activity-panel { padding: 24px; }
.panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-bottom: 20px; }
h2 { margin: 0; font-size: 16px; letter-spacing: -.3px; font-weight: 600; }
.panel-heading p { margin: 7px 0 0; font-size: 12px; color: #a5b4c8; }
.step-tag { color: #9aaec5; font-size: 9px; font-weight: 600; letter-spacing: 1px; white-space: nowrap; }
.scenario-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.scenario { text-align: left; background: #0d1626; border: 1px solid #344259; border-radius: 10px; padding: 18px; color: #edf3fa; }
.scenario:hover:not(:disabled) { border-color: #65c1cf; }
.scenario.selected { border-color: #68ccd6; background: #132838; }
.scenario-symbol { width: 30px; height: 30px; border-radius: 8px; display: grid; place-items: center; font-weight: bold; margin-bottom: 14px; }
.scenario-symbol.suspicious { background: #443427; color: #ffbf8a; }
.scenario-symbol.clean { background: #173b36; color: #83e4bc; }
.scenario strong { display: block; font-size: 13px; }
.scenario small { display: block; color: #b0bfd1; font-size: 11px; margin: 7px 0 16px; line-height: 1.5; }
.choice-label { font-size: 10px; color: #84dce3; }
.advanced { margin-top: 22px; border: 1px solid #2c3b53; border-radius: 8px; }
summary { cursor: pointer; color: #c3d0e1; font-size: 12px; padding: 14px; }
.advanced summary span { float: right; color: #9aaec5; font-size: 10px; }
.editor { padding: 0 14px 14px; }
.editor label { font-size: 12px; display: block; margin-top: 5px; }
.editor p { font-size: 10px; color: #a5b4c8; }
textarea { width: 100%; padding: 14px; background: #0b1220; border: 1px solid #35465f; border-radius: 6px; font: 12px/1.6 Consolas, monospace; color: #c1e1ed; resize: vertical; }
.scan-action { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 22px; }
.scan-action > span { color: #a5b4c8; font-size: 11px; }
.primary { display: flex; align-items: center; justify-content: center; gap: 20px; background: #85e2e7; border: 1px solid #85e2e7; color: #092431; border-radius: 8px; padding: 12px 20px; font-size: 12px; font-weight: 700; }
.primary:hover:not(:disabled) { background: #b1f4f4; }
.error { border: 1px solid #875160; border-radius: 8px; padding: 15px; margin-top: 18px; color: #ffd3d8; background: #34212f; overflow-wrap: anywhere; font-size: 12px; }
.error p { margin: 7px 0 0; }
.findings-panel > .panel-heading { padding: 24px 24px 0; }
.text-button { background: none; border: 0; padding: 4px; color: #85dce6; font-size: 11px; white-space: nowrap; }
.empty-state { text-align: center; padding: 34px 20px 50px; }
.empty-icon { display: grid; place-items: center; width: 46px; height: 46px; background: #1b2a40; border: 1px solid #344259; border-radius: 12px; margin: 0 auto 16px; color: #91c2d7; font-size: 30px; }
h3 { font-size: 14px; font-weight: 600; margin: 0; }
.empty-state p { color: #a5b4c8; font-size: 12px; }
.result-banner { margin: 0 24px 18px; display: flex; align-items: center; gap: 9px; border: 1px solid #36574f; background: #17302e; border-radius: 8px; padding: 12px; font-size: 11px; }
.result-banner.flagged { border-color: #6e5135; background: #332b25; }
.result-banner.flagged .status-dot { background: #ffc38a; }
.result-banner > span:last-child { margin-left: auto; font-size: 9px; color: #c2cbd6; }
.table-scroll { overflow-x: auto; }
table { width: 100%; text-align: left; border-collapse: collapse; font-size: 11px; }
th { color: #a5b4c8; font-size: 10px; font-weight: 500; background: #0f192a; }
th, td { padding: 15px 20px; border-top: 1px solid #29374f; }
td strong { display: block; font-size: 11px; min-width: 145px; line-height: 1.5; }
td small { display: block; color: #9aaec5; margin-top: 4px; }
.mono { font-family: Consolas, monospace; white-space: nowrap; }
.severity-pill { display: inline-block; font-size: 9px; font-weight: 700; padding: 5px 8px; border-radius: 4px; background: #24324b; }
.high, .critical { color: #ffbc93; }
.severity-pill.high, .severity-pill.critical { background: #453126; }
.medium { color: #f0db87; }
.severity-pill.medium { background: #3a3524; }
.low { color: #87e0c0; }
.neutral { color: #c3d0e1; }
.no-findings { margin: 20px 24px; color: #b0c0d2; font-size: 12px; }
.raw-result { margin: 10px 24px 20px; border-top: 1px solid #2a3750; }
.raw-result summary { padding: 14px 0; font-size: 11px; color: #a5b4c8; }
pre { overflow: auto; max-height: 360px; padding: 14px; border-radius: 8px; background: #0b1220; font: 11px/1.6 Consolas, monospace; color: #c1e1ed; }
.live-tag { color: #9de4e9; font-size: 9px; border: 1px solid #345366; border-radius: 20px; padding: 5px 8px; white-space: nowrap; }
.mascot-stage { background: #101827; border-radius: 10px; display: flex; justify-content: center; align-items: center; height: 192px; overflow: hidden; margin-bottom: 20px; }
.mascot-stage img { width: 100%; max-width: 245px; height: 180px; object-fit: contain; image-rendering: pixelated; }
.state-copy { min-height: 92px; }
.state-copy p { font-size: 11px; color: #a5b4c8; margin: 8px 0 0; }
.workflow { display: flex; align-items: center; gap: 8px; justify-content: space-between; border-top: 1px solid #2a3750; padding: 18px 0; margin-top: 14px; font-size: 10px; color: #9aaec5; }
.workflow i { font-style: normal; }
.workflow .active { color: #9ef2ec; background: #1a3844; border-radius: 4px; padding: 5px 9px; }
.response-box { padding: 15px; background: #0d1727; border: 1px solid #2a3750; border-radius: 9px; }
.response-box > div { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.response-box strong { font-size: 11px; }
.simulation-tag { font-size: 8px; color: #b7a9dc; letter-spacing: .5px; }
.response-box p { font-size: 10px; color: #a5b4c8; }
.secondary { width: 100%; padding: 10px; background: #1b2b40; border: 1px solid #40536d; border-radius: 6px; color: #e3ecf5; font-size: 11px; font-weight: 600; }
.secondary:hover:not(:disabled) { border-color: #7ec9d6; }
.quiet { color: #a5b4c8; font-size: 11px; margin-bottom: 0; }
.activity-list { list-style: none; padding: 0; margin: 0; }
.activity-list li { display: flex; gap: 12px; padding: 11px 0; border-bottom: 1px solid #26334a; }
.activity-list li:last-child { border-bottom: 0; padding-bottom: 0; }
.log-dot { display: block; width: 5px; height: 5px; border-radius: 50%; background: #7acdd9; margin-top: 7px; flex-shrink: 0; }
.activity-list p { font-size: 10px; margin: 0 0 4px; color: #c8d5e5; }
.activity-list time { font-size: 9px; color: #9aaec5; }
.rule-note { padding: 2px 8px; }
.rule-note h3 { font-size: 12px; margin-top: 10px; }
.rule-note p { font-size: 11px; color: #a5b4c8; }
footer { display: flex; justify-content: space-between; gap: 16px; margin-top: 32px; padding-top: 20px; border-top: 1px solid #253047; color: #9aaec5; font-size: 10px; }
.footer-dot { padding: 0 8px; color: #5c728c; }
.spinner { height: 12px; width: 12px; border: 2px solid #21616b; border-top-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 1050px) { .workspace { grid-template-columns: minmax(0, 1fr) 300px; gap: 18px; } .input-panel, .defense-panel, .activity-panel { padding: 18px; } .metric { padding: 16px; } }
@media (max-width: 820px) { .workspace { grid-template-columns: 1fr; } .side-column { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; } .rule-note { grid-column: 1 / -1; } .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } .page-heading { align-items: flex-start; } }
@media (max-width: 560px) { main { padding: 28px 16px 18px; } .topbar { padding: 16px; } .portfolio-tag { display: none; } .page-heading { flex-direction: column; gap: 18px; } .connection { width: 100%; } .metrics { gap: 10px; } .metric small { font-size: 9px; } .side-column { display: flex; } .scenario-grid { grid-template-columns: 1fr; } .panel-heading { align-items: flex-start; } .step-tag { display: none; } .scan-action { align-items: stretch; flex-direction: column; } footer { flex-direction: column; } .result-banner { flex-wrap: wrap; } .result-banner > span:last-child { width: 100%; margin-left: 16px; } }
@media (prefers-reduced-motion: reduce) { .mascot-stage { display: none; } .spinner { animation: none; } button { transition: none; } }
</style>
