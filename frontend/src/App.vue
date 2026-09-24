
<script setup>
import { ref, computed } from 'vue'

// CYBERZILLA: ATOMIC DEFENSE SYSTEM
// Version 0.4 - Mascot Integration

const systemStatus = ref('MONITORING')
const mascotState = ref('monitoring')

const scanning = ref(false)
const threats = ref([])
const scanCount = ref(0)

const mascotImages = {
  monitoring: '/mascots/godzilla-monitoring.png',
  scanning: '/mascots/mothra-scanning.png',
  atomic: '/mascots/godzilla-atomic.png',
  defeated: '/mascots/destoroyah-defeated.png'
}

const currentMascot = computed(() => {
  return mascotImages[mascotState.value]
})

const currentMessage = computed(() => {
  switch (mascotState.value) {
    case 'scanning':
      return 'Mothra is scanning security events...'

    case 'atomic':
      return 'ATOMIC BREATH ACTIVATED!'

    case 'defeated':
      return 'Threat neutralized!'

    default:
      return threats.value.length > 0
        ? 'Suspicious activity detected!'
        : 'All systems secure.'
  }
})

function startScan() {
  if (scanning.value) return

  scanning.value = true
  mascotState.value = 'scanning'
  systemStatus.value = 'SCANNING'
  threats.value = []

  // Demo scan using simulated security events.
  // Python backend integration comes next.

  setTimeout(() => {
    scanning.value = false
    scanCount.value++

    threats.value = [
      {
        rule_id: 'CZ-001',
        source_ip: '192.0.2.10',
        rule_name: 'Repeated Failed Login Attempts',
        severity: 'HIGH',
        attempts: 5,
        status: 'DETECTED'
      }
    ]

    mascotState.value = 'monitoring'
async function startScan() {
  if (scanning.value) return

  scanning.value = true
  mascotState.value = 'scanning'
  systemStatus.value = 'SCANNING'
  threats.value = []

  try {
    // Send a scan request to our Python API
    const response = await fetch(
      'http://127.0.0.1:8000/api/scan',
      {
        method: 'POST'
      }
    )

    if (!response.ok) {
      throw new Error(
        `API returned status ${response.status}`
      )
    }

    // Read the real detection results
    const data = await response.json()

    // Keep Mothra visible for at least 2.5 seconds
    await new Promise(resolve =>
      setTimeout(resolve, 2500)
    )

    // Update the dashboard with Python results
    threats.value = data.threats
    scanCount.value++

    mascotState.value = 'monitoring'

    if (data.threats_detected > 0) {
      systemStatus.value = 'THREAT DETECTED'
    } else {
      systemStatus.value = 'MONITORING'
    }

    console.log(
      '[CYBERZILLA] Scan completed:',
      data
    )

  } catch (error) {
    console.error(
      '[CYBERZILLA] Scan failed:',
      error
    )

    systemStatus.value = 'SCAN FAILED'
    mascotState.value = 'monitoring'

    alert(
      'Cyberzilla could not connect to the Python API. ' +
      'Check that the backend is running.'
    )

  } finally {
    scanning.value = false
  }
}
    systemStatus.value = 'THREAT DETECTED'
  }, 2500)
}

function atomicBreath(threat) {
  if (scanning.value || threat.status !== 'DETECTED') {
    return
  }

  scanning.value = true
  mascotState.value = 'atomic'
  systemStatus.value = 'ATOMIC BREATH'

  // Simulated defensive response.
  // No real IP addresses are blocked.

  setTimeout(() => {
    threat.status = 'NEUTRALIZED (SIMULATED)'

    mascotState.value = 'defeated'
    systemStatus.value = 'THREAT NEUTRALIZED'
    scanning.value = false
  }, 2500)
}

function resetDashboard() {
  if (scanning.value) return

  threats.value = []
  mascotState.value = 'monitoring'
  systemStatus.value = 'MONITORING'
}
</script>

<template>
  <div class="dashboard">

    <!-- HEADER -->
    <header class="header">
      <div>
        <h1>CYBERZILLA</h1>
        <p>ATOMIC DEFENSE SYSTEM</p>
      </div>

      <span class="status">
        {{ systemStatus }}
      </span>
    </header>

    <!-- MASCOT SECTION -->
    <section class="hero">

      <div class="mascot-container">

        <img
          :src="currentMascot"
          :class="['mascot-image', mascotState]"
          alt="Cyberzilla security mascot"
        />

      </div>

      <div class="hero-content">

        <h2>{{ currentMessage }}</h2>

        <p v-if="mascotState === 'scanning'">
          Analyzing authentication events...
        </p>

        <p v-else-if="mascotState === 'atomic'">
          Executing simulated defensive response...
        </p>

        <p v-else-if="mascotState === 'defeated'">
          The simulated threat has been neutralized.
        </p>

        <p v-else>
          Cyberzilla is monitoring your environment.
        </p>

        <button
          @click="startScan"
          :disabled="scanning"
        >
          {{ scanning ? 'PROCESSING...' : 'START SCAN' }}
        </button>

        <button
          class="secondary"
          @click="resetDashboard"
          :disabled="scanning"
        >
          RESET
        </button>

      </div>
    </section>

    <!-- STATISTICS -->
    <section class="stats">

      <div class="stat-card">
        <h3>THREATS DETECTED</h3>
        <strong>{{ threats.length }}</strong>
      </div>

      <div class="stat-card">
        <h3>SCANS COMPLETED</h3>
        <strong>{{ scanCount }}</strong>
      </div>

      <div class="stat-card">
        <h3>SYSTEM STATUS</h3>
        <strong class="small">
          {{ systemStatus }}
        </strong>
      </div>

    </section>

    <!-- THREAT INTELLIGENCE -->
    <section class="alerts">

      <h2>THREAT INTELLIGENCE</h2>

      <div
        v-if="threats.length === 0"
        class="empty"
      >
        No active alerts.
      </div>

      <div
        v-for="threat in threats"
        :key="threat.rule_id"
        class="threat-card"
      >

        <div class="threat-header">
          <h3>{{ threat.rule_name }}</h3>

          <span class="severity">
            {{ threat.severity }}
          </span>
        </div>

        <p>Rule: {{ threat.rule_id }}</p>
        <p>Source IP: {{ threat.source_ip }}</p>
        <p>Failed attempts: {{ threat.attempts }}</p>
        <p>Status: {{ threat.status }}</p>

        <button
          class="atomic-button"
          :disabled="scanning || threat.status !== 'DETECTED'"
          @click="atomicBreath(threat)"
        >
          ☢️ ATOMIC BREATH
        </button>

      </div>

    </section>

    <footer>
      CYBERZILLA v0.4 · ATOMIC DEFENSE SYSTEM
      <br />
      DEMO MODE · SIMULATED SECURITY EVENTS
    </footer>

  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #080f1d;
  color: #e8f4ff;
  font-family: Arial, sans-serif;
}

button {
  background: #1789d4;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: bold;
  cursor: pointer;
  margin-right: 10px;
  margin-top: 15px;
}

button:hover:not(:disabled) {
  background: #36b6ff;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dashboard {
  max-width: 1200px;
  margin: auto;
  padding: 30px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #27435c;
  padding-bottom: 20px;
}

.header h1 {
  color: #63d8ff;
  margin-bottom: 5px;
}

.header p {
  color: #8baabe;
  letter-spacing: 3px;
}

.status {
  color: #68e7b0;
  background: #123a35;
  padding: 10px;
  border-radius: 8px;
  font-size: 12px;
}

.hero {
  display: flex;
  align-items: center;
  gap: 40px;
  background: #111f33;
  padding: 40px;
  border-radius: 15px;
  margin-top: 30px;
  min-height: 350px;
}

.mascot-container {
  width: 350px;
  min-width: 250px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.mascot-image {
  width: 100%;
  max-height: 320px;
  object-fit: contain;
  filter: drop-shadow(0 0 15px #1789d455);
}

.mascot-image.monitoring {
  animation: breathe 2s ease-in-out infinite alternate;
}

.mascot-image.scanning {
  animation: fly 1.2s ease-in-out infinite alternate;
}

.mascot-image.atomic {
  animation: atomicPulse 0.5s ease-in-out infinite alternate;
}

.mascot-image.defeated {
  animation: defeated 0.6s ease-out;
}

@keyframes breathe {
  from {
    transform: scale(1);
  }

  to {
    transform: scale(1.04);
  }
}

@keyframes fly {
  from {
    transform: translateY(10px);
  }

  to {
    transform: translateY(-15px);
  }
}

@keyframes atomicPulse {
  from {
    transform: scale(1);
    filter: drop-shadow(0 0 10px #1789d4);
  }

  to {
    transform: scale(1.08);
    filter: drop-shadow(0 0 30px #00d9ff);
  }
}

@keyframes defeated {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.hero h2 {
  color: #6fe0ff;
}

.secondary {
  background: #304457;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 30px;
}

.stat-card {
  background: #111f33;
  border-radius: 12px;
  padding: 25px;
}

.stat-card h3 {
  font-size: 12px;
  color: #8baabe;
}

.stat-card strong {
  font-size: 32px;
  color: #63d8ff;
}

.stat-card .small {
  font-size: 16px;
}

.alerts {
  background: #111f33;
  border-radius: 12px;
  padding: 25px;
  margin-top: 30px;
}

.empty {
  padding: 30px;
  color: #8baabe;
  text-align: center;
}

.threat-card {
  background: #1a2c42;
  border-left: 4px solid #ff5959;
  padding: 20px;
  border-radius: 8px;
}

.threat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.severity {
  background: #632b2b;
  color: #ff9999;
  padding: 7px;
  border-radius: 5px;
}

.atomic-button {
  background: #087bb5;
}

footer {
  margin-top: 40px;
  text-align: center;
  color: #65839a;
  font-size: 12px;
  line-height: 2;
}

@media (max-width: 700px) {
  .header,
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .mascot-container {
    width: 100%;
    min-width: 0;
  }

  .stats {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .mascot-image {
    animation: none !important;
  }
}
</style>