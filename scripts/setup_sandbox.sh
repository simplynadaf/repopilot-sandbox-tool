#!/usr/bin/env bash
# Create the disposable-sandbox CodeBuild project + a least-privilege role for RepoPilot's
# run_in_sandbox tool. Idempotent-ish: safe to re-run. Region us-east-1.
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
ROLE_NAME="repopilot-sandbox-role"
PROJECT="repopilot-sandbox"
ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
HERE="$(cd "$(dirname "$0")/.." && pwd)"

echo "Account: $ACCOUNT  Region: $REGION"

# 1. IAM role for CodeBuild (trust) -------------------------------------------------------
if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  echo "role $ROLE_NAME exists"
else
  aws iam create-role --role-name "$ROLE_NAME" \
    --assume-role-policy-document "file://$HERE/iam/codebuild-trust.json" >/dev/null
  echo "created role $ROLE_NAME"
fi
aws iam put-role-policy --role-name "$ROLE_NAME" \
  --policy-name repopilot-sandbox-logs \
  --policy-document "file://$HERE/iam/codebuild-permissions.json"
echo "attached least-privilege logs policy"
ROLE_ARN="arn:aws:iam::${ACCOUNT}:role/${ROLE_NAME}"
sleep 8  # let the role propagate

# 2. CodeBuild project --------------------------------------------------------------------
# A tiny Linux container, short timeout, no artifacts, source = NO_SOURCE (we clone in the
# buildspec, overridden per run). Logs to CloudWatch so the tool can read them back.
ENV_JSON=$(cat <<JSON
{
  "type": "LINUX_CONTAINER",
  "image": "aws/codebuild/amazonlinux2-x86_64-standard:5.0",
  "computeType": "BUILD_GENERAL1_SMALL",
  "imagePullCredentialsType": "CODEBUILD"
}
JSON
)
SRC_JSON='{ "type": "NO_SOURCE", "buildspec": "version: 0.2\nphases:\n  build:\n    commands:\n      - echo placeholder" }'
ART_JSON='{ "type": "NO_ARTIFACTS" }'
LOGS_JSON='{ "cloudWatchLogs": { "status": "ENABLED", "groupName": "/aws/codebuild/repopilot-sandbox" } }'

if aws codebuild batch-get-projects --names "$PROJECT" --region "$REGION" \
     --query 'projects[0].name' --output text 2>/dev/null | grep -q "$PROJECT"; then
  echo "project $PROJECT exists -> updating"
  aws codebuild update-project --name "$PROJECT" --region "$REGION" \
    --service-role "$ROLE_ARN" --environment "$ENV_JSON" --source "$SRC_JSON" \
    --artifacts "$ART_JSON" --logs-config "$LOGS_JSON" --timeout-in-minutes 10 >/dev/null
else
  aws codebuild create-project --name "$PROJECT" --region "$REGION" \
    --service-role "$ROLE_ARN" --environment "$ENV_JSON" --source "$SRC_JSON" \
    --artifacts "$ART_JSON" --logs-config "$LOGS_JSON" --timeout-in-minutes 10 \
    --description "Disposable sandbox: RepoPilot clones a repo and runs its install here." >/dev/null
  echo "created project $PROJECT"
fi

echo ""
echo "DONE. Export this for the agent:"
echo "  export REPOPILOT_SANDBOX_PROJECT=$PROJECT"
