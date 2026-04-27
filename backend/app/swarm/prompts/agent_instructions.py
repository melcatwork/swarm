"""
agent_instructions.py

Instruction blocks injected into persona agent prompts to direct
them to use real vulnerability references when building attack paths.
"""

VULN_GROUNDED_INSTRUCTION = """
You have been provided with a vulnerability intelligence context block
above. This block lists real documented vulnerabilities affecting the
assets in this infrastructure, with citations to public sources
including ExploitDB, Nuclei templates, CISA KEV, and EPSS scores.

MANDATORY RULES for attack path construction:

1. PRIORITISE referenced vulnerabilities. If an asset has a CVE with
   an ExploitDB or Nuclei template reference, prefer that over a
   generic misconfiguration finding of the same class.

2. CITE your sources in every step that uses a known vulnerability.
   Include the CVE ID and at least one source reference from the
   context block — EDB-ID, GHSA-ID, Nuclei template ID, or KEV flag.

3. KEV-listed vulnerabilities are actively exploited in the wild.
   Your persona would know about these and always prioritise them
   over non-KEV findings of equivalent CVSS score.

4. EPSS above 0.7 means greater than 70 percent probability of
   exploitation in the next 30 days. Weight these heavily when
   choosing which path to build.

5. EOL runtimes with no matched CVEs should be treated as an
   unpatched unknown vulnerability surface — note this explicitly
   in the relevant attack path step.

6. If no CVEs are matched for an asset, reason about:
   - Misconfiguration patterns specific to your persona doctrine
   - Network exposure visible in the open ports or public endpoint
   - IAM policy weaknesses visible in the serialised IaC

7. Every attack path step output MUST include these fields where
   a CVE applies:
     cve_id:       the CVE identifier e.g. CVE-2021-44228
     exploit_ref:  the primary PoC reference e.g. EDB-50592
     epss:         the EPSS score as a float e.g. 0.973
     kev_listed:   true or false

   Set these fields to null for misconfiguration-only steps.

Your goal is attack paths that a client can hand to their developers
with the instruction: fix this specific CVE on this specific asset.
Not generic advice — specific, cited, actionable findings.
"""
