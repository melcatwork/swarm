# Swarm TM System Architecture Documentation

This directory contains comprehensive architecture diagrams for the Swarm TM threat modeling platform.

## Available Diagrams

### 1. Simplified Architecture (Recommended for Management Presentations)

**Files**:
- [`architecture-simple.md`](architecture-simple.md) - Markdown with Mermaid diagram + explanations
- [`architecture-simple.png`](architecture-simple.png) - PNG image (82KB, 2400×1400)
- [`architecture-simple.svg`](architecture-simple.svg) - SVG image (27KB, scalable)

**Use Case**: Executive presentations, board meetings, sales pitches, non-technical stakeholders

**Description**: 5-step linear flow showing the end-to-end process from IaC upload to results dashboard. Focuses on business value and high-level architecture without overwhelming technical detail.

**Key Sections**:
1. INPUT - Infrastructure-as-Code upload
2. PARSE & ANALYZE - Asset discovery + vulnerability lookup
3. MULTI-AGENT THREAT MODELING - 13 personas with 3-layer validation
4. RISK QUANTIFICATION - Scoring + mitigation selection
5. OUTPUT - Interactive dashboard + archive system

**Includes**:
- Process time breakdown (total ~25 minutes)
- ROI calculation ($17,700 savings per threat model)
- Technology stack summary
- Key differentiators vs. traditional tools

### 2. Detailed Technical Architecture

**Files**:
- [`architecture-diagram.md`](architecture-diagram.md) - Markdown with Mermaid diagram + component details
- [`architecture.png`](architecture.png) - PNG image (635KB, 3000×2400)
- [`architecture.svg`](architecture.svg) - SVG image (106KB, scalable)

**Use Case**: Technical documentation, developer onboarding, security team training, system design reviews

**Description**: Comprehensive architecture showing all 9 layers with data flows, component relationships, and external integrations. Color-coded by layer type.

**Key Layers**:
1. **User Interface Layer** (Blue) - React dashboard, components
2. **API Gateway Layer** (Orange) - FastAPI routers, endpoints
3. **IaC Processing Layer** (Purple) - Parsers, normalizers, upload handlers
4. **Vulnerability Intelligence Layer** (Pink) - SQLite intel.db, CVE/EPSS/KEV data
5. **Multi-Agent Orchestration Layer** (Green) - CrewAI, 13 personas, 3-layer validation, stigmergic graph
6. **LLM Provider Layer** (Yellow) - Ollama, Bedrock, Anthropic
7. **Output Processing Layer** (Purple) - Mitigation mapping, risk calculation, output filtering
8. **Data Persistence Layer** (Pink) - Archive system, persona YAML, threat actor data
9. **External Intelligence Sources** (Gray) - CISA KEV, MITRE ATT&CK, StopRansomware, NVD

**Includes**:
- Complete data flow paths with 60+ connections
- Component responsibilities and technologies
- Design principles and architectural decisions
- External integrations and dependencies

## When to Use Each Diagram

| Audience | Recommended Diagram | Format | Reason |
|----------|-------------------|--------|--------|
| **C-Level Executives** | Simplified | PNG/PPT slide | Focus on business value, ROI, and high-level process |
| **Board of Directors** | Simplified | PNG/PPT slide | Clear 5-step narrative, easy to understand |
| **Security Leadership** | Both | PNG + PDF report | Start simple, provide detailed version for deep-dive |
| **Security Practitioners** | Detailed | SVG/PDF | Need technical understanding of components |
| **DevOps/SRE Teams** | Detailed | SVG/Interactive | Integration points, data flows, deployment architecture |
| **Software Engineers** | Detailed | Markdown + SVG | Codebase navigation, contribution guidelines |
| **Compliance/Audit** | Simplified | PNG/PDF | Data flows for regulatory review (GDPR, SOC 2) |
| **Sales Prospects** | Simplified | PNG/PPT slide | Quick value proposition, competitive differentiation |

## Viewing the Diagrams

### In GitHub
Both markdown files (`.md`) render automatically in GitHub with interactive Mermaid diagrams.

**View Links**:
- [Simplified Architecture](architecture-simple.md)
- [Detailed Architecture](architecture-diagram.md)

### In Presentations (PowerPoint, Keynote, Google Slides)
Use the PNG files for maximum compatibility:
- `architecture-simple.png` - Best for executive slides (clean, readable)
- `architecture.png` - Best for technical deep-dive slides

**Tips**:
- Set slide background to white or light gray (PNGs have transparent backgrounds)
- Add slide title: "Swarm TM System Architecture"
- Include source attribution: "Source: docs/architecture-simple.png"

### In Documentation (PDF, Word, Confluence)
Use the SVG files for scalable, print-quality diagrams:
- `architecture-simple.svg` - Scales perfectly to any size
- `architecture.svg` - High-quality technical diagram

**Tips**:
- SVG files can be scaled infinitely without pixelation
- Perfect for A3/A4 print documents
- Embed in Confluence pages for interactive zoom

### In Markdown/GitHub README
Reference the diagrams using relative paths:

```markdown
![Swarm TM Architecture](docs/architecture-simple.png)
*5-step end-to-end threat modeling process*
```

Or use Mermaid directly:
```markdown
\`\`\`mermaid
graph LR
    A[Input] --> B[Process] --> C[Output]
\`\`\`
```

## Architecture Highlights for Management

### Business Value
- **98% faster** threat modeling (20 min vs. 2-4 weeks)
- **$352K annual savings** vs. manual process (20 systems/year)
- **Superior coverage** through 13 threat actor perspectives + emergent insights
- **Zero vendor lock-in** (Ollama local, AWS Bedrock, or Anthropic API)

### Technical Innovation
1. **Stigmergic Coordination**: Ant colony optimization applied to threat modeling (novel approach)
2. **3-Layer Validation**: Defense-in-depth for AI-generated content (exploration → evaluation → adversarial)
3. **Vulnerability-Grounded**: Real CVE/EPSS/KEV data, not theoretical risks
4. **Living Intelligence**: Automatic persona updates from CISA KEV, MITRE ATT&CK

### Security & Compliance
- **No code execution**: IaC parsed, never executed (zero risk to production)
- **Data sovereignty**: 100% self-hosted option with Ollama (air-gapped environments)
- **Audit trail**: Archive system preserves historical threat models (compliance evidence)
- **Industry standards**: MITRE ATT&CK, CSA CII, CVSS, EPSS

## Architecture Evolution

### Current State (v2.0.0 - April 2026)
- ✅ 4 pipeline modes (Full Swarm, Quick Run, Single Agent, Stigmergic Swarm)
- ✅ 13 threat actor personas with security reasoning approach
- ✅ SQLite intel.db with CVE/EPSS/KEV data
- ✅ Living intelligence system (auto-updates from threat signals)
- ✅ 3 LLM providers (Ollama, Bedrock, Anthropic)
- ✅ React Flow interactive visualization
- ✅ Completeness-based mitigation with residual risk calculation

### Planned Enhancements (Q3-Q4 2026)
- 🔄 GCP and Azure support (multi-cloud threat modeling)
- 🔄 Multi-file analysis (analyze related IaC files together)
- 🔄 Background job submission (CI/CD integration)
- 🔄 Real-time streaming progress (WebSocket updates)
- 🔄 PDF/DOCX export (board-ready reports)

### Future Vision (2027+)
- 🎯 Live infrastructure analysis (connect to AWS APIs, not just IaC)
- 🎯 Historical risk tracking dashboard (time-series charts)
- 🎯 SIEM integration (Splunk, ElasticSearch, QRadar)
- 🎯 Red team scenario generator (Metasploit, Cobalt Strike)

## Contributing to Architecture Documentation

If you're updating the architecture:

1. **Update the Mermaid diagram** in the `.md` files
2. **Regenerate images** using mermaid-cli:
   ```bash
   cd docs
   npx -p @mermaid-js/mermaid-cli mmdc -i architecture-simple.md -o architecture-simple.png -w 2400 -H 1400
   npx -p @mermaid-js/mermaid-cli mmdc -i architecture-diagram.md -o architecture.png -w 3000 -H 2400
   ```
3. **Update this README** with any new sections or changes
4. **Commit all files** (markdown + images) together

## Questions?

For questions about the architecture:
- **Technical**: See [`CLAUDE.md`](../CLAUDE.md) for implementation details
- **Business**: See [`README.md`](../README.md) for value proposition and ROI
- **Security**: See security section in main README

---

**Last Updated**: 2026-04-27  
**Version**: 2.0.0  
**Maintained By**: Swarm TM Development Team
