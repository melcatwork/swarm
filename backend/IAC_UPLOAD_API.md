# IaC Upload API Documentation

## Overview

The IaC Upload API provides endpoints for uploading and parsing Infrastructure-as-Code files (Terraform and CloudFormation). The API extracts assets, relationships, and trust boundaries for threat modeling analysis.

## Endpoints

### 1. GET /api/iac/supported

Get list of supported IaC formats.

**Response:**
```json
{
  "formats": [
    {
      "name": "Terraform",
      "extensions": [".tf"]
    },
    {
      "name": "AWS CloudFormation",
      "extensions": [".yaml", ".yml", ".json"]
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/iac/supported
```

---

### 2. POST /api/iac/upload

Upload and parse an IaC file. Returns the complete AssetGraph with assets, relationships, and trust boundaries.

**Request:**
- Content-Type: `multipart/form-data`
- Parameter: `file` (UploadFile)
- Supported extensions: `.tf`, `.yaml`, `.yml`, `.json`

**Response:**
```json
{
  "assets": [
    {
      "id": "aws_vpc.main",
      "name": "main",
      "type": "network.vpc",
      "cloud": "aws",
      "service": "VPC",
      "properties": {},
      "data_sensitivity": "low",
      "trust_boundary": "private"
    }
  ],
  "relationships": [
    {
      "source": "aws_subnet.public",
      "target": "aws_vpc.main",
      "type": "depends_on",
      "properties": {
        "dependency_type": "network"
      }
    }
  ],
  "trust_boundaries": [
    {
      "id": "boundary_internet",
      "name": "Internet Facing",
      "assets": ["aws_lb.web"],
      "exposure": "internet"
    }
  ],
  "metadata": {
    "source_file": "terraform",
    "format": "hcl2",
    "parsed_at": "2026-04-09T14:11:45.068414+00:00",
    "resource_count": 12
  }
}
```

**Example (Terraform):**
```bash
curl -X POST http://localhost:8000/api/iac/upload \
  -F "file=@infrastructure.tf"
```

**Example (CloudFormation YAML):**
```bash
curl -X POST http://localhost:8000/api/iac/upload \
  -F "file=@template.yaml"
```

**Example (CloudFormation JSON):**
```bash
curl -X POST http://localhost:8000/api/iac/upload \
  -F "file=@template.json"
```

**Error Responses:**

- **400 Bad Request**: No filename provided
  ```json
  {"detail": "No filename provided"}
  ```

- **422 Unprocessable Entity**: Invalid or unsupported file
  ```json
  {"detail": "Invalid HCL2 syntax: ..."}
  {"detail": "JSON file does not appear to be a CloudFormation template (missing 'Resources' key)"}
  {"detail": "Unsupported file format. Supported extensions: .tf, .yaml, .yml, .json"}
  ```

- **500 Internal Server Error**: Unexpected parsing error
  ```json
  {"detail": "Failed to parse file: ..."}
  ```

---

### 3. POST /api/iac/validate

Validate an IaC file without returning the full graph. Returns validation status and metadata.

**Request:**
- Content-Type: `multipart/form-data`
- Parameter: `file` (UploadFile)
- Supported extensions: `.tf`, `.yaml`, `.yml`, `.json`

**Response:**
```json
{
  "valid": true,
  "format": "terraform",
  "resource_count": 12,
  "asset_types": [
    "compute.vm",
    "identity.iam_role",
    "network.gateway",
    "network.lb",
    "network.security_group",
    "network.subnet",
    "network.vpc",
    "storage.database",
    "storage.object"
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/iac/validate \
  -F "file=@infrastructure.tf"
```

**Error Responses:**
Same as `/api/iac/upload` endpoint.

---

## File Type Detection

The API automatically detects the IaC format based on file extension:

1. **Terraform** (`.tf`):
   - Parsed using `TerraformParser`
   - Supports HCL2 syntax
   - Extracts Terraform resource references (e.g., `aws_vpc.main.id`)

2. **CloudFormation YAML** (`.yaml`, `.yml`):
   - Parsed using `CloudFormationParser`
   - Supports CloudFormation intrinsic functions (!Ref, !GetAtt, !Sub, etc.)
   - Requires YAML with valid CloudFormation structure

3. **CloudFormation JSON** (`.json`):
   - Parsed using `CloudFormationParser`
   - Must have top-level `"Resources"` key to distinguish from plain JSON
   - Supports CloudFormation intrinsic functions ({"Ref": "..."}, {"Fn::GetAtt": [...]})

---

## Asset Graph Structure

### Assets
Each asset represents an infrastructure component:

```json
{
  "id": "aws_instance.web",
  "name": "web",
  "type": "compute.vm",
  "cloud": "aws",
  "service": "EC2",
  "properties": {
    "internet_facing": true,
    "ports": [80, 443],
    "iam_role": "aws_iam_role.ec2_role",
    "vpc": "aws_vpc.main",
    "subnet": "aws_subnet.public",
    "encryption_at_rest": true
  },
  "data_sensitivity": "medium",
  "trust_boundary": "vpc-internal"
}
```

**Normalized Asset Types:**
- `compute.vm` - EC2 instances
- `compute.container` - ECS tasks
- `compute.serverless` - Lambda functions
- `storage.object` - S3 buckets
- `storage.database` - RDS, DynamoDB
- `storage.filesystem` - EFS, FSx
- `network.vpc` - VPCs
- `network.subnet` - Subnets
- `network.security_group` - Security groups
- `network.lb` - Load balancers (ALB, ELB)
- `network.gateway` - Internet gateways, NAT gateways, API Gateway
- `network.cdn` - CloudFront distributions
- `identity.iam_role` - IAM roles
- `identity.iam_policy` - IAM policies
- `security.kms_key` - KMS keys
- `security.secret` - Secrets Manager secrets

**Data Sensitivity Levels:**
- `high` - Storage and database resources
- `medium` - Compute resources
- `low` - Networking and monitoring resources

### Relationships
Relationships describe how assets interact:

```json
{
  "source": "aws_instance.web",
  "target": "aws_iam_role.ec2_role",
  "type": "iam_binding",
  "properties": {
    "permission_type": "iam_instance_profile"
  }
}
```

**Relationship Types:**
- `network_access` - Network connectivity (security groups, load balancers)
- `iam_binding` - IAM permissions and role assignments
- `data_flow` - Data movement between assets (e.g., Lambda → S3)
- `depends_on` - Infrastructure dependencies (e.g., subnet → VPC)

### Trust Boundaries
Trust boundaries group assets by exposure level:

```json
{
  "id": "boundary_internet",
  "name": "Internet Facing",
  "assets": ["aws_lb.web"],
  "exposure": "internet"
}
```

**Exposure Levels:**
- `internet` - Internet-facing resources (public load balancers, CloudFront)
- `vpc-internal` - Resources within VPC with explicit subnets
- `private` - Private resources without direct exposure
- `management` - IAM and control plane resources

---

## Test Results

### Terraform File (12 resources)
✓ Successfully parsed
- **Assets**: 12
- **Relationships**: 11
- **Trust Boundaries**: 3
- **Asset Types**: compute.vm, identity.iam_role, network.gateway, network.lb, network.security_group, network.subnet, network.vpc, storage.database, storage.object

### CloudFormation YAML (15 resources)
✓ Successfully parsed
- **Assets**: 15
- **Relationships**: 16
- **Trust Boundaries**: 4

### CloudFormation JSON (7 resources)
✓ Successfully parsed
- **Assets**: 7
- **Relationships**: 5
- **Trust Boundaries**: 3

---

## Integration Example (Python)

```python
import requests

# Upload and parse a Terraform file
with open("infrastructure.tf", "rb") as f:
    files = {"file": ("infrastructure.tf", f)}
    response = requests.post(
        "http://localhost:8000/api/iac/upload",
        files=files
    )

if response.status_code == 200:
    asset_graph = response.json()

    print(f"Assets: {len(asset_graph['assets'])}")
    print(f"Relationships: {len(asset_graph['relationships'])}")

    # Find internet-facing assets
    internet_assets = [
        asset for asset in asset_graph['assets']
        if asset['trust_boundary'] == 'internet'
    ]

    print(f"Internet-facing assets: {len(internet_assets)}")
    for asset in internet_assets:
        print(f"  - {asset['name']} ({asset['service']})")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

---

## Integration Example (JavaScript/Frontend)

```javascript
async function uploadIaCFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/api/iac/upload', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const assetGraph = await response.json();

      console.log(`Assets: ${assetGraph.assets.length}`);
      console.log(`Relationships: ${assetGraph.relationships.length}`);

      // Process asset graph for visualization
      return assetGraph;
    } else {
      const error = await response.json();
      throw new Error(error.detail);
    }
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
}

// Usage with file input
document.getElementById('file-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file) {
    try {
      const assetGraph = await uploadIaCFile(file);
      // Render asset graph visualization
      renderAssetGraph(assetGraph);
    } catch (error) {
      alert(`Failed to parse file: ${error.message}`);
    }
  }
});
```

---

## Next Steps

The IaC Upload API is now ready for:
1. Frontend integration for uploading and visualizing infrastructure
2. Threat modeling analysis using the extracted asset graphs
3. Security assessment based on trust boundaries and relationships
4. Attack path identification across infrastructure components
