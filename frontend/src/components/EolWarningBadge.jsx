/**
 * EolWarningBadge.jsx
 *
 * Amber badge shown when an IaC asset uses an EOL runtime or engine.
 * Accepts runtime name and EOL date as props.
 */

import React from "react";

export default function EolWarningBadge({ runtime, eolDate }) {
  if (!runtime || !eolDate) return null;

  return (
    <span
      title={`${runtime} reached end-of-life on ${eolDate} and no longer receives security patches`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "2px 7px",
        borderRadius: 4,
        background: "#2D1F1B",
        border: "1px solid #EF9F27",
        color: "#EF9F27",
        fontSize: 11,
        fontWeight: 600,
        cursor: "help",
      }}
    >
      ⚠ EOL
      <span style={{ fontWeight: 400, color: "#D4A25A" }}>
        {runtime} · {eolDate}
      </span>
    </span>
  );
}
