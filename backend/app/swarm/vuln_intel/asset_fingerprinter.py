"""
asset_fingerprinter.py

Extracts queryable identifiers from IaC-parsed asset data.
Produces CPE strings, package name+version pairs, and EOL markers
that the multi-source intel adapters use to look up real CVEs.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date
from app.swarm.iac_asset_classifier import IaCAssetClassifier, AssetClass

RUNTIME_EOL = {
    "python3.7":  date(2023, 6, 27),
    "python3.8":  date(2024, 10, 7),
    "python3.9":  date(2025, 10, 5),
    "nodejs12.x": date(2023, 4, 30),
    "nodejs14.x": date(2023, 4, 30),
    "nodejs16.x": date(2024, 9, 11),
    "java8":      date(2030, 12, 31),
    "java11":     date(2026, 9, 30),
    "dotnet5":    date(2022, 5, 10),
    "dotnet6":    date(2024, 11, 12),
}


@dataclass
class AssetFingerprint:
    asset_id:          str
    resource_type:     str
    cpe_strings:       list[str] = field(default_factory=list)
    package_queries:   list[dict] = field(default_factory=list)
    runtime:           Optional[str] = None
    runtime_eol:       bool = False
    runtime_eol_date:  Optional[str] = None
    engine:            Optional[str] = None
    engine_version:    Optional[str] = None
    ami_id:            Optional[str] = None
    docker_image:      Optional[str] = None
    open_ports:        list[int] = field(default_factory=list)
    public_endpoint:   bool = False
    tags:              dict = field(default_factory=dict)
    raw_config:        dict = field(default_factory=dict)


class AssetFingerprinter:
    """
    Converts IaC asset dicts from IaCSerialiser into AssetFingerprint
    objects with CPE strings and package queries ready for intel lookup.
    """

    def fingerprint(self, asset: dict) -> AssetFingerprint:
        # Handle both Asset model format (id, type) and legacy format (asset_id, resource_type)
        asset_id = asset.get("asset_id") or asset.get("id", "")

        # Try to get resource_type field first (legacy format)
        rtype = asset.get("resource_type", "")

        # If not present, extract from asset_id (Asset model format)
        # Asset IDs have format "aws_resource_type.resource_name"
        if not rtype and asset_id and "." in asset_id:
            rtype = asset_id.split(".")[0]

        # If still not found, use normalized type field
        if not rtype:
            rtype = asset.get("type", "")

        fp = AssetFingerprint(
            asset_id=asset_id,
            resource_type=rtype,
            raw_config=asset,
        )
        handler = {
            "aws_lambda_function":      self._fingerprint_lambda,
            "aws_rds_instance":         self._fingerprint_rds,
            "aws_rds_cluster":          self._fingerprint_rds,
            "aws_instance":             self._fingerprint_ec2,
            "aws_ecs_task_definition":  self._fingerprint_ecs,
            "aws_eks_cluster":          self._fingerprint_eks,
            "aws_elasticsearch_domain": self._fingerprint_opensearch,
            "aws_opensearch_domain":    self._fingerprint_opensearch,
            "aws_s3_bucket":            self._fingerprint_s3_bucket,
            "aws_iam_role":             self._fingerprint_iam_role,
            "aws_iam_instance_profile": self._fingerprint_iam_instance_profile,
            "aws_security_group":       self._fingerprint_security_group,
        }.get(rtype)
        if handler:
            handler(asset, fp)
        return fp

    def fingerprint_all(
        self,
        assets: list[dict],
        classify: bool = True,
    ) -> list[AssetFingerprint]:
        """
        Fingerprint a list of assets. When classify=True (default),
        only attackable assets and security controls are fingerprinted.
        Configuration resources are skipped silently.
        """
        if not classify:
            return [self.fingerprint(a) for a in assets]

        classifier = IaCAssetClassifier()
        fingerprints = []
        for asset in assets:
            cr = classifier.classify(asset)
            if cr.asset_class in (
                AssetClass.ATTACKABLE,
                AssetClass.SECURITY_CTRL,
            ):
                fingerprints.append(self.fingerprint(asset))
        return fingerprints

    def _fingerprint_lambda(self, asset: dict, fp: AssetFingerprint):
        runtime = asset.get("runtime", "")
        fp.runtime = runtime
        version_map = {
            "python3.8":  ("python", "3.8"),
            "python3.9":  ("python", "3.9"),
            "python3.10": ("python", "3.10"),
            "python3.11": ("python", "3.11"),
            "python3.12": ("python", "3.12"),
            "nodejs18.x": ("node.js", "18"),
            "nodejs16.x": ("node.js", "16"),
            "nodejs14.x": ("node.js", "14"),
            "java11":     ("java_se", "11"),
            "java17":     ("java_se", "17"),
        }
        if runtime in version_map:
            vendor, version = version_map[runtime]
            fp.cpe_strings.append(
                f"cpe:2.3:a:python:{vendor}:{version}:*:*:*:*:*:*:*"
            )
        eol = RUNTIME_EOL.get(runtime)
        if eol and date.today() > eol:
            fp.runtime_eol = True
            fp.runtime_eol_date = eol.isoformat()
        handler_str = asset.get("handler", "")
        fp.tags["handler"] = handler_str
        env_vars = asset.get("environment", {}) or {}
        env_keys = list((env_vars.get("variables") or {}).keys())
        fp.tags["env_keys"] = env_keys

    def _fingerprint_rds(self, asset: dict, fp: AssetFingerprint):
        engine = asset.get("engine", "")
        version = asset.get("engine_version", "")
        fp.engine = engine
        fp.engine_version = version
        if engine and version:
            cpe_vendor = {
                "mysql":        "oracle:mysql",
                "postgres":     "postgresql:postgresql",
                "mariadb":      "mariadb:mariadb",
                "sqlserver-se": "microsoft:sql_server",
            }.get(engine, f"amazon:{engine}")
            fp.cpe_strings.append(
                f"cpe:2.3:a:{cpe_vendor}:{version}:*:*:*:*:*:*:*"
            )
        fp.public_endpoint = asset.get("publicly_accessible", False)

    def _fingerprint_ec2(self, asset: dict, fp: AssetFingerprint):
        fp.ami_id = asset.get("ami", "")
        ingress = asset.get("vpc_security_group_ingress", []) or []
        for rule in ingress:
            from_p = rule.get("from_port")
            to_p = rule.get("to_port")
            cidr = rule.get("cidr_blocks", []) or []
            if "0.0.0.0/0" in cidr and from_p is not None:
                for port in range(int(from_p), int(to_p or from_p) + 1):
                    fp.open_ports.append(port)
                fp.public_endpoint = True

    def _fingerprint_ecs(self, asset: dict, fp: AssetFingerprint):
        containers = asset.get("container_definitions", []) or []
        for container in containers:
            image = container.get("image", "")
            fp.docker_image = image
            if ":" in image:
                name, tag = image.rsplit(":", 1)
            else:
                name, tag = image, "latest"
            fp.package_queries.append({
                "ecosystem": "docker",
                "name": name,
                "version": tag,
            })

    def _fingerprint_eks(self, asset: dict, fp: AssetFingerprint):
        version = asset.get("version", "")
        if version:
            fp.cpe_strings.append(
                f"cpe:2.3:a:amazon:elastic_kubernetes_service:{version}:*:*:*:*:*:*:*"
            )
            fp.package_queries.append({
                "ecosystem": "kubernetes",
                "name": "kubernetes",
                "version": version,
            })

    def _fingerprint_opensearch(self, asset: dict, fp: AssetFingerprint):
        version = (asset.get("elasticsearch_version") or
                   asset.get("engine_version") or "")
        if version:
            fp.cpe_strings.append(
                f"cpe:2.3:a:elastic:elasticsearch:{version}:*:*:*:*:*:*:*"
            )
        ep = asset.get("endpoint_options") or {}
        fp.public_endpoint = not ep.get("enforce_https", True)

    def _fingerprint_s3_bucket(self, asset: dict, fp: AssetFingerprint):
        """
        S3 bucket fingerprinting. Extracts bucket-level security
        posture indicators relevant to data exfiltration and
        audit trail destruction attack paths.
        """
        # Public access block — absence is a critical signal
        pab = asset.get("public_access_block") or {}
        block_all = (
            pab.get("block_public_acls", False) and
            pab.get("block_public_policy", False) and
            pab.get("ignore_public_acls", False) and
            pab.get("restrict_public_buckets", False)
        )
        fp.public_endpoint = not block_all
        fp.tags["public_access_blocked"] = block_all

        # Versioning — absence means deleted objects are unrecoverable
        versioning = asset.get("versioning") or {}
        fp.tags["versioning_enabled"] = (
            versioning.get("enabled", False) or
            versioning.get("status", "").lower() == "enabled"
        )

        # MFA delete — absence enables ransomware deletion
        fp.tags["mfa_delete_enabled"] = (
            versioning.get("mfa_delete", "").lower() == "enabled"
        )

        # Logging — absence means no access audit trail
        logging_cfg = asset.get("logging") or {}
        fp.tags["access_logging_enabled"] = bool(
            logging_cfg.get("target_bucket")
        )

        # Encryption — absence means data at rest is unencrypted
        sse = asset.get("server_side_encryption_configuration") or {}
        fp.tags["encryption_enabled"] = bool(sse)

        # Bucket name for public exposure check
        bucket_name = asset.get("bucket", "") or asset.get("id", "")
        fp.tags["bucket_name"] = bucket_name

    def _fingerprint_iam_role(self, asset: dict, fp: AssetFingerprint):
        """
        IAM role fingerprinting. Extracts trust policy and permission
        scope indicators relevant to privilege escalation paths.
        """
        # Trust policy — who can assume this role
        assume_policy = asset.get("assume_role_policy", "") or ""
        fp.tags["assume_role_policy_raw"] = assume_policy[:500]

        # Check for overly broad trust — any AWS principal
        fp.tags["trust_allows_any_aws"] = (
            '"AWS": "*"' in assume_policy or
            '"Service": "*"' in assume_policy
        )

        # Check for cross-account trust
        fp.tags["cross_account_trust"] = (
            "sts:AssumeRole" in assume_policy and
            "AWS" in assume_policy
        )

        # Inline policies — signals what permissions are attached
        inline = asset.get("inline_policy") or []
        fp.tags["has_inline_policy"] = bool(inline)

        # Max session duration — longer = more time to use stolen creds
        max_session = asset.get("max_session_duration", 3600)
        fp.tags["max_session_duration"] = max_session
        fp.tags["extended_session"] = max_session > 3600

    def _fingerprint_iam_instance_profile(
        self, asset: dict, fp: AssetFingerprint
    ):
        """
        IAM instance profile fingerprinting. Extracts the role ARN
        so agents know what permissions a compromised EC2 instance
        would inherit via IMDS credential theft (T1552.005).
        """
        role = asset.get("role", "") or ""
        fp.tags["attached_role"] = role
        fp.tags["imds_credential_target"] = role
        # Instance profiles are always credential-granting assets
        fp.tags["credential_theft_vector"] = "IMDS T1552.005"

    def _fingerprint_security_group(
        self, asset: dict, fp: AssetFingerprint
    ):
        """
        Security group fingerprinting. Extracts inbound rules to
        detect overly permissive access. Results are tagged onto
        the security group but intended to be associated with the
        asset the group protects.
        """
        ingress = asset.get("ingress", []) or []
        dangerous_rules = []
        for rule in ingress:
            cidrs = rule.get("cidr_blocks", []) or []
            ipv6_cidrs = rule.get("ipv6_cidr_blocks", []) or []
            all_cidrs = cidrs + ipv6_cidrs
            from_port = rule.get("from_port", 0)
            to_port = rule.get("to_port", 65535)
            protocol = rule.get("protocol", "-1")
            public = "0.0.0.0/0" in all_cidrs or "::/0" in all_cidrs
            if public:
                fp.public_endpoint = True
                for port in [from_port, to_port]:
                    if port and port not in fp.open_ports:
                        fp.open_ports.append(int(port))
                dangerous_rules.append({
                    "from_port": from_port,
                    "to_port": to_port,
                    "protocol": protocol,
                    "public": True,
                })
        fp.tags["dangerous_ingress_rules"] = dangerous_rules
        fp.tags["allows_public_ingress"] = fp.public_endpoint
