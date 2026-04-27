/**
 * VulnIntelSummary.jsx
 *
 * Aggregates CVE intelligence across all returned attack paths
 * and displays a compact summary row above the path cards.
 * Helps the user immediately understand the severity profile
 * of the findings before reading individual path steps.
 */

import React from "react";

function StatBox({ label, value, colour }) {
  return (
    <div style={{
      flex: 1,
      minWidth: 100,
      padding: "10px 14px",
      borderRadius: 6,
      background: "#1C2333",
      border: `1px solid ${colour}22`,
      textAlign: "center",
    }}>
      <div style={{
        fontSize: 22,
        fontWeight: 700,
        color: colour,
        lineHeight: 1.2,
      }}>
        {value}
      </div>
      <div style={{
        fontSize: 10,
        color: "#6B7280",
        marginTop: 2,
        textTransform: "uppercase",
        letterSpacing: "0.06em",
      }}>
        {label}
      </div>
    </div>
  );
}

export default function VulnIntelSummary({ paths }) {
  if (!paths || paths.length === 0) return null;

  const allSteps = paths.flatMap(p => p.steps || []);
  const stepsWithCve = allSteps.filter(s => s.cve_id);

  if (stepsWithCve.length === 0) return null;

  const kevCount = stepsWithCve.filter(s => s.kev_listed).length;
  const pocCount = stepsWithCve.filter(s => s.exploit_ref).length;
  const uniqueCves = new Set(stepsWithCve.map(s => s.cve_id)).size;
  const maxEpss = Math.max(
    0, ...stepsWithCve.map(s => s.epss || 0)
  );
  const criticalCount = stepsWithCve.filter(
    s => s.cvss_score >= 9
  ).length;

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{
        fontSize: 11,
        color: "#6B7280",
        marginBottom: 8,
        textTransform: "uppercase",
        letterSpacing: "0.06em",
      }}>
        Vulnerability Intelligence Summary
      </div>
      <div style={{
        display: "flex",
        gap: 8,
        flexWrap: "wrap",
      }}>
        <StatBox
          label="Unique CVEs"
          value={uniqueCves}
          colour="#60A5FA"
        />
        <StatBox
          label="KEV Listed"
          value={kevCount}
          colour={kevCount > 0 ? "#E24B4A" : "#6B7280"}
        />
        <StatBox
          label="PoC Confirmed"
          value={pocCount}
          colour={pocCount > 0 ? "#EF9F27" : "#6B7280"}
        />
        <StatBox
          label="CVSS Critical"
          value={criticalCount}
          colour={criticalCount > 0 ? "#E24B4A" : "#6B7280"}
        />
        <StatBox
          label="Peak EPSS"
          value={`${Math.round(maxEpss * 100)}%`}
          colour={maxEpss >= 0.7
            ? "#E24B4A"
            : maxEpss >= 0.4 ? "#EF9F27" : "#6B7280"}
        />
      </div>
    </div>
  );
}
