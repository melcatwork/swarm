/**
 * ExecutionTimeline Component
 *
 * Displays execution timeline for both standard and stigmergic runs.
 * - Standard runs: Shows agent count and execution time
 * - Stigmergic runs: Shows detailed persona sequence with stats
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, Users, CheckCircle, TrendingUp, Clock } from 'lucide-react';
import './ExecutionTimeline.css';

export default function ExecutionTimeline({
  result,
  runType = 'standard'  // 'standard' or 'stigmergic'
}) {
  const [expanded, setExpanded] = useState(true);

  if (!result) return null;

  // Stigmergic run timeline
  if (runType === 'stigmergic' && result.personas_execution_sequence) {
    const {
      personas_execution_sequence = [],
      execution_order = 'capability_ascending',
      activity_log = [],
      shared_graph_snapshot = {}
    } = result;

    // Helper to get stats for each persona
    const getPersonaStats = (personaName) => {
      const personaLogs = activity_log.filter(log => log.persona === personaName);
      const deposits = personaLogs.filter(log => log.action === 'deposit').length;
      const reinforcements = personaLogs.filter(log => log.action === 'reinforce').length;
      return { deposits, reinforcements };
    };

    return (
      <div className="execution-timeline-container">
        <div
          className="execution-timeline-header"
          onClick={() => setExpanded(!expanded)}
          style={{ cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Users size={20} />
            <h3 style={{ margin: 0 }}>Swarm Execution Timeline</h3>
          </div>
          {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>

        {expanded && (
          <div className="execution-timeline-content">
            <div className="timeline-meta">
              <span className="timeline-label">
                Execution Order: <strong>{execution_order}</strong>
              </span>
              <span className="timeline-label">
                {personas_execution_sequence.length} Agents Executed
              </span>
            </div>

            <div className="persona-timeline">
              {personas_execution_sequence.map((personaName, index) => {
                const stats = getPersonaStats(personaName);
                const hasReinforcements = stats.reinforcements > 0;

                return (
                  <div key={index} className="persona-timeline-item">
                    <div className="timeline-connector" />
                    <div className={`persona-card ${hasReinforcements ? 'reinforced' : 'diverged'}`}>
                      <div className="persona-order">{index + 1}</div>
                      <div className="persona-name">{personaName}</div>
                      <div className="persona-stats">
                        <span className="stat-item">
                          {stats.deposits} deposits
                        </span>
                        {hasReinforcements && (
                          <span className="stat-item reinforcement">
                            <CheckCircle size={14} />
                            {stats.reinforcements} reinforced
                          </span>
                        )}
                        {!hasReinforcements && (
                          <span className="stat-item divergence">
                            <TrendingUp size={14} />
                            diverged
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Standard run timeline (Full Swarm, Quick Run, Single Agent)
  const exploration_summary = result.exploration_summary || {};
  const agents_used = exploration_summary.agents_used || 0;
  const execution_time = exploration_summary.execution_time_seconds || 0;
  const raw_paths_found = exploration_summary.raw_paths_found || 0;
  const consensus_findings = exploration_summary.consensus_findings || 0;

  if (agents_used === 0) return null;

  return (
    <div className="execution-timeline-container">
      <div
        className="execution-timeline-header"
        onClick={() => setExpanded(!expanded)}
        style={{ cursor: 'pointer' }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Users size={20} />
          <h3 style={{ margin: 0 }}>Swarm Execution Timeline</h3>
        </div>
        {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </div>

      {expanded && (
        <div className="execution-timeline-content">
          <div className="standard-timeline-grid">
            <div className="timeline-stat-card">
              <div className="stat-icon">
                <Users size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{agents_used}</div>
                <div className="stat-label">Agents Executed</div>
              </div>
            </div>

            <div className="timeline-stat-card">
              <div className="stat-icon">
                <Clock size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{execution_time}s</div>
                <div className="stat-label">Exploration Time</div>
              </div>
            </div>

            <div className="timeline-stat-card">
              <div className="stat-icon">
                <TrendingUp size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{raw_paths_found}</div>
                <div className="stat-label">Paths Discovered</div>
              </div>
            </div>

            <div className="timeline-stat-card">
              <div className="stat-icon">
                <CheckCircle size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{consensus_findings}</div>
                <div className="stat-label">Consensus Findings</div>
              </div>
            </div>
          </div>

          <div className="timeline-description">
            <p style={{ margin: 0, fontSize: 12, color: 'var(--color-text-tertiary)' }}>
              {agents_used} threat actor persona{agents_used !== 1 ? 's' : ''} analyzed the infrastructure
              and discovered {raw_paths_found} potential attack path{raw_paths_found !== 1 ? 's' : ''},
              with {consensus_findings} high-consensus finding{consensus_findings !== 1 ? 's' : ''}
              validated by multiple agents.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
