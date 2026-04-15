/**
 * StigmergicResultsView Component
 *
 * Displays Phase 10 stigmergic swarm exploration results with:
 * - Swarm execution timeline
 * - Emergent insights panel
 * - Shared graph visualization
 * - Attack paths with swarm indicators
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, Network, CheckCircle, TrendingUp, AlertCircle, Users } from 'lucide-react';
import './StigmergicResultsView.css';

const StigmergicResultsView = ({ results }) => {
  const [expandedSections, setExpandedSections] = useState({
    timeline: true,
    insights: true,
    graph: true,
    paths: true
  });
  const [expandedPaths, setExpandedPaths] = useState(new Set());
  const [hoveredNode, setHoveredNode] = useState(null);

  if (!results) return null;

  const {
    attack_paths = [],
    shared_graph_snapshot = {},
    emergent_insights = {},
    activity_log = [],
    personas_execution_sequence = [],
    execution_order = 'capability_ascending'
  } = results;

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const togglePath = (index) => {
    const newExpanded = new Set(expandedPaths);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedPaths(newExpanded);
  };

  // Kill chain phase colors (reused from project)
  const getKillChainPhaseColor = (phase) => {
    const colors = {
      'Reconnaissance': { bg: '#f3f4f6', border: '#9ca3af', text: '#374151' },
      'Initial Access': { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' },
      'Execution & Persistence': { bg: '#fed7aa', border: '#f97316', text: '#9a3412' },
      'Lateral Movement & Privilege Escalation': { bg: '#e9d5ff', border: '#a855f7', text: '#6b21a8' },
      'Objective (Exfiltration/Impact)': { bg: '#fecaca', border: '#ef4444', text: '#991b1b' },
      'Covering Tracks': { bg: '#e5e7eb', border: '#6b7280', text: '#1f2937' },
    };
    return colors[phase] || colors['Reconnaissance'];
  };

  const getImpactTypeColor = (impactType) => {
    const colors = {
      confidentiality: { bg: '#dbeafe', text: '#1e40af', label: 'Confidentiality' },
      integrity: { bg: '#fed7aa', text: '#9a3412', label: 'Integrity' },
      availability: { bg: '#fecaca', text: '#991b1b', label: 'Availability' },
    };
    return colors[impactType] || colors.confidentiality;
  };

  const formatTechniqueUrl = (techniqueId) => {
    const formatted = techniqueId.replace('.', '/');
    return `https://attack.mitre.org/techniques/${formatted}/`;
  };

  // Calculate persona stats from activity log
  const getPersonaStats = (personaName) => {
    const deposits = activity_log.filter(
      log => log.deposited_by === personaName && log.action === 'deposit_node'
    ).length;
    const reinforcements = activity_log.filter(
      log => log.deposited_by === personaName &&
      (log.action === 'reinforce_node' || log.action === 'reinforce_edge')
    ).length;
    return { deposits, reinforcements };
  };

  // Section 1: SWARM EXECUTION TIMELINE
  const renderExecutionTimeline = () => (
    <div className="stigmergic-section">
      <div className="section-header" onClick={() => toggleSection('timeline')}>
        <h3>
          <Users size={20} />
          Swarm Execution Timeline
        </h3>
        {expandedSections.timeline ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </div>

      {expandedSections.timeline && (
        <div className="timeline-container">
          <div className="timeline-header">
            <span className="timeline-label">Execution Order: <strong>{execution_order}</strong></span>
            <span className="timeline-label">{personas_execution_sequence.length} Agents Executed</span>
          </div>

          <div className="persona-timeline">
            {personas_execution_sequence.map((personaName, index) => {
              const stats = getPersonaStats(personaName);
              const hasReinforcements = stats.reinforcements > 0;

              return (
                <div key={index} className="persona-badge-timeline">
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

  // Section 2: EMERGENT INSIGHTS PANEL
  const renderEmergentInsights = () => {
    const {
      high_confidence_techniques = [],
      convergent_paths = [],
      coverage_gaps = [],
      technique_clusters = []
    } = emergent_insights;

    return (
      <div className="stigmergic-section">
        <div className="section-header" onClick={() => toggleSection('insights')}>
          <h3>
            <Network size={20} />
            Emergent Insights
          </h3>
          {expandedSections.insights ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>

        {expandedSections.insights && (
          <div className="insights-grid">
            {/* High Confidence Techniques */}
            <div className="insight-card">
              <h4>
                <CheckCircle size={18} />
                High Confidence Techniques
              </h4>
              <p className="insight-description">
                Techniques independently discovered by multiple agents
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
                        {tech.times_reinforced + 1} agents
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-state">No reinforced techniques found</p>
              )}
            </div>

            {/* Convergent Paths */}
            <div className="insight-card">
              <h4>
                <TrendingUp size={18} />
                Convergent Paths
              </h4>
              <p className="insight-description">
                Attack sequences discovered by multiple personas
              </p>
              {convergent_paths.length > 0 ? (
                <div className="convergent-paths-list">
                  {convergent_paths.slice(0, 5).map((path, idx) => (
                    <div key={idx} className="convergent-path-item">
                      <div className="path-sequence">
                        {path.technique_sequence.map((tech, techIdx) => (
                          <span key={techIdx}>
                            <code className="technique-code">{tech}</code>
                            {techIdx < path.technique_sequence.length - 1 && ' → '}
                          </span>
                        ))}
                      </div>
                      <span className="convergence-badge">
                        {path.path_length} steps, Avg pheromone: {path.avg_pheromone.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-state">No convergent paths detected</p>
              )}
            </div>

            {/* Coverage Gaps */}
            <div className="insight-card">
              <h4>
                <AlertCircle size={18} />
                Coverage Gaps
              </h4>
              <p className="insight-description">
                Assets not explored by any agent
              </p>
              {coverage_gaps.length > 0 ? (
                <div className="gap-list">
                  {coverage_gaps.slice(0, 10).map((asset, idx) => (
                    <div key={idx} className="gap-item">
                      <code>{asset}</code>
                    </div>
                  ))}
                  {coverage_gaps.length > 10 && (
                    <p className="more-items">+ {coverage_gaps.length - 10} more assets</p>
                  )}
                </div>
              ) : (
                <p className="empty-state">Full coverage achieved</p>
              )}
            </div>

            {/* Technique Clusters */}
            <div className="insight-card">
              <h4>
                <Network size={18} />
                Technique Clusters
              </h4>
              <p className="insight-description">
                Frequently co-occurring technique pairs
              </p>
              {technique_clusters.length > 0 ? (
                <div className="cluster-list">
                  {technique_clusters.slice(0, 8).map((cluster, idx) => (
                    <div key={idx} className="cluster-item">
                      <div className="cluster-techniques">
                        <code>{cluster.techniques[0]}</code>
                        <span className="cluster-arrow">⇄</span>
                        <code>{cluster.techniques[1]}</code>
                      </div>
                      <span className="cluster-count">
                        {cluster.co_occurrence_count}× co-occurrence
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-state">No clusters detected</p>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Section 3: SHARED GRAPH VISUALIZATION
  const renderSharedGraph = () => {
    const nodes = shared_graph_snapshot.nodes || [];
    const edges = shared_graph_snapshot.edges || [];

    if (nodes.length === 0) {
      return null;
    }

    // Simple force-directed layout calculation
    const layoutNodes = () => {
      const width = 800;
      const height = 600;
      const centerX = width / 2;
      const centerY = height / 2;

      // Position nodes in a circular layout by kill chain phase
      const phaseOrder = [
        'Reconnaissance',
        'Initial Access',
        'Execution & Persistence',
        'Lateral Movement & Privilege Escalation',
        'Objective (Exfiltration/Impact)',
        'Covering Tracks'
      ];

      const nodesByPhase = {};
      nodes.forEach(node => {
        const phase = node.kill_chain_phase || 'Unknown';
        if (!nodesByPhase[phase]) nodesByPhase[phase] = [];
        nodesByPhase[phase].push(node);
      });

      const positioned = [];
      let phaseIndex = 0;

      Object.keys(nodesByPhase).forEach(phase => {
        const phaseNodes = nodesByPhase[phase];
        const angleStep = (2 * Math.PI) / phaseNodes.length;
        const radius = 150 + (phaseIndex * 60);

        phaseNodes.forEach((node, idx) => {
          const angle = idx * angleStep;
          positioned.push({
            ...node,
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
            radius: Math.max(5, Math.min(20, node.pheromone_strength * 8))
          });
        });

        phaseIndex++;
      });

      return positioned;
    };

    const positionedNodes = layoutNodes();
    const nodeMap = {};
    positionedNodes.forEach(node => {
      nodeMap[node.node_id] = node;
    });

    return (
      <div className="stigmergic-section">
        <div className="section-header" onClick={() => toggleSection('graph')}>
          <h3>
            <Network size={20} />
            Shared Attack Graph
          </h3>
          {expandedSections.graph ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>

        {expandedSections.graph && (
          <div className="graph-container">
            <div className="graph-legend">
              <div className="legend-item">
                <div className="legend-indicator" style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#64748b' }} />
                <span>Node size = pheromone strength</span>
              </div>
              <div className="legend-item">
                <div className="legend-indicator" style={{ width: '20px', height: '2px', backgroundColor: '#94a3b8' }} />
                <span>Edge thickness = reinforcement</span>
              </div>
            </div>

            <svg className="graph-svg" viewBox="0 0 800 600">
              {/* Render edges */}
              <g className="edges">
                {edges.map((edge, idx) => {
                  const source = nodeMap[edge.source_node_id];
                  const target = nodeMap[edge.target_node_id];
                  if (!source || !target) return null;

                  const strokeWidth = Math.max(1, Math.min(4, edge.times_reinforced + 1));

                  return (
                    <line
                      key={idx}
                      x1={source.x}
                      y1={source.y}
                      x2={target.x}
                      y2={target.y}
                      stroke="#cbd5e1"
                      strokeWidth={strokeWidth}
                      opacity={0.6}
                    />
                  );
                })}
              </g>

              {/* Render nodes */}
              <g className="nodes">
                {positionedNodes.map((node, idx) => {
                  const phaseColor = getKillChainPhaseColor(node.kill_chain_phase);
                  const isHovered = hoveredNode === node.node_id;

                  return (
                    <g
                      key={idx}
                      onMouseEnter={() => setHoveredNode(node.node_id)}
                      onMouseLeave={() => setHoveredNode(null)}
                    >
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={node.radius}
                        fill={phaseColor.bg}
                        stroke={phaseColor.border}
                        strokeWidth={isHovered ? 3 : 2}
                        opacity={isHovered ? 1 : 0.8}
                        style={{ cursor: 'pointer' }}
                      />
                      {isHovered && (
                        <g>
                          <rect
                            x={node.x + 15}
                            y={node.y - 30}
                            width="200"
                            height="80"
                            fill="white"
                            stroke="#cbd5e1"
                            strokeWidth="1"
                            rx="4"
                            filter="drop-shadow(0 2px 4px rgba(0,0,0,0.1))"
                          />
                          <text x={node.x + 25} y={node.y - 10} fontSize="12" fontWeight="600">
                            {node.technique_id}
                          </text>
                          <text x={node.x + 25} y={node.y + 5} fontSize="10" fill="#64748b">
                            Asset: {node.asset_id.slice(0, 20)}...
                          </text>
                          <text x={node.x + 25} y={node.y + 20} fontSize="10" fill="#64748b">
                            By: {node.deposited_by}
                          </text>
                          <text x={node.x + 25} y={node.y + 35} fontSize="10" fill="#64748b">
                            Pheromone: {node.pheromone_strength.toFixed(2)}
                          </text>
                          <text x={node.x + 25} y={node.y + 50} fontSize="10" fill="#64748b">
                            Reinforced: {node.times_reinforced}×
                          </text>
                        </g>
                      )}
                    </g>
                  );
                })}
              </g>
            </svg>

            <div className="graph-stats">
              <span>{nodes.length} nodes</span>
              <span>•</span>
              <span>{edges.length} edges</span>
              <span>•</span>
              <span>{nodes.filter(n => n.times_reinforced > 0).length} reinforced</span>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Section 4: ATTACK PATHS (with swarm indicators)
  const renderAttackPaths = () => {
    if (attack_paths.length === 0) {
      return null;
    }

    return (
      <div className="stigmergic-section">
        <div className="section-header" onClick={() => toggleSection('paths')}>
          <h3>
            Attack Paths ({attack_paths.length})
          </h3>
          {expandedSections.paths ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>

        {expandedSections.paths && (
          <div className="paths-container">
            {attack_paths.map((path, pathIndex) => {
              const isExpanded = expandedPaths.has(pathIndex);
              const impactColor = getImpactTypeColor(path.impact_type);
              const compositeScore = path.composite_score;

              return (
                <div key={pathIndex} className="attack-path-card-stigmergic">
                  {/* Header */}
                  <div className="path-header-stigmergic">
                    <div className="path-title-section">
                      <h4 className="path-name">{path.name}</h4>
                      {path.objective && (
                        <div className="path-objective">
                          <strong>Objective:</strong> {path.objective}
                        </div>
                      )}
                    </div>

                    <div className="path-badges-section">
                      <span className="badge badge-actor">{path.threat_actor || 'Unknown Actor'}</span>
                      <span
                        className="badge badge-impact"
                        style={{ backgroundColor: impactColor.bg, color: impactColor.text }}
                      >
                        {impactColor.label}
                      </span>
                      <span className="badge badge-difficulty">{path.difficulty}</span>

                      {/* Swarm indicators */}
                      {path.reinforces_swarm && (
                        <span className="badge badge-reinforces">
                          <CheckCircle size={12} />
                          Reinforces Swarm
                        </span>
                      )}
                      {path.diverges_from_swarm && (
                        <span className="badge badge-diverges">
                          <TrendingUp size={12} />
                          Diverges from Swarm
                        </span>
                      )}

                      {compositeScore && (
                        <span className="badge badge-score">
                          Score: {compositeScore.toFixed(1)}/10
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Kill Chain Steps */}
                  <button
                    className="expand-toggle"
                    onClick={() => togglePath(pathIndex)}
                  >
                    {isExpanded ? (
                      <>
                        <ChevronUp size={16} />
                        Hide Details
                      </>
                    ) : (
                      <>
                        <ChevronDown size={16} />
                        Show {path.steps?.length || 0} Steps
                      </>
                    )}
                  </button>

                  {isExpanded && path.steps && (
                    <div className="kill-chain-container">
                      {path.steps.map((step, stepIndex) => {
                        const phaseColor = getKillChainPhaseColor(step.kill_chain_phase);
                        const isLastStep = stepIndex === path.steps.length - 1;

                        return (
                          <div key={stepIndex} className="kill-chain-step-wrapper">
                            <div className="kill-chain-step" style={{ borderColor: phaseColor.border }}>
                              <div
                                className="step-phase-header"
                                style={{
                                  backgroundColor: phaseColor.bg,
                                  color: phaseColor.text,
                                  borderBottom: `2px solid ${phaseColor.border}`
                                }}
                              >
                                <span className="step-number-badge">{step.step_number || stepIndex + 1}</span>
                                <span className="phase-name">{step.kill_chain_phase}</span>
                              </div>

                              <div className="step-content">
                                <div className="step-technique-row">
                                  <a
                                    href={formatTechniqueUrl(step.technique_id)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="technique-badge"
                                    title="View on MITRE ATT&CK"
                                  >
                                    {step.technique_id}
                                  </a>
                                  <span className="technique-name-display">{step.technique_name}</span>
                                </div>

                                <div className="step-target-row">
                                  <strong>Target:</strong> <code>{step.target_asset}</code>
                                </div>

                                <p className="step-action">
                                  {step.action_description || step.description}
                                </p>

                                {step.outcome && (
                                  <div className="step-outcome-box">
                                    <strong>Outcome:</strong> {step.outcome}
                                  </div>
                                )}
                              </div>
                            </div>

                            {!isLastStep && (
                              <div className="kill-chain-arrow">
                                <ChevronDown size={24} />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="stigmergic-results-view">
      <div className="stigmergic-header">
        <h2>🧪 Multi-agents Swarm Exploration Results</h2>
        <p className="stigmergic-subtitle">
          Agents built on each other's discoveries through shared graph coordination
        </p>
      </div>

      {renderExecutionTimeline()}
      {renderEmergentInsights()}
      {renderSharedGraph()}
      {renderAttackPaths()}
    </div>
  );
};

export default StigmergicResultsView;
