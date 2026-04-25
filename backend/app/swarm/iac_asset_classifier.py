"""
iac_asset_classifier.py

Classifies IaC resources as attackable assets or configuration
resources for the purpose of vulnerability matching and fingerprinting.

Three tests determine attackability:
  Test 1 — Network reachable: has an endpoint, port, or API surface
  Test 2 — Stores data: holds data an attacker would steal or destroy
  Test 3 — Grants credentials: holds or grants IAM permissions or
            secrets that an attacker could steal and reuse

A resource passing any one test is an attackable asset.
Security groups are a special case — classified as configuration
but their inbound rules are extracted and associated with the
asset they protect.

This module is the single source of truth for asset classification.
All other modules (fingerprinter, vuln_matcher, context_builder)
use this classifier to determine what to process.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AssetClass(str, Enum):
    ATTACKABLE    = "attackable"
    CONFIGURATION = "configuration"
    SECURITY_CTRL = "security_control"   # security groups, NACLs


@dataclass
class ClassifiedResource:
    resource_type:  str
    asset_id:       str
    asset_class:    AssetClass
    test_passed:    Optional[str]        # "network" | "data" | "credentials" | None
    reason:         str
    raw_config:     dict = field(default_factory=dict)


# ── Test 1 — Network reachable ────────────────────────────────────────────────
# Resources that have an endpoint, port, DNS name, or invoke URL
# that an attacker can send traffic or API calls to directly.

NETWORK_REACHABLE = {
    # Compute
    "aws_instance",
    "aws_spot_instance_request",
    # Serverless
    "aws_lambda_function",
    "aws_lambda_function_url",
    # Containers
    "aws_ecs_service",
    "aws_ecs_task_definition",
    "aws_eks_cluster",
    "aws_eks_node_group",
    # Load balancers and gateways
    "aws_lb",
    "aws_alb",
    "aws_elb",
    "aws_api_gateway_rest_api",
    "aws_api_gateway_v2_api",
    "aws_apigatewayv2_api",
    # Databases with network endpoints
    "aws_rds_instance",
    "aws_rds_cluster",
    "aws_db_instance",
    "aws_redshift_cluster",
    "aws_elasticache_cluster",
    "aws_elasticache_replication_group",
    "aws_elasticsearch_domain",
    "aws_opensearch_domain",
    # Messaging and streaming (API callable)
    "aws_sqs_queue",
    "aws_sns_topic",
    "aws_kinesis_stream",
    "aws_msk_cluster",
    # Transfer and access
    "aws_transfer_server",
    "aws_cloudfront_distribution",
    "aws_route53_record",
}

# ── Test 2 — Stores or processes data ─────────────────────────────────────────
# Resources that hold data at rest that an attacker would read,
# exfiltrate, tamper with, or destroy.

STORES_DATA = {
    # Object storage
    "aws_s3_bucket",
    "aws_s3_object",
    # Relational databases
    "aws_rds_instance",
    "aws_rds_cluster",
    "aws_db_instance",
    "aws_db_snapshot",
    "aws_rds_cluster_snapshot",
    # NoSQL
    "aws_dynamodb_table",
    # Data warehouse
    "aws_redshift_cluster",
    "aws_redshift_snapshot",
    # Search
    "aws_elasticsearch_domain",
    "aws_opensearch_domain",
    # Cache (may hold session tokens or sensitive data)
    "aws_elasticache_cluster",
    "aws_elasticache_replication_group",
    # Secrets and parameters
    "aws_secretsmanager_secret",
    "aws_secretsmanager_secret_version",
    "aws_ssm_parameter",
    # Logs and audit trails
    "aws_cloudwatch_log_group",
    "aws_cloudtrail",
    # Backups
    "aws_backup_vault",
    "aws_ebs_snapshot",
    # AI and ML model storage
    "aws_sagemaker_model",
    "aws_sagemaker_endpoint",
    "aws_bedrockagent_knowledge_base",
}

# ── Test 3 — Grants credentials or permissions ────────────────────────────────
# Resources that hold or grant IAM permissions, access keys,
# certificates, or tokens that an attacker could steal and reuse.

GRANTS_CREDENTIALS = {
    # IAM identity resources
    "aws_iam_role",
    "aws_iam_user",
    "aws_iam_group",
    "aws_iam_access_key",
    "aws_iam_instance_profile",
    # IAM policy attachment (reveals what permissions exist)
    "aws_iam_role_policy",
    "aws_iam_role_policy_attachment",
    "aws_iam_user_policy",
    "aws_iam_user_policy_attachment",
    # Federation and trust
    "aws_iam_saml_provider",
    "aws_iam_openid_connect_provider",
    # Cryptographic keys
    "aws_kms_key",
    "aws_kms_alias",
    # Certificates
    "aws_acm_certificate",
    # Secrets (overlaps with Test 2 intentionally)
    "aws_secretsmanager_secret",
    "aws_ssm_parameter",
    # Service-linked credentials
    "aws_codecommit_repository",    # may contain embedded credentials
    "aws_ecr_repository",           # registry credentials
}

# ── Security controls — special case ──────────────────────────────────────────
# These fail all three tests but their misconfiguration enables
# attacks on the assets they protect. Classified separately so
# the fingerprinter can associate their rules with protected assets.

SECURITY_CONTROLS = {
    "aws_security_group",
    "aws_security_group_rule",
    "aws_network_acl",
    "aws_network_acl_rule",
    "aws_vpc_endpoint",
    "aws_wafv2_web_acl",
    "aws_wafv2_web_acl_association",
    "aws_shield_protection",
}

# ── Pure configuration — fails all three tests ────────────────────────────────
# Topology, routing, grouping, and association resources.
# Serialised as agent context text but not fingerprinted.

CONFIGURATION_ONLY = {
    "aws_vpc",
    "aws_internet_gateway",
    "aws_nat_gateway",
    "aws_subnet",
    "aws_route_table",
    "aws_route_table_association",
    "aws_route",
    "aws_main_route_table_association",
    "aws_vpc_peering_connection",
    "aws_vpc_peering_connection_accepter",
    "aws_db_subnet_group",
    "aws_elasticache_subnet_group",
    "aws_redshift_subnet_group",
    "aws_eks_fargate_profile",
    "aws_placement_group",
    "aws_key_pair",                 # SSH key reference only — key not stored
    "aws_eip",                      # Elastic IP — address allocation only
    "aws_eip_association",
    "aws_network_interface",
    "aws_flow_log",                 # log destination is the asset, not the flow log
    "aws_cloudwatch_log_subscription_filter",
    "aws_cloudwatch_metric_alarm",
    "aws_cloudwatch_dashboard",
    "aws_sns_topic_subscription",
    "aws_sqs_queue_policy",         # policy on the queue, not the queue itself
    "aws_s3_bucket_policy",         # policy on the bucket
    "aws_s3_bucket_public_access_block",
    "aws_s3_bucket_versioning",
    "aws_s3_bucket_logging",
    "aws_s3_bucket_notification",
    "aws_s3_bucket_server_side_encryption_configuration",
    "aws_s3_bucket_acl",
    "aws_s3_bucket_cors_configuration",
    "aws_s3_bucket_lifecycle_configuration",
    "aws_s3_bucket_website_configuration",
    "aws_lambda_permission",        # permission on the Lambda, not the function
    "aws_lambda_event_source_mapping",
    "aws_lambda_layer_version",
    "aws_lambda_alias",
    "aws_ecs_cluster",              # cluster definition, not the running tasks
    "aws_ecs_capacity_provider",
    "aws_autoscaling_group",        # scaling config, not the instances
    "aws_launch_template",
    "aws_launch_configuration",
    "aws_cloudfront_origin_access_identity",
    "aws_cloudfront_origin_access_control",
    "aws_lb_listener",
    "aws_lb_listener_rule",
    "aws_lb_target_group",
    "aws_lb_target_group_attachment",
    "aws_api_gateway_deployment",
    "aws_api_gateway_stage",
    "aws_api_gateway_resource",
    "aws_api_gateway_method",
    "aws_api_gateway_integration",
    "aws_api_gateway_authorizer",
    "aws_codecommit_trigger",
    "aws_codepipeline",             # pipeline definition
    "aws_codebuild_project",        # build config
    "aws_codedeploy_app",
    "aws_codedeploy_deployment_group",
}


class IaCAssetClassifier:
    """
    Classifies IaC resource dicts as attackable assets,
    security controls, or configuration resources.

    Usage:
        classifier = IaCAssetClassifier()
        result = classifier.classify(asset_dict)
        attackable = classifier.filter_attackable(asset_list)
    """

    def classify(self, asset: dict) -> ClassifiedResource:
        """
        Classify a single asset dict. Returns a ClassifiedResource
        with asset_class, test_passed, and reason populated.

        Accepts both Asset model format (id, type) and legacy format
        (asset_id, resource_type).
        """
        # Handle both Asset model format and legacy format
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

        rtype = rtype.lower()

        # Security controls — special case
        if rtype in SECURITY_CONTROLS:
            return ClassifiedResource(
                resource_type=rtype,
                asset_id=asset_id,
                asset_class=AssetClass.SECURITY_CTRL,
                test_passed=None,
                reason=(
                    "Security control — rules are associated with "
                    "the asset they protect, not treated independently"
                ),
                raw_config=asset,
            )

        # Test 1 — Network reachable
        if rtype in NETWORK_REACHABLE:
            return ClassifiedResource(
                resource_type=rtype,
                asset_id=asset_id,
                asset_class=AssetClass.ATTACKABLE,
                test_passed="network",
                reason=(
                    "Network reachable — has an endpoint, port, or "
                    "API surface that an attacker can send traffic to"
                ),
                raw_config=asset,
            )

        # Test 2 — Stores data
        if rtype in STORES_DATA:
            return ClassifiedResource(
                resource_type=rtype,
                asset_id=asset_id,
                asset_class=AssetClass.ATTACKABLE,
                test_passed="data",
                reason=(
                    "Stores data — holds data at rest that an attacker "
                    "would exfiltrate, tamper with, or destroy"
                ),
                raw_config=asset,
            )

        # Test 3 — Grants credentials
        if rtype in GRANTS_CREDENTIALS:
            return ClassifiedResource(
                resource_type=rtype,
                asset_id=asset_id,
                asset_class=AssetClass.ATTACKABLE,
                test_passed="credentials",
                reason=(
                    "Grants credentials — holds or grants IAM permissions "
                    "or secrets that an attacker could steal and reuse"
                ),
                raw_config=asset,
            )

        # Known configuration — fails all three tests
        if rtype in CONFIGURATION_ONLY:
            return ClassifiedResource(
                resource_type=rtype,
                asset_id=asset_id,
                asset_class=AssetClass.CONFIGURATION,
                test_passed=None,
                reason=(
                    "Configuration only — defines topology, routing, "
                    "grouping, or association with no independent "
                    "attack surface"
                ),
                raw_config=asset,
            )

        # Unknown resource type — classify as attackable by default
        # to avoid silently dropping potentially important resources
        return ClassifiedResource(
            resource_type=rtype,
            asset_id=asset_id,
            asset_class=AssetClass.ATTACKABLE,
            test_passed="unknown",
            reason=(
                f"Unknown resource type '{rtype}' — classified as "
                "attackable by default to avoid silent omission. "
                "Add to CONFIGURATION_ONLY if confirmed non-attackable."
            ),
            raw_config=asset,
        )

    def classify_all(
        self, assets: list[dict]
    ) -> list[ClassifiedResource]:
        """Classify a list of asset dicts."""
        return [self.classify(a) for a in assets]

    def filter_attackable(
        self, assets: list[dict]
    ) -> list[dict]:
        """
        Return only the asset dicts that are attackable assets
        or security controls. Configuration resources are excluded.
        This is the list passed to the fingerprinter and vuln_matcher.
        """
        results = []
        for asset in assets:
            cr = self.classify(asset)
            if cr.asset_class in (
                AssetClass.ATTACKABLE,
                AssetClass.SECURITY_CTRL,
            ):
                results.append(asset)
        return results

    def filter_configuration(
        self, assets: list[dict]
    ) -> list[dict]:
        """
        Return only configuration resources. Used to build the
        topology context block for agent prompts separately from
        the vulnerability context block.
        """
        results = []
        for asset in assets:
            cr = self.classify(asset)
            if cr.asset_class == AssetClass.CONFIGURATION:
                results.append(asset)
        return results

    def classification_report(
        self, assets: list[dict]
    ) -> dict:
        """
        Returns a summary dict for logging and debugging.
        Shows counts by class and lists each resource with its
        classification and reason.
        """
        classified = self.classify_all(assets)
        report = {
            "total": len(classified),
            "attackable": 0,
            "security_control": 0,
            "configuration": 0,
            "unknown": 0,
            "resources": [],
        }
        for cr in classified:
            if cr.asset_class == AssetClass.ATTACKABLE:
                key = "unknown" if cr.test_passed == "unknown" \
                    else "attackable"
                report[key] += 1
            elif cr.asset_class == AssetClass.SECURITY_CTRL:
                report["security_control"] += 1
            else:
                report["configuration"] += 1

            report["resources"].append({
                "asset_id":   cr.asset_id,
                "type":       cr.resource_type,
                "class":      cr.asset_class.value,
                "test":       cr.test_passed,
                "reason":     cr.reason,
            })
        return report
