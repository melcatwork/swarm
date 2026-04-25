import React, { useState } from 'react';
import { Network, CheckCircle, AlertCircle, ChevronUp, ChevronDown } from 'lucide-react';
import './EmergentInsightsStandard.css';

/**
 * EmergentInsightsStandard Component
 *
 * Displays emergent insights (high-confidence techniques and coverage gaps)
 * for standard run types (Full Swarm, Quick Run, Single Agent).
 *
 * This is a simplified version of the stigmergic emergent insights,
 * showing only:
 * - High Confidence Techniques (techniques appearing in 2+ paths)
 * - Coverage Gaps (attackable assets not targeted in any path)
 */
const EmergentInsightsStandard = ({ emergentInsights }) => {
  const [expanded, setExpanded] = useState(true);

  if (!emergentInsights) {
    return null;
  }

  const high_confidence_techniques = emergentInsights.high_confidence_techniques || [];
  const coverage_gaps = emergentInsights.coverage_gaps || [];
  const summary = emergentInsights.summary || {};

  const formatTechniqueUrl = (techniqueId) => {
    if (!techniqueId) return '#';
    const cleanId = techniqueId.replace(/\./g, '/');
    return `https://attack.mitre.org/techniques/${cleanId}/`;
  };

  return (
    <div className="emergent-insights-standard">
      <div className="section-header" onClick={() => setExpanded(!expanded)}>
        <h3>
          <Network size={20} />
          Emergent Insights
        </h3>
        {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </div>

      {expanded && (
        <div className="insights-grid-standard">
          {/* High Confidence Techniques */}
          <div className="insight-card-standard">
            <h4>
              <CheckCircle size={18} />
              High Confidence Techniques
            </h4>
            <p className="insight-description">
              Techniques appearing in multiple attack paths ({high_confidence_techniques.length} found)
            </p>
            {high_confidence_techniques.length > 0 ? (
              <div className="technique-list">
                {high_confidence_techniques.slice(0, 10).map((tech, idx) => (
                  <div key={idx} className="technique-item">
                    <a
                      href={formatTechniqueUrl(tech.technique_id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="technique-badge-link"
                    >
                      {tech.technique_id}
                    </a>
                    <span className="technique-name">{tech.technique_name}</span>
                    <span className="technique-reinforcement">
                      {tech.path_count} paths
                    </span>
                  </div>
                ))}
                {high_confidence_techniques.length > 10 && (
                  <p className="more-items">
                    ... and {high_confidence_techniques.length - 10} more
                  </p>
                )}
              </div>
            ) : (
              <p className="empty-state">
                No high-confidence techniques found (all techniques appear in only one path)
              </p>
            )}
          </div>

          {/* Coverage Gaps */}
          <div className="insight-card-standard">
            <h4>
              <AlertCircle size={18} />
              Coverage Gaps
            </h4>
            <p className="insight-description">
              Attackable assets not targeted in any attack path ({coverage_gaps.length} found)
            </p>
            {coverage_gaps.length > 0 ? (
              <div className="gap-list">
                {coverage_gaps.slice(0, 10).map((asset, idx) => (
                  <div key={idx} className="gap-item">
                    <code>{asset}</code>
                  </div>
                ))}
                {coverage_gaps.length > 10 && (
                  <p className="more-items">
                    ... and {coverage_gaps.length - 10} more
                  </p>
                )}
              </div>
            ) : (
              <p className="empty-state">
                No coverage gaps - all attackable assets targeted in at least one path
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EmergentInsightsStandard;
