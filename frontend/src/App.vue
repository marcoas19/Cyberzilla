
<script setup>
import { computed, ref } from 'vue'

// CYBERZILLA: ATOMIC DEFENSE SYSTEM
// Version 0.5 — Python API + Threat Evidence Viewer

const API_URL = 'http://127.0.0.1:8000'

const systemStatus = ref('MONITORING')
const mascotState = ref('monitoring')
const scanning = ref(false)
const threats = ref([])
const scanCount = ref(0)
const totalEvents = ref(0)
const errorMessage = ref('')

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
      return 'Threat response completed!'

    default:
      if (systemStatus.value === 'SCAN FAILED') {
        return 'Unable to complete the scan.'
      }

      return threats.value.some(
        threat => threat.status === 'DETECTED'
      )
        ? 'Suspicious activity detected!'
        : 'All systems secure.'
  }
})

const detectedThreats = computed(() => {
  return threats.value.filter(
    threat => threat.status === 'DETECTED'
  ).length
})

function delay(milliseconds) {
  return new Promise(resolve => {
    setTimeout(resolve, milliseconds)
  })
}

// Run the real Python detection engine
async function startScan() {
  if (scanning.value) return

  scanning.value = true
  mascotState.value = 'scanning'
  systemStatus.value = 'SCANNING'
  errorMessage.value = ''

  // Clear previous results before the new scan
  threats.value = []
  totalEvents.value = 0

  try {
    const response = await fetch(
      `${API_URL}/api/scan`,
      {
        method: 'POST'
      }
    )

    if (!response.ok) {
      throw new Error(
        `Cyberzilla API returned HTTP ${response.status}`
      )
    }

    const data = await response.json()

    if (!Array.isArray(data.threats)) {
      throw new Error(
        'Invalid API response: threats must be an array.'
      )
    }

    console.log(
      '[CYBERZILLA] Full Python API response:',
      data
    )

    // Keep Mothra visible long enough to enjoy the animation
    await delay(2500)

    // IMPORTANT:
    // Preserve the complete threat objects returned by Python.
    // This includes evidence, timestamps and descriptions.
    threats.value = data.threats.map(threat => ({
      ...threat,
      evidence: Array.isArray(threat.evidence)
        ? threat.evidence
        : []
    }))

    totalEvents.value = data.total_events ?? 0
    scanCount.value++

    mascotState.value = 'monitoring'

    systemStatus.value =
      threats.value.length > 0
        ? 'THREAT DETECTED'
        : 'MONITORING'

  } catch (error) {
    console.error(
      '[CYBERZILLA] Scan failed:',
      error
    )

    errorMessage.value =
      'Could not complete the scan. Check that the Python API is running on port 8000.'

    mascotState.value = 'monitoring'
    systemStatus.value = 'SCAN FAILED'

  } finally {
    scanning.value = false
  }
}

// Simulated defensive response.
// This does NOT block IP addresses or change firewall rules.

async function atomicBreath(threat) {
  if (
    scanning.value ||
    threat.status !== 'DETECTED'
  ) {
    return
  }

  scanning.value = true
  mascotState.value = 'atomic'
  systemStatus.value = 'ATOMIC BREATH'
  errorMessage.value = ''

  // Simulated defensive response.
  // No real IP addresses are blocked.
  await delay(2500)

  threat.status = 'NEUTRALIZED (SIMULATED)'
  threat.response = 'SIMULATED'

  // Check whether other alerts remain active.
  const remainingThreats = threats.value.filter(
    item => item.status === 'DETECTED'
  ).length

  if (remainingThreats > 0) {
    mascotState.value = 'monitoring'
    systemStatus.value = 'THREAT DETECTED'
  } else {
    mascotState.value = 'defeated'
    systemStatus.value = 'THREATS NEUTRALIZED (SIMULATED)'
  }

  scanning.value = false
}

function resetDashboard() {
  if (scanning.value) return

  threats.value = []
  totalEvents.value = 0
  mascotState.value = 'monitoring'
  systemStatus.value = 'MONITORING'
  errorMessage.value = ''
}

// Format API timestamps for easier reading
function formatTimestamp(timestamp) {
  if (!timestamp) return 'Not available'

  return timestamp.replace('T', ' ')
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

      <span
        class="status"
        :class="{
          'status-danger': systemStatus === 'THREAT DETECTED',
          'status-error': systemStatus === 'SCAN FAILED'
        }"
      >
        {{ systemStatus }}
      </span>
    </header>

    <!-- MASCOT / SCAN SECTION -->
    <section class="hero">

      <div class="mascot-container">
        <img
          :src="currentMascot"
          :class="['mascot-image', mascotState]"
          :alt="`Cyberzilla mascot: ${mascotState}`"
        />
      </div>

      <div class="hero-content">
        <h2>{{ currentMessage }}</h2>

        <p v-if="mascotState === 'scanning'">
          Analyzing authentication events with the
          Cyberzilla Python detection engine...
        </p>

        <p v-else-if="mascotState === 'atomic'">
          Executing simulated defensive response...
        </p>

        <p v-else-if="mascotState === 'defeated'">
          The simulated defensive response has completed.
          No real network changes were made.
        </p>

        <p v-else-if="systemStatus === 'SCAN FAILED'">
          The detection engine could not be reached.
        </p>

        <p v-else>
          Cyberzilla is ready to analyze sample
          authentication logs.
        </p>

        <div class="hero-actions">
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

        <p
          v-if="errorMessage"
          class="error-message"
          role="alert"
        >
          {{ errorMessage }}
        </p>
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
        <h3>EVENTS ANALYZED</h3>
        <strong>{{ totalEvents }}</strong>
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

      <div class="section-heading">
        <div>
          <h2>THREAT INTELLIGENCE</h2>
          <p>
            Detection results from the Python engine
          </p>
        </div>

        <span
          v-if="threats.length > 0"
          class="alert-count"
        >
          {{ detectedThreats }} ACTIVE
        </span>
      </div>

      <div
        v-if="threats.length === 0"
        class="empty"
      >
        No active alerts. Run a scan to analyze
        the sample authentication events.
      </div>

      <!-- THREAT CARDS -->
      <div
        v-for="(threat, threatIndex) in threats"
        :key="`${threat.rule_id}-${threat.source_ip}-${threatIndex}`"
        class="threat-card"
      >

        <div class="threat-header">
          <h3>{{ threat.rule_name }}</h3>

          <span
            class="severity"
            :class="`severity-${String(threat.severity).toLowerCase()}`"
          >
            {{ threat.severity }}
          </span>
        </div>

        <div class="threat-details">
          <p>
            <strong>Rule:</strong>
            {{ threat.rule_id }}
          </p>

          <p>
            <strong>Source IP:</strong>
            {{ threat.source_ip }}
          </p>

          <p>
            <strong>Failed attempts:</strong>
            {{ threat.attempts ?? 'N/A' }}
          </p>

          <p>
            <strong>Status:</strong>
            <span
              :class="{
                'status-neutralized':
                  threat.status === 'NEUTRALIZED (SIMULATED)'
              }"
            >
              {{ threat.status }}
            </span>
          </p>
        </div>

        <!-- EVIDENCE VIEWER -->
        <details class="evidence-panel">

          <summary>
            <span>🔍 VIEW EVIDENCE</span>

            <span class="evidence-count">
              {{ threat.evidence?.length ?? 0 }} events
            </span>
          </summary>

          <div class="evidence-content">

            <p class="evidence-description">
              {{
                threat.description ||
                'No detection description available.'
              }}
            </p>

            <div class="evidence-times">
              <p>
                <strong>First seen:</strong>
                {{ formatTimestamp(threat.first_seen) }}
              </p>

              <p>
                <strong>Last seen:</strong>
                {{ formatTimestamp(threat.last_seen) }}
              </p>
            </div>

            <div
              v-if="threat.evidence?.length"
              class="evidence-table-wrapper"
            >
              <table class="evidence-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Source IP</th>
                    <th>Username</th>
                    <th>Event Type</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="(event, eventIndex) in threat.evidence"
                    :key="eventIndex"
                  >
                    <td>
                      {{ formatTimestamp(event.timestamp) }}
                    </td>

                    <td>
                      {{ event.source_ip }}
                    </td>

                    <td>
                      {{ event.username }}
                    </td>

                    <td>
                      <span class="event-badge">
                        {{ event.event_type }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p
              v-else
              class="no-evidence"
            >
              No supporting events available.
            </p>

          </div>
        </details>
        <!-- END EVIDENCE VIEWER -->

        <!-- ATOMIC BREATH IS OUTSIDE <details> -->
        <button
          class="atomic-button"
          :disabled="
            scanning ||
            threat.status !== 'DETECTED'
          "
          @click="atomicBreath(threat)"
        >
          ☢️ ATOMIC BREATH
        </button>

      </div>
    </section>

    <!-- FOOTER -->
    <footer>
      CYBERZILLA v0.5 · ATOMIC DEFENSE SYSTEM
      <br />
      SAMPLE LOG ANALYSIS · SIMULATED DEFENSIVE RESPONSE
    </footer>

  </div>
</template>

<style>
/* GENERAL */

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #080f1d;
  color: #e8f4ff;
  font-family: Arial, Helvetica, sans-serif;
}

button {
  background: #1789d4;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s ease;
}

button:hover:not(:disabled) {
  background: #36b6ff;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dashboard {
  max-width: 1300px;
  margin: auto;
  padding: 30px;
}

/* HEADER */

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  border-bottom: 1px solid #27435c;
  padding-bottom: 20px;
}

.header h1 {
  color: #63d8ff;
  margin: 0 0 8px;
  letter-spacing: 2px;
}

.header p {
  color: #8baabe;
  letter-spacing: 3px;
  font-size: 12px;
  margin: 0;
}

.status {
  color: #68e7b0;
  background: #123a35;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: bold;
  text-align: center;
}

.status-danger {
  color: #ffaaaa;
  background: #512b35;
}

.status-error {
  color: #ffd1d1;
  background: #632b2b;
}

/* HERO / MASCOTS */

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

.hero-content {
  flex: 1;
}

.hero-content h2 {
  color: #6fe0ff;
  margin-top: 0;
}

.hero-content p {
  color: #d8eaf5;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.secondary {
  background: #304457;
}

.error-message {
  color: #ffaaaa !important;
  background: #512b35;
  padding: 12px;
  border-radius: 8px;
  margin-top: 20px;
}

/* MASCOT ANIMATIONS */

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

/* STATISTICS */

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  margin-top: 0;
}

.stat-card strong {
  font-size: 32px;
  color: #63d8ff;
}

.stat-card .small {
  font-size: 15px;
  overflow-wrap: anywhere;
}

/* THREAT INTELLIGENCE */

.alerts {
  background: #111f33;
  border-radius: 12px;
  padding: 25px;
  margin-top: 30px;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.section-heading h2 {
  margin: 0 0 8px;
}

.section-heading p {
  color: #8baabe;
  font-size: 13px;
  margin: 0;
}

.alert-count {
  background: #512b35;
  color: #ffaaaa;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: bold;
  white-space: nowrap;
}

.empty {
  padding: 30px;
  color: #8baabe;
  text-align: center;
}

.threat-card {
  background: #1a2c42;
  border-left: 4px solid #ff5959;
  padding: 25px;
  border-radius: 8px;
  margin-top: 15px;
}

.threat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.threat-header h3 {
  margin: 0;
}

.severity {
  background: #632b2b;
  color: #ff9999;
  padding: 7px 10px;
  border-radius: 5px;
  font-size: 13px;
  font-weight: bold;
}

.severity-medium {
  background: #58411d;
  color: #ffd17d;
}

.severity-low {
  background: #16443b;
  color: #89e6c1;
}

.threat-details {
  margin-top: 22px;
}

.threat-details p {
  margin: 12px 0;
  overflow-wrap: anywhere;
}

.threat-details strong {
  color: #b4d1e4;
}

.status-neutralized {
  color: #89e6c1;
}

/* EVIDENCE VIEWER */

.evidence-panel {
  margin-top: 24px;
  margin-bottom: 18px;
  border: 1px solid #34516d;
  border-radius: 10px;
  background: #101d2e;
  overflow: hidden;
}

.evidence-panel summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  color: #70deff;
  font-weight: bold;
  list-style: none;
}

.evidence-panel summary::-webkit-details-marker {
  display: none;
}

.evidence-panel summary:hover {
  background: #1b344c;
}

.evidence-panel[open] summary {
  border-bottom: 1px solid #34516d;
}

.evidence-count {
  color: #9eb7ca;
  font-size: 12px;
  white-space: nowrap;
}

.evidence-content {
  padding: 18px;
}

.evidence-description {
  color: #d8eaf5;
  line-height: 1.6;
  margin-top: 0;
}

.evidence-times {
  color: #a8c0d2;
  font-size: 13px;
  margin: 16px 0;
}

.evidence-times p {
  margin: 8px 0;
}

.evidence-table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.evidence-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
}

.evidence-table th,
.evidence-table td {
  padding: 12px;
  border-bottom: 1px solid #294057;
  white-space: nowrap;
}

.evidence-table th {
  color: #70deff;
  background: #172c42;
}

.evidence-table td {
  color: #dcecf7;
}

.evidence-table tbody tr:hover {
  background: #1b344c;
}

.event-badge {
  display: inline-block;
  padding: 5px 8px;
  border-radius: 5px;
  background: #512b35;
  color: #ffaaaa;
  font-size: 11px;
  font-weight: bold;
}

.no-evidence {
  color: #9eb7ca;
}

/* ATOMIC BREATH BUTTON */

.atomic-button {
  background: #087bb5;
  margin-top: 4px;
}

.atomic-button:hover:not(:disabled) {
  background: #00a7eb;
}

/* FOOTER */

footer {
  margin-top: 40px;
  text-align: center;
  color: #65839a;
  font-size: 12px;
  line-height: 2;
}

/* RESPONSIVE */

@media (max-width: 900px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 700px) {
  .dashboard {
    padding: 16px;
  }

  .header,
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero {
    padding: 24px;
    gap: 20px;
  }

  .mascot-container {
    width: 100%;
    min-width: 0;
  }

  .mascot-image {
    max-height: 260px;
  }

  .stats {
    grid-template-columns: 1fr;
  }

  .section-heading,
  .threat-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .alerts,
  .threat-card {
    padding: 18px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .mascot-image {
    animation: none !important;
  }
}
</style>