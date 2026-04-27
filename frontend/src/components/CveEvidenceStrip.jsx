/**
 * CveEvidenceStrip.jsx
 *
 * Displays vulnerability evidence for a single attack path step.
 * Only renders when the step contains a cve_id from the backend.
 * All fields are optional — renders gracefully with partial data.
 */

import React from "react";

const PRIORITY_COLOURS = {
  "CRITICAL": { bg: "#2D1B1B", border: "#E24B4A", text: "#E24B4A" },
  "HIGH":     { bg: "#2D1F1B", border: "#EF9F27", text: "#EF9F27" },
  "MEDIUM-HIGH": { bg: "#1E2420", border: "#1D9E75", text: "#1D9E75" },
  "MEDIUM":   { bg: "#1C1F24", border: "#6B7280", text: "#9CA3AF" },
};

function priorityColour(label) {
  if (!label) return PRIORITY_COLOURS["MEDIUM"];
  const key = Object.keys(PRIORITY_COLOURS).find(k =>
    label.toUpperCase().startsWith(k)
  );
  return PRIORITY_COLOURS[key] || PRIORITY_COLOURS["MEDIUM"];
}

function EpssBar({ score }) {
  if (score == null) return null;
  const pct = Math.round(score * 100);
  const colour = pct >= 70 ? "#E24B4A" : pct >= 40 ? "#EF9F27" : "#1D9E75";
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
      <span style={{ fontSize: 10, color: "#9CA3AF" }}>EPSS</span>
      <span style={{
        display: "inline-block",
        width: 48,
        height: 6,
        background: "#374151",
        borderRadius: 3,
        overflow: "hidden",
        verticalAlign: "middle",
      }}>
        <span style={{
          display: "block",
          width: `${pct}%`,
          height: "100%",
          background: colour,
          borderRadius: 3,
          transition: "width 0.3s ease",
        }} />
      </span>
      <span style={{ fontSize: 11, color: colour, fontWeight: 600 }}>
        {pct}%
      </span>
    </span>
  );
}

export default function CveEvidenceStrip({ step }) {
  if (!step || !step.cve_id) return null;

  const {
    cve_id,
    cvss_score,
    epss,
    kev_listed,
    exploit_ref,
    nuclei_template,
    ghsa_id,
    exploit_priority_label,
  } = step;

  const colours = priorityColour(exploit_priority_label);

  return (
    <div style={{
      marginTop: 8,
      padding: "8px 10px",
      borderRadius: 6,
      background: colours.bg,
      border: `1px solid ${colours.border}`,
      fontSize: 12,
    }}>
      {/* Top row — CVE, CVSS, EPSS, KEV */}
      <div style={{
        display: "flex",
        alignItems: "center",
        flexWrap: "wrap",
        gap: 10,
        marginBottom: 4,
      }}>
        <span style={{
          fontFamily: "monospace",
          fontWeight: 700,
          color: colours.text,
          fontSize: 12,
        }}>
          {cve_id}
        </span>

        {cvss_score != null && (
          <span style={{
            padding: "1px 6px",
            borderRadius: 4,
            background: cvss_score >= 9
              ? "#2D1B1B"
              : cvss_score >= 7 ? "#2D1F1B" : "#1C1F24",
            border: `1px solid ${cvss_score >= 9
              ? "#E24B4A"
              : cvss_score >= 7 ? "#EF9F27" : "#6B7280"}`,
            color: cvss_score >= 9
              ? "#E24B4A"
              : cvss_score >= 7 ? "#EF9F27" : "#9CA3AF",
            fontWeight: 600,
            fontSize: 11,
          }}>
            CVSS {cvss_score.toFixed(1)}
          </span>
        )}

        <EpssBar score={epss} />

        {kev_listed && (
          <span style={{
            padding: "1px 6px",
            borderRadius: 4,
            background: "#2D1B1B",
            border: "1px solid #E24B4A",
            color: "#E24B4A",
            fontWeight: 700,
            fontSize: 10,
            letterSpacing: "0.05em",
          }}>
            ● KEV
          </span>
        )}
      </div>

      {/* Priority label */}
      {exploit_priority_label && (
        <div style={{
          color: colours.text,
          fontSize: 11,
          marginBottom: 4,
          fontWeight: 500,
        }}>
          {exploit_priority_label}
        </div>
      )}

      {/* References row */}
      {(exploit_ref || nuclei_template || ghsa_id) && (
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 8,
          marginTop: 4,
          paddingTop: 4,
          borderTop: "1px solid #374151",
        }}>
          <span style={{ color: "#6B7280", fontSize: 10 }}>
            References:
          </span>
          {exploit_ref && (
            <a
              href={`https://www.exploit-db.com/exploits/${exploit_ref.replace("EDB-", "")}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: "#60A5FA",
                textDecoration: "none",
                fontSize: 11,
                fontFamily: "monospace",
              }}
            >
              {exploit_ref} ↗
            </a>
          )}
          {nuclei_template && (
            <a
              href={`https://github.com/projectdiscovery/nuclei-templates/search?q=${nuclei_template}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: "#60A5FA",
                textDecoration: "none",
                fontSize: 11,
                fontFamily: "monospace",
              }}
            >
              Nuclei: {nuclei_template} ↗
            </a>
          )}
          {ghsa_id && (
            <a
              href={`https://github.com/advisories/${ghsa_id}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: "#60A5FA",
                textDecoration: "none",
                fontSize: 11,
                fontFamily: "monospace",
              }}
            >
              {ghsa_id} ↗
            </a>
          )}
        </div>
      )}
    </div>
  );
}
