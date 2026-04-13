"""
Defense in Depth and Cyber by Design mitigation layers.

This module implements a multi-layered security approach with:
- Preventive controls (stop attacks before they occur)
- Detective controls (identify attacks in progress)
- Corrective controls (respond to and recover from attacks)
- Administrative controls (policies, procedures, training)

Each attack technique has multiple mitigations across different layers,
implementing true defense-in-depth principles.
"""

from typing import Dict, List
from enum import Enum


class DefenseLayer(str, Enum):
    """Defense in depth layers."""
    PREVENTIVE = "preventive"  # Stop attack before it happens
    DETECTIVE = "detective"    # Detect attack in progress
    CORRECTIVE = "corrective"  # Respond to and recover from attack
    ADMINISTRATIVE = "administrative"  # Policies, procedures, training


class MitigationPriority(str, Enum):
    """Mitigation implementation priority."""
    CRITICAL = "critical"  # Implement immediately
    HIGH = "high"          # Implement within 30 days
    MEDIUM = "medium"      # Implement within 90 days
    LOW = "low"            # Implement as resources allow


# Comprehensive defense-in-depth mitigations for AWS cloud
# Each technique has multiple mitigations across different layers
DEFENSE_IN_DEPTH_MITIGATIONS = {
    "T1078.004": {  # Cloud Accounts
        DefenseLayer.PREVENTIVE: [
            {
                "mitigation_id": "M1078.004-P1",
                "mitigation_name": "Enforce MFA on All Cloud Accounts",
                "description": "Require multi-factor authentication for all IAM users, root account, and federated access. Use hardware MFA tokens for privileged accounts. Implement conditional access policies that enforce MFA based on risk level.",
                "aws_service_action": "Enable MFA on root account and all IAM users via IAM console. Configure AWS SSO with MFA enforcement. Use SCPs to deny API calls without MFA: aws:MultiFactorAuthPresent=false",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1-2 days",
                "effectiveness": "High - Blocks 90%+ of credential-based attacks",
            },
            {
                "mitigation_id": "M1078.004-P2",
                "mitigation_name": "Implement Least Privilege IAM Policies",
                "description": "Grant minimum permissions required for each role. Use permission boundaries to limit maximum permissions. Implement session policies for temporary elevated access. Review and remove unused permissions quarterly.",
                "aws_service_action": "Use IAM Access Analyzer to identify overly permissive policies. Implement permission boundaries. Create fine-grained policies with explicit Allow and Deny statements. Use aws:PrincipalOrgID conditions.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Medium - 1-2 weeks per application",
                "effectiveness": "High - Reduces blast radius of compromised credentials",
            },
            {
                "mitigation_id": "M1078.004-P3",
                "mitigation_name": "Restrict Access by IP and Context",
                "description": "Use IAM policy conditions to restrict access based on source IP, time of day, and request context. Implement VPN or Private Link for sensitive operations. Deny access from known malicious IP ranges.",
                "aws_service_action": "Add IAM policy conditions: aws:SourceIp, aws:CurrentTime, aws:SecureTransport. Use AWS WAF IP sets for known threats. Implement VPC endpoints for private API access.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week",
                "effectiveness": "Medium - Reduces attack surface",
            },
        ],
        DefenseLayer.DETECTIVE: [
            {
                "mitigation_id": "M1078.004-D1",
                "mitigation_name": "Enable Comprehensive CloudTrail Logging",
                "description": "Log all API calls across all regions. Enable CloudTrail Insights for anomaly detection. Send logs to centralized S3 bucket with encryption and MFA Delete. Forward logs to SIEM for correlation.",
                "aws_service_action": "Enable organization trail with S3 encryption and log validation. Enable CloudTrail Insights. Configure CloudWatch Logs for real-time analysis. Use EventBridge rules for alerting.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1-2 days",
                "effectiveness": "High - Provides visibility into all account activity",
            },
            {
                "mitigation_id": "M1078.004-D2",
                "mitigation_name": "Monitor Authentication Anomalies with GuardDuty",
                "description": "Enable GuardDuty to detect suspicious authentication patterns, compromised credentials, and unusual API calls. Configure findings to trigger automated response workflows. Monitor for impossible travel scenarios.",
                "aws_service_action": "Enable GuardDuty in all accounts and regions. Configure findings severity thresholds. Set up EventBridge rules to trigger Lambda functions for automated response. Export findings to Security Hub.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1 day",
                "effectiveness": "High - Detects known attack patterns",
            },
            {
                "mitigation_id": "M1078.004-D3",
                "mitigation_name": "Implement Real-Time IAM Activity Monitoring",
                "description": "Create CloudWatch alarms for critical IAM changes: CreateUser, AttachUserPolicy, CreateAccessKey, AssumeRole from unusual principals. Alert on console sign-ins from new locations.",
                "aws_service_action": "Create CloudWatch metric filters for IAM API calls. Configure SNS topics for critical alerts. Use Lambda for automated response (e.g., suspend user, trigger incident response).",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Low - 2-3 days",
                "effectiveness": "High - Rapid detection of account manipulation",
            },
        ],
        DefenseLayer.CORRECTIVE: [
            {
                "mitigation_id": "M1078.004-C1",
                "mitigation_name": "Automated Credential Rotation and Revocation",
                "description": "Automatically rotate compromised credentials. Revoke suspicious sessions immediately. Use AWS Systems Manager Parameter Store or Secrets Manager for automated rotation. Implement break-glass procedures for emergency access.",
                "aws_service_action": "Use Secrets Manager with automatic rotation. Create Lambda functions to revoke access keys on GuardDuty findings. Implement Systems Manager Session Manager for break-glass access.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week",
                "effectiveness": "High - Limits exposure time of compromised credentials",
            },
            {
                "mitigation_id": "M1078.004-C2",
                "mitigation_name": "Incident Response Playbooks",
                "description": "Develop and test incident response procedures for compromised credentials. Include isolation steps, forensic data collection, and communication plans. Conduct regular tabletop exercises.",
                "aws_service_action": "Create AWS Systems Manager Automation runbooks for common incidents. Use AWS Step Functions for orchestration. Store playbooks in Wiki or Confluence.",
                "priority": MitigationPriority.MEDIUM,
                "implementation_effort": "High - 2-4 weeks",
                "effectiveness": "Medium - Reduces mean time to respond (MTTR)",
            },
        ],
        DefenseLayer.ADMINISTRATIVE: [
            {
                "mitigation_id": "M1078.004-A1",
                "mitigation_name": "Security Awareness Training",
                "description": "Conduct quarterly phishing simulations and security training. Train developers on secure credential handling. Require security training for cloud console access.",
                "aws_service_action": "Use AWS Training and Certification resources. Implement phishing simulation tools. Track completion in LMS. Make training prerequisite for IAM user creation.",
                "priority": MitigationPriority.MEDIUM,
                "implementation_effort": "Low - Ongoing",
                "effectiveness": "Medium - Reduces human error",
            },
            {
                "mitigation_id": "M1078.004-A2",
                "mitigation_name": "Regular Access Reviews and Audits",
                "description": "Conduct quarterly access reviews to remove unused accounts and permissions. Implement automated reports for access certification. Document all privileged access approvals.",
                "aws_service_action": "Use IAM Access Analyzer and AWS Config for compliance reports. Create Lambda functions for automated access reviews. Use AWS Audit Manager for continuous auditing.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week setup, ongoing reviews",
                "effectiveness": "Medium - Reduces attack surface over time",
            },
        ],
    },

    "T1190": {  # Exploit Public-Facing Application
        DefenseLayer.PREVENTIVE: [
            {
                "mitigation_id": "M1190-P1",
                "mitigation_name": "Deploy AWS WAF with Managed Rule Groups",
                "description": "Place all public-facing applications behind AWS WAF. Enable managed rule groups for OWASP Top 10, known bad inputs, and IP reputation. Configure rate limiting to prevent brute force attacks.",
                "aws_service_action": "Create WAF WebACL with AWS Managed Rules (Core, OWASP, IP Reputation). Associate with CloudFront, ALB, or API Gateway. Enable request/response logging to S3 or CloudWatch.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1-2 days",
                "effectiveness": "High - Blocks known exploits and attack patterns",
            },
            {
                "mitigation_id": "M1190-P2",
                "mitigation_name": "Implement Application Security Best Practices",
                "description": "Use parameterized queries to prevent SQL injection. Validate and sanitize all user inputs. Implement proper authentication and session management. Keep all frameworks and dependencies up to date.",
                "aws_service_action": "Use AWS CodeGuru for code review. Implement AWS Secrets Manager for credentials. Use RDS with IAM authentication. Regular patching with Systems Manager Patch Manager.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "High - Varies by application",
                "effectiveness": "High - Reduces exploitable vulnerabilities",
            },
            {
                "mitigation_id": "M1190-P3",
                "mitigation_name": "Network Segmentation and Access Controls",
                "description": "Place web tier in public subnet, application tier in private subnet, and data tier in isolated subnet. Use security groups as stateful firewalls. Implement network ACLs for subnet-level protection.",
                "aws_service_action": "Design VPC with public/private/data subnets. Configure security groups with least-privilege rules. Use AWS Network Firewall for deep packet inspection. Enable VPC Flow Logs.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week for new apps",
                "effectiveness": "High - Limits blast radius",
            },
        ],
        DefenseLayer.DETECTIVE: [
            {
                "mitigation_id": "M1190-D1",
                "mitigation_name": "Web Application Monitoring and Logging",
                "description": "Enable detailed application logging. Send logs to centralized SIEM. Monitor for suspicious patterns: SQL injection attempts, XSS, authentication failures. Alert on unusual traffic patterns.",
                "aws_service_action": "Enable ALB access logs to S3. Use CloudWatch Logs for application logs. Create CloudWatch alarms for HTTP 4xx/5xx errors. Use AWS WAF logging for attack analysis.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Low - 2-3 days",
                "effectiveness": "High - Early warning of attacks",
            },
            {
                "mitigation_id": "M1190-D2",
                "mitigation_name": "Continuous Vulnerability Scanning",
                "description": "Scan applications for vulnerabilities weekly. Use AWS Inspector for EC2 instances and container images. Integrate SAST/DAST tools in CI/CD pipeline. Track and remediate findings.",
                "aws_service_action": "Enable Amazon Inspector automatic scanning. Integrate security scanning in CodePipeline. Use AWS Security Hub for centralized findings. Set up automated ticketing for high-severity issues.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week",
                "effectiveness": "High - Identifies vulnerabilities before exploitation",
            },
        ],
        DefenseLayer.CORRECTIVE: [
            {
                "mitigation_id": "M1190-C1",
                "mitigation_name": "Automated Patching and Remediation",
                "description": "Implement automated patching for OS and application dependencies. Use AWS Systems Manager for patch compliance. Deploy security updates within 24 hours of release for critical vulnerabilities.",
                "aws_service_action": "Configure Systems Manager Patch Manager with maintenance windows. Use AWS CloudFormation for immutable infrastructure. Implement blue-green deployments for rapid rollback.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Medium - 1-2 weeks",
                "effectiveness": "High - Reduces window of exposure",
            },
        ],
        DefenseLayer.ADMINISTRATIVE: [
            {
                "mitigation_id": "M1190-A1",
                "mitigation_name": "Secure Development Lifecycle (SDL)",
                "description": "Implement security requirements in design phase. Conduct threat modeling for new features. Perform security code reviews. Run penetration tests before production deployment.",
                "aws_service_action": "Use AWS Well-Architected Framework security pillar. Implement CodeGuru Security for automated code review. Conduct quarterly penetration tests. Document security requirements in tickets.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "High - Cultural change, 3-6 months",
                "effectiveness": "High - Prevents vulnerabilities from reaching production",
            },
        ],
    },

    "T1530": {  # Data from Cloud Storage Object
        DefenseLayer.PREVENTIVE: [
            {
                "mitigation_id": "M1530-P1",
                "mitigation_name": "Enable S3 Block Public Access",
                "description": "Enable S3 Block Public Access at account and bucket level to prevent accidental public exposure. Review existing public buckets and restrict access. Use S3 Access Analyzer to identify unintended access.",
                "aws_service_action": "Enable S3 Block Public Access at account level. Use S3 Access Analyzer. Implement bucket policies with aws:PrincipalOrgID conditions. Use VPC endpoints for private S3 access.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1 day",
                "effectiveness": "High - Prevents most data exfiltration scenarios",
            },
            {
                "mitigation_id": "M1530-P2",
                "mitigation_name": "Implement Least Privilege S3 Access",
                "description": "Grant minimum required permissions for S3 bucket access. Use IAM policies, bucket policies, and ACLs together. Implement conditions for source VPC, IP, or MFA. Review permissions quarterly.",
                "aws_service_action": "Use IAM Access Analyzer for S3. Implement S3 bucket policies with conditions. Use SCPs to enforce encryption in transit. Regular access reviews with AWS Config rules.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Medium - 1-2 weeks",
                "effectiveness": "High - Reduces unauthorized access",
            },
            {
                "mitigation_id": "M1530-P3",
                "mitigation_name": "Enable S3 Encryption at Rest",
                "description": "Encrypt all S3 objects with SSE-S3, SSE-KMS, or SSE-C. Use KMS for sensitive data with key rotation. Implement bucket policies to deny unencrypted uploads. Use AWS Macie for data classification.",
                "aws_service_action": "Enable default encryption on all buckets with aws:kms. Use bucket policies to deny PutObject without encryption. Enable S3 Object Lock for immutability. Use Macie for sensitive data discovery.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Low - 2-3 days",
                "effectiveness": "High - Protects data at rest",
            },
        ],
        DefenseLayer.DETECTIVE: [
            {
                "mitigation_id": "M1530-D1",
                "mitigation_name": "Enable S3 Access Logging and Monitoring",
                "description": "Enable S3 server access logging for all buckets. Forward logs to centralized bucket. Create CloudWatch alarms for suspicious patterns: bulk downloads, unusual access times, access from new IPs.",
                "aws_service_action": "Enable S3 server access logging. Use CloudTrail S3 data events. Create CloudWatch metric filters for GetObject requests. Set up GuardDuty S3 protection. Use EventBridge for real-time alerting.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1-2 days",
                "effectiveness": "High - Detects data access anomalies",
            },
            {
                "mitigation_id": "M1530-D2",
                "mitigation_name": "Monitor with AWS Macie",
                "description": "Use AWS Macie to discover and classify sensitive data in S3. Monitor for unusual data access patterns. Alert on discovery of PII, credentials, or financial data in unexpected locations.",
                "aws_service_action": "Enable Macie with automated discovery jobs. Configure custom data identifiers for organization-specific sensitive data. Set up Macie findings to Security Hub. Create automated remediation for sensitive data exposure.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week",
                "effectiveness": "High - Identifies sensitive data exposure",
            },
        ],
        DefenseLayer.CORRECTIVE: [
            {
                "mitigation_id": "M1530-C1",
                "mitigation_name": "Implement S3 Versioning and Object Lock",
                "description": "Enable S3 versioning to prevent data deletion. Use S3 Object Lock for compliance and ransomware protection. Implement MFA Delete for additional protection. Regular backup to separate account.",
                "aws_service_action": "Enable versioning on all buckets. Configure Object Lock with retention policies. Enable MFA Delete on critical buckets. Use S3 Replication to backup account. Implement lifecycle policies.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Low - 2-3 days",
                "effectiveness": "High - Enables recovery from incidents",
            },
        ],
        DefenseLayer.ADMINISTRATIVE: [
            {
                "mitigation_id": "M1530-A1",
                "mitigation_name": "Data Classification and Handling Policy",
                "description": "Implement data classification scheme (public, internal, confidential, restricted). Define handling requirements for each class. Train employees on proper S3 usage. Regular compliance audits.",
                "aws_service_action": "Use resource tags for data classification. Implement tag-based access control. Use AWS Organizations tag policies. Document policies in Wiki. Automate compliance checks with AWS Config.",
                "priority": MitigationPriority.MEDIUM,
                "implementation_effort": "High - 2-3 months",
                "effectiveness": "Medium - Long-term risk reduction",
            },
        ],
    },

    "T1098": {  # Account Manipulation
        DefenseLayer.PREVENTIVE: [
            {
                "mitigation_id": "M1098-P1",
                "mitigation_name": "Implement SCPs to Restrict IAM Changes",
                "description": "Use AWS Organizations Service Control Policies to prevent unauthorized IAM modifications. Restrict CreateUser, AttachUserPolicy, and PutUserPolicy actions to specific roles. Implement break-glass procedures.",
                "aws_service_action": "Create SCPs that deny IAM write actions except for specific admin roles. Use condition keys like aws:PrincipalOrgID and aws:RequestedRegion. Test SCPs in non-production first.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Medium - 1 week",
                "effectiveness": "High - Prevents unauthorized privilege escalation",
            },
            {
                "mitigation_id": "M1098-P2",
                "mitigation_name": "Implement IAM Permission Boundaries",
                "description": "Use permission boundaries to set maximum permissions for IAM entities. Require all IAM users and roles to have boundaries. Implement centralized permission boundary management.",
                "aws_service_action": "Create standard permission boundaries for different roles. Use SCPs to enforce boundary attachment. Implement Lambda functions to automatically attach boundaries to new IAM entities.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "High - 2-3 weeks",
                "effectiveness": "High - Limits potential damage",
            },
        ],
        DefenseLayer.DETECTIVE: [
            {
                "mitigation_id": "M1098-D1",
                "mitigation_name": "Real-Time IAM Change Monitoring",
                "description": "Monitor all IAM API calls in real-time. Alert on CreateUser, AttachUserPolicy, CreateAccessKey, and AssumeRole. Correlate with user context and behavior baselines.",
                "aws_service_action": "Create CloudWatch Events rules for IAM API calls. Use EventBridge to trigger Lambda for automated analysis. Integrate with SIEM. Set up SNS notifications for critical changes.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Medium - 1 week",
                "effectiveness": "High - Rapid detection of account manipulation",
            },
            {
                "mitigation_id": "M1098-D2",
                "mitigation_name": "Enable AWS Config for IAM Compliance",
                "description": "Use AWS Config rules to detect non-compliant IAM configurations. Monitor for users without MFA, over-permissive policies, and unused credentials. Generate compliance reports.",
                "aws_service_action": "Enable AWS Config with managed rules: iam-user-mfa-enabled, iam-user-unused-credentials-check, iam-policy-no-statements-with-admin-access. Create custom rules for organization policies.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Low - 2-3 days",
                "effectiveness": "High - Continuous compliance monitoring",
            },
        ],
        DefenseLayer.CORRECTIVE: [
            {
                "mitigation_id": "M1098-C1",
                "mitigation_name": "Automated IAM Remediation",
                "description": "Automatically remediate non-compliant IAM configurations. Revoke suspicious permissions. Disable compromised users. Implement automated rollback of unauthorized changes.",
                "aws_service_action": "Use AWS Config remediation actions with Systems Manager Automation. Create Lambda functions for custom remediation. Implement approval workflows for sensitive changes. Log all automated actions.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "High - 2-4 weeks",
                "effectiveness": "High - Reduces exposure time",
            },
        ],
        DefenseLayer.ADMINISTRATIVE: [
            {
                "mitigation_id": "M1098-A1",
                "mitigation_name": "Regular IAM Access Reviews",
                "description": "Conduct quarterly reviews of all IAM users, roles, and policies. Remove unused accounts and permissions. Certify that all access is still required. Document review process and findings.",
                "aws_service_action": "Use IAM credential reports and access advisor. Create automated reports with Lambda and SES. Implement approval workflow for access continuation. Use AWS Audit Manager for audit trail.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week setup, ongoing",
                "effectiveness": "Medium - Reduces attack surface over time",
            },
        ],
    },

    "T1133": {  # External Remote Services
        DefenseLayer.PREVENTIVE: [
            {
                "mitigation_id": "M1133-P1",
                "mitigation_name": "Use AWS Systems Manager Session Manager",
                "description": "Replace SSH/RDP access with Systems Manager Session Manager for secure shell access without exposing ports. No bastion hosts required. All sessions logged to CloudTrail.",
                "aws_service_action": "Install SSM agent on EC2 instances. Create IAM policies for session permissions. Configure Session Manager preferences for logging to S3/CloudWatch. Remove SSH/RDP from security groups.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Medium - 1-2 weeks",
                "effectiveness": "High - Eliminates exposed management interfaces",
            },
            {
                "mitigation_id": "M1133-P2",
                "mitigation_name": "Implement Zero Trust Network Access",
                "description": "Use AWS Client VPN with certificate-based authentication and MFA. Implement Private Link for internal service access. Restrict security groups to known IP ranges for legacy remote access.",
                "aws_service_action": "Deploy AWS Client VPN with Mutual TLS. Use AWS Directory Service for authentication. Implement network ACLs for subnet isolation. Use VPC endpoints for private access to AWS services.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "High - 2-4 weeks",
                "effectiveness": "High - Secure remote access",
            },
        ],
        DefenseLayer.DETECTIVE: [
            {
                "mitigation_id": "M1133-D1",
                "mitigation_name": "Monitor Remote Access Sessions",
                "description": "Log all remote access sessions to centralized SIEM. Alert on new session sources, unusual access times, and privilege escalation attempts. Use VPC Flow Logs for network visibility.",
                "aws_service_action": "Enable Session Manager logging to S3 and CloudWatch. Create CloudWatch alarms for remote access from new IPs. Enable VPC Flow Logs. Use GuardDuty for threat intelligence correlation.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Low - 2-3 days",
                "effectiveness": "High - Detects unauthorized access",
            },
        ],
        DefenseLayer.CORRECTIVE: [
            {
                "mitigation_id": "M1133-C1",
                "mitigation_name": "Automated Session Termination",
                "description": "Automatically terminate sessions based on risk signals: access from unusual locations, failed authentication attempts, or suspicious commands. Implement session timeout policies.",
                "aws_service_action": "Use Lambda functions triggered by GuardDuty findings to terminate sessions. Configure Session Manager with idle timeout and max duration. Implement automated incident response workflows.",
                "priority": MitigationPriority.MEDIUM,
                "implementation_effort": "Medium - 1-2 weeks",
                "effectiveness": "Medium - Limits attacker dwell time",
            },
        ],
        DefenseLayer.ADMINISTRATIVE: [
            {
                "mitigation_id": "M1133-A1",
                "mitigation_name": "Remote Access Policy and Training",
                "description": "Define and enforce remote access policies. Require MFA and secure endpoints. Train staff on secure remote work practices. Regular policy reviews and updates.",
                "aws_service_action": "Document remote access requirements. Use AWS IAM conditions to enforce policies. Implement AWS SSO for centralized access management. Track compliance with AWS Config.",
                "priority": MitigationPriority.MEDIUM,
                "implementation_effort": "Medium - 2-4 weeks",
                "effectiveness": "Medium - Reduces human error",
            },
        ],
    },

    "T1562.001": {  # Impair Defenses: Disable or Modify Tools
        DefenseLayer.PREVENTIVE: [
            {
                "mitigation_id": "M1562.001-P1",
                "mitigation_name": "Use SCPs to Protect Security Services",
                "description": "Implement Service Control Policies that prevent disabling CloudTrail, GuardDuty, Config, Security Hub, and Macie. Deny StopLogging, DeleteTrail, DisableSecurityHub, and similar API calls.",
                "aws_service_action": "Create SCPs with explicit deny for security service modifications. Apply to all OUs except designated security team. Use condition keys to allow only specific admin roles. Test thoroughly.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1-2 days",
                "effectiveness": "High - Prevents security tool tampering",
            },
            {
                "mitigation_id": "M1562.001-P2",
                "mitigation_name": "Implement Security Service Redundancy",
                "description": "Deploy logging and monitoring to multiple accounts and regions. Use AWS Control Tower for centralized governance. Implement cross-account log aggregation. Use immutable log storage.",
                "aws_service_action": "Enable organization trail across all accounts. Use S3 Cross-Region Replication for logs. Implement S3 Object Lock on log buckets. Deploy GuardDuty and Security Hub in delegated admin account.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1-2 weeks",
                "effectiveness": "High - Ensures logging continuity",
            },
        ],
        DefenseLayer.DETECTIVE: [
            {
                "mitigation_id": "M1562.001-D1",
                "mitigation_name": "Monitor Security Service Status Changes",
                "description": "Create real-time alerts for any attempts to disable security services. Monitor CloudTrail for StopLogging, DeleteTrail, DisableGuardDuty, and DisableSecurityHub API calls. Alert security team immediately.",
                "aws_service_action": "Create CloudWatch Events rules for security service API calls. Use EventBridge to trigger Lambda for immediate notification. Integrate with incident response tools. Generate high-severity tickets.",
                "priority": MitigationPriority.CRITICAL,
                "implementation_effort": "Low - 1 day",
                "effectiveness": "High - Immediate threat detection",
            },
            {
                "mitigation_id": "M1562.001-D2",
                "mitigation_name": "Continuous Security Service Health Checks",
                "description": "Implement automated health checks for all security services. Verify CloudTrail is logging, GuardDuty is enabled, Config is recording. Alert on any service degradation or outage.",
                "aws_service_action": "Create Lambda function to check security service status every 5 minutes. Use CloudWatch Synthetics for API checks. Generate CloudWatch alarms for service failures. Implement automated recovery.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "Medium - 1 week",
                "effectiveness": "High - Detects service failures",
            },
        ],
        DefenseLayer.CORRECTIVE: [
            {
                "mitigation_id": "M1562.001-C1",
                "mitigation_name": "Automated Security Service Recovery",
                "description": "Automatically re-enable disabled security services. Implement self-healing infrastructure for monitoring and logging. Escalate to security team when automation fails.",
                "aws_service_action": "Use AWS Config remediation to re-enable services. Create Lambda functions for automated recovery. Use Step Functions for complex recovery workflows. Log all recovery actions to Security Hub.",
                "priority": MitigationPriority.HIGH,
                "implementation_effort": "High - 2-3 weeks",
                "effectiveness": "High - Minimizes security blind spots",
            },
        ],
        DefenseLayer.ADMINISTRATIVE: [
            {
                "mitigation_id": "M1562.001-A1",
                "mitigation_name": "Security Service Governance Policy",
                "description": "Document requirements for security service availability. Define escalation procedures for service failures. Conduct regular disaster recovery drills. Maintain runbooks for service recovery.",
                "aws_service_action": "Create policy documents and runbooks. Store in centralized wiki or Confluence. Use AWS Organizations tag policies to enforce standards. Regular reviews and updates. Include in onboarding training.",
                "priority": MitigationPriority.MEDIUM,
                "implementation_effort": "Medium - 2-3 weeks",
                "effectiveness": "Medium - Ensures organizational readiness",
            },
        ],
    },
}


def get_defense_in_depth_mitigations(technique_id: str) -> Dict[DefenseLayer, List[Dict]]:
    """
    Get all defense-in-depth mitigations for a technique.

    Args:
        technique_id: MITRE ATT&CK technique ID (e.g., "T1078.004")

    Returns:
        Dictionary mapping defense layers to lists of mitigations
    """
    # Try exact match first
    if technique_id in DEFENSE_IN_DEPTH_MITIGATIONS:
        return DEFENSE_IN_DEPTH_MITIGATIONS[technique_id]

    # Try parent technique (e.g., T1078 for T1078.004)
    if "." in technique_id:
        parent_technique = technique_id.split(".")[0]
        if parent_technique in DEFENSE_IN_DEPTH_MITIGATIONS:
            return DEFENSE_IN_DEPTH_MITIGATIONS[parent_technique]

    # Return empty structure if no mitigations found
    return {
        DefenseLayer.PREVENTIVE: [],
        DefenseLayer.DETECTIVE: [],
        DefenseLayer.CORRECTIVE: [],
        DefenseLayer.ADMINISTRATIVE: [],
    }


def get_all_mitigations_for_technique(technique_id: str) -> List[Dict]:
    """
    Get all mitigations for a technique across all layers as a flat list.

    Args:
        technique_id: MITRE ATT&CK technique ID

    Returns:
        List of all mitigations with layer information added
    """
    layered_mitigations = get_defense_in_depth_mitigations(technique_id)
    all_mitigations = []

    for layer, mitigations in layered_mitigations.items():
        for mitigation in mitigations:
            mitigation_with_layer = mitigation.copy()
            mitigation_with_layer["defense_layer"] = layer.value
            all_mitigations.append(mitigation_with_layer)

    return all_mitigations


def get_critical_mitigations(technique_id: str) -> List[Dict]:
    """
    Get only critical priority mitigations for a technique.

    Args:
        technique_id: MITRE ATT&CK technique ID

    Returns:
        List of critical priority mitigations
    """
    all_mitigations = get_all_mitigations_for_technique(technique_id)
    return [m for m in all_mitigations if m.get("priority") == MitigationPriority.CRITICAL]
