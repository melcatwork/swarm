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
import { ChevronDown, ChevronUp, Network, CheckCircle, TrendingUp, AlertCircle, Users, Shield, Copy } from 'lucide-react';
import SharedAttackGraph from './SharedAttackGraph';
import './StigmergicResultsView.css';

const StigmergicResultsView = ({ results }) => {
  const [expandedSections, setExpandedSections] = useState({
    assetGraph: true,
    evaluation: true,
    timeline: true,
    insights: true,
    graph: true,
    paths: true
  });
  const [expandedPaths, setExpandedPaths] = useState(new Set());
  const [expandedMitigations, setExpandedMitigations] = useState(new Set());
  const [selectedMitigations, setSelectedMitigations] = useState({});
  const [toast, setToast] = useState(null);

  if (!results) return null;

  const {
    attack_paths = [],
    shared_graph_snapshot = {},
    emergent_insights = {},
    activity_log = [],
    personas_execution_sequence = [],
    execution_order = 'capability_ascending',
    asset_graph = {},
    evaluation_summary = {}
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

  const toggleMitigations = (index) => {
    const newExpanded = new Set(expandedMitigations);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedMitigations(newExpanded);
  };

  // Handle mitigation checkbox toggle
  const toggleMitigationSelection = (pathId, stepNumber, mitigationId) => {
    const key = `${pathId}:${stepNumber}:${mitigationId}`;
    setSelectedMitigations(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  // Clear all mitigation selections
  const clearAllMitigations = () => {
    setSelectedMitigations({});
  };

  // Select all mitigations for a specific attack path
  const selectAllMitigations = (path) => {
    const newSelections = {};
    path.steps.forEach(step => {
      // Handle layered mitigations
      if (step.mitigations_by_layer) {
        Object.values(step.mitigations_by_layer).forEach(layerMitigations => {
          if (Array.isArray(layerMitigations)) {
            layerMitigations.forEach(mitigation => {
              const key = `${path.id || path.name}:${step.step_number}:${mitigation.mitigation_id}`;
              newSelections[key] = true;
            });
          }
        });
      }
      // Handle single mitigation (backward compatibility)
      if (step.mitigation) {
        const key = `${path.id || path.name}:${step.step_number}:${step.mitigation.mitigation_id}`;
        newSelections[key] = true;
      }
    });
    setSelectedMitigations(prev => ({ ...prev, ...newSelections }));
  };

  // Copy all mitigations to clipboard
  const copyMitigationsToClipboard = (path) => {
    const mitigationText = path.steps
      .map((step) => {
        const stepMitigations = [];

        // Collect layered mitigations
        if (step.mitigations_by_layer) {
          Object.entries(step.mitigations_by_layer).forEach(([layer, mitigations]) => {
            if (Array.isArray(mitigations)) {
              mitigations.forEach(mitigation => {
                stepMitigations.push({
                  layer,
                  ...mitigation
                });
              });
            }
          });
        }

        // Handle single mitigation (backward compatibility)
        if (step.mitigation && stepMitigations.length === 0) {
          stepMitigations.push(step.mitigation);
        }

        if (stepMitigations.length === 0) return '';

        const mitigationDetails = stepMitigations.map(mit =>
          `  - ${mit.mitigation_id}: ${mit.mitigation_name}${mit.layer ? ` [${mit.layer}]` : ''}\n` +
          `    Description: ${mit.description}\n` +
          (mit.aws_service_action ? `    AWS Action: ${mit.aws_service_action}\n` : '') +
          (mit.priority ? `    Priority: ${mit.priority}\n` : '')
        ).join('\n');

        return `Step ${step.step_number} - ${step.kill_chain_phase}\n` +
               `Technique: ${step.technique_id} - ${step.technique_name}\n` +
               `Mitigations:\n${mitigationDetails}\n`;
      })
      .filter(Boolean)
      .join('---\n\n');

    navigator.clipboard.writeText(mitigationText);
    setToast({
      message: 'Mitigations copied to clipboard!',
      type: 'success'
    });

    // Auto-hide toast after 3 seconds
    setTimeout(() => setToast(null), 3000);
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

  // Group assets by trust boundary
  const groupAssetsByBoundary = (assetGraph) => {
    const assets = assetGraph.assets || [];
    const boundaries = {};

    assets.forEach(asset => {
      const boundary = asset.trust_boundary || 'unknown';
      if (!boundaries[boundary]) {
        boundaries[boundary] = [];
      }
      boundaries[boundary].push(asset);
    });

    return boundaries;
  };

  // Calculate evaluation statistics
  const calculateEvaluationStats = (paths) => {
    if (!paths || paths.length === 0) return null;

    const stats = {
      feasibility: [],
      impact: [],
      detection: [],
      novelty: [],
      coherence: [],
      composite: []
    };

    paths.forEach(path => {
      const evaluation = path.evaluation || {};
      if (evaluation.feasibility_score) stats.feasibility.push(evaluation.feasibility_score);
      if (evaluation.impact_score) stats.impact.push(evaluation.impact_score);
      if (evaluation.detection_score) stats.detection.push(evaluation.detection_score);
      if (evaluation.novelty_score) stats.novelty.push(evaluation.novelty_score);
      if (evaluation.coherence_score) stats.coherence.push(evaluation.coherence_score);
      const compositeScore = evaluation.composite_score || path.composite_score;
      if (compositeScore) stats.composite.push(compositeScore);
    });

    const average = (arr) => arr.length > 0 ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
    const max = (arr) => arr.length > 0 ? Math.max(...arr) : 0;
    const min = (arr) => arr.length > 0 ? Math.min(...arr) : 0;

    return {
      feasibility: { avg: average(stats.feasibility), max: max(stats.feasibility), min: min(stats.feasibility) },
      impact: { avg: average(stats.impact), max: max(stats.impact), min: min(stats.impact) },
      detection: { avg: average(stats.detection), max: max(stats.detection), min: min(stats.detection) },
      novelty: { avg: average(stats.novelty), max: max(stats.novelty), min: min(stats.novelty) },
      coherence: { avg: average(stats.coherence), max: max(stats.coherence), min: min(stats.coherence) },
      composite: { avg: average(stats.composite), max: max(stats.composite), min: min(stats.composite) }
    };
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

  // Section 1: INFRASTRUCTURE ASSET GRAPH
  const renderInfrastructureAssetGraph = () => {
    if (!asset_graph || !asset_graph.assets || asset_graph.assets.length === 0) {
      return null;
    }

    return (
      <div className="stigmergic-section">
        <div className="section-header" onClick={() => toggleSection('assetGraph')}>
          <h3>
            <Shield size={20} />
            Infrastructure Asset Graph ({asset_graph.assets.length} assets)
          </h3>
          {expandedSections.assetGraph ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>

        {expandedSections.assetGraph && (
          <div className="asset-table-container">
            {Object.entries(groupAssetsByBoundary(asset_graph)).map(([boundary, assets]) => (
              <div key={boundary} className="boundary-group" style={{marginBottom: '1.5rem'}}>
                <h4 style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '1rem',
                  fontWeight: 600,
                  marginBottom: '0.75rem',
                  padding: '0.75rem',
                  background: '#f1f5f9',
                  borderRadius: '0.375rem',
                }}>
                  <Shield size={16} />
                  {boundary}
                  <span style={{
                    marginLeft: 'auto',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    color: '#64748b'
                  }}>({assets.length} assets)</span>
                </h4>
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '0.875rem'
                }}>
                  <thead>
                    <tr style={{background: '#f8fafc', borderBottom: '2px solid #e2e8f0'}}>
                      <th style={{padding: '0.75rem', textAlign: 'left', fontWeight: 600}}>Asset Name</th>
                      <th style={{padding: '0.75rem', textAlign: 'left', fontWeight: 600}}>Type</th>
                      <th style={{padding: '0.75rem', textAlign: 'left', fontWeight: 600}}>Service</th>
                      <th style={{padding: '0.75rem', textAlign: 'left', fontWeight: 600}}>Internet Facing</th>
                      <th style={{padding: '0.75rem', textAlign: 'left', fontWeight: 600}}>Trust Boundary</th>
                    </tr>
                  </thead>
                  <tbody>
                    {assets.map((asset, idx) => (
                      <tr key={idx} style={{borderBottom: '1px solid #e2e8f0'}}>
                        <td style={{padding: '0.75rem', fontWeight: 500}}>{asset.name}</td>
                        <td style={{padding: '0.75rem', color: '#64748b'}}>{asset.type}</td>
                        <td style={{padding: '0.75rem', color: '#64748b'}}>{asset.service}</td>
                        <td style={{padding: '0.75rem'}}>
                          {asset.properties?.internet_facing ? (
                            <span style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '0.25rem',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              background: '#fee2e2',
                              color: '#991b1b'
                            }}>Yes</span>
                          ) : (
                            <span style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '0.25rem',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              background: '#dcfce7',
                              color: '#166534'
                            }}>No</span>
                          )}
                        </td>
                        <td style={{padding: '0.75rem', color: '#64748b'}}>{asset.trust_boundary || 'unknown'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Section 2: EVALUATION SUMMARY
  const renderEvaluationSummary = () => {
    const evalStats = calculateEvaluationStats(attack_paths);
    if (!evalStats) return null;

    return (
      <div className="stigmergic-section">
        <div className="section-header" onClick={() => toggleSection('evaluation')}>
          <h3>
            📊 Evaluation Summary
          </h3>
          {expandedSections.evaluation ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>

        {expandedSections.evaluation && (
          <div style={{padding: '1rem'}}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <p style={{fontSize: '0.875rem', color: '#64748b', margin: 0}}>
                Multi-criteria scoring across {attack_paths.length} attack path{attack_paths.length !== 1 ? 's' : ''}
              </p>
              <div style={{
                textAlign: 'center',
                padding: '1rem',
                background: '#f8fafc',
                borderRadius: '0.5rem',
                border: '2px solid #e2e8f0'
              }}>
                <div style={{fontSize: '2rem', fontWeight: 700, color: '#0f172a'}}>
                  {evalStats.composite.avg.toFixed(1)}
                </div>
                <div style={{fontSize: '0.75rem', fontWeight: 500, color: '#64748b', marginTop: '0.25rem'}}>
                  Avg Risk Score
                </div>
              </div>
            </div>

            {/* Metrics Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
              marginBottom: '1.5rem'
            }}>
              {['feasibility', 'impact', 'detection', 'novelty', 'coherence', 'composite'].map(metric => {
                const icons = {
                  feasibility: '🎯',
                  impact: '💥',
                  detection: '🕵️',
                  novelty: '✨',
                  coherence: '🧩',
                  composite: '📈'
                };
                const colors = {
                  feasibility: '#3b82f6',
                  impact: '#ef4444',
                  detection: '#8b5cf6',
                  novelty: '#f59e0b',
                  coherence: '#10b981',
                  composite: '#0f172a'
                };
                return (
                  <div key={metric} style={{
                    padding: '1rem',
                    background: '#f8fafc',
                    borderRadius: '0.5rem',
                    border: '1px solid #e2e8f0'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginBottom: '0.75rem'
                    }}>
                      <span>{icons[metric]}</span>
                      <span style={{fontSize: '0.875rem', fontWeight: 600, textTransform: 'capitalize'}}>
                        {metric}
                      </span>
                    </div>
                    <div style={{fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem'}}>
                      {evalStats[metric].avg.toFixed(1)}/10
                    </div>
                    <div style={{fontSize: '0.75rem', color: '#64748b'}}>
                      Range: {evalStats[metric].min.toFixed(1)} - {evalStats[metric].max.toFixed(1)}
                    </div>
                    <div style={{
                      marginTop: '0.5rem',
                      height: '4px',
                      background: '#e2e8f0',
                      borderRadius: '2px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        height: '100%',
                        width: `${(evalStats[metric].avg / 10) * 100}%`,
                        background: colors[metric],
                        transition: 'width 0.3s ease'
                      }}></div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Key Findings */}
            <div style={{
              padding: '1rem',
              background: '#f1f5f9',
              borderRadius: '0.5rem',
              border: '1px solid #cbd5e1'
            }}>
              <h4 style={{fontSize: '0.9375rem', marginBottom: '0.75rem', color: '#1e293b'}}>
                🔍 Key Findings
              </h4>
              <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
                {evalStats.composite.avg >= 7.0 && (
                  <div style={{
                    padding: '0.5rem',
                    background: '#fee2e2',
                    borderLeft: '4px solid #ef4444',
                    borderRadius: '0.25rem',
                    fontSize: '0.875rem'
                  }}>
                    <strong style={{color: '#991b1b'}}>Critical:</strong> High average composite score ({evalStats.composite.avg.toFixed(1)}/10) indicates significant threat exposure
                  </div>
                )}
                {evalStats.feasibility.avg >= 7.0 && (
                  <div style={{
                    padding: '0.5rem',
                    background: '#fed7aa',
                    borderLeft: '4px solid #f97316',
                    borderRadius: '0.25rem',
                    fontSize: '0.875rem'
                  }}>
                    <strong style={{color: '#9a3412'}}>High:</strong> Attack paths demonstrate high feasibility ({evalStats.feasibility.avg.toFixed(1)}/10) - immediate action recommended
                  </div>
                )}
                {evalStats.composite.avg < 5.0 && (
                  <div style={{
                    padding: '0.5rem',
                    background: '#dbeafe',
                    borderLeft: '4px solid #3b82f6',
                    borderRadius: '0.25rem',
                    fontSize: '0.875rem'
                  }}>
                    <strong style={{color: '#1e40af'}}>Low:</strong> Overall risk score is moderate ({evalStats.composite.avg.toFixed(1)}/10) - standard security posture adequate
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Section 3: SWARM EXECUTION TIMELINE
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

  // Section 4: EMERGENT INSIGHTS PANEL
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

  // Section 5: SHARED GRAPH VISUALIZATION
  const renderSharedGraph = () => {
    if (!shared_graph_snapshot || !shared_graph_snapshot.nodes || shared_graph_snapshot.nodes.length === 0) {
      return null;
    }

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
          <div style={{
            width: '100%',
            minHeight: 600,
            position: 'relative',
            padding: 0,
            margin: 0,
            boxSizing: 'border-box',
          }}>
            <SharedAttackGraph
              data={shared_graph_snapshot}
              coverageGaps={emergent_insights?.coverage_gaps || []}
              convergentPaths={emergent_insights?.convergent_paths || []}
            />
          </div>
        )}
      </div>
    );
  };

  // Section 6: ATTACK PATHS (with swarm indicators and defence-in-depth mitigations)
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
              const evaluation = path.evaluation || {};
              const compositeScore = evaluation.composite_score || path.composite_score;

              // Calculate confidence from composite score if not explicitly set
              let confidence = path.confidence;
              if (!confidence && compositeScore) {
                confidence = compositeScore >= 7 ? 'high' : compositeScore >= 5 ? 'medium' : 'low';
              }
              const confidenceBadge = confidence ? getConfidenceBadge(confidence) : null;

              return (
                <div key={pathIndex} className="attack-path-card-stigmergic">
                  {/* Header */}
                  <div className="path-header-stigmergic">
                    <div style={{ flex: 1, minWidth: '300px' }}>
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

                      {/* Challenged badge */}
                      {path.challenged && (
                        <span className="badge badge-challenged">Challenged</span>
                      )}

                      {/* Confidence badge */}
                      {confidenceBadge && (
                        <span
                          className="badge badge-confidence"
                          style={{ backgroundColor: confidenceBadge.bg, color: confidenceBadge.color }}
                        >
                          {confidenceBadge.label}
                        </span>
                      )}

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
                      </div>
                    </div>

                    {/* Score circle indicator */}
                    {compositeScore && (
                      <div className="path-score-indicator">
                        <div className="score-circle">
                          <span className="score-value">{compositeScore.toFixed(1)}</span>
                          <span className="score-label">/10</span>
                        </div>
                      </div>
                    )}
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

                  {/* Defence-in-Depth Mitigations Section */}
                  {isExpanded && path.steps && (
                    <div style={{marginTop: '1rem'}}>
                      <button
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          padding: '0.75rem 1rem',
                          width: '100%',
                          background: expandedMitigations.has(pathIndex) ? '#dbeafe' : '#f1f5f9',
                          border: '1px solid #cbd5e1',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.9375rem',
                          fontWeight: 600,
                          color: '#0f172a',
                          transition: 'all 0.2s'
                        }}
                        onClick={() => toggleMitigations(pathIndex)}
                      >
                        <Shield size={16} />
                        {expandedMitigations.has(pathIndex) ? 'Hide Defence-in-Depth Mitigations' : 'Show Defence-in-Depth Mitigations'}
                      </button>

                      {expandedMitigations.has(pathIndex) && (
                        <div style={{
                          marginTop: '1rem',
                          padding: '1rem',
                          background: '#f8fafc',
                          borderRadius: '0.375rem',
                          border: '1px solid #e2e8f0'
                        }}>
                          <div style={{marginBottom: '1rem'}}>
                            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.75rem'}}>
                              <div>
                                <h5 style={{fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem'}}>
                                  Defence-in-Depth Mitigations
                                </h5>
                                <p style={{fontSize: '0.875rem', color: '#64748b'}}>
                                  Multiple layers of security controls following Cyber by Design principles
                                </p>
                              </div>
                              <div style={{display: 'flex', gap: '0.5rem', flexShrink: 0}}>
                                <button
                                  className="btn btn-ghost btn-sm"
                                  onClick={() => selectAllMitigations(path)}
                                  style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.375rem',
                                    padding: '0.375rem 0.75rem',
                                    fontSize: '0.8125rem',
                                    background: 'white',
                                    border: '1px solid #cbd5e1',
                                    borderRadius: '0.375rem',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                  }}
                                  onMouseEnter={(e) => e.currentTarget.style.background = '#f1f5f9'}
                                  onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                                >
                                  <CheckCircle size={14} />
                                  Select All
                                </button>
                                <button
                                  className="btn btn-ghost btn-sm"
                                  onClick={() => copyMitigationsToClipboard(path)}
                                  style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.375rem',
                                    padding: '0.375rem 0.75rem',
                                    fontSize: '0.8125rem',
                                    background: 'white',
                                    border: '1px solid #cbd5e1',
                                    borderRadius: '0.375rem',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                  }}
                                  onMouseEnter={(e) => e.currentTarget.style.background = '#f1f5f9'}
                                  onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                                >
                                  <Copy size={14} />
                                  Copy All
                                </button>
                              </div>
                            </div>
                          </div>

                          {/* Defense Layer Legend */}
                          <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                            gap: '0.75rem',
                            marginBottom: '1.5rem',
                            padding: '1rem',
                            background: '#f1f5f9',
                            borderRadius: '0.375rem'
                          }}>
                            <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                              <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#10b981'}}></div>
                              <span style={{fontSize: '0.875rem', fontWeight: 500}}>Preventive</span>
                            </div>
                            <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                              <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#3b82f6'}}></div>
                              <span style={{fontSize: '0.875rem', fontWeight: 500}}>Detective</span>
                            </div>
                            <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                              <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b'}}></div>
                              <span style={{fontSize: '0.875rem', fontWeight: 500}}>Corrective</span>
                            </div>
                            <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                              <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#8b5cf6'}}></div>
                              <span style={{fontSize: '0.875rem', fontWeight: 500}}>Administrative</span>
                            </div>
                          </div>

                          {/* Mitigations by Step */}
                          {path.steps.map((step, stepIndex) => {
                            const mitigationsByLayer = step.mitigations_by_layer || {};
                            const hasMitigations = Object.keys(mitigationsByLayer).length > 0;
                            const singleMitigation = step.mitigation;

                            if (!hasMitigations && !singleMitigation) return null;

                            const renderLayeredMitigation = (mitigation, layer, stepNumber, pathId) => {
                              const selectionKey = `${pathId}:${stepNumber}:${mitigation.mitigation_id}`;
                              const isSelected = selectedMitigations[selectionKey] || false;

                              const priorityColors = {
                                critical: {bg: '#fee2e2', text: '#991b1b'},
                                high: {bg: '#fed7aa', text: '#9a3412'},
                                medium: {bg: '#fef3c7', text: '#92400e'},
                                low: {bg: '#dbeafe', text: '#1e40af'},
                              };
                              const priorityColor = priorityColors[mitigation.priority] || priorityColors.medium;

                              const layerColors = {
                                preventive: '#10b981',
                                detective: '#3b82f6',
                                corrective: '#f59e0b',
                                administrative: '#8b5cf6'
                              };

                              return (
                                <div key={mitigation.mitigation_id} style={{
                                  background: '#f8fafc',
                                  border: '1px solid #e2e8f0',
                                  borderLeft: `4px solid ${layerColors[layer]}`,
                                  borderRadius: '0.375rem',
                                  padding: '0.75rem',
                                  marginBottom: '0.5rem'
                                }}>
                                  <div style={{display: 'flex', alignItems: 'flex-start', gap: '0.75rem'}}>
                                    {/* Checkbox */}
                                    <input
                                      type="checkbox"
                                      id={selectionKey}
                                      checked={isSelected}
                                      onChange={() => toggleMitigationSelection(pathId, stepNumber, mitigation.mitigation_id)}
                                      style={{marginTop: '0.25rem'}}
                                    />

                                    {/* Mitigation Content */}
                                    <div style={{flex: 1}}>
                                      {/* Title Row */}
                                      <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap'}}>
                                        <strong style={{fontSize: '0.875rem'}}>{mitigation.mitigation_id}</strong>
                                        <span style={{fontSize: '0.875rem'}}>{mitigation.mitigation_name}</span>
                                        {mitigation.priority && (
                                          <span style={{
                                            padding: '0.125rem 0.5rem',
                                            borderRadius: '0.25rem',
                                            fontSize: '0.75rem',
                                            fontWeight: 600,
                                            textTransform: 'uppercase',
                                            background: priorityColor.bg,
                                            color: priorityColor.text,
                                          }}>
                                            {mitigation.priority}
                                          </span>
                                        )}
                                      </div>

                                      {/* Description */}
                                      <p style={{fontSize: '0.8125rem', color: '#475569', marginBottom: '0.5rem'}}>
                                        {mitigation.description}
                                      </p>

                                      {/* AWS Action */}
                                      {mitigation.aws_service_action && (
                                        <div style={{
                                          background: '#1e293b',
                                          color: '#e2e8f0',
                                          padding: '0.5rem',
                                          borderRadius: '0.25rem',
                                          fontSize: '0.8125rem',
                                          fontFamily: 'monospace',
                                          marginBottom: '0.5rem',
                                        }}>
                                          <strong style={{color: '#fbbf24'}}>AWS Action:</strong> {mitigation.aws_service_action}
                                        </div>
                                      )}

                                      {/* Implementation Details */}
                                      <div style={{display: 'flex', gap: '1rem', fontSize: '0.75rem', color: '#64748b', flexWrap: 'wrap'}}>
                                        {mitigation.implementation_effort && (
                                          <span>⏱️ {mitigation.implementation_effort}</span>
                                        )}
                                        {mitigation.effectiveness && (
                                          <span>📊 {mitigation.effectiveness}</span>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              );
                            };

                            return (
                              <div key={stepIndex} style={{
                                border: '1px solid #e2e8f0',
                                borderRadius: '0.5rem',
                                padding: '1rem',
                                marginBottom: '1rem',
                                background: '#ffffff'
                              }}>
                                {/* Step Header */}
                                <div style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.75rem',
                                  marginBottom: '1rem',
                                  paddingBottom: '0.75rem',
                                  borderBottom: '2px solid #e2e8f0'
                                }}>
                                  <span style={{
                                    background: '#3b82f6',
                                    color: 'white',
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '0.25rem',
                                    fontWeight: 600,
                                    fontSize: '0.875rem'
                                  }}>
                                    Step {step.step_number}
                                  </span>
                                  <div>
                                    <div style={{fontWeight: 600, fontSize: '0.9375rem'}}>
                                      {step.technique_id} - {step.technique_name}
                                    </div>
                                    <div style={{fontSize: '0.8125rem', color: '#64748b'}}>
                                      {step.kill_chain_phase}
                                    </div>
                                  </div>
                                </div>

                                {/* Defense Layers */}
                                {hasMitigations ? (
                                  <div>
                                    {/* Preventive Layer */}
                                    {mitigationsByLayer.preventive && mitigationsByLayer.preventive.length > 0 && (
                                      <div style={{marginBottom: '1rem'}}>
                                        <div style={{
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '0.5rem',
                                          marginBottom: '0.75rem',
                                          fontSize: '0.9375rem',
                                          fontWeight: 600,
                                          color: '#10b981'
                                        }}>
                                          <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#10b981'}}></div>
                                          Preventive Controls ({mitigationsByLayer.preventive.length})
                                        </div>
                                        {mitigationsByLayer.preventive.map(mit => renderLayeredMitigation(mit, 'preventive', step.step_number, path.id || path.name))}
                                      </div>
                                    )}

                                    {/* Detective Layer */}
                                    {mitigationsByLayer.detective && mitigationsByLayer.detective.length > 0 && (
                                      <div style={{marginBottom: '1rem'}}>
                                        <div style={{
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '0.5rem',
                                          marginBottom: '0.75rem',
                                          fontSize: '0.9375rem',
                                          fontWeight: 600,
                                          color: '#3b82f6'
                                        }}>
                                          <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#3b82f6'}}></div>
                                          Detective Controls ({mitigationsByLayer.detective.length})
                                        </div>
                                        {mitigationsByLayer.detective.map(mit => renderLayeredMitigation(mit, 'detective', step.step_number, path.id || path.name))}
                                      </div>
                                    )}

                                    {/* Corrective Layer */}
                                    {mitigationsByLayer.corrective && mitigationsByLayer.corrective.length > 0 && (
                                      <div style={{marginBottom: '1rem'}}>
                                        <div style={{
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '0.5rem',
                                          marginBottom: '0.75rem',
                                          fontSize: '0.9375rem',
                                          fontWeight: 600,
                                          color: '#f59e0b'
                                        }}>
                                          <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b'}}></div>
                                          Corrective Controls ({mitigationsByLayer.corrective.length})
                                        </div>
                                        {mitigationsByLayer.corrective.map(mit => renderLayeredMitigation(mit, 'corrective', step.step_number, path.id || path.name))}
                                      </div>
                                    )}

                                    {/* Administrative Layer */}
                                    {mitigationsByLayer.administrative && mitigationsByLayer.administrative.length > 0 && (
                                      <div style={{marginBottom: '1rem'}}>
                                        <div style={{
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '0.5rem',
                                          marginBottom: '0.75rem',
                                          fontSize: '0.9375rem',
                                          fontWeight: 600,
                                          color: '#8b5cf6'
                                        }}>
                                          <div style={{width: '12px', height: '12px', borderRadius: '50%', background: '#8b5cf6'}}></div>
                                          Administrative Controls ({mitigationsByLayer.administrative.length})
                                        </div>
                                        {mitigationsByLayer.administrative.map(mit => renderLayeredMitigation(mit, 'administrative', step.step_number, path.id || path.name))}
                                      </div>
                                    )}
                                  </div>
                                ) : (
                                  /* Fallback: Show single mitigation with checkbox */
                                  singleMitigation && (() => {
                                    const selectionKey = `${path.id || path.name}:${step.step_number}:${singleMitigation.mitigation_id}`;
                                    const isSelected = selectedMitigations[selectionKey] || false;

                                    return (
                                      <div style={{
                                        background: '#f8fafc',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '0.375rem',
                                        padding: '0.75rem'
                                      }}>
                                        <div style={{display: 'flex', alignItems: 'flex-start', gap: '0.75rem'}}>
                                          <input
                                            type="checkbox"
                                            id={selectionKey}
                                            checked={isSelected}
                                            onChange={() => toggleMitigationSelection(path.id || path.name, step.step_number, singleMitigation.mitigation_id)}
                                            style={{marginTop: '0.25rem'}}
                                          />
                                          <div style={{flex: 1}}>
                                            <div style={{marginBottom: '0.5rem'}}>
                                              <strong>{singleMitigation.mitigation_id}</strong> - {singleMitigation.mitigation_name}
                                            </div>
                                            <p style={{fontSize: '0.875rem', color: '#475569', marginBottom: '0.5rem'}}>
                                              {singleMitigation.description}
                                            </p>
                                            {singleMitigation.aws_service_action && (
                                              <div style={{
                                                background: '#1e293b',
                                                color: '#e2e8f0',
                                                padding: '0.5rem',
                                                borderRadius: '0.25rem',
                                                fontSize: '0.8125rem',
                                                fontFamily: 'monospace',
                                              }}>
                                                <strong style={{color: '#fbbf24'}}>AWS Action:</strong> {singleMitigation.aws_service_action}
                                              </div>
                                            )}
                                          </div>
                                        </div>
                                      </div>
                                    );
                                  })()
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Provenance Footer (Evaluation Details) */}
                  {isExpanded && (
                    <details className="provenance-section">
                      <summary className="provenance-toggle">
                        <span>▼ View Evaluation Details & Provenance</span>
                      </summary>

                      <div className="provenance-content">
                        {/* Evaluation Scores */}
                        {evaluation.composite_score && (
                          <div className="provenance-item">
                            <h6>EVALUATION SCORES</h6>
                            <div className="evaluation-scores-grid">
                              <div className="eval-score-item">
                                <span className="eval-label">Feasibility</span>
                                <span className="eval-value">{evaluation.feasibility_score || 0}/10</span>
                              </div>
                              <div className="eval-score-item">
                                <span className="eval-label">Detection Difficulty</span>
                                <span className="eval-value">{evaluation.detection_score || 0}/10</span>
                              </div>
                              <div className="eval-score-item">
                                <span className="eval-label">Impact</span>
                                <span className="eval-value">{evaluation.impact_score || 0}/10</span>
                              </div>
                              <div className="eval-score-item">
                                <span className="eval-label">Novelty</span>
                                <span className="eval-value">{evaluation.novelty_score || 0}/10</span>
                              </div>
                              <div className="eval-score-item">
                                <span className="eval-label">Coherence</span>
                                <span className="eval-value">{evaluation.coherence_score || 0}/10</span>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Swarm Provenance */}
                        {(path.reinforces_swarm || path.diverges_from_swarm) && (
                          <div className="provenance-item">
                            <h6>Swarm Intelligence</h6>
                            <p>
                              {path.reinforces_swarm && 'This path reinforces techniques discovered by multiple agents in the swarm, indicating high-confidence attack vectors.'}
                              {path.diverges_from_swarm && 'This path explores novel attack vectors not previously discovered by other agents, expanding attack surface coverage.'}
                            </p>
                          </div>
                        )}

                        {/* Validation Notes */}
                        {path.validation_notes && (
                          <div className="provenance-item">
                            <h6>Validation Notes</h6>
                            <p>{path.validation_notes}</p>
                          </div>
                        )}
                      </div>
                    </details>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  // Helper function to get confidence badge styling
  const getConfidenceBadge = (confidence) => {
    const badges = {
      high: { color: '#10b981', bg: '#d1fae5', label: 'HIGH' },
      medium: { color: '#f59e0b', bg: '#fef3c7', label: 'MEDIUM' },
      low: { color: '#ef4444', bg: '#fee2e2', label: 'LOW' }
    };
    return badges[confidence] || badges.medium;
  };

  // Generate executive summary
  const generateExecutiveSummary = () => {
    if (attack_paths.length === 0) return null;

    const highScorePaths = attack_paths.filter(p => {
      const score = p.evaluation?.composite_score || p.composite_score || 0;
      return score >= 7;
    }).length;

    const coverage = emergent_insights?.summary?.coverage_percentage || 0;
    const reinforcedTechniques = emergent_insights?.high_confidence_techniques?.length || 0;

    return `Stigmergic swarm analysis completed with ${personas_execution_sequence.length} threat actor personas executing in ${execution_order} order. Discovered ${attack_paths.length} attack paths with ${reinforcedTechniques} high-confidence techniques validated by multiple agents. Infrastructure coverage: ${coverage.toFixed(1)}%. ${highScorePaths > 0 ? `${highScorePaths} high-risk paths (score ≥7.0) require immediate attention.` : 'Risk levels vary across the attack surface.'}`;
  };

  return (
    <div className="stigmergic-results-view">
      <div className="stigmergic-header">
        <h2>🧪 Multi-agents Swarm Exploration Results</h2>
        <p className="stigmergic-subtitle">
          Agents built on each other's discoveries through shared graph coordination
        </p>
      </div>

      {/* Executive Summary */}
      {(() => {
        const summary = generateExecutiveSummary();
        if (!summary) return null;

        return (
          <div className="executive-summary">
            <h3>Executive Summary</h3>
            <p>{summary}</p>
          </div>
        );
      })()}

      {/* Stats Bar */}
      <div className="results-stats-bar">
        <div className="stat-item">
          <span className="stat-label">Total Paths</span>
          <span className="stat-value">{attack_paths.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Avg Confidence</span>
          <span className="stat-value">
            {(() => {
              // Calculate confidence from composite scores if not explicitly set
              const pathsWithConfidence = attack_paths.map(p => {
                if (p.confidence) return p;
                const score = p.evaluation?.composite_score || p.composite_score || 0;
                const confidence = score >= 7 ? 'high' : score >= 5 ? 'medium' : 'low';
                return { ...p, confidence };
              });
              const high = pathsWithConfidence.filter(p => p.confidence === 'high').length;
              const medium = pathsWithConfidence.filter(p => p.confidence === 'medium').length;
              const low = pathsWithConfidence.filter(p => p.confidence === 'low').length;
              return `${high}H / ${medium}M / ${low}L`;
            })()}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Coverage</span>
          <span className="stat-value">
            {emergent_insights?.summary?.coverage_percentage
              ? `${emergent_insights.summary.coverage_percentage.toFixed(1)}%`
              : 'N/A'}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Execution Time</span>
          <span className="stat-value">
            {results.execution_time_seconds
              ? `${Math.round(results.execution_time_seconds / 60)}m`
              : 'N/A'}
          </span>
        </div>
      </div>

      {renderInfrastructureAssetGraph()}
      {renderEvaluationSummary()}
      {renderExecutionTimeline()}
      {renderEmergentInsights()}
      {renderSharedGraph()}
      {renderAttackPaths()}

      {/* Mitigation Action Bar */}
      {attack_paths.length > 0 && (
        <div className="mitigation-action-bar">
          <div className="mitigation-action-info">
            <span className="mitigation-count">
              {Object.values(selectedMitigations).filter(Boolean).length} mitigation(s) selected
            </span>
          </div>
          <div className="mitigation-action-buttons">
            <button className="btn btn-secondary" onClick={clearAllMitigations}>
              Clear Selections
            </button>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toast && (
        <div style={{
          position: 'fixed',
          top: '1.5rem',
          right: '1.5rem',
          background: toast.type === 'success' ? '#10b981' : '#ef4444',
          color: 'white',
          padding: '1rem 1.5rem',
          borderRadius: '0.5rem',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          animation: 'slideIn 0.3s ease-out'
        }}>
          <CheckCircle size={20} />
          <span style={{fontWeight: 600}}>{toast.message}</span>
        </div>
      )}
    </div>
  );
};

export default StigmergicResultsView;
