import asyncio
from dataclasses import dataclass, field
from typing import Optional
from .cve_adapter import CVEAdapter, CVEMatch
from .abuse_kb_loader import AbuseKBLoader

@dataclass
class MatchedVuln:
    """
    A specific vulnerability or abuse pattern confirmed applicable
    to a specific resource in the uploaded IaC.
    """
    vuln_id: str            # CVE-YYYY-NNNNN or AWS-IMDS-001 etc
    vuln_type: str          # CVE / CLOUD_ABUSE
    name: str
    description: str
    resource_id: str
    resource_type: str
    kill_chain_phase: str
    technique_id: str
    technique_name: str
    cvss_score: float       # 0.0 for abuse patterns without CVSS
    epss_score: float       # 0.0 for abuse patterns
    in_kev: bool
    exploitation_difficulty: str   # LOW / MEDIUM / HIGH
    exploitation_commands: list[str]
    detection_gap: str
    cloudtrail_logged: bool
    guardduty_detects: bool
    poc_references: list[str]
    match_confidence: str   # CONFIRMED / PROBABLE / POSSIBLE
    match_reason: str
    remediation: str

    # Exploit and PoC source references (enriched from exploit_adapters)
    edb_ids:           list[str] = field(default_factory=list)
    edb_titles:        list[str] = field(default_factory=list)
    nuclei_templates:  list[str] = field(default_factory=list)
    nuclei_severity:   str = ""
    poc_available:     bool = False
    poc_sources:       list[str] = field(default_factory=list)

    @property
    def risk_score(self) -> float:
        """
        Composite risk score for prioritisation.
        Combines CVSS, EPSS, KEV, and exploitation difficulty.
        """
        base = self.cvss_score if self.cvss_score > 0 else 5.0
        epss_bonus = self.epss_score * 3.0
        kev_bonus = 2.0 if self.in_kev else 0.0
        diff_map = {'LOW': 1.5, 'MEDIUM': 1.0, 'HIGH': 0.5}
        diff_multiplier = diff_map.get(
            self.exploitation_difficulty, 1.0
        )
        detection_bonus = (
            1.5 if not self.cloudtrail_logged else 1.0
        )
        return min(10.0, (
            (base + epss_bonus + kev_bonus)
            * diff_multiplier
            * detection_bonus
        ) / 3.0)


@dataclass
class VulnRecord:
    """
    Enriched vulnerability record with exploit intelligence from multiple sources.
    Used for agent prompt injection with full CVE context and PoC references.
    """
    cve_id: str
    description: str
    cvss_score: float
    epss_score: float
    epss_percentile: float
    kev_listed: bool
    attck_technique: Optional[str] = None

    # Exploit and PoC source references
    edb_ids:           list[str] = field(default_factory=list)
    edb_titles:        list[str] = field(default_factory=list)
    nuclei_templates:  list[str] = field(default_factory=list)
    nuclei_severity:   Optional[str] = None
    ghsa_id:           Optional[str] = None
    packetstorm_refs:  list[str] = field(default_factory=list)
    affected_versions: list[str] = field(default_factory=list)
    patch_available:   bool = False
    poc_available:     bool = False
    poc_sources:       list[str] = field(default_factory=list)

    def exploit_priority_label(self) -> str:
        """Human-readable priority label for agent prompt injection."""
        if self.kev_listed and self.poc_available:
            return "CRITICAL — KEV-listed with public PoC confirmed"
        if self.kev_listed:
            return "HIGH — actively exploited per CISA KEV"
        if self.poc_available:
            return "HIGH — public exploit or PoC available"
        if self.epss_score > 0.5:
            return "MEDIUM-HIGH — EPSS exploitation probability above 50%"
        return "MEDIUM — no known public exploit at this time"

    def to_agent_context(self) -> str:
        """
        Formats this VulnRecord as a cited block for injection into
        a persona agent prompt. All source references are included.
        """
        lines = [
            f"  CVE: {self.cve_id}",
            f"  CVSS: {self.cvss_score:.1f}  "
            f"EPSS: {self.epss_score:.3f} "
            f"({self.epss_percentile:.0f}th percentile)",
            f"  Priority: {self.exploit_priority_label()}",
            f"  ATT&CK: {self.attck_technique or 'unmapped'}",
            f"  Description: {self.description[:200]}",
        ]
        if self.edb_ids:
            refs = ", ".join(f"EDB-{e}" for e in self.edb_ids)
            lines.append(f"  ExploitDB: {refs}")
        if self.nuclei_templates:
            lines.append(
                f"  Nuclei: {', '.join(self.nuclei_templates)}"
            )
        if self.ghsa_id:
            lines.append(f"  GitHub Advisory: {self.ghsa_id}")
        if self.packetstorm_refs:
            lines.append(f"  PacketStorm: {self.packetstorm_refs[0]}")
        return "\n".join(lines)


class VulnMatcher:
    """
    Matches specific CVEs and cloud abuse patterns to resources
    in the uploaded IaC asset graph.

    Matching logic:
    1. For each resource, check cloud abuse KB for applicable
       patterns based on resource type and config attributes.
    2. For software-running resources (RDS, Lambda, EKS), query
       CVE adapter for version-specific CVEs.
    3. Combine results, deduplicate, and rank by risk_score.
    """

    def __init__(self, nvd_api_key: Optional[str] = None):
        self.cve_adapter = CVEAdapter(nvd_api_key=nvd_api_key)
        self.abuse_loader = AbuseKBLoader()

    async def match(
        self,
        asset_graph: dict,
        cloud_signals: list,
        include_cve_lookup: bool = True,
    ) -> list[MatchedVuln]:
        matched = []

        # Match cloud abuse patterns from KB
        abuse_matches = self._match_abuse_patterns(
            asset_graph, cloud_signals
        )
        matched.extend(abuse_matches)

        # Match version-specific CVEs via NVD
        if include_cve_lookup:
            try:
                cve_matches = await self.cve_adapter\
                    .find_cves_for_asset_graph(asset_graph)
                for cve in cve_matches:
                    matched.append(self._cve_to_matched_vuln(cve))
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f'CVE lookup skipped: {e}'
                )

        # Deduplicate by vuln_id + resource_id
        seen = set()
        deduped = []
        for m in matched:
            key = f'{m.vuln_id}:{m.resource_id}'
            if key not in seen:
                seen.add(key)
                deduped.append(m)

        # Enrich CVE matches with exploit intelligence
        from .exploit_adapters import ExploitDBAdapter, NucleiTemplateAdapter
        _edb = ExploitDBAdapter()
        _nuclei = NucleiTemplateAdapter()

        for record in deduped:
            # Only enrich CVE entries, not cloud abuse patterns
            if not record.vuln_id.startswith('CVE-'):
                continue

            # Look up ExploitDB entries
            edb_results = _edb.lookup_by_cve(record.vuln_id)
            if edb_results:
                record.edb_ids = [r["edb_id"] for r in edb_results]
                record.edb_titles = [r["title"] for r in edb_results]
                record.poc_available = True
                record.poc_sources.extend(
                    [f"ExploitDB:{r['edb_id']}" for r in edb_results]
                )

            # Look up Nuclei templates
            nuclei_results = _nuclei.lookup_by_cve(record.vuln_id)
            if nuclei_results:
                record.nuclei_templates = [
                    r["template_id"] for r in nuclei_results
                ]
                record.nuclei_severity = nuclei_results[0].get("severity", "")
                record.poc_available = True
                record.poc_sources.extend(
                    [f"Nuclei:{r['template_id']}" for r in nuclei_results]
                )

        # Sort by risk_score descending
        deduped.sort(key=lambda m: m.risk_score, reverse=True)
        return deduped

    def _match_abuse_patterns(
        self,
        asset_graph: dict,
        cloud_signals: list,
    ) -> list[MatchedVuln]:
        signal_ids = {s.signal_id for s in cloud_signals}
        matched = []

        # Signal-to-abuse-ID mapping (using ATT&CK IDs from intel.db)
        SIGNAL_TO_ABUSE = {
            'IMDS_V1_ENABLED': ['ATTCK-T1552-005'],  # Cloud Instance Metadata API
            'IAM_S3_WILDCARD': ['ATTCK-T1530', 'ATTCK-T1537'],  # Data from Cloud Storage, Transfer Data to Cloud Account
            'IAM_PRIVILEGE_ESCALATION_ACTIONS': [
                'ATTCK-T1548',  # Abuse Elevation Control Mechanism
                'ATTCK-T1098',  # Account Manipulation
                'ATTCK-T1136-003'  # Create Account: Cloud Account
            ],
            'CLOUDTRAIL_NO_S3_DATA_EVENTS': [
                'ATTCK-T1562-008'  # Impair Defenses: Disable Cloud Logs
            ],
            'SHARED_IAM_INSTANCE_PROFILE': [
                'ATTCK-T1078-004'  # Valid Accounts: Cloud Accounts
            ],
            'S3_NO_RESOURCE_POLICY': ['ATTCK-T1530'],  # Data from Cloud Storage
            'PUBLIC_INGRESS_OPEN': [
                'ATTCK-T1190'  # Exploit Public-Facing Application
            ],
            'UNRESTRICTED_EGRESS': [
                'ATTCK-T1567'  # Exfiltration Over Web Service (unrestricted egress enables this)
            ],
        }

        for signal in cloud_signals:
            abuse_ids = SIGNAL_TO_ABUSE.get(signal.signal_id, [])
            for abuse_id in abuse_ids:
                abuse = self.abuse_loader.get_abuse_by_id(abuse_id)
                if not abuse:
                    continue
                # Match directly to signal's resource
                # Signal already has the specific resource_id from signal extractor
                matched.append(MatchedVuln(
                    vuln_id=abuse_id,
                    vuln_type='CLOUD_ABUSE',
                    name=abuse.get('name', ''),
                    description=abuse.get('description', ''),
                    resource_id=signal.resource_id,
                    resource_type=signal.resource_type,
                    kill_chain_phase=abuse.get(
                        'kill_chain_phase', ''),
                    technique_id=abuse.get('technique_id', ''),
                    technique_name=abuse.get(
                        'technique_name', ''),
                    cvss_score=float(
                        abuse.get('cvss_equivalent', 7.0)
                    ),
                    epss_score=0.0,
                    in_kev=False,
                    exploitation_difficulty=abuse.get(
                        'exploitation_difficulty', 'MEDIUM'
                    ),
                    exploitation_commands=abuse.get(
                        'exploitation_commands', []
                    ),
                    detection_gap=abuse.get(
                        'detection_gap', ''
                    ),
                    cloudtrail_logged=abuse.get(
                        'cloudtrail_logged', True
                    ),
                    guardduty_detects=bool(
                        abuse.get('guardduty_finding')
                    ),
                    poc_references=abuse.get(
                        'references', []
                    ),
                    match_confidence='CONFIRMED',
                    match_reason=(
                        f'Signal {signal.signal_id} detected: '
                        f'{signal.detail}'
                    ),
                    remediation=abuse.get('remediation', ''),
                ))

        # Also match by resource type regardless of signals
        for asset in asset_graph.get('assets', []):
            asset_type = asset.get('type', '')
            type_abuses = self.abuse_loader\
                .get_abuses_for_resource_type(asset_type)
            for abuse in type_abuses:
                abuse_id = abuse.get('abuse_id', '')
                # Only add if not already matched via signal
                already = any(
                    m.vuln_id == abuse_id
                    and m.resource_id == asset.get('id', '')
                    for m in matched
                )
                if not already:
                    matched.append(MatchedVuln(
                        vuln_id=abuse_id,
                        vuln_type='CLOUD_ABUSE',
                        name=abuse.get('name', ''),
                        description=abuse.get('description', ''),
                        resource_id=asset.get('id', ''),
                        resource_type=asset_type,
                        kill_chain_phase=abuse.get(
                            'kill_chain_phase', ''),
                        technique_id=abuse.get('technique_id', ''),
                        technique_name=abuse.get(
                            'technique_name', ''),
                        cvss_score=float(
                            abuse.get('cvss_equivalent', 5.0)
                        ),
                        epss_score=0.0,
                        in_kev=False,
                        exploitation_difficulty=abuse.get(
                            'exploitation_difficulty', 'MEDIUM'
                        ),
                        exploitation_commands=abuse.get(
                            'exploitation_commands', []
                        ),
                        detection_gap=abuse.get(
                            'detection_gap', ''
                        ),
                        cloudtrail_logged=abuse.get(
                            'cloudtrail_logged', True
                        ),
                        guardduty_detects=bool(
                            abuse.get('guardduty_finding')
                        ),
                        poc_references=abuse.get(
                            'references', []
                        ),
                        match_confidence='PROBABLE',
                        match_reason=(
                            f'Resource type {asset_type} is '
                            f'affected by this abuse pattern'
                        ),
                        remediation=abuse.get('remediation', ''),
                    ))

        return matched

    def _cve_to_matched_vuln(self, cve: CVEMatch) -> MatchedVuln:
        return MatchedVuln(
            vuln_id=cve.cve_id,
            vuln_type='CVE',
            name=cve.cve_id,
            description=cve.description,
            resource_id=cve.matched_resource_id,
            resource_type=cve.matched_resource_type,
            kill_chain_phase='initial_access',
            technique_id=(
                cve.technique_ids[0]
                if cve.technique_ids else 'T1190'
            ),
            technique_name='Exploit Public-Facing Application',
            cvss_score=cve.cvss_v3_score,
            epss_score=cve.epss_score,
            in_kev=cve.in_kev,
            exploitation_difficulty=(
                'LOW' if cve.cvss_v3_score >= 9.0
                else 'MEDIUM' if cve.cvss_v3_score >= 7.0
                else 'HIGH'
            ),
            exploitation_commands=[],
            detection_gap='',
            cloudtrail_logged=True,
            guardduty_detects=False,
            poc_references=cve.poc_references,
            match_confidence='CONFIRMED',
            match_reason=cve.match_reason,
            remediation=cve.remediation,
        )

    def format_for_prompt(
        self,
        matched_vulns: list[MatchedVuln],
        max_vulns: int = 10,
    ) -> str:
        if not matched_vulns:
            return (
                'VULNERABILITY SCAN: No specific CVEs or cloud '
                'abuse patterns matched this infrastructure.'
            )
        top = matched_vulns[:max_vulns]
        lines = [
            'MATCHED VULNERABILITIES AND ABUSE PATTERNS:',
            'These are specific CVEs and documented cloud abuse',
            'patterns confirmed applicable to this infrastructure.',
            'Use these as the basis for attack path generation.',
            'Prefer these over generic ATT&CK technique reasoning.',
            '',
        ]
        kev = [v for v in top if v.in_kev]
        non_kev = [v for v in top if not v.in_kev]
        if kev:
            lines.append(
                f'ACTIVELY EXPLOITED (CISA KEV) — {len(kev)} matches:'
            )
            for v in kev:
                lines.extend(
                    self._format_single(v)
                )
        if non_kev:
            lines.append(
                f'HIGH/CRITICAL SEVERITY — {len(non_kev)} matches:'
            )
            for v in non_kev:
                lines.extend(self._format_single(v))
        return '\n'.join(lines)

    def _format_single(
        self, v: MatchedVuln
    ) -> list[str]:
        lines = [
            f'  [{v.vuln_id}] {v.name}',
            f'  Resource: {v.resource_id} ({v.resource_type})',
            f'  ATT&CK: {v.technique_id} | '
            f'Phase: {v.kill_chain_phase}',
            f'  Risk score: {v.risk_score:.1f}/10 | '
            f'CVSS: {v.cvss_score} | '
            f'Difficulty: {v.exploitation_difficulty} | '
            f'KEV: {v.in_kev}',
            f'  Confidence: {v.match_confidence} — {v.match_reason}',
        ]
        if v.exploitation_commands:
            lines.append('  Exploitation commands:')
            for cmd in v.exploitation_commands[:3]:
                lines.append(f'    {cmd}')
        if v.detection_gap:
            lines.append(
                f'  Detection gap: {v.detection_gap}'
            )
        if v.poc_references:
            lines.append(
                f'  Reference: {v.poc_references[0]}'
            )
        lines.append('')
        return lines
