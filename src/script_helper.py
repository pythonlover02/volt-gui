import os, stat

class HelperManager:
    """
    Manages the creation of the volt-helper script.
    """

    BASH_SCRIPT_CONTENT = r"""#!/bin/bash

set -euo pipefail

check_commands() {
    for cmd in pgrep pkill sleep chmod grep cut; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: Required command \"$cmd\" not found" >&2
            exit 1
        fi
    done
}

terminate_schedulers() {
    pgrep -f "^scx_" >/dev/null 2>&1 && pkill -INT -f "^scx_" && sleep 0.5
    pgrep -f "^scx_" >/dev/null 2>&1 && pkill -TERM -f "^scx_" && sleep 0.5
    pgrep -f "^scx_" >/dev/null 2>&1 && pkill -KILL -f "^scx_" && sleep 0.2
    return 0
}

apply_cpu() {
    local governor=""
    local scheduler=""
    local max_freq=""
    local min_freq=""
    local has_scheduler=false

    for arg in "$@"; do
        case "$arg" in
            governor:*) governor="${arg#governor:}" ;;
            max_freq:*) max_freq="${arg#max_freq:}" ;;
            min_freq:*) min_freq="${arg#min_freq:}" ;;
            scheduler:*)
                scheduler="${arg#scheduler:}"
                has_scheduler=true
                ;;
        esac
    done

    if [[ -n "$governor" ]]; then
        for path in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            echo "$governor" > "$path"
        done
    fi

    if [[ -n "$min_freq" ]]; then
        for path in /sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq; do
            echo "$min_freq" > "$path"
        done
    fi

    if [[ -n "$max_freq" ]]; then
        for path in /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq; do
            echo "$max_freq" > "$path"
        done
    fi

    terminate_schedulers

    if [[ "$has_scheduler" == true && "$scheduler" != "none" ]]; then
        "$scheduler" &
        sleep 1
    fi
}

apply_disk() {
    for arg in "$@"; do
        [[ "$arg" == *":"* ]] && echo "${arg#*:}" > "/sys/block/${arg%%:*}/queue/scheduler"
    done
}

apply_kernel() {
    for arg in "$@"; do
        echo "${arg#*:}" > "${arg%%:*}"
    done
}

apply_gpu() {
    local settings_file="$1"
    local volt_path="$2"
    local script_content="#!/bin/bash\n\n"

    while IFS="=" read -r key value; do
        [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue

        key="${key// /}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"

        if [[ "$key" == "launch_options" ]]; then
            continue
        elif [[ -n "$value" ]]; then
            script_content+="export ${key}=\"${value}\"\n"
        elif [[ "$key" == unset:* ]]; then
            script_content+="unset ${key#unset:}\n"
        fi
    done < "$settings_file"

    script_content+="\n"

    if grep -q "^launch_options=" "$settings_file" 2>/dev/null; then
        local launch_opts=""
        launch_opts="$(grep "^launch_options=" "$settings_file" | cut -d"=" -f2-)"
        launch_opts="${launch_opts#"${launch_opts%%[![:space:]]*}"}"
        launch_opts="${launch_opts%"${launch_opts##*[![:space:]]}"}"
        script_content+="${launch_opts} \"\$@\"\n"
    else
        script_content+="\"\$@\"\n"
    fi

    echo -e "$script_content" > "$volt_path"
    chmod 755 "$volt_path"
}

main() {
    check_commands
    local volt_path=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|--cpu)
                shift
                local cpu_args=()
                while [[ $# -gt 0 && "$1" != -* ]]; do
                    cpu_args+=("$1")
                    shift
                done
                apply_cpu "${cpu_args[@]}"
                ;;
            -d|--disk)
                shift
                local disk_args=()
                while [[ $# -gt 0 && "$1" != -* ]]; do
                    disk_args+=("$1")
                    shift
                done
                apply_disk "${disk_args[@]}"
                ;;
            -k|--kernel)
                shift
                local kernel_args=()
                while [[ $# -gt 0 && "$1" != -* ]]; do
                    kernel_args+=("$1")
                    shift
                done
                apply_kernel "${kernel_args[@]}"
                ;;
            -p|--path)
                volt_path="$2"
                shift 2
                ;;
            -g|--gpu)
                apply_gpu "$2" "$volt_path"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
}

main "$@"
"""

    @staticmethod
    def create_helper_script():
        """
        Creates the volt-helper bash script in /tmp with executable permissions.
        """
        with open("/tmp/volt-helper", "w") as f:
            f.write(HelperManager.BASH_SCRIPT_CONTENT)

        os.chmod("/tmp/volt-helper", stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
