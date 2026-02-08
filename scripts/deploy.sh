#!/usr/bin/env bash
set -euo pipefail

# OmniPrice Terraform deploy helper
#
# This script wraps Terraform commands for the AWS deployment stack.
# It expects Terraform files under infra/terraform.

TF_DIR="${TF_DIR:-infra/terraform}"

log() {
  printf '[deploy] %s\n' "$1"
}

die() {
  printf '[deploy][error] %s\n' "$1" >&2
  exit 1
}

check_tools() {
  command -v terraform >/dev/null 2>&1 || die "terraform is not installed"
  command -v aws >/dev/null 2>&1 || die "aws cli is not installed"
}

check_tf_dir() {
  [[ -d "$TF_DIR" ]] || die "terraform directory not found: $TF_DIR"
  compgen -G "$TF_DIR/*.tf" >/dev/null || die "no *.tf files found in $TF_DIR"
}

tf_init() {
  log "terraform init ($TF_DIR)"
  terraform -chdir="$TF_DIR" init
}

tf_fmt_validate() {
  log "terraform fmt + validate ($TF_DIR)"
  terraform -chdir="$TF_DIR" fmt -recursive
  terraform -chdir="$TF_DIR" validate
}

tf_plan() {
  log "terraform plan ($TF_DIR)"
  terraform -chdir="$TF_DIR" plan
}

tf_apply() {
  log "terraform apply ($TF_DIR)"
  terraform -chdir="$TF_DIR" apply
}

tf_outputs() {
  log "terraform outputs ($TF_DIR)"
  terraform -chdir="$TF_DIR" output || true
}

usage() {
  cat <<USAGE
Usage: $0 [init|validate|plan|apply|deploy|outputs]

Commands:
  init      terraform init
  validate  terraform fmt + validate
  plan      init + validate + plan
  apply     init + validate + apply
  deploy    init + validate + plan + apply + outputs
  outputs   print terraform outputs
USAGE
}

main() {
  local cmd="${1:-deploy}"

  check_tools
  check_tf_dir

  case "$cmd" in
    init)
      tf_init
      ;;
    validate)
      tf_init
      tf_fmt_validate
      ;;
    plan)
      tf_init
      tf_fmt_validate
      tf_plan
      ;;
    apply)
      tf_init
      tf_fmt_validate
      tf_apply
      tf_outputs
      ;;
    deploy)
      tf_init
      tf_fmt_validate
      tf_plan
      tf_apply
      tf_outputs
      ;;
    outputs)
      tf_outputs
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
