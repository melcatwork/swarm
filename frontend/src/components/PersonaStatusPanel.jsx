/**
 * PersonaStatusPanel.jsx
 *
 * Displays the intelligence currency status of all 13 personas.
 * Shows patch count, last updated date, and contributing sources
 * for each persona. Fetches from /api/swarm/persona-status.
 */

import React, { useEffect, useState } from "react";
import { syncIntelligence } from "../api/client";

const PERSONA_LABELS = {
  cloud_native_attacker:  "Cloud-Native Attacker",
  apt29_cozy_bear:        "APT29 — Cozy Bear",
  lazarus_group:          "Lazarus Group",
  volt_typhoon:           "Volt Typhoon",
  fin7:                   "FIN7 / Carbanak",
  scattered_spider:       "Scattered Spider",
  ransomware_operator:    "Ransomware Operator",
  supply_chain_attacker:  "Supply Chain Attacker",
  insider_threat:         "Insider Threat",
  cryptominer:            "Cryptominer",
  nation_state_apt:       "Nation-State APT",
  opportunistic_attacker: "Opportunistic Attacker",
  red_team_operator:      "Red Team Operator",
};

function StatusDot({ lastUpdated }) {
  if (!lastUpdated) return (
    <span style={{
      display: "inline-block", width: 8, height: 8,
      borderRadius: "50%", background: "#6B7280",
    }} title="No updates applied" />
  );
  const days = Math.floor(
    (Date.now() - new Date(lastUpdated).getTime()) / 86400000
  );
  const colour = days <= 7
    ? "#1D9E75"
    : days <= 30 ? "#EF9F27" : "#E24B4A";
  const label = days <= 7
    ? "Updated within 7 days"
    : days <= 30
      ? `Updated ${days} days ago`
      : `Last updated ${days} days ago — consider re-syncing`;
  return (
    <span style={{
      display: "inline-block", width: 8, height: 8,
      borderRadius: "50%", background: colour,
    }} title={label} />
  );
}

export default function PersonaStatusPanel() {
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");

  const fetchStatus = () => {
    fetch("/api/swarm/persona-status")
      .then(r => r.json())
      .then(d => { setStatus(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleSyncNow = async () => {
    setSyncing(true);
    setSyncMessage("");

    try {
      const result = await syncIntelligence();
      setSyncMessage(`✓ ${result.message}`);

      // Auto-refresh status after 5 seconds
      setTimeout(() => {
        fetchStatus();
        setSyncMessage("✓ Intelligence sync completed. Status refreshed.");
      }, 5000);

      setSyncing(false);
    } catch (error) {
      setSyncMessage(`✗ Sync failed: ${error.message}`);
      setSyncing(false);
    }
  };

  const totalPatches = Object.values(status)
    .reduce((sum, s) => sum + (s.patch_count || 0), 0);

  const lastSync = Object.values(status)
    .map(s => s.last_updated)
    .filter(Boolean)
    .sort()
    .reverse()[0];

  return (
    <div style={{
      border: "1px solid #374151",
      borderRadius: 8,
      overflow: "hidden",
      marginBottom: 16,
      background: "#111827",
    }}>
      {/* Header — always visible */}
      <div
        onClick={() => setExpanded(e => !e)}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 14px",
          cursor: "pointer",
          background: "#1C2333",
          userSelect: "none",
        }}
      >
        <div style={{
          display: "flex", alignItems: "center", gap: 8
        }}>
          <span style={{
            fontSize: 13, fontWeight: 600, color: "#E5E7EB"
          }}>
            Persona Intelligence Status
          </span>
          {!loading && (
            <span style={{
              padding: "1px 7px",
              borderRadius: 4,
              background: "#1D3020",
              border: "1px solid #1D9E75",
              color: "#1D9E75",
              fontSize: 11,
              fontWeight: 600,
            }}>
              {totalPatches} patches applied
            </span>
          )}
        </div>
        <div style={{
          display: "flex", alignItems: "center", gap: 8
        }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleSyncNow();
            }}
            disabled={syncing}
            style={{
              padding: "4px 10px",
              borderRadius: 4,
              border: "1px solid #667eea",
              background: syncing ? "#374151" : "#667eea",
              color: "#fff",
              fontSize: 11,
              fontWeight: 600,
              cursor: syncing ? "not-allowed" : "pointer",
              opacity: syncing ? 0.6 : 1,
              transition: "all 0.2s",
            }}
            title="Fetch latest threat intelligence and update personas"
          >
            {syncing ? "Syncing..." : "Sync Now"}
          </button>
          {lastSync && (
            <span style={{ fontSize: 11, color: "#6B7280" }}>
              Last sync: {lastSync.slice(0, 10)}
            </span>
          )}
          <span style={{ color: "#6B7280", fontSize: 12 }}>
            {expanded ? "▲" : "▼"}
          </span>
        </div>
      </div>

      {/* Sync status message */}
      {syncMessage && (
        <div style={{
          padding: "8px 14px",
          background: syncMessage.startsWith("✓") ? "#1D302015" : "#2D1B1B15",
          borderBottom: "1px solid #374151",
          fontSize: 11,
          color: syncMessage.startsWith("✓") ? "#1D9E75" : "#E24B4A",
        }}>
          {syncMessage}
        </div>
      )}

      {/* Expanded table */}
      {expanded && (
        <div style={{ padding: "8px 0" }}>
          {loading ? (
            <div style={{
              padding: "16px", color: "#6B7280",
              fontSize: 12, textAlign: "center"
            }}>
              Loading persona status...
            </div>
          ) : (
            Object.entries(PERSONA_LABELS).map(([id, label]) => {
              const s = status[id] || {};
              return (
                <div
                  key={id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "6px 14px",
                    borderBottom: "1px solid #1F2937",
                    fontSize: 12,
                  }}
                >
                  <div style={{
                    display: "flex", alignItems: "center", gap: 8
                  }}>
                    <StatusDot lastUpdated={s.last_updated} />
                    <span style={{ color: "#D1D5DB" }}>{label}</span>
                  </div>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    color: "#6B7280",
                  }}>
                    {s.patch_count > 0 && (
                      <span style={{ color: "#9CA3AF" }}>
                        {s.patch_count} patch{s.patch_count !== 1 ? "es" : ""}
                      </span>
                    )}
                    {s.sources && (
                      <span style={{
                        fontSize: 10,
                        color: "#4B5563",
                        maxWidth: 200,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }} title={s.sources}>
                        {s.sources}
                      </span>
                    )}
                    {s.last_updated && (
                      <span style={{ fontSize: 11 }}>
                        {s.last_updated.slice(0, 10)}
                      </span>
                    )}
                    {!s.last_updated && (
                      <span style={{
                        fontSize: 10, color: "#4B5563"
                      }}>
                        base only
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
