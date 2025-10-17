import os, stat

class HelperManager:
    """
    Manages the creation of the volt-helper script.
    """

    BASH_SCRIPT_CONTENT = """#!/bin/bash

set -euo pipefail

check_commands() {
    for cmd in chmod grep cut sed tr; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: Required command "$cmd" not found" >&2
            exit 1
        fi
    done
}

apply_governor() {
    for CPU_PATH in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "$1" > "$CPU_PATH"
    done
}

apply_max_freq() {
    for CPU_PATH in /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq; do
        echo "$1" > "$CPU_PATH"
    done
}

apply_min_freq() {
    for CPU_PATH in /sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq; do
        echo "$1" > "$CPU_PATH"
    done
}

terminate_existing_schedulers() {
    pkill -INT -f "^scx_" 2>/dev/null || true
    sleep 0.5
    pkill -TERM -f "^scx_" 2>/dev/null || true
    sleep 0.5
    pkill -KILL -f "^scx_" 2>/dev/null || true
    sleep 0.2
}

handle_scheduler() {
    local scheduler="$1"

    terminate_existing_schedulers

    if [ -n "$scheduler" ] && [ "$scheduler" != "none" ]; then
        "$scheduler" &
        sleep 1
    fi
}

manage_cpu() {
    local governor="" scheduler="" max_freq="" min_freq=""

    for arg in "$@"; do
        case "$arg" in
            governor:*) governor="${arg#governor:}" ;;
            scheduler:*) scheduler="${arg#scheduler:}" ;;
            max_freq:*) max_freq="${arg#max_freq:}" ;;
            min_freq:*) min_freq="${arg#min_freq:}" ;;
        esac
    done

    [ -n "$governor" ] && apply_governor "$governor"
    [ -n "$min_freq" ] && apply_min_freq "$min_freq"
    [ -n "$max_freq" ] && apply_max_freq "$max_freq"
    [ -n "$scheduler" ] && handle_scheduler "$scheduler"
}

apply_disk_scheduler() {
    echo "$2" > "/sys/block/$1/queue/scheduler"
}

manage_disk() {
    for arg in "$@"; do
        [[ "$arg" == *":"* ]] && apply_disk_scheduler "${arg%%:*}" "${arg#*:}"
    done
}

apply_kernel_parameter() {
    echo "$2" > "$1" 2>/dev/null
}

manage_kernel() {
    for setting in "$@"; do
        apply_kernel_parameter "${setting%%:*}" "${setting#*:}"
    done
}

read_gpu_settings() {
    local script_content="#!/bin/bash\\n\\n"

    while IFS="=" read -r key value || [ -n "$key" ]; do
        [ -z "$key" ] || [[ "$key" =~ ^[[:space:]]*# ]] && continue

        key=$(echo "$key" | tr -d " ")
        value=$(echo "$value" | sed "s/^[[:space:]]*//;s/[[:space:]]*$//")

        if [ "$key" = "launch_options" ]; then
            continue
        elif [ -n "$value" ]; then
            script_content="${script_content}export ${key}=\\"${value}\\"\\n"
        elif [[ "$key" == unset:* ]]; then
            script_content="${script_content}unset ${key#unset:}\\n"
        fi
    done < "$1"

    echo -e "$script_content"
}

add_launch_options() {
    local script_content="$2\\n\\n"
    local launch_options=$(grep "^launch_options=" "$1" 2>/dev/null | cut -d"=" -f2- | sed "s/^[[:space:]]*//;s/[[:space:]]*$//")

    if [ -n "$launch_options" ]; then
        script_content="${script_content}${launch_options} \\"\\$@\\"\\n"
    else
        script_content="${script_content}\\"\\$@\\"\\n"
    fi

    echo -e "$script_content"
}

manage_gpu() {
    local script_content=$(read_gpu_settings "$1")
    script_content=$(add_launch_options "$1" "$script_content")

    mkdir -p "$(dirname "$2")" 2>/dev/null
    echo -e "$script_content" > "$2" 2>/dev/null
    chmod 755 "$2" 2>/dev/null
}

parse_arguments() {
    local volt_path=""

    while [ $# -gt 0 ]; do
        case "$1" in
            -c|--cpu)
                shift
                local cpu_args=()
                while [ $# -gt 0 ] && [[ "$1" != -* ]]; do
                    cpu_args+=("$1")
                    shift
                done
                manage_cpu "${cpu_args[@]}"
                ;;
            -d|--disk)
                shift
                local disk_args=()
                while [ $# -gt 0 ] && [[ "$1" != -* ]]; do
                    disk_args+=("$1")
                    shift
                done
                manage_disk "${disk_args[@]}"
                ;;
            -k|--kernel)
                shift
                local kernel_args=()
                while [ $# -gt 0 ] && [[ "$1" != -* ]]; do
                    kernel_args+=("$1")
                    shift
                done
                manage_kernel "${kernel_args[@]}"
                ;;
            -p|--path)
                volt_path="$2"
                shift 2
                ;;
            -g|--gpu)
                manage_gpu "$2" "$volt_path"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
}

check_commands
parse_arguments "$@"
"""

    @staticmethod
    def create_helper_script():
        """
        Creates the volt-helper bash script in /tmp with executable permissions.
        """
        script_path = "/tmp/volt-helper"

        with open(script_path, "w") as f:
            f.write(HelperManager.BASH_SCRIPT_CONTENT)

        os.chmod(script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
