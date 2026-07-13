#!/usr/bin/env bash

set -Eeuo pipefail

readonly EXPECTED_IMAGE_PREFIX="ghcr.io/alcyoneptis/clusters-ext-tools@sha256:"
readonly CONTAINER_NAME="clusters-ext-api"
readonly SERVICE_NAME="clusters-ext-api"
readonly APP_DIR="${APP_DIR:-/home/deisdd2434/clusters_ext_tools}"
readonly COMPOSE_FILE="${APP_DIR}/docker-compose.yml"
readonly DEPLOY_ENV="${APP_DIR}/.deploy.env"

if [[ $# -ne 1 ]]; then
    echo "Usage: APP_DIR=/path/to/app $0 <image-ref-by-digest>" >&2
    exit 2
fi

readonly IMAGE_REF="$1"
image_digest="${IMAGE_REF#"${EXPECTED_IMAGE_PREFIX}"}"
if [[ "${IMAGE_REF}" != "${EXPECTED_IMAGE_PREFIX}${image_digest}" ]] || \
   [[ ! "${image_digest}" =~ ^[0-9a-f]{64}$ ]]; then
    echo "Refusing invalid image reference: ${IMAGE_REF}" >&2
    exit 2
fi

if [[ ! -d "${APP_DIR}" ]]; then
    echo "Application directory does not exist: ${APP_DIR}" >&2
    exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
    echo "Production Compose file does not exist: ${COMPOSE_FILE}" >&2
    exit 1
fi

if [[ ! -f "${APP_DIR}/.env" ]]; then
    echo "Runtime environment file does not exist: ${APP_DIR}/.env" >&2
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE=(docker-compose)
else
    echo "Neither docker compose nor docker-compose is installed." >&2
    exit 1
fi

exec 9>"${APP_DIR}/.deploy.lock"
if ! flock -n 9; then
    echo "Another deployment is already running." >&2
    exit 1
fi

compose() {
    "${COMPOSE[@]}" \
        --env-file "${DEPLOY_ENV}" \
        -f "${COMPOSE_FILE}" \
        "$@"
}

write_image_ref() {
    local image_ref="$1"
    local temporary_env="${DEPLOY_ENV}.tmp"

    umask 077
    printf 'IMAGE_REF=%s\n' "${image_ref}" > "${temporary_env}"
    mv "${temporary_env}" "${DEPLOY_ENV}"
}

wait_until_healthy() {
    local status

    for _ in $(seq 1 18); do
        status=$(docker inspect \
            --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
            "${CONTAINER_NAME}" 2>/dev/null || true)

        case "${status}" in
            healthy)
                return 0
                ;;
            unhealthy|exited|dead)
                return 1
                ;;
        esac

        sleep 5
    done

    return 1
}

previous_image_ref=""
if [[ -f "${DEPLOY_ENV}" ]]; then
    previous_image_ref=$(sed -n 's/^IMAGE_REF=//p' "${DEPLOY_ENV}" | head -n 1)
fi
if [[ -z "${previous_image_ref}" ]]; then
    previous_image_ref=$(docker inspect \
        --format '{{.Config.Image}}' \
        "${CONTAINER_NAME}" 2>/dev/null || true)
fi

rollback() {
    if [[ -z "${previous_image_ref}" ]]; then
        echo "No previous image is available for rollback." >&2
        return 1
    fi

    echo "Rolling back to ${previous_image_ref}"
    write_image_ref "${previous_image_ref}"
    compose up -d --no-build --remove-orphans
    wait_until_healthy
}

write_image_ref "${IMAGE_REF}"

if ! compose pull "${SERVICE_NAME}"; then
    echo "Image pull failed." >&2
    if [[ -n "${previous_image_ref}" ]]; then
        write_image_ref "${previous_image_ref}"
    fi
    exit 1
fi

if ! compose up -d --no-build --remove-orphans; then
    echo "Container update failed." >&2
    rollback || true
    exit 1
fi

if ! wait_until_healthy; then
    echo "Container did not become healthy." >&2
    compose logs --tail=100 "${SERVICE_NAME}" || true
    rollback || true
    exit 1
fi

echo "Deployment completed: ${IMAGE_REF}"
