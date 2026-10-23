#!/usr/bin/env bash
# Tear down the sandbox CodeBuild project + role so nothing lingers / costs. Run after demo.
set -uo pipefail
REGION="${AWS_REGION:-us-east-1}"
ROLE_NAME="repopilot-sandbox-role"
PROJECT="repopilot-sandbox"

aws codebuild delete-project --name "$PROJECT" --region "$REGION" 2>/dev/null && echo "deleted project $PROJECT" || echo "project gone"
aws iam delete-role-policy --role-name "$ROLE_NAME" --policy-name repopilot-sandbox-logs 2>/dev/null || true
aws iam delete-role --role-name "$ROLE_NAME" 2>/dev/null && echo "deleted role $ROLE_NAME" || echo "role gone"
aws logs delete-log-group --log-group-name "/aws/codebuild/repopilot-sandbox" --region "$REGION" 2>/dev/null && echo "deleted log group" || true
echo "teardown complete"
