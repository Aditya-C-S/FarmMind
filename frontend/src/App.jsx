import { useState, useEffect } from "react";
import {
  Home, Sprout, Bug, FileText, Settings as SettingsIcon,
  CloudRain, TrendingDown, RefreshCw,
  Check, ChevronRight, Upload, Package,
} from "lucide-react";

// ---------------------------------------------------------------------------
// Design tokens.
// ---------------------------------------------------------------------------
const STYLE = `
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

.fd-app {
  --bg: #F6F8F4;
  --card: #FFFFFF;
  --border: #E3E8DF;
  --text: #202A22;
  --text-dim: #6E7A6F;
  --green: #3F8F5C;
  --green-soft: #E7F3EA;
  --amber: #C98A28;
  --amber-soft: #FBF0DC;
  --red: #C4483F;
  --red-soft: #FBE9E7;
  --blue: #3E7699;
  --blue-soft: #E7F0F5;
  --sidebar-bg: #16201A;
  --sidebar-text: #B9C4B4;
  --sidebar-active: #2A362C;
  --serif: 'Fraunces', Georgia, serif;
  --sans: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
  --mono: 'IBM Plex Mono', ui-monospace, monospace;

  display: flex;
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  border-radius: 14px;
  overflow: hidden;
  width: 100%;
  min-height: 100vh;
}
.fd-app * { box-sizing: border-box; }

/* --- Sidebar --- */
.fd-sidebar {
  width: 180px;
  flex-shrink: 0;
  align-self: stretch;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.fd-logo {
  font-family: var(--serif);
  font-weight: 600;
  font-size: 18px;
  color: #EAE6D9;
  padding: 4px 10px 18px 10px;
}
.fd-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 500;
  color: var(--sidebar-text);
  background: none;
  border: none;
  border-radius: 7px;
  padding: 9px 10px;
  cursor: pointer;
  text-align: left;
  width: 100%;
}
.fd-nav-item svg { width: 16px; height: 16px; flex-shrink: 0; }
.fd-nav-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
.fd-nav-item.active { background: var(--sidebar-active); color: #fff; }
.fd-nav-item:focus-visible { outline: 2px solid var(--green); outline-offset: 1px; }

/* --- Main --- */
.fd-main { flex: 1; padding: 26px 30px; overflow-y: auto; }

.fd-topbar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; gap: 16px; flex-wrap: wrap; }
.fd-crop-name { font-family: var(--serif); font-weight: 600; font-size: 26px; margin: 0 0 3px 0; }
.fd-crop-sub { color: var(--text-dim); font-size: 13px; margin: 0; }

.fd-crop-select {
  font-family: var(--serif); font-weight: 600; font-size: 26px;
  color: var(--text); background: transparent; border: none;
  padding: 0; margin: 0 0 3px 0; cursor: pointer; appearance: none;
  max-width: 420px;
}
.fd-crop-select:focus-visible { outline: 2px solid var(--green); outline-offset: 2px; }

/* --- Activity logger --- */
.fd-quick-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.fd-quick-btn {
  font-size: 12px; font-weight: 500; color: var(--text);
  background: var(--bg); border: 1px solid var(--border); border-radius: 20px;
  padding: 7px 13px; cursor: pointer;
}
.fd-quick-btn:hover { border-color: var(--green); }
.fd-quick-btn.selected { background: var(--green-soft); border-color: var(--green); color: var(--green); }
.fd-log-input {
  width: 100%; padding: 9px 11px; border: 1px solid var(--border); border-radius: 7px;
  font-family: var(--sans); font-size: 13px; background: var(--bg); color: var(--text);
  margin-bottom: 8px;
}
.fd-log-input:focus-visible { outline: 2px solid var(--green); outline-offset: 1px; }
.fd-log-submit {
  background: var(--green); color: #fff; border: none; border-radius: 7px;
  padding: 8px 15px; font-size: 13px; font-weight: 500; cursor: pointer;
}
.fd-log-submit:hover { background: #357a4d; }
.fd-log-submit:disabled { background: var(--border); color: var(--text-dim); cursor: not-allowed; }
.fd-log-note { font-size: 12px; margin-top: 8px; }
.fd-log-note.success { color: var(--green); }
.fd-log-note.error { color: var(--red); }
.fd-activity-divider { border-top: 1px solid var(--border); margin: 16px 0; }

.fd-status-pill {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 13px; font-weight: 600;
  padding: 8px 14px; border-radius: 20px;
}
.fd-status-pill.healthy { background: var(--green-soft); color: var(--green); }
.fd-status-pill.attention { background: var(--amber-soft); color: var(--amber); }
.fd-status-pill.immediate { background: var(--red-soft); color: var(--red); }
.fd-dot { width: 8px; height: 8px; border-radius: 50%; }
.fd-dot.healthy { background: var(--green); }
.fd-dot.attention { background: var(--amber); }
.fd-dot.immediate { background: var(--red); }

.fd-refresh-btn {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-family: var(--mono); color: var(--text-dim);
  background: var(--card); border: 1px solid var(--border); border-radius: 7px;
  padding: 7px 11px; cursor: pointer;
}
.fd-refresh-btn:hover { color: var(--text); border-color: var(--text-dim); }
.fd-refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.fd-refresh-btn svg { width: 13px; height: 13px; }
.fd-spin { animation: fd-spin 0.9s linear infinite; }
@keyframes fd-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .fd-spin { animation: none; } }

/* --- Summary card row --- */
.fd-summary-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
@media (max-width: 860px) { .fd-summary-row { grid-template-columns: repeat(2, 1fr); } }
.fd-summary-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 14px 16px;
}
.fd-summary-icon { width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
.fd-summary-icon svg { width: 15px; height: 15px; }
.fd-summary-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 2px; }
.fd-summary-main { font-family: var(--serif); font-weight: 600; font-size: 17px; color: var(--text); }
.fd-summary-sub { font-size: 12px; color: var(--text-dim); margin-top: 1px; }
.fd-summary-card.muted { opacity: 0.6; }

/* --- Section card shell --- */
.fd-section {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
  padding: 20px; margin-bottom: 16px;
}
.fd-section-title {
  font-family: var(--serif); font-weight: 600; font-size: 17px;
  margin: 0 0 14px 0; display: flex; align-items: center; justify-content: space-between;
}
.fd-empty { color: var(--text-dim); font-size: 13px; padding: 8px 0; }
.fd-error-note { color: var(--red); font-size: 12px; padding: 6px 0; }

/* ---------- Weather Intelligence ---------- */

.fd-weather-grid {display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px;}

.fd-weather-card {background: white; border: 1px solid var(--border); border-radius: 16px; padding: 18px; text-align: center; transition: .2s;}

.fd-weather-card:hover {transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,.08);}

.fd-weather-day {font-weight: 700; color: var(--text);}
.fd-weather-temp {font-size: 26px; font-weight: 700; color: var(--blue);}
.fd-weather-row {margin-top: 8px; font-size: 14px; color: var(--text-dim);}

/* --- Recommendations (dominant card) --- */
.fd-rec-item {
  display: flex; align-items: center; gap: 14px;
  border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 16px; margin-bottom: 10px;
}
.fd-rec-rank { font-family: var(--serif); font-size: 20px; color: var(--text-dim); width: 26px; }
.fd-rec-body { flex: 1; }
.fd-rec-task { font-size: 15px; font-weight: 500; margin-bottom: 2px; }
.fd-rec-detail { font-size: 12px; color: var(--text-dim); }
.fd-rec-detail button {
  background: none; border: none; color: var(--blue); font-size: 12px;
  cursor: pointer; padding: 0; font-family: var(--sans); display: inline-flex; align-items: center; gap: 2px;
}
.fd-rec-detail svg { width: 11px; height: 11px; }
.fd-rec-priority { text-align: right; }
.fd-rec-pct { font-family: var(--mono); font-weight: 600; font-size: 15px; }
.fd-rec-expand {
  margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border);
  display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; color: var(--text-dim);
}
.fd-rec-expand b { color: var(--text); font-weight: 500; }

/* --- Crop timeline (signature element) --- */
.fd-timeline { display: flex; align-items: flex-start; padding: 6px 4px 0 4px; }
.fd-tl-stage { flex: 1; display: flex; flex-direction: column; align-items: center; text-align: center; cursor: pointer; background: none; border: none; padding: 0; }
.fd-tl-node { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; border: 2px solid var(--border); background: var(--card); }
.fd-tl-node svg { width: 13px; height: 13px; }
.fd-tl-node.done { background: var(--green); border-color: var(--green); }
.fd-tl-node.done svg { color: #fff; }
.fd-tl-node.current { border-color: var(--green); background: var(--green-soft); }
.fd-tl-dot-current { width: 9px; height: 9px; border-radius: 50%; background: var(--green); }
.fd-tl-line { flex: 1; height: 2px; background: var(--border); margin-top: 13px; }
.fd-tl-line.done { background: var(--green); }
.fd-tl-label { font-size: 12px; font-weight: 500; color: var(--text); }
.fd-tl-label.current { color: var(--green); font-weight: 600; }
.fd-tl-label.muted { color: var(--text-dim); }
.fd-tl-detail {
  margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--border);
  font-size: 13px; color: var(--text-dim);
}

/* --- Farm status panel (Context Fusion, unnamed) --- */
.fd-status-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
@media (max-width: 860px) { .fd-status-grid { grid-template-columns: repeat(2, 1fr); } }
.fd-status-item-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 4px; }
.fd-status-item-val { font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 6px; }

/* --- Activity history --- */
.fd-activity-item { display: flex; gap: 12px; padding: 9px 0; border-bottom: 1px solid var(--border); }
.fd-activity-item:last-child { border-bottom: none; }
.fd-activity-when { font-family: var(--mono); font-size: 11px; color: var(--text-dim); width: 84px; flex-shrink: 0; padding-top: 2px; }
.fd-activity-what { font-size: 13px; display: flex; align-items: center; gap: 6px; }
.fd-activity-what svg { width: 13px; height: 13px; color: var(--green); }

/* --- Today's Guidance card --- */
.fd-guidance-section { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.fd-guidance-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 8px; }
.fd-guidance-list { list-style: none; margin: 0; padding: 0; }
.fd-guidance-list li { font-size: 13px; color: var(--text); padding: 4px 0 4px 18px; position: relative; }
.fd-guidance-list li::before { content: "–"; position: absolute; left: 0; color: var(--text-dim); }
.fd-spoilage-item { font-size: 13px; color: var(--text); padding: 4px 0 4px 18px; position: relative; }
.fd-spoilage-item::before { content: "!"; position: absolute; left: 0; color: var(--amber); font-weight: 600; font-size: 11px; top: 5px; }

/* --- Settings page --- */
.fd-settings-field { margin-bottom: 14px; max-width: 420px; }
.fd-settings-field label { display: block; font-size: 12px; font-weight: 500; color: var(--text-dim); margin-bottom: 5px; }
.fd-settings-field input {
  width: 100%; padding: 9px 11px; border: 1px solid var(--border); border-radius: 7px;
  font-family: var(--mono); font-size: 13px; background: var(--bg); color: var(--text);
}
.fd-settings-field input:focus-visible { outline: 2px solid var(--green); outline-offset: 1px; }

/* --- Coming soon / placeholder page --- */
.fd-soon { border: 1px dashed var(--border); border-radius: 14px; padding: 50px 24px; text-align: center; color: var(--text-dim); }
.fd-soon-title { font-family: var(--serif); color: var(--text); font-size: 18px; margin-bottom: 6px; }

/* --- Upload affordance --- */
.fd-upload-btn {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-dim); background: var(--bg);
  border: 1px dashed var(--border); border-radius: 7px; padding: 7px 12px;
  cursor: not-allowed; opacity: 0.7;
}
.fd-upload-btn svg { width: 13px; height: 13px; }

/* ── Storage Status Card ─────────────────────────────────────────────────── */
/* Shelf life progress bar */
.fd-shelf-bar {
  height: 6px; border-radius: 3px;
  background: var(--border); overflow: hidden;
  margin: 6px 0 3px;
}
.fd-shelf-fill { height: 100%; border-radius: 3px; transition: width 0.4s ease; }
.fd-shelf-fill.good   { background: var(--green); }
.fd-shelf-fill.medium { background: var(--amber); }
.fd-shelf-fill.low    { background: var(--red); }

/* Risk badge */
.fd-risk-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 9px; border-radius: 20px;
  font-size: 12px; font-weight: 600;
}
.fd-risk-badge.low      { background: var(--green-soft); color: var(--green); }
.fd-risk-badge.moderate { background: var(--amber-soft); color: var(--amber); }
.fd-risk-badge.high     { background: var(--red-soft);   color: var(--red); }

/* Storage card data grid */
.fd-storage-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}
@media (max-width: 600px) { .fd-storage-grid { grid-template-columns: 1fr; } }
.fd-storage-cell { background: var(--bg); border-radius: 8px; padding: 11px 13px; }
.fd-storage-cell-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-dim); margin-bottom: 3px; }
.fd-storage-cell-val { font-size: 14px; font-weight: 600; color: var(--text); }

/* Divider inside card */
.fd-card-divider { border: none; border-top: 1px solid var(--border); margin: 14px 0; }

/* Condition check log form inside card */
.fd-condition-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.fd-condition-row input,
.fd-condition-row select {
  flex: 1; min-width: 100px;
  padding: 8px 10px; border: 1px solid var(--border); border-radius: 7px;
  font-family: var(--sans); font-size: 13px;
  background: var(--bg); color: var(--text);
}
.fd-condition-row input:focus-visible,
.fd-condition-row select:focus-visible { outline: 2px solid var(--green); outline-offset: 1px; }

/* Spoilage sign list */
.fd-warning-item {
  font-size: 13px; color: var(--text);
  padding: 4px 0 4px 18px; position: relative;
}
.fd-warning-item::before {
  content: "!"; position: absolute; left: 0; top: 5px;
  color: var(--amber); font-weight: 700; font-size: 11px;
}
`;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function dig(obj, ...paths) {
  for (const path of paths) {
    let cur = obj;
    let ok = true;
    for (const key of path) {
      if (cur && typeof cur === "object" && key in cur) cur = cur[key];
      else { ok = false; break; }
    }
    if (ok && cur !== undefined && cur !== null) return cur;
  }
  return null;
}

function deepFind(obj, key) {
  if (!obj || typeof obj !== "object") return undefined;
  if (Array.isArray(obj)) {
    for (const item of obj) { const r = deepFind(item, key); if (r !== undefined) return r; }
    return undefined;
  }
  if (key in obj) return obj[key];
  for (const k of Object.keys(obj)) {
    const r = deepFind(obj[k], key);
    if (r !== undefined) return r;
  }
  return undefined;
}

function titleCase(s) {
  if (!s) return s;
  return String(s).replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function severityTier(level) {
  if (!level) return "low";
  const l = String(level).toLowerCase();
  if (["low", "mild"].includes(l)) return "low";
  if (["medium", "moderate"].includes(l)) return "medium";
  return "high";
}

const TOMATO_STAGES = ["nursery", "vegetative", "flowering", "fruiting", "harvest"];
const RICE_STAGES = ["nursery", "transplanting", "tillering", "panicle_initiation", "booting_flowering", "grain_filling", "harvest"];
const RICE_ONLY = new Set(["transplanting", "tillering", "panicle_initiation", "booting_flowering", "grain_filling"]);

function guessCropType(payload) {
  const explicit = deepFind(payload, "crop_type") || deepFind(payload, "crop");
  if (explicit) return String(explicit).toLowerCase();
  const stageId = dig(payload, ["current_stage", "stage_id"]);
  if (stageId && RICE_ONLY.has(String(stageId).toLowerCase())) return "rice";
  return "tomato";
}

function weatherInsight(triggers) {
  const map = {
    high_humidity: "High humidity increases disease risk.",
    heavy_rainfall: "Heavy rain may affect drainage — check low-lying rows.",
    high_temperature: "Heat stress risk — crops may need extra water.",
    drought: "No meaningful rain in over a week — irrigation is due.",
  };
  for (const t of triggers) if (map[t]) return map[t];
  return "Conditions look stable for this stage.";
}

function timeAgo(dateString) {
  if (!dateString) return "";
  const then = new Date(dateString);
  if (isNaN(then)) return dateString;
  const days = Math.floor((Date.now() - then.getTime()) / (1000 * 60 * 60 * 24));
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  return `${days} days ago`;
}

function formatDateTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString("en-IN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

// ---------------------------------------------------------------------------
// Small shared bits
// ---------------------------------------------------------------------------
function StatusPill({ tier }) {
  const labels = { healthy: "Healthy", attention: "Needs Attention", immediate: "Immediate Action" };
  return (
    <span className={`fd-status-pill ${tier}`}>
      <span className={`fd-dot ${tier}`} />
      {labels[tier]}
    </span>
  );
}

function SummaryCard({ icon, iconBg, label, main, sub, muted }) {
  return (
    <div className={`fd-summary-card ${muted ? "muted" : ""}`}>
      <div className="fd-summary-icon" style={{ background: iconBg }}>{icon}</div>
      <div className="fd-summary-label">{label}</div>
      <div className="fd-summary-main">{main}</div>
      {sub && <div className="fd-summary-sub">{sub}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Crop timeline
// ---------------------------------------------------------------------------
function CropTimeline({ workflow, cropType }) {
  const [expanded, setExpanded] = useState(null);
  const stages = cropType === "rice" ? RICE_STAGES : TOMATO_STAGES;
  const currentStageId = String(dig(workflow, ["current_stage", "stage_id"]) || "").toLowerCase();
  const currentIndex = stages.indexOf(currentStageId);

  const currentStage = dig(workflow, ["current_stage"]);
  const pests = dig(currentStage, ["common_pests"], ["pests"]) || [];
  const diseases = dig(currentStage, ["common_diseases"], ["diseases"]) || [];

  return (
    <div>
      <div className="fd-timeline">
        {stages.map((stageId, i) => {
          const done = currentIndex >= 0 && i < currentIndex;
          const isCurrent = i === currentIndex;
          return (
            <div key={stageId} style={{ display: "flex", alignItems: "center", flex: i === stages.length - 1 ? "0 0 auto" : 1 }}>
              <button
                className="fd-tl-stage"
                onClick={() => setExpanded(expanded === stageId ? null : stageId)}
                style={{ width: 90 }}
              >
                <div className={`fd-tl-node ${done ? "done" : ""} ${isCurrent ? "current" : ""}`}>
                  {done ? <Check /> : isCurrent ? <span className="fd-tl-dot-current" /> : null}
                </div>
                <span className={`fd-tl-label ${isCurrent ? "current" : done ? "" : "muted"}`}>
                  {titleCase(stageId)}
                </span>
              </button>
              {i < stages.length - 1 && <div className={`fd-tl-line ${done ? "done" : ""}`} />}
            </div>
          );
        })}
      </div>
      {expanded && (
        <div className="fd-tl-detail">
          {expanded === currentStageId ? (
            <div>
              <div style={{ marginBottom: 6 }}>
                <b style={{ color: "var(--text)" }}>Common pests: </b>
                {pests.length ? pests.map((p) => titleCase(p.name || p.pest_id)).join(", ") : "none reported"}
              </div>
              <div>
                <b style={{ color: "var(--text)" }}>Common diseases: </b>
                {diseases.length ? diseases.map((d) => titleCase(d.name || d.disease_id)).join(", ") : "none reported"}
              </div>
            </div>
          ) : (
            "Details for this stage aren't loaded until the crop reaches it."
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Weather Intelligence
// ---------------------------------------------------------------------------
function WeatherIntelligenceCard({ forecast }) {

  if (!forecast || forecast.length === 0) {
    return null;
  }

  const weatherIcon = (rainfall) => {
    if (rainfall >= 10) return "🌧️";
    if (rainfall >= 2) return "🌦️";
    if (rainfall > 0) return "☁️";
    return "☀️";
  };

  const dayName = (date) =>
    new Date(date).toLocaleDateString("en-US", {
      weekday: "short",
    });

  return (
    <div className="fd-section">

      <div className="fd-section-title">
        🌦 Weather Intelligence
      </div>

      <div className="fd-weather-grid">

        {forecast.map((day) => (

          <div
            key={day.date}
            className="fd-weather-card"
          >

            <div className="fd-weather-day">
              {dayName(day.date)}
            </div>

            <div
              style={{
                fontSize: 34,
                margin: "10px 0",
              }}
            >
              {weatherIcon(day.rainfall)}
            </div>

            <div className="fd-weather-temp">
              {Math.round(day.temperature_max)}°
            </div>

            <div className="fd-weather-row">
              💧 {day.humidity}%
            </div>

            <div className="fd-weather-row">
              🌧 {day.rainfall} mm
            </div>

            <div className="fd-weather-row">
              💨 {day.wind_speed} km/h
            </div>

          </div>

        ))}

      </div>

    </div>
  );
}

// ---------------------------------------------------------------------------
// Today's Recommendations
// ---------------------------------------------------------------------------
function priorityTier(score) {
  if (score >= 0.75) return "immediate";
  if (score >= 0.45) return "attention";
  return "healthy";
}

function RecommendationsCard({ actions, loading, error }) {
  const [openIndex, setOpenIndex] = useState(null);

  return (
    <div className="fd-section">
      <div className="fd-section-title">Today's Recommendations</div>
      {loading && <div className="fd-empty">Working out what matters most today…</div>}
      {error && <div className="fd-error-note">{error}</div>}
      {!loading && !error && (!actions || actions.length === 0) && (
        <div className="fd-empty">Nothing urgent right now — the field looks clear.</div>
      )}
      {!loading && !error && actions && actions.map((action, i) => {
        const pct = Math.round((action.score || 0) * 100);
        const tier = priorityTier(action.score || 0);
        const open = openIndex === i;
        return (
          <div className="fd-rec-item" key={i}>
            <div className="fd-rec-rank">{i + 1}</div>
            <div className="fd-rec-body">
              <div className="fd-rec-task">{action.task}</div>
              <div className="fd-rec-detail">
                <button onClick={() => setOpenIndex(open ? null : i)}>
                  Factors considered <ChevronRight style={{ transform: open ? "rotate(90deg)" : "none" }} />
                </button>
              </div>
              {open && (
                <div className="fd-rec-expand">
                  <span><b>Urgency</b> {Math.round((action.urgency || 0) * 100)}%</span>
                  <span><b>Risk</b> {Math.round((action.risk || 0) * 100)}%</span>
                  <span><b>Economic loss</b> {action.loss ? `₹${Math.round(action.loss).toLocaleString("en-IN")}` : "None reported"}</span>
                  <span><b>Effort</b> {Math.round((action.effort || 0) * 100)}%</span>
                </div>
              )}
            </div>
            <div className="fd-rec-priority">
              <div className="fd-rec-pct" style={{ color: `var(--${tier === "healthy" ? "green" : tier === "attention" ? "amber" : "red"})` }}>
                {pct}%
              </div>
              <span className={`fd-dot ${tier}`} style={{ display: "inline-block" }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Today's Guidance
// ---------------------------------------------------------------------------
function GuidanceCard({ workflow, guidance }) {
  const workFlowGuidance = dig(workflow, ["guidance"]);
  const stageId = String(dig(workflow, ["current_stage", "stage_id"]) || "").toLowerCase();
  const stageName = dig(workflow, ["current_stage", "stage"]) || titleCase(stageId) || "Current Stage";
  const isHarvest = stageId === "harvest";

  if (!workFlowGuidance) return null;

  const tasks = workFlowGuidance.tasks || [];
  const irrigation = workFlowGuidance.irrigation || {};
  const monitoring = workFlowGuidance.monitoring || [];
  const bestPractices = workFlowGuidance.best_practices || [];
  const postHarvest = workFlowGuidance.post_harvest || null;
  const spoilageChecks = workFlowGuidance.spoilage_checks || null;
  const maturityIndicators = workFlowGuidance.maturity_indicators || [];
  const irrigationPractices = irrigation.practice || [];
  const irrigationNote = irrigation.critical === false ? "Not required at this stage." : null;
  const liveIrrigation = guidance?.irrigation;
  const diseasePrevention = guidance?.disease_prevention || [];
  const diseaseAlerts = workFlowGuidance.disease_alerts || [];

  console.log(workFlowGuidance.disease_alerts);

  return (
    <div className="fd-section">
      <div className="fd-section-title">Today's Guidance — {stageName}</div>

      {tasks.length > 0 && (
        <div className="fd-guidance-section" style={{ marginTop: 0, paddingTop: 0, borderTop: "none" }}>
          <div className="fd-guidance-label">Tasks</div>
          <ul className="fd-guidance-list">
            {tasks.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
        </div>
      )}

      {monitoring.length > 0 && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">What to Monitor</div>
          <ul className="fd-guidance-list">
            {monitoring.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </div>
      )}

      {(irrigationPractices.length > 0 || irrigationNote) && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">Irrigation</div>
          <ul className="fd-guidance-list">
            {irrigationNote && <li>{irrigationNote}</li>}
            {irrigationPractices.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
      )}

      {liveIrrigation && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">
            Today's Irrigation Advice
          </div>

          <div style={{ fontWeight: 600 }}>
            {liveIrrigation.level}
          </div>

          <div
            style={{
              fontSize: 13,
              color: "var(--text-dim)",
              marginTop: 4
            }}
          >
            {liveIrrigation.reason}
          </div>
        </div>
      )}

      {diseasePrevention.length > 0 && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">
            Disease Prevention
          </div>

          {diseasePrevention.map((disease, i) => (
            <div key={i} style={{ marginBottom: 14 }}>

              <div style={{ fontWeight: 600 }}>
                {disease.disease}
              </div>

              <div style={{ fontSize: 13, color: "var(--text-dim)", marginBottom: 6 }}>
                Risk: {disease.risk}
              </div>

              <div style={{ fontSize: 13, marginBottom: 8 }}>
                {disease.reason}
              </div>

              <ul className="fd-guidance-list">
                {disease.recommendations.map((r, j) => (
                  <li key={j}>{r}</li>
                ))}
              </ul>

            </div>
          ))}
        </div>
      )}

      {diseaseAlerts.length > 0 && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">
            Disease Alerts & Treatment
          </div>

          {diseaseAlerts.map((disease, i) => (
            <div key={i} style={{ marginBottom: 18 }}>

              <div style={{ fontWeight: 600 }}>
                {disease.common_name}
              </div>

              <div
                style={{
                  fontSize: 13,
                  color: "var(--text-dim)",
                  marginBottom: 8
                }}
              >
                Risk: {disease.risk_level}
              </div>

              {disease.treatment ? (
                <>
                  <div><strong>Recommended pesticide:</strong></div>
                  <div>{disease.treatment.primary}</div>

                  <div style={{ marginTop: 6 }}>
                    <strong>Dose:</strong>
                  </div>
                  <div>{disease.treatment.dose}</div>

                  <div style={{ marginTop: 6 }}>
                    <strong>Application:</strong>
                  </div>
                  <div>{disease.treatment.method}</div>

                  <div style={{ marginTop: 6 }}>
                    <strong>Frequency:</strong>
                  </div>
                  <div>{disease.treatment.frequency}</div>

                  {disease.treatment.alternate && (
                    <>
                      <div style={{ marginTop: 6 }}>
                        <strong>Alternate:</strong>
                      </div>
                      <div>{disease.treatment.alternate}</div>
                    </>
                  )}
                </>
              ) : (
                <div style={{ color: "var(--text-dim)" }}>
                  No treatment recommendation available.
                </div>
              )}

            </div>
          ))}
        </div>
      )}

      {bestPractices.length > 0 && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">Best Practices</div>
          <ul className="fd-guidance-list">
            {bestPractices.map((b, i) => <li key={i}>{b}</li>)}
          </ul>
        </div>
      )}

      {isHarvest && maturityIndicators.length > 0 && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">Maturity Indicators</div>
          <ul className="fd-guidance-list">
            {maturityIndicators.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </div>
      )}

      {isHarvest && postHarvest && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label">Post-Harvest Steps</div>
          {Object.entries(postHarvest).map(([step, data]) => (
            <div key={step} style={{ marginBottom: 10 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text)", marginBottom: 4 }}>
                {titleCase(step)}
              </div>
              <ul className="fd-guidance-list">
                {(data.recommended_practices || data.storage_methods || []).map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
                {step === "storage" && data.safe_storage_conditions && (
                  data.safe_storage_conditions.map((c, i) => <li key={`sc-${i}`}>{c}</li>)
                )}
                {step === "storage" && data.recommended_temperature_celsius && (
                  <li>Store at {data.recommended_temperature_celsius}°C, {data.relative_humidity_percent}% RH</li>
                )}
                {step === "drying" && data.target_moisture_percent && (
                  <li>
                    Target: grain ≤{data.target_moisture_percent.grain}%
                    {data.target_moisture_percent.seed ? `, seed ≤${data.target_moisture_percent.seed}%` : ""}
                  </li>
                )}
              </ul>
            </div>
          ))}
        </div>
      )}

      {isHarvest && spoilageChecks && (
        <div className="fd-guidance-section">
          <div className="fd-guidance-label" style={{ color: "var(--amber)" }}>
            Spoilage Checks · {spoilageChecks.inspection_frequency}
          </div>
          {spoilageChecks.description && (
            <div style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 8 }}>
              {spoilageChecks.description}
            </div>
          )}
          <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text)", marginBottom: 4 }}>Warning signs</div>
          <div>
            {(spoilageChecks.risk_indicators || []).map((r, i) => (
              <div key={i} className="fd-spoilage-item">{r}</div>
            ))}
          </div>
          {(spoilageChecks.corrective_actions || []).length > 0 && (
            <>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text)", margin: "10px 0 4px" }}>If you find a problem</div>
              <ul className="fd-guidance-list">
                {spoilageChecks.corrective_actions.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Activity Logger
// ---------------------------------------------------------------------------
const QUICK_ACTIVITIES = [
  "Irrigated the field.",
  "Applied fertilizer.",
  "Sprayed pesticide.",
  "Controlled weeds.",
  "Inspected the crop.",
];

function ActivityLogger({ baseUrl, cropId, onLogged }) {
  const [text, setText] = useState("");
  const [logging, setLogging] = useState(false);
  const [note, setNote] = useState(null);

  async function submit() {
    if (!text.trim()) {
      setNote({ type: "error", message: "Describe what you did before logging it." });
      return;
    }
    setLogging(true);
    setNote(null);
    try {
      const res = await fetch(`${baseUrl}/activities`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          crop_id: cropId,
          activity_type: text.trim(),
          activity_date: new Date().toISOString().slice(0, 10),
        }),
      });
      if (!res.ok) throw new Error(`Logging failed (${res.status}) — check the real activity route matches this one.`);
      setText("");
      setNote({ type: "success", message: "Logged. Refreshing today's recommendations…" });
      await onLogged();
    } catch (e) {
      setNote({
        type: "error",
        message: e instanceof TypeError ? `Couldn't reach ${baseUrl} to log this — is the backend running?` : e.message,
      });
    } finally {
      setLogging(false);
    }
  }

  return (
    <div>
      <div className="fd-quick-row">
        {QUICK_ACTIVITIES.map((activity) => (
          <button
            key={activity}
            className={`fd-quick-btn ${text === activity ? "selected" : ""}`}
            onClick={() => setText(activity)}
            type="button"
          >
            {activity.replace(/\.$/, "")}
          </button>
        ))}
      </div>
      <input
        className="fd-log-input"
        placeholder="Or describe what you did today…"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button className="fd-log-submit" onClick={submit} disabled={logging}>
        {logging ? "Logging…" : "Log today's activity"}
      </button>
      {note && <div className={`fd-log-note ${note.type}`}>{note.message}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// ── Storage Status Card ──────────────────────────────────────────────────────
//
// One API call: GET /post-harvest/{crop_id}
// The backend returns harvest_record + latest storage log + engine output
// in a single response. The card renders all three sections from that.
// ---------------------------------------------------------------------------

function shelfTier(pct) {
  if (pct > 50) return "good";
  if (pct > 20) return "medium";
  return "low";
}

function riskColor(level) {
  if (level === "low") return "var(--green)";
  if (level === "moderate") return "var(--amber)";
  return "var(--red)";
}

// Small sub-component: one labelled data cell in the storage grid
function StorageCell({ label, value, valueColor }) {
  return (
    <div className="fd-storage-cell">
      <div className="fd-storage-cell-label">{label}</div>
      <div className="fd-storage-cell-val" style={valueColor ? { color: valueColor } : {}}>
        {value ?? "—"}
      </div>
    </div>
  );
}

// Condition check-in form (lives inside the card, no separate page)
function ConditionLogForm({ baseUrl, cropId, cropType, onLogged }) {
  const isRice = cropType === "rice";
  const [form, setForm] = useState({
    temperature_c: "",
    humidity_percent: "",
    moisture_percent: "",
    visual_condition: "good",
  });
  const [submitting, setSubmitting] = useState(false);
  const [note, setNote] = useState(null);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  async function submit() {
    setSubmitting(true);
    setNote(null);
    try {
      const body = { visual_condition: form.visual_condition };
      if (!isRice) {
        if (form.temperature_c) body.temperature_c = parseFloat(form.temperature_c);
        if (form.humidity_percent) body.humidity_percent = parseFloat(form.humidity_percent);
      } else {
        if (form.moisture_percent) body.moisture_percent = parseFloat(form.moisture_percent);
      }

      // Endpoint: POST /post-harvest/{crop_id}/storage-log
      const res = await fetch(`${baseUrl}/post-harvest/${cropId}/storage-log`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${res.status})`);
      }
      setNote({ type: "success", message: "Check logged. Refreshing…" });
      setForm({ temperature_c: "", humidity_percent: "", moisture_percent: "", visual_condition: "good" });
      await onLogged();
    } catch (e) {
      setNote({ type: "error", message: e.message });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <hr className="fd-card-divider" />
      <div className="fd-guidance-label">Log a Storage Check</div>
      <div className="fd-condition-row">
        {!isRice && (
          <>
            <input
              type="number" step="0.1" placeholder="Temp (°C)"
              value={form.temperature_c} onChange={set("temperature_c")}
            />
            <input
              type="number" step="0.1" min="0" max="100" placeholder="Humidity (%)"
              value={form.humidity_percent} onChange={set("humidity_percent")}
            />
          </>
        )}
        {isRice && (
          <input
            type="number" step="0.1" min="0" max="30" placeholder="Grain moisture (%)"
            value={form.moisture_percent} onChange={set("moisture_percent")}
          />
        )}
        <select value={form.visual_condition} onChange={set("visual_condition")}>
          <option value="good">✓ Looks Good</option>
          <option value="early_spoilage">⚠ Early Signs</option>
          <option value="critical">✗ Critical</option>
        </select>
      </div>
      <button className="fd-log-submit" onClick={submit} disabled={submitting}>
        {submitting ? "Saving…" : "Log Check"}
      </button>
      {note && <div className={`fd-log-note ${note.type}`}>{note.message}</div>}
    </div>
  );
}

// The main Storage Status card — rendered when crop is harvested
// ---------------------------------------------------------------------------
// HarvestRecordForm — shown inside StorageStatusCard when no record exists.
// POSTs to POST /post-harvest/ then triggers a reload of the card.
// ---------------------------------------------------------------------------
const STORAGE_GUIDANCE = {
  rice: {
    recommendedStorage: {
      ambient: {
        title: "Ambient Warehouse",
        reason:
          "Properly dried rice (≤14% moisture) stores safely for long periods in ambient conditions.",
        shelfLife: 180,
      },
      cold_room: {
        title: "Cold Storage",
        reason:
          "Suitable for premium seed rice or long-term storage.",
        shelfLife: 240,
      },
      covered_shed: {
        title: "Covered Shed",
        reason:
          "Provides protection from rain while maintaining airflow.",
        shelfLife: 150,
      },
      open: {
        title: "Open Storage",
        reason:
          "Not recommended due to moisture, insects and rodents.",
        shelfLife: 90,
      },
    },

    practices: [
      "Dry harvested grain until moisture ≤14%",
      "Remove broken and infected grains",
      "Clean storage area before loading",
      "Use airtight bags or metal bins",
      "Inspect grain every 2 weeks",
    ],

    checklist: [
      "Dry grain to ≤14%",
      "Remove damaged grains",
      "Clean storage area",
      "Use clean containers",
      "Protect against rodents",
      "Record harvest quantity",
      "Choose storage method",
    ],
  },

  tomato: {
    recommendedStorage: {
      cold_room: {
        title: "Cold Storage",
        reason:
          "Cold storage slows ripening and greatly extends shelf life.",
        shelfLife: 28,
      },
      ambient: {
        title: "Ventilated Ambient Storage",
        reason:
          "Suitable only for short-term storage.",
        shelfLife: 7,
      },
      covered_shed: {
        title: "Covered Ventilated Shed",
        reason:
          "Provides shade but limited storage life.",
        shelfLife: 10,
      },
      open: {
        title: "Open Storage",
        reason:
          "Not recommended because tomatoes spoil rapidly.",
        shelfLife: 3,
      },
    },

    practices: [
      "Remove damaged fruits immediately",
      "Sort fruits by ripeness",
      "Avoid stacking heavily",
      "Use ventilated crates",
      "Cool produce soon after harvest",
    ],

    checklist: [
      "Remove damaged fruits",
      "Sort by ripeness",
      "Wash crates",
      "Use ventilated containers",
      "Avoid direct sunlight",
      "Record harvest quantity",
      "Choose storage method",
    ],
  },
};

function HarvestRecordForm({ baseUrl, cropId, cropType, onCreated }) {
  const defaultStorage =
    cropType?.toLowerCase() === "tomato"
      ? "cold_room"
      : "ambient";

  const [form, setForm] = useState({
    harvest_date: new Date().toISOString().slice(0, 10),
    quantity_kg: "",
    storage_type: defaultStorage,
    storage_location: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  async function submit() {
    if (!form.quantity_kg || parseFloat(form.quantity_kg) <= 0) {
      setError("Enter a valid harvested quantity.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch(`${baseUrl}/post-harvest/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          crop_id: cropId,
          harvest_date: form.harvest_date,
          quantity_kg: parseFloat(form.quantity_kg),
          storage_type: form.storage_type,
          storage_location: form.storage_location || null,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Failed (${res.status})`);
      }
      await onCreated();
    } catch (e) {
      setError(e instanceof TypeError ? `Couldn't reach ${baseUrl} — is the backend running?` : e.message);
    } finally {
      setSubmitting(false);
    }
  }

  const kb = STORAGE_GUIDANCE[cropType?.toLowerCase()] || STORAGE_GUIDANCE.rice;
  const storage = kb.recommendedStorage[form.storage_type] ?? kb.recommendedStorage.ambient;

  return (
    <div className="fd-section">
      <div className="fd-section-title">
        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Package size={16} color="var(--amber)" /> Storage Status
        </span>
      </div>

      <div style={{ fontSize: 13, color: "var(--text-dim)", marginBottom: 16 }}>
        No harvest record yet. Fill in the details below to start tracking storage and get spoilage intelligence.
      </div>

      {/* Two-column grid matching the rest of the card's style */}
      {/* FarmMind Recommendations */}

      <div
        style={{
          background: "var(--green-soft)",
          border: "1px solid var(--green)",
          borderRadius: 10,
          padding: 18,
          marginBottom: 18,
        }}
      >

        <div
          style={{
            fontWeight: 600,
            color: "var(--green)",
            marginBottom: 14,
            fontSize: 16,
          }}
        >
          🌾 FarmMind Recommendations
        </div>

        <div className="fd-guidance-label">
          Recommended Post-Harvest Practices
        </div>

        <ul className="fd-guidance-list">
          {kb.practices.map((p) => (
            <li key={p}>{p}</li>
          ))}
        </ul>

        <hr className="fd-card-divider" />

        <div className="fd-guidance-label">
          Recommended Storage Method
        </div>

        <div
          style={{
            padding: 12,
            borderRadius: 8,
            background: "white",
            border: "1px solid var(--border)",
            marginBottom: 14,
          }}
        >
          <div style={{ fontWeight: 600, fontSize: 15, }}>
            {storage.title}
          </div>

          <div style={{ color: "var(--text-dim)", fontSize: 13, marginTop: 6 }}>
            {storage.reason}
          </div>

          <div
            style={{ marginTop: 10, fontSize: 13, }}>
            Expected Shelf Life

            <b>
              {" "}
              {storage.shelfLife} days
            </b>
          </div>
        </div>

        <div className="fd-guidance-label">
          Before Storage Checklist
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {kb.checklist.map((item) => (
            <label
              key={item}
              style={{ fontSize: 13, display: "flex", gap: 8, alignItems: "center", }}>
              <input type="checkbox" />

              {item}
            </label>
          ))}
        </div>

      </div>
      <div className="fd-storage-grid">
        <div className="fd-storage-cell">
          <div className="fd-storage-cell-label">Harvest Date</div>
          <input
            type="date"
            value={form.harvest_date}
            onChange={set("harvest_date")}
            style={{ width: "100%", marginTop: 4, padding: "6px 8px", border: "1px solid var(--border)", borderRadius: 6, fontFamily: "var(--mono)", fontSize: 13, background: "var(--bg)", color: "var(--text)" }}
          />
        </div>
        <div className="fd-storage-cell">
          <div className="fd-storage-cell-label">Quantity (kg)</div>
          <input
            type="number" min="0.1" step="0.1"
            placeholder="e.g. 1200"
            value={form.quantity_kg}
            onChange={set("quantity_kg")}
            style={{ width: "100%", marginTop: 4, padding: "6px 8px", border: "1px solid var(--border)", borderRadius: 6, fontFamily: "var(--mono)", fontSize: 13, background: "var(--bg)", color: "var(--text)" }}
          />
        </div>
        <div className="fd-storage-cell">
          <div className="fd-storage-cell-label">Storage Type</div>
          <select
            value={form.storage_type}
            onChange={set("storage_type")}
            style={{ width: "100%", marginTop: 4, padding: "6px 8px", border: "1px solid var(--border)", borderRadius: 6, fontFamily: "var(--sans)", fontSize: 13, background: "var(--bg)", color: "var(--text)" }}
          >
            <option value="cold_room">Cold Room</option>
            <option value="ambient">Ambient (Bag / Hermetic)</option>
            <option value="covered_shed">Covered Shed</option>
            <option value="open">Open</option>
          </select>
        </div>
        <div className="fd-storage-cell">
          <div className="fd-storage-cell-label">Storage Location (optional)</div>
          <input
            type="text"
            placeholder="e.g. Warehouse B"
            value={form.storage_location}
            onChange={set("storage_location")}
            style={{ width: "100%", marginTop: 4, padding: "6px 8px", border: "1px solid var(--border)", borderRadius: 6, fontFamily: "var(--sans)", fontSize: 13, background: "var(--bg)", color: "var(--text)" }}
          />
        </div>
      </div>

      <button
        className="fd-log-submit"
        onClick={submit}
        disabled={submitting}
        style={{ marginTop: 14, width: "100%", padding: "10px" }}
      >
        {submitting ? "Saving…" : "Record Harvest & Start Tracking"}
      </button>
      {error && <div className="fd-log-note error" style={{ marginTop: 8 }}>{error}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// StorageStatusCard
// ---------------------------------------------------------------------------
function StorageStatusCard({ baseUrl, cropId, cropType, onRefresh }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      // Single endpoint — backend assembles harvest_record + latest log + engine output
      const res = await fetch(`${baseUrl}/post-harvest/${cropId}`);
      if (res.status === 404) {
        // Crop is harvested but no harvest record yet — handled gracefully below
        setData(null);
        setLoading(false);
        return;
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${res.status})`);
      }
      setData(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [cropId, baseUrl]); // eslint-disable-line

  // ── Loading state ──
  if (loading) {
    return (
      <div className="fd-section">
        <div className="fd-section-title">
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Package size={16} color="var(--amber)" /> Storage Status
          </span>
        </div>
        <div className="fd-empty">Loading storage data…</div>
      </div>
    );
  }

  // ── Error state ──
  if (error) {
    return (
      <div className="fd-section">
        <div className="fd-section-title">
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Package size={16} color="var(--amber)" /> Storage Status
          </span>
        </div>
        <div className="fd-error-note">{error}</div>
      </div>
    );
  }

  // ── No harvest record yet — show creation form ──
  if (!data) {
    return (
      <HarvestRecordForm
        baseUrl={baseUrl}
        cropId={cropId}
        cropType={cropType}
        onCreated={load}
      />
    );
  }

  // ── Full card ──
  const {
    // From harvest_record
    harvest_date, quantity_kg, storage_type, storage_location,
    // From latest storage_condition_log
    latest_log,
    // From the Post-Harvest Intelligence Engine — exact keys from post_harvest_engine.py
    remaining_shelf_life_days,
    shelf_life_consumed_percent,   // 0–100, how much is gone
    estimated_shelf_life_days,
    storage_health,                // string: optimal | acceptable | at_risk | critical
    spoilage_risk,                 // string: low | moderate | high | critical
    risk_factors,
    recommendations,               // [{priority, action, reason, urgency}]
    storage_best_practices,
    health_summary,
    spoilage_summary,
  } = data;

  // Derive % remaining from consumed %
  const pctRemaining = Math.max(0, 100 - (shelf_life_consumed_percent || 0));
  const pct = Math.round(pctRemaining);
  const tier = shelfTier(pct);

  // Map urgency string → 0–1 score for the priority colour logic
  const urgencyScore = { immediate: 0.9, within_24h: 0.7, within_week: 0.45, routine: 0.2 };

  const latestTemp = latest_log?.temperature_c;
  const latestHumidity = latest_log?.humidity_percent;
  const latestMoisture = latest_log?.moisture_percent;
  const latestVisual = latest_log?.visual_condition;
  const latestTime = latest_log?.recorded_at;

  const outOfRange = risk_factors || [];

  return (
    <div className="fd-section">

      {/* ── Card header ── */}
      <div className="fd-section-title">
        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Package size={16} color="var(--amber)" />
          Storage Status
        </span>
        <button className="fd-refresh-btn" onClick={load} disabled={loading}>
          {loading ? <RefreshCw className="fd-spin" /> : <RefreshCw />}
          Refresh
        </button>
      </div>

      {/* ── Section 1: Harvest Record ── */}
      <div className="fd-guidance-label">Harvest Record</div>
      <div className="fd-storage-grid">
        <StorageCell label="Harvest Date" value={harvest_date} />
        <StorageCell label="Quantity" value={quantity_kg ? `${quantity_kg} kg` : "—"} />
        <StorageCell label="Storage Type" value={titleCase(storage_type)} />
        <StorageCell label="Storage Location" value={storage_location || "Not specified"} />
      </div>

      <hr className="fd-card-divider" />

      {/* ── Section 2: Latest Storage Check ── */}
      <div className="fd-guidance-label">Latest Storage Check</div>
      {latest_log ? (
        <div className="fd-storage-grid">
          {latestTemp != null && <StorageCell label="Temperature" value={`${latestTemp}°C`} />}
          {latestHumidity != null && <StorageCell label="Humidity" value={`${latestHumidity}%`} />}
          {latestMoisture != null && <StorageCell label="Grain Moisture" value={`${latestMoisture}%`} />}
          <StorageCell
            label="Visual Condition"
            value={titleCase(latestVisual || "Good")}
            valueColor={latestVisual === "critical" ? "var(--red)" : latestVisual === "early_spoilage" ? "var(--amber)" : "var(--green)"}
          />
          <StorageCell label="Recorded" value={formatDateTime(latestTime)} />
        </div>
      ) : (
        <div className="fd-empty" style={{ marginBottom: 12 }}>
          No condition check logged yet. Use the form below to log your first check.
        </div>
      )}

      {/* Risk factors — shown if any out-of-range conditions detected */}
      {outOfRange.length > 0 && outOfRange[0] !== "No condition log recorded yet — conditions unverified." && (
        <div style={{ fontSize: 12, color: "var(--red)", marginBottom: 12, fontWeight: 500 }}>
          ⚠ {outOfRange[0]}
        </div>
      )}

      <hr className="fd-card-divider" />

      {/* ── Section 3: Engine Output ── */}
      <div className="fd-guidance-label">Storage Intelligence</div>

      {/* Shelf life bar */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--text-dim)", marginBottom: 2 }}>
          <span>Remaining Shelf Life</span>
          <span style={{ fontWeight: 600, color: "var(--text)" }}>
            {remaining_shelf_life_days} days
            <span style={{ fontWeight: 400, color: "var(--text-dim)" }}> of {estimated_shelf_life_days}</span>
          </span>
        </div>
        <div className="fd-shelf-bar">
          <div className={`fd-shelf-fill ${tier}`} style={{ width: `${pct}%` }} />
        </div>
        <div style={{ fontSize: 11, color: "var(--text-dim)" }}>{pct}% remaining</div>
      </div>

      {/* Spoilage risk badge */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <span style={{ fontSize: 13, color: "var(--text-dim)" }}>Spoilage Risk</span>
        <span className={`fd-risk-badge ${spoilage_risk || "low"}`}>
          <span className={`fd-dot ${spoilage_risk === "low" ? "healthy" : spoilage_risk === "moderate" ? "attention" : "immediate"}`} />
          {titleCase(spoilage_risk || "Low")}
        </span>
      </div>

      {/* Storage health summary */}
      {health_summary && (
        <div style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 14 }}>{health_summary}</div>
      )}

      {/* Recommendations from engine — {priority, action, reason, urgency} */}
      {recommendations && recommendations.length > 0 && (
        <div style={{ marginBottom: 14 }}>
          <div className="fd-guidance-label">Recommendations</div>
          {recommendations.map((rec, i) => {
            const score = urgencyScore[rec.urgency] || 0.2;
            const t = priorityTier(score);
            const pct2 = Math.round(score * 100);
            return (
              <div
                key={i}
                style={{
                  display: "flex", alignItems: "flex-start", gap: 10,
                  padding: "10px 0",
                  borderBottom: i < recommendations.length - 1 ? "1px solid var(--border)" : "none",
                }}
              >
                <span style={{ fontFamily: "var(--serif)", fontSize: 18, color: "var(--text-dim)", width: 22, flexShrink: 0 }}>{rec.priority}</span>
                <span style={{ flex: 1, fontSize: 13, fontWeight: 500 }}>{rec.action}</span>
                <span style={{
                  fontFamily: "var(--mono)", fontWeight: 600, fontSize: 13, flexShrink: 0,
                  color: `var(--${t === "healthy" ? "green" : t === "attention" ? "amber" : "red"})`
                }}>
                  {pct2}%
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Best practices */}
      {storage_best_practices && storage_best_practices.length > 0 && (
        <div>
          <div className="fd-guidance-label">Best Practices</div>
          <ul className="fd-guidance-list">
            {storage_best_practices.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
      )}

      {/* ── Condition log form at the bottom ── */}
      <ConditionLogForm
        baseUrl={baseUrl}
        cropId={cropId}
        cropType={cropType}
        onLogged={load}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Dashboard Page
// ---------------------------------------------------------------------------
function DashboardPage({ baseUrl, cropId, asOf, crops, cropsLoading, onChangeCrop }) {
  const [state, setState] = useState({
    loading: false,
    error: null,
    workflow: null,
    fusion: null,
    actions: null,
    guidance: null,
    activities: null,
    activitiesUnavailable: false,
  });
  const [forecast, setForecast] = useState([]);

  async function loadAll() {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const wfRes = await fetch(`${baseUrl}/crops/${cropId}/workflow-status${asOf ? `?as_of=${asOf}` : ""}`);
      const workflow = wfRes.ok ? await wfRes.json() : null;

      const fusionRes = await fetch(`${baseUrl}/crops/${cropId}/context-status${asOf ? `?as_of=${asOf}` : ""}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ detections: [] }),
      });
      const fusion = fusionRes.ok ? await fusionRes.json() : null;

      const decisionRes = await fetch(`${baseUrl}/crops/${cropId}/recommendations${asOf ? `?as_of=${asOf}` : ""}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ detections: [] }),
      });
      const decisionBody = decisionRes.ok ? await decisionRes.json() : null;
      const actions = decisionBody ? (decisionBody.actions || deepFind(decisionBody, "actions") || []) : null;
      const guidance = decisionBody?.guidance || {};

      let activities = null;
      let activitiesUnavailable = false;
      try {
        const actRes = await fetch(`${baseUrl}/activities/crop/${cropId}`);
        activities = actRes.ok ? await actRes.json() : null;
        if (!actRes.ok) activitiesUnavailable = true;
      } catch {
        activitiesUnavailable = true;
      }

      // Fetch 5-day weather forecast
      const weatherRes = await fetch(
        `${baseUrl}/weather/intelligence?lat=12.9716&lon=77.5946&crop_type=${cropType}`);

      const weatherData = weatherRes.ok
        ? await weatherRes.json()
        : { forecast: [] };

      setForecast(weatherData.forecast || []);
      // console.log(forecast)

      setState({
        loading: false, error: null,
        workflow, fusion, actions, guidance, activities, activitiesUnavailable,
      });
    } catch (e) {
      setState((s) => ({
        ...s, loading: false,
        error: e instanceof TypeError ? `Couldn't reach ${baseUrl} — is the backend running?` : e.message,
      }));
    }
  }

  useEffect(() => { if (cropId && baseUrl) loadAll(); }, [cropId, baseUrl, asOf]); // eslint-disable-line

  const { workflow, fusion, actions, guidance, activities, activitiesUnavailable } = state;
  // Resolve crop type: crops list is authoritative (has the real crop_type from DB).
  // guessCropType is only a fallback if the crops list hasn't loaded yet.
  const cropRecord = crops.find((c) => c.crop_id === cropId);
  const cropType = cropRecord
    ? String(cropRecord.crop_type).toLowerCase()
    : guessCropType(workflow || fusion || {});
  const stageName = dig(workflow, ["current_stage", "stage"], ["current_stage", "name"]) ||
    titleCase(dig(workflow, ["current_stage", "stage_id"])) || "Unknown stage";

  // Derive the current stage ID — used to decide whether to show StorageStatusCard
  const stageId = String(dig(workflow, ["current_stage", "stage_id"]) || "").toLowerCase();
  // Show the card when the crop is at harvest stage, OR when the crop status
  // in the crops list is marked "Harvested" (covers the case where the workflow
  // hasn't loaded yet but we already know the crop is done).
  const cropStatus = String(cropRecord?.status || "").toLowerCase();
  const isHarvestedCrop = stageId === "harvest" || cropStatus === "harvested";

  const weather = dig(fusion, ["weather_context"]) || dig(fusion, ["weather"]);
  const rawAlerts = dig(weather, ["triggered_alerts"]) || dig(weather, ["alerts"]) || [];
  let triggers = rawAlerts.map((a) => (typeof a === "string" ? a : a.weather_id)).filter(Boolean);
  const temp = dig(weather, ["current", "temperature"], ["temperature"], ["temperature_2m"]);

  const confirmedDisease = (deepFind(fusion, "confirmed") || [])[0];
  const expectedDisease = (deepFind(fusion, "expected_unconfirmed") || [])[0];
  const topDisease = confirmedDisease || expectedDisease;

  const topScore = actions && actions.length > 0 ? (actions[0].score || 0) : 0;
  const hasConfirmed = !!confirmedDisease;
  const overallTier = hasConfirmed || topScore >= 0.75 ? "immediate" : topScore >= 0.45 ? "attention" : "healthy";

  return (
    <div>
      {/* ── Topbar ── */}
      <div className="fd-topbar">
        <div>
          {crops && crops.length > 0 ? (
            <select
              className="fd-crop-select"
              value={cropId}
              onChange={(e) => onChangeCrop(e.target.value)}
            >
              {crops.map((c) => (
                <option key={c.crop_id} value={c.crop_id}>
                  {titleCase(c.crop_type)}{c.variety ? ` — ${c.variety}` : ""}
                </option>
              ))}
            </select>
          ) : (
            <h1 className="fd-crop-name">{titleCase(cropType)} Field</h1>
          )}
          <p className="fd-crop-sub">
            {stageName} · Crop ID {cropId.slice(0, 8)}…
            {cropsLoading && " · loading your farms…"}
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <StatusPill tier={overallTier} />
          <button className="fd-refresh-btn" onClick={loadAll} disabled={state.loading}>
            {state.loading ? <RefreshCw className="fd-spin" /> : <RefreshCw />}
            Refresh
          </button>
        </div>
      </div>

      {state.error && <div className="fd-section"><div className="fd-error-note">{state.error}</div></div>}

      {/* ── Summary cards ── */}
      <div className="fd-summary-row">
        <SummaryCard
          icon={<Sprout color="var(--green)" />} iconBg="var(--green-soft)"
          label="Crop" main={titleCase(cropType)} sub={stageName}
        />
        <SummaryCard
          icon={<CloudRain color="var(--blue)" />} iconBg="var(--blue-soft)"
          label="Weather"
          main={temp !== null ? `${temp}°C` : "—"}
          sub={triggers.length > 0 ? titleCase(triggers[0]) : "Stable"}
        />
        <SummaryCard
          icon={<Bug color="var(--red)" />} iconBg="var(--red-soft)"
          label="Disease"
          main={topDisease ? titleCase(topDisease.disease || topDisease.disease_id) : "None detected"}
          sub={topDisease ? titleCase(topDisease.severity_class || topDisease.risk_level || "") : "Field looks clear"}
        />
        <SummaryCard
          icon={<TrendingDown color="var(--text-dim)" />} iconBg="var(--border)"
          label="Market"
          main={MARKET_PRICES[titleCase(cropType)]?.Karnataka
            ? `₹${MARKET_PRICES[titleCase(cropType)].Karnataka}/kg`
            : "—"}
          sub={MARKET_PRICES[titleCase(cropType)] ? "Karnataka · Agmarknet Jul 2026" : "Not connected yet"}
          muted={!MARKET_PRICES[titleCase(cropType)]}
        />
      </div>

      {/* ── Recommendations (dominant card) ── */}
      <RecommendationsCard actions={actions} loading={state.loading} error={null} />

      <WeatherIntelligenceCard forecast={forecast} />

      {/* ── Guidance (workflow knowledge base) ── */}
      {workflow && <GuidanceCard workflow={workflow} guidance={guidance} />}

      {/* ── Storage Status Card ──────────────────────────────────────────────
          Appears only when the crop is at harvest stage or marked Harvested.
          Single API call to GET /post-harvest/{crop_id}.
          Renders: harvest record → latest condition log → engine output.
      ─────────────────────────────────────────────────────────────────────── */}
      {isHarvestedCrop && (
        <StorageStatusCard
          baseUrl={baseUrl}
          cropId={cropId}
          cropType={cropType}
          onRefresh={loadAll}
        />
      )}

      {/* ── Crop Timeline ── */}
      <div className="fd-section">
        <div className="fd-section-title">Crop Timeline</div>
        {workflow ? <CropTimeline workflow={workflow} cropType={cropType} /> : <div className="fd-empty">Timeline loads once workflow data is available.</div>}
      </div>

      {/* ── Farm Status (Context Fusion output, no engine name exposed) ── */}
      <div className="fd-section">
        <div className="fd-section-title">Farm Status</div>
        {fusion || workflow ? (
          <div className="fd-status-grid">
            <div>
              <div className="fd-status-item-label">Crop Stage</div>
              <div className="fd-status-item-val">{stageName}</div>
            </div>
            <div>
              <div className="fd-status-item-label">Disease Risk</div>
              <div className="fd-status-item-val">
                <span className={`fd-dot ${severityTier(topDisease?.severity_class || topDisease?.risk_level) === "high" ? "immediate" : severityTier(topDisease?.severity_class || topDisease?.risk_level) === "medium" ? "attention" : "healthy"}`} />
                {topDisease ? titleCase(topDisease.severity_class || topDisease.risk_level) : "Low"}
              </div>
            </div>
            <div>
              <div className="fd-status-item-label">Weather Risk</div>
              <div className="fd-status-item-val">
                <span className={`fd-dot ${triggers.length > 0 ? "attention" : "healthy"}`} />
                {triggers.length > 0 ? `${triggers.length} alert${triggers.length > 1 ? "s" : ""}` : "Stable"}
              </div>
            </div>
            <div>
              <div className="fd-status-item-label">Farm Activity</div>
              <div className="fd-status-item-val">{activitiesUnavailable ? "Not connected" : "Normal"}</div>
            </div>
          </div>
        ) : (
          <div className="fd-empty">Load farm data to see current status.</div>
        )}
        {weather && (
          <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid var(--border)", fontSize: 13, color: "var(--text-dim)" }}>
            {weatherInsight(triggers)}
          </div>
        )}
      </div>

      {/* ── Activity Logger ── */}
      <div className="fd-section">
        <div className="fd-section-title">Log Today's Activity</div>
        <ActivityLogger baseUrl={baseUrl} cropId={cropId} onLogged={loadAll} />
      </div>

      {/* ── Recent Activity ── */}
      <div className="fd-section">
        <div className="fd-section-title">Recent Activity</div>
        {activitiesUnavailable && (
          <div className="fd-empty">
            Activity history isn't wired up yet — this needs an endpoint listing logged activities per crop.
          </div>
        )}
        {!activitiesUnavailable && (!activities || (Array.isArray(activities) && activities.length === 0)) && (
          <div className="fd-empty">No activity logged yet.</div>
        )}
        {!activitiesUnavailable && Array.isArray(activities) && activities.length > 0 && (
          <div>
            {activities.slice(0, 6).map((a, i) => (
              <div className="fd-activity-item" key={i}>
                <div className="fd-activity-when">{timeAgo(a.date || a.created_at || a.timestamp)}</div>
                <div className="fd-activity-what"><Check />{a.activity_type || a.task || "Activity logged"}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Disease Analysis Page
// Translates Aditya's Gradio app.py into FarmMind's React design system.
// All data, logic, and thresholds are preserved exactly from app.py.
// ---------------------------------------------------------------------------

// Market prices from app.py — Agmarknet July 2026
const MARKET_PRICES = {
  Rice: { Karnataka: 40.5, "Andhra Pradesh": 38.0, "Tamil Nadu": 39.0, "West Bengal": 37.2, Punjab: 36.0, Telangana: 38.5, Other: 40.3 },
  Tomato: { Karnataka: 22.0, "Andhra Pradesh": 35.2, "Tamil Nadu": 24.0, "West Bengal": 27.8, Punjab: 20.0, Telangana: 25.0, Other: 24.8 },
};


const STATES = ["Karnataka", "Andhra Pradesh", "Tamil Nadu", "West Bengal", "Punjab", "Telangana", "Other"];
// Stage options: union of tomato + rice stages, exactly as pipeline encoders know them
const PIPELINE_STAGES = ["booting", "flowering", "fruiting", "harvest", "heading", "maturity", "seedling", "tillering", "vegetative"];
const SEASONS = ["kharif", "rabi", "summer", "winter"];

function severityColor(cls) {
  return { Mild: "var(--green)", Moderate: "var(--amber)", Severe: "var(--red)", Healthy: "var(--green)" }[cls] || "var(--text-dim)";
}
function severityBg(cls) {
  return { Mild: "var(--green-soft)", Moderate: "var(--amber-soft)", Severe: "var(--red-soft)", Healthy: "var(--green-soft)" }[cls] || "var(--bg)";
}
function occColor(occ) {
  return occ > 65 ? "var(--red)" : occ > 35 ? "var(--amber)" : "var(--green)";
}
function occLabel(occ) {
  return occ > 65 ? "HIGH" : occ > 35 ? "MEDIUM" : "LOW";
}
function progColor(prog) {
  return { Worsening: "var(--red)", Stable: "var(--amber)", Improving: "var(--green)" }[prog] || "var(--text-dim)";
}
function progIcon(prog) {
  return { Worsening: "↑", Stable: "→", Improving: "↓" }[prog] || "→";
}

// Recommendation logic from app.py — translated verbatim
function buildRecommendation(prog, sclass, extra, days) {
  if (prog === "Worsening" && (sclass === "Moderate" || sclass === "Severe")) {
    return {
      color: "var(--red)", title: "Urgent Action Required",
      body: `Disease is ${sclass} severity and actively worsening. Every ${days}-day delay costs an additional ₹${Math.round(extra).toLocaleString("en-IN")} more. Contact your agricultural extension officer or nearest Krishi Vigyan Kendra (KVK) immediately.`,
    };
  } else if (prog === "Worsening") {
    return {
      color: "var(--amber)", title: "Treatment Recommended Within 2–3 Days",
      body: "Disease trend is worsening under current weather conditions. Apply recommended fungicide or pesticide before condition escalates to Severe stage.",
    };
  } else if (sclass === "Severe") {
    return {
      color: "var(--red)", title: "Severe Infection — Immediate Intervention",
      body: "High-severity infection detected. Immediate treatment required regardless of weather trend. Consult your local KVK or agricultural extension officer for crop-specific guidance.",
    };
  } else if (prog === "Improving") {
    return {
      color: "var(--green)", title: "Condition Improving — Continue Treatment",
      body: "Disease is responding well to current weather and treatment conditions. Maintain your current regime and monitor daily. Reassess in 5 days.",
    };
  }
  return {
    color: "var(--amber)", title: "Monitor Closely",
    body: "Moderate risk detected with stable progression. No immediate intervention required but inspect crop daily. Prepare treatment materials if condition worsens.",
  };
}

// Input row: label + control — matches settings page style
function AnalysisField({ label, children }) {
  return (
    <div className="fd-settings-field" style={{ maxWidth: "none", marginBottom: 10 }}>
      <label>{label}</label>
      {children}
    </div>
  );
}

function AnalysisSelect({ value, onChange, options }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        width: "100%", padding: "9px 11px", border: "1px solid var(--border)",
        borderRadius: 7, fontFamily: "var(--sans)", fontSize: 13,
        background: "var(--bg)", color: "var(--text)",
      }}
    >
      {options.map((o) => (
        <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? titleCase(String(o.value ?? o))}</option>
      ))}
    </select>
  );
}

function AnalysisInput({ type = "number", value, onChange, placeholder, min, max, step }) {
  return (
    <input
      type={type}
      className="fd-settings-field"
      value={value}
      onChange={(e) => onChange(type === "number" ? parseFloat(e.target.value) || 0 : e.target.value)}
      placeholder={placeholder}
      min={min} max={max} step={step}
      style={{
        width: "100%", padding: "9px 11px", border: "1px solid var(--border)",
        borderRadius: 7, fontFamily: "var(--mono)", fontSize: 13,
        background: "var(--bg)", color: "var(--text)", margin: 0,
      }}
    />
  );
}

// Result display — mirrors all four sections from app.py
function AnalysisResult({ result }) {
  const {
    crop, disease, confidence, severity_score, severity_class,
    occurrence_prob, progression, economic_loss, market_price, state,
  } = result;

  const econ = economic_loss || {};
  const treatment = result.treatment || null;
  const now = econ.loss_if_act_now || 0;
  const delayed = econ.loss_if_delayed || 0;
  const extra = econ.extra_loss_from_delay || 0;
  const days = econ.delay_days || 7;
  const rec = buildRecommendation(progression, severity_class, extra, days);
  const diseaseName = String(disease || "").replace(/_/g, " ");

  return (
    <div>
      {/* ── Header: primary diagnosis + confidence ── */}
      <div className="fd-section" style={{ marginBottom: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
          <div>
            <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-dim)", marginBottom: 6 }}>
              Primary Diagnosis
            </div>
            <div style={{ fontFamily: "var(--serif)", fontSize: 22, fontWeight: 600, color: "var(--text)" }}>
              {diseaseName}
            </div>
            <div style={{ fontSize: 12, color: "var(--text-dim)", marginTop: 4 }}>
              Crop: <span style={{ color: "var(--text)", fontWeight: 500 }}>{crop}</span>
              &nbsp;·&nbsp;
              Price ref: <span style={{ color: "var(--text)" }}>₹{market_price}/kg</span>
              &nbsp;·&nbsp;
              <span style={{ fontSize: 11 }}>Agmarknet Jul 2026 · {state}</span>
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-dim)", marginBottom: 6 }}>
              AI Confidence
            </div>
            <div style={{ fontFamily: "var(--mono)", fontSize: 28, fontWeight: 700, color: confidence > 75 ? "var(--green)" : confidence > 50 ? "var(--amber)" : "var(--red)" }}>
              {confidence}%
            </div>
            <div style={{ height: 4, width: 120, background: "var(--border)", borderRadius: 99, marginTop: 6, overflow: "hidden" }}>
              <div style={{ height: 4, width: `${confidence}%`, borderRadius: 99, background: confidence > 75 ? "var(--green)" : confidence > 50 ? "var(--amber)" : "var(--red)" }} />
            </div>
          </div>
        </div>
      </div>

      {/* ── 2×2 metric grid ── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 12 }}>

        {/* Severity */}
        <div className="fd-section" style={{ marginBottom: 0 }}>
          <div className="fd-storage-cell-label">Severity</div>
          <div style={{ marginTop: 8 }}>
            <span style={{ background: severityBg(severity_class), color: severityColor(severity_class), fontSize: 11, fontWeight: 700, letterSpacing: "0.05em", padding: "3px 10px", borderRadius: 99 }}>
              {(severity_class || "").toUpperCase()}
            </span>
          </div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 24, fontWeight: 700, color: severityColor(severity_class), marginTop: 8 }}>
            {severity_score}%
          </div>
          <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>disease area coverage</div>
        </div>

        {/* Disease Occurrence Risk */}
        <div className="fd-section" style={{ marginBottom: 0 }}>
          <div className="fd-storage-cell-label">Disease Occurrence Risk</div>
          <div style={{ marginTop: 8 }}>
            <span style={{ background: `${occColor(occurrence_prob)}18`, color: occColor(occurrence_prob), fontSize: 11, fontWeight: 700, letterSpacing: "0.05em", padding: "3px 10px", borderRadius: 99 }}>
              {occLabel(occurrence_prob)}
            </span>
          </div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 24, fontWeight: 700, color: occColor(occurrence_prob), marginTop: 8 }}>
            {occurrence_prob}%
          </div>
          <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>pre-symptom risk from weather</div>
        </div>

        {/* Economic Loss — Act Now */}
        <div className="fd-section" style={{ marginBottom: 0 }}>
          <div className="fd-storage-cell-label">Economic Loss · Act Now</div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 22, fontWeight: 700, color: "var(--green)", marginTop: 8 }}>
            ₹{Math.round(now).toLocaleString("en-IN")}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>estimated loss if treated today</div>
        </div>

        {/* Cost of Delay */}
        <div className="fd-section" style={{ marginBottom: 0, borderLeft: "3px solid var(--amber)" }}>
          <div className="fd-storage-cell-label" style={{ color: "var(--amber)" }}>Cost of {days}-Day Delay</div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 22, fontWeight: 700, color: "var(--amber)", marginTop: 8 }}>
            +₹{Math.round(extra).toLocaleString("en-IN")}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>additional loss from waiting</div>
        </div>
      </div>

      {/* ── Watch Conditions block — shown when occurrence_prob > 35 ── */}
      {occurrence_prob > 35 && (
        <div style={{
          background: "var(--amber-soft)", border: "1px solid var(--amber)",
          borderRadius: 12, padding: "14px 18px", marginBottom: 12,
        }}>
          <div style={{ fontWeight: 700, color: "var(--amber)", fontSize: 13, marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}>
            👁 Watch Conditions
          </div>
          <div style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.7 }}>
            Weather conditions give a{" "}
            <span style={{ fontWeight: 700, color: occColor(occurrence_prob) }}>{occurrence_prob}%</span>
            {" "}probability of disease spread in the coming days.
            Inspect crop daily and consider a preventive treatment if humidity or temperature trends continue.
          </div>
        </div>
      )}

      {/* ── Progression timeline ── */}
      <div className="fd-section" style={{ marginBottom: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-dim)" }}>
            5-Day Disease Progression
          </div>
          <span style={{ background: `${progColor(progression)}18`, color: progColor(progression), fontSize: 11, fontWeight: 700, padding: "3px 12px", borderRadius: 99, border: `1px solid ${progColor(progression)}33` }}>
            {progIcon(progression)} {progression}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ fontSize: 11, color: "var(--text-dim)", width: 32 }}>Now</div>
          <div style={{ flex: 1, height: 4, background: "var(--border)", borderRadius: 99, overflow: "hidden" }}>
            <div style={{
              height: 4, borderRadius: 99,
              background: progColor(progression),
              width: progression === "Worsening" ? "85%" : progression === "Improving" ? "40%" : "55%",
            }} />
          </div>
          <div style={{ fontSize: 11, color: "var(--text-dim)", width: 32, textAlign: "right" }}>D+5</div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10 }}>
          {[1, 2, 3, 4, 5].map((d) => {
            const opacity = progression === "Worsening" ? 0.3 + (d / 5) * 0.7
              : progression === "Improving" ? 1.0 - (d / 5) * 0.5 : 0.6;
            return (
              <div key={d} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 5 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: progColor(progression), opacity }} />
                <div style={{ fontSize: 10, color: "var(--text-dim)" }}>D+{d}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Treatment (new) ── */}
      {treatment && (
        <div style={{ background: "#FDF6F2", border: "1px solid #FEDCC5", borderLeft: "3px solid #EA6A28", borderRadius: 12, padding: "16px 18px", marginBottom: 20 }}>
          <div style={{ fontWeight: 700, color: "#EA6A28", fontSize: 14, marginBottom: 12 }}>
            ✓ Treatment Recommended
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16, marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-dim)", marginBottom: 6 }}>
                Primary Product
              </div>
              <div style={{ fontWeight: 600, color: "var(--text)" }}>
                {treatment.primary}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-dim)", marginBottom: 6 }}>
                Dosage
              </div>
              <div style={{ fontWeight: 600, color: "var(--text)" }}>
                {treatment.dose}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-dim)", marginBottom: 6 }}>
                Application Method
              </div>
              <div style={{ fontWeight: 600, color: "var(--text)" }}>
                {treatment.method}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-dim)", marginBottom: 6, }}>
                Frequency
              </div>
              <div style={{ fontWeight: 600, color: "var(--text)", lineHeight: 1.5, }}>
                {treatment.frequency}
              </div>
              <div style={{ marginTop: 6, fontSize: 11, color: "var(--text-dim)", }}>Recommended spray interval</div>
            </div>
          </div>

          <div style={{ marginTop: 12 }}>
            <div style={{ fontWeight: 700, color: "var(--text)", fontSize: 13, marginBottom: 6 }}>
              Important Precautions
            </div>
            {treatment.do_not && (
              <div
                style={{
                  marginTop: 10,
                  padding: "12px",
                  borderRadius: 8,
                  background: "var(--amber-soft)",
                  borderLeft: "3px solid var(--amber)",
                }}
              >
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "var(--amber)",
                    marginBottom: 6,
                    textTransform: "uppercase",
                  }}
                >
                  ⚠ Important
                </div>

                <div
                  style={{
                    fontSize: 12,
                    color: "var(--text)",
                    lineHeight: 1.6,
                  }}
                >
                  {treatment.do_not}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Recommendation ── */}
      <div style={{ background: `${rec.color}0D`, border: `1px solid ${rec.color}22`, borderLeft: `3px solid ${rec.color}`, borderRadius: 12, padding: "16px 18px" }}>
        <div style={{ fontWeight: 700, color: rec.color, fontSize: 13, marginBottom: 8 }}>
          {rec.title}
        </div>
        <div style={{ fontSize: 13, color: "var(--text-dim)", lineHeight: 1.7 }}>{rec.body}</div>
      </div>
    </div>
  );
}

function DiseaseAnalysisPage({ baseUrl, cropId }) {
  const [form, setForm] = useState({
    crop_stage: "flowering",
    season: "kharif",
    state: "Karnataka",
    temperature: 28.0,
    humidity: 75.0,
    rainfall: 5.0,
    wind_speed: 10.0,
    farm_area: 2.0,
    expected_yield: 5000,
    delay_days: 7,
  });
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const analysis = result || {};

  const disease = analysis.disease || {};
  const severity = analysis.severity || {};
  const occurrence = analysis.occurrence || {};
  const economic = analysis.economic_loss || {};
  const treatment = analysis.treatment || {};
  const overlay = analysis.overlay_image;

  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  function handleImageChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImage(file);
    setResult(null);
    setError(null);
    const reader = new FileReader();
    reader.onload = (ev) => setImagePreview(ev.target.result);
    reader.readAsDataURL(file);
  }

  async function fetchWeather() {
    setWeatherLoading(true);
    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946` +
        `&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m&forecast_days=1`
      );
      const data = await res.json();
      const c = data.current;
      setForm((f) => ({
        ...f,
        temperature: Math.round(c.temperature_2m * 10) / 10,
        humidity: Math.round(c.relative_humidity_2m * 10) / 10,
        rainfall: Math.round((c.rain || 0) * 10) / 10,
        wind_speed: Math.round(c.wind_speed_10m * 10) / 10,
      }));
    } catch (e) {
      // Silently leave existing values
    } finally {
      setWeatherLoading(false);
    }
  }

  async function runAnalysis() {
    if (!image) { setError("Upload a leaf image first."); return; }
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const body = new FormData();
      body.append("image", image);
      Object.entries(form).forEach(([k, v]) => body.append(k, String(v)));

      const res = await fetch(`${baseUrl}/crops/${cropId}/analyse-disease`, {
        method: "POST",
        body,
      });

      if (res.status === 503) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Disease analysis pipeline is not available on the server.");
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Analysis failed (${res.status})`);
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(
        e instanceof TypeError
          ? `Couldn't reach ${baseUrl} — is the backend running?`
          : e.message
      );
    } finally {
      setRunning(false);
    }
  }

  return (
    <div>
      <div className="fd-topbar">
        <div>
          <h1 className="fd-crop-name">Disease Analysis</h1>
          <p className="fd-crop-sub">Upload a leaf photo — YOLO detection + severity + economic loss</p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, alignItems: "start" }}>

        {/* ── Left: inputs ── */}
        <div>
          {/* Image upload */}
          <div className="fd-section">
            <div className="fd-section-title">Leaf Image</div>
            <label
              htmlFor="leaf-upload"
              style={{
                display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                border: `1.5px dashed ${imagePreview ? "var(--green)" : "var(--border)"}`,
                borderRadius: 10, padding: 20, cursor: "pointer",
                background: imagePreview ? "var(--green-soft)" : "var(--bg)",
                minHeight: 160, textAlign: "center", transition: "all 0.2s",
              }}
            >
              {imagePreview ? (
                <img src={imagePreview} alt="Leaf preview" style={{ maxHeight: 180, maxWidth: "100%", borderRadius: 8, objectFit: "contain" }} />
              ) : (
                <>
                  <Upload size={24} color="var(--text-dim)" style={{ marginBottom: 8 }} />
                  <div style={{ fontSize: 13, color: "var(--text-dim)" }}>Drop a leaf image here or click to browse</div>
                  <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 4 }}>Tomato or Rice · JPEG / PNG</div>
                </>
              )}
            </label>
            <input id="leaf-upload" type="file" accept="image/*" onChange={handleImageChange} style={{ display: "none" }} />
            {imagePreview && (
              <button
                onClick={() => { setImage(null); setImagePreview(null); setResult(null); }}
                style={{ marginTop: 8, fontSize: 12, color: "var(--text-dim)", background: "none", border: "none", cursor: "pointer", padding: 0 }}
              >
                Remove image
              </button>
            )}
          </div>

          {/* Crop context */}
          <div className="fd-section">
            <div className="fd-section-title">Crop Context</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <AnalysisField label="Crop Stage">
                <AnalysisSelect value={form.crop_stage} onChange={set("crop_stage")}
                  options={PIPELINE_STAGES.map((s) => ({ value: s, label: titleCase(s) }))} />
              </AnalysisField>
              <AnalysisField label="Season">
                <AnalysisSelect value={form.season} onChange={set("season")}
                  options={SEASONS.map((s) => ({ value: s, label: titleCase(s) }))} />
              </AnalysisField>
              <AnalysisField label="State (for market price)">
                <AnalysisSelect value={form.state} onChange={set("state")}
                  options={STATES.map((s) => ({ value: s, label: s }))} />
              </AnalysisField>
            </div>
          </div>

          {/* Weather */}
          <div className="fd-section">
            <div className="fd-section-title">
              Weather
              <button className="fd-refresh-btn" onClick={fetchWeather} disabled={weatherLoading}>
                {weatherLoading ? <RefreshCw className="fd-spin" /> : <RefreshCw />}
                {weatherLoading ? "Fetching…" : "Live weather"}
              </button>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <AnalysisField label="Temperature (°C)">
                <AnalysisInput value={form.temperature} onChange={set("temperature")} step="0.1" />
              </AnalysisField>
              <AnalysisField label="Humidity (%)">
                <AnalysisInput value={form.humidity} onChange={set("humidity")} min={0} max={100} step="0.1" />
              </AnalysisField>
              <AnalysisField label="Rainfall (mm)">
                <AnalysisInput value={form.rainfall} onChange={set("rainfall")} min={0} step="0.1" />
              </AnalysisField>
              <AnalysisField label="Wind Speed (km/h)">
                <AnalysisInput value={form.wind_speed} onChange={set("wind_speed")} min={0} step="0.1" />
              </AnalysisField>
            </div>
          </div>

          {/* Farm economics */}
          <div className="fd-section">
            <div className="fd-section-title">Farm Economics</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <AnalysisField label="Farm Area (acres)">
                <AnalysisInput value={form.farm_area} onChange={set("farm_area")} min={0.1} step="0.1" />
              </AnalysisField>
              <AnalysisField label="Expected Yield (kg)">
                <AnalysisInput value={form.expected_yield} onChange={set("expected_yield")} min={1} />
              </AnalysisField>
            </div>
            <AnalysisField label={`Delay scenario: ${form.delay_days} days without action`}>
              <input
                type="range" min={1} max={14} step={1}
                value={form.delay_days}
                onChange={(e) => set("delay_days")(parseInt(e.target.value))}
                style={{ width: "100%", accentColor: "var(--amber)" }}
              />
            </AnalysisField>
          </div>

          <button
            className="fd-log-submit"
            onClick={runAnalysis}
            disabled={running || !image}
            style={{ width: "100%", padding: "12px", fontSize: 14, fontWeight: 600, opacity: !image ? 0.5 : 1 }}
          >
            {running ? "Running analysis…" : "Run Analysis →"}
          </button>
          {error && <div className="fd-log-note error" style={{ marginTop: 10 }}>{error}</div>}
        </div>

        {/* ── Right: results ── */}
        <div>
          {!result && !running && (
            <div className="fd-soon" style={{ minHeight: 400 }}>
              <div style={{ fontSize: 32, marginBottom: 12, opacity: 0.4 }}>🌿</div>
              <div className="fd-soon-title">No analysis yet</div>
              <p>Upload a leaf image and click Run Analysis to view diagnostic metrics.</p>
            </div>
          )}
          {running && (
            <div className="fd-soon" style={{ minHeight: 400 }}>
              <div className="fd-soon-title">Running analysis…</div>
              <p style={{ fontSize: 12 }}>YOLO detection → severity → occurrence → economic loss</p>
            </div>
          )}
          {result && !running && <AnalysisResult result={result} />}
        </div>
      </div>
    </div>
  );
}

function MyFarmsPage({ crops, cropsLoading, cropsError, activeCropId, onSelectCrop, onReload }) {
  return (
    <div>
      <div className="fd-topbar">
        <h1 className="fd-crop-name">My Farms</h1>
        <button className="fd-refresh-btn" onClick={onReload} disabled={cropsLoading}>
          {cropsLoading ? <RefreshCw className="fd-spin" /> : <RefreshCw />}
          Reload
        </button>
      </div>
      {cropsLoading && <div className="fd-empty">Loading your crops…</div>}
      {!cropsLoading && cropsError && (
        <div className="fd-section">
          <div className="fd-error-note">{cropsError}</div>
          <p style={{ fontSize: 12, color: "var(--text-dim)", marginTop: 6 }}>
            You can still switch crops manually by pasting a Crop ID in Settings.
          </p>
        </div>
      )}
      {!cropsLoading && !cropsError && crops.length === 0 && (
        <div className="fd-empty">No crops found for this backend yet.</div>
      )}
      {!cropsLoading && crops.length > 0 && (
        <div className="fd-summary-row" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
          {crops.map((c) => (
            <button
              key={c.crop_id}
              className="fd-summary-card"
              style={{ textAlign: "left", cursor: "pointer", color: "inherit", border: c.crop_id === activeCropId ? "1px solid var(--green)" : undefined }}
              onClick={() => onSelectCrop(c.crop_id)}
            >
              <div className="fd-summary-icon" style={{ background: "var(--green-soft)" }}>
                <Sprout color="var(--green)" />
              </div>
              <div className="fd-summary-main">{titleCase(c.crop_type)}</div>
              <div className="fd-summary-sub">
                {c.variety ? `${c.variety} · ` : ""}{c.status ? titleCase(c.status) : "Active"}
              </div>
              {c.sowing_date && <div className="fd-summary-sub">Sown {c.sowing_date}</div>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function ComingSoonPage({ title, blurb }) {
  return (
    <div className="fd-soon">
      <div className="fd-soon-title">{title}</div>
      <p>{blurb}</p>
    </div>
  );
}

function SettingsPage({ baseUrl, setBaseUrl, cropId, setCropId, asOf, setAsOf }) {
  return (
    <div className="fd-section" style={{ maxWidth: 480 }}>
      <div className="fd-section-title">Settings</div>
      <div className="fd-settings-field">
        <label>Backend URL</label>
        <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
      </div>
      <div className="fd-settings-field">
        <label>Crop ID</label>
        <input value={cropId} onChange={(e) => setCropId(e.target.value)} />
      </div>
      <div className="fd-settings-field">
        <label>Viewing data as of</label>
        <input type="date" value={asOf} onChange={(e) => setAsOf(e.target.value)} />
      </div>
      <p style={{ fontSize: 12, color: "var(--text-dim)" }}>
        In a real deployment these would come from account setup and farm selection, not a settings
        form — kept here for now since there's one farm and one backend to point at.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------
export default function FarmMindApp() {
  const [page, setPage] = useState("dashboard");
  const [baseUrl, setBaseUrl] = useState("http://localhost:8000");
  const [cropId, setCropId] = useState("b1ed8268-1d93-4f82-bd15-3cbe98900632");
  const [asOf, setAsOf] = useState(() => new Date().toISOString().slice(0, 10));

  const [crops, setCrops] = useState([]);
  const [cropsLoading, setCropsLoading] = useState(false);
  const [cropsError, setCropsError] = useState(null);

  async function loadCrops() {
    setCropsLoading(true);
    setCropsError(null);
    try {
      const res = await fetch(`${baseUrl}/crops`);
      if (!res.ok) throw new Error(`Couldn't load your crop list (${res.status}).`);
      const body = await res.json();
      const list = Array.isArray(body) ? body : deepFind(body, "crops") || [];
      setCrops(list);
    } catch (e) {
      setCropsError(
        e instanceof TypeError
          ? `Couldn't reach ${baseUrl} to list crops — is the backend running?`
          : e.message
      );
      setCrops([]);
    } finally {
      setCropsLoading(false);
    }
  }

  useEffect(() => { loadCrops(); }, [baseUrl]); // eslint-disable-line

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <Home /> },
    { id: "myfarms", label: "My Farms", icon: <Sprout /> },
    { id: "disease", label: "Disease Analysis", icon: <Bug /> },
    { id: "settings", label: "Settings", icon: <SettingsIcon /> },
  ];

  return (
    <div className="fd-app">
      <style>{STYLE}</style>
      <div className="fd-sidebar">
        <div className="fd-logo">FarmMind</div>
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`fd-nav-item ${page === item.id ? "active" : ""}`}
            onClick={() => setPage(item.id)}
          >
            {item.icon}{item.label}
          </button>
        ))}
      </div>
      <div className="fd-main">
        {page === "dashboard" && (
          <DashboardPage
            baseUrl={baseUrl} cropId={cropId} asOf={asOf}
            crops={crops} cropsLoading={cropsLoading}
            onChangeCrop={setCropId}
          />
        )}
        {page === "myfarms" && (
          <MyFarmsPage
            crops={crops} cropsLoading={cropsLoading} cropsError={cropsError}
            activeCropId={cropId}
            onSelectCrop={(id) => { setCropId(id); setPage("dashboard"); }}
            onReload={loadCrops}
          />
        )}
        {page === "disease" && <DiseaseAnalysisPage baseUrl={baseUrl} cropId={cropId} />}
        {page === "settings" && (
          <SettingsPage
            baseUrl={baseUrl} setBaseUrl={setBaseUrl}
            cropId={cropId} setCropId={setCropId}
            asOf={asOf} setAsOf={setAsOf}
          />
        )}
      </div>
    </div>
  );
}