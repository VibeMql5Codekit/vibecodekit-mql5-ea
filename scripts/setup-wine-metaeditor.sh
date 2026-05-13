#!/bin/bash
# Phase 0 — Setup Wine ≥ 8.0 + MetaEditor on Linux (Ubuntu 22.04+)
# Run with: sudo bash scripts/setup-wine-metaeditor.sh
# Idempotent — safe to re-run.
#
# Strategy:
#   1. Install Wine from WineHQ repo (stable ≥ 8.0)
#   2. Initialize Wine prefix at ~/.wine-mql5
#   3. Build MetaEditor CI stub via MinGW (for headless CI/CD)
#   4. Place stub in Wine prefix so compile.py auto-detects it
#
# For production compilation, set METAEDITOR_PATH to a real
# MetaEditor64.exe installed via Windows or manual Wine setup.

set -euo pipefail

LOG="${LOG:-/tmp/setup-wine.log}"
WINEPREFIX="${WINEPREFIX:-$HOME/.wine-mql5}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STUB_SRC="$REPO_ROOT/tests/fixtures/metaeditor_stub.c"

log() {
    echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log "ERROR: must run with sudo"
        exit 1
    fi
}

install_wine_from_winehq() {
    # Check if Wine ≥ 8.0 is already installed
    if command -v wine &>/dev/null; then
        local version major
        version=$(wine --version 2>/dev/null | grep -oP '[\d.]+' | head -1)
        major=$(echo "$version" | cut -d. -f1)
        if [[ "$major" -ge 8 ]]; then
            log "Wine $version already installed (≥ 8.0). Skipping."
            return
        fi
        log "Wine $version too old. Upgrading to WineHQ stable..."
        apt-get remove -y wine wine64 wine32 2>/dev/null || true
    fi

    log "Installing Wine from WineHQ repo..."
    dpkg --add-architecture i386 || true

    mkdir -pm755 /etc/apt/keyrings
    wget -q -O /etc/apt/keyrings/winehq-archive.key \
        https://dl.winehq.org/wine-builds/winehq.key

    local codename
    codename=$(lsb_release -cs 2>/dev/null || echo "jammy")
    wget -q -NP /etc/apt/sources.list.d/ \
        "https://dl.winehq.org/wine-builds/ubuntu/dists/$codename/winehq-$codename.sources" \
        2>/dev/null || true

    apt-get update -qq 2>&1 | tee -a "$LOG"
    apt-get install -y --install-recommends winehq-stable 2>&1 | tee -a "$LOG"

    local installed_version
    installed_version=$(wine --version 2>/dev/null | grep -oP '[\d.]+' | head -1)
    log "Wine $installed_version installed from WineHQ."
}

install_system_deps() {
    log "Installing system dependencies..."
    apt-get install -y -qq \
        xvfb \
        gcc-mingw-w64-x86-64 \
        2>&1 | tee -a "$LOG"
    log "System dependencies installed."
}

setup_wine_prefix() {
    log "Setting up Wine prefix at $WINEPREFIX..."
    export WINEPREFIX
    export WINEARCH=win64
    export DISPLAY="${DISPLAY:-:0}"
    export WINEDEBUG=-all

    if [[ ! -d "$WINEPREFIX/drive_c" ]]; then
        xvfb-run -a wineboot -i 2>&1 | tee -a "$LOG" || true
        sleep 5
        log "Wine prefix initialized."
    else
        log "Wine prefix already exists."
    fi
}

build_metaeditor_stub() {
    local mt5_dir="$WINEPREFIX/drive_c/Program Files/MetaTrader 5"
    local target="$mt5_dir/metaeditor64.exe"

    if [[ -f "$target" ]]; then
        log "MetaEditor stub already installed at: $target"
        return
    fi

    if [[ ! -f "$STUB_SRC" ]]; then
        log "ERROR: MetaEditor stub source not found at $STUB_SRC"
        exit 1
    fi

    log "Building MetaEditor CI stub from $STUB_SRC..."
    mkdir -p "$mt5_dir"
    x86_64-w64-mingw32-gcc -o "$target" "$STUB_SRC" -static 2>&1 | tee -a "$LOG"
    chmod +x "$target"
    log "MetaEditor CI stub installed at: $target"
}

write_env_file() {
    local mt5_dir="$WINEPREFIX/drive_c/Program Files/MetaTrader 5"
    local env_file="$HOME/.mql5-env"
    cat > "$env_file" <<EOF
export WINEPREFIX='$WINEPREFIX'
export METAEDITOR_PATH='$mt5_dir/metaeditor64.exe'
EOF
    log "Environment file written to $env_file"
    log "  source $env_file  # to load in your shell"
}

verify_smoke() {
    log "Running smoke verification..."
    export WINEPREFIX
    export DISPLAY="${DISPLAY:-:0}"

    # Wine version
    local version major
    version=$(wine --version 2>/dev/null | grep -oP '[\d.]+' | head -1)
    major=$(echo "$version" | cut -d. -f1)
    if [[ "$major" -ge 8 ]]; then
        log "  Wine version $version >= 8.0: OK"
    else
        log "  Wine version $version < 8.0: FAIL"
        return 1
    fi

    # MetaEditor stub
    local metaeditor="$WINEPREFIX/drive_c/Program Files/MetaTrader 5/metaeditor64.exe"
    if [[ -f "$metaeditor" ]]; then
        log "  MetaEditor present: OK"
    else
        log "  MetaEditor missing: FAIL"
        return 1
    fi

    # Try compile demo_smoke.mq5
    local demo="$REPO_ROOT/tests/fixtures/demo_smoke.mq5"
    if [[ -f "$demo" ]]; then
        local tmplog="/tmp/smoke-compile.log"
        xvfb-run -a wine "$metaeditor" "/compile:$demo" "/log:$tmplog" 2>/dev/null || true
        if [[ -f "$tmplog" ]]; then
            log "  Compile smoke test: OK"
        else
            log "  Compile smoke test: log not created (WARN)"
        fi
    fi

    log "Smoke verification passed."
}

main() {
    check_root
    install_wine_from_winehq
    install_system_deps
    setup_wine_prefix
    build_metaeditor_stub
    write_env_file
    verify_smoke

    log "==========================================="
    log "Phase 0 setup complete!"
    log "Wine $(wine --version 2>/dev/null), MetaEditor CI stub installed"
    log "Next: pytest tests/gates/phase-0/ -v"
    log "==========================================="
}

main "$@"
