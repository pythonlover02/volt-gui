import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QLineEdit, QTabWidget
from PySide6.QtCore import Qt

class KernelManager:

    KERNEL_SETTINGS_CATEGORIES = {
        "CPU": {
            'sched_cfs_bandwidth_slice_us': {
                'path': '/proc/sys/kernel/sched_cfs_bandwidth_slice_us',
                'text': 'CFS bandwidth slice duration (microseconds). Higher values reduce scheduler overhead for CPU-bound applications.\nRecommended: 4000',
                'is_dynamic': False
            },
            'sched_autogroup_enabled': {
                'path': '/proc/sys/kernel/sched_autogroup_enabled',
                'text': 'Automatic process grouping for desktop responsiveness. Helps prioritize foreground applications.\nRecommended: 1 or 0 to use nice',
                'is_dynamic': False
            },
            'sched_rt_runtime_us': {
                'path': '/proc/sys/kernel/sched_rt_runtime_us',
                'text': 'Maximum CPU time (microseconds) for realtime tasks per period. -1 allows unlimited usage.\nRecommended: 950000 or -1',
                'is_dynamic': False
            },
            'sched_rt_period_us': {
                'path': '/proc/sys/kernel/sched_rt_period_us',
                'text': 'Period over which realtime task CPU usage is measured (microseconds). Works with sched_rt_runtime_us.\nRecommended: 1000000 (1 second, default)',
                'is_dynamic': False
            },
            'sched_schedstats': {
                'path': '/proc/sys/kernel/sched_schedstats',
                'text': 'Scheduler statistics collection. Disable to eliminate tracing overhead.\nRecommended: 0',
                'is_dynamic': False
            },
            'timer_migration': {
                'path': '/proc/sys/kernel/timer_migration',
                'text': 'Allows timer interrupts to migrate between CPUs. Disabling reduces latency at cost of power efficiency.\nRecommended: 0',
                'is_dynamic': False
            },
            'numa_balancing': {
                'path': '/proc/sys/kernel/numa_balancing',
                'text': 'Automatic NUMA memory migration. Creates overhead without significant benefits for most workloads.\nRecommended: 0',
                'is_dynamic': False
            }
        },
        "Memory": {
            'compaction_proactiveness': {
                'path': '/proc/sys/vm/compaction_proactiveness',
                'text': 'Controls memory compaction aggressiveness (0-100). Lower values reduce CPU overhead during intensive workloads.\nRecommended: 0',
                'is_dynamic': False
            },
            'watermark_boost_factor': {
                'path': '/proc/sys/vm/watermark_boost_factor',
                'text': 'Memory reclaim aggressiveness during fragmentation (units of 10,000). Lower values prevent background reclaim during high-load scenarios.\nRecommended: 0',
                'is_dynamic': False
            },
            'watermark_scale_factor': {
                'path': '/proc/sys/vm/watermark_scale_factor',
                'text': 'Controls kswapd aggressiveness (units of 10,000). Higher values mean more free memory maintained. Default is 10 (0.1% of memory).\nRecommended: 10 (default) or higher for latency-sensitive workloads',
                'is_dynamic': False
            },
            'extfrag_threshold': {
                'path': '/proc/sys/vm/extfrag_threshold',
                'text': 'External fragmentation threshold that triggers compaction (0-1000). Higher values reduce compaction overhead.\nRecommended: 500',
                'is_dynamic': False
            },
            'compact_unevictable_allowed': {
                'path': '/proc/sys/vm/compact_unevictable_allowed',
                'text': 'Allow compaction to examine unevictable (mlocked) pages. May cause minor page faults but improves compaction effectiveness.\nRecommended: 1 (default), 0 for RT systems',
                'is_dynamic': False
            },
            'defrag_mode': {
                'path': '/proc/sys/vm/defrag_mode',
                'text': 'Proactive fragmentation prevention for hugepage allocations. Reduces long-term fragmentation at cost of immediate overhead.\nRecommended: 0(less overhead), 1 (for long-running systems)',
                'is_dynamic': False
            },
            'swappiness': {
                'path': '/proc/sys/vm/swappiness',
                'text': 'Kernel preference for swap vs RAM reclaim (0-200). Lower values prioritize keeping data in RAM for latency-sensitive workloads.\nRecommended: 10 (16GB+ RAM), 30-60 (8GB RAM). If using zram or zswap, higher values (60-120) are recommended to take advantage of compressed swap benefits.',
                'is_dynamic': False
            },
            'page-cluster': {
                'path': '/proc/sys/vm/page-cluster',
                'text': 'Number of pages to read/write together during swap operations as log2. Set to 0 for SSD-based systems.\nRecommended: 0',
                'is_dynamic': False
            },
            'vfs_cache_pressure': {
                'path': '/proc/sys/vm/vfs_cache_pressure',
                'text': 'Tenderness to reclaim filesystem caches relative to pagecache/swap. Lower values improve asset loading performance by keeping metadata cached.\nRecommended: 50',
                'is_dynamic': False
            },
            'min_free_kbytes': {
                'path': '/proc/sys/vm/min_free_kbytes',
                'text': 'Minimum reserved memory. Do not set below 1024 KB or above 5% of system memory.\nRecommended values: 1024-...',
                'is_dynamic': False
            },
            'overcommit_memory': {
                'path': '/proc/sys/vm/overcommit_memory',
                'text': 'Memory overcommit policy: 0=heuristic, 1=always, 2=strict. Mode 1 maximizes available memory.\nRecommended: 1',
                'is_dynamic': False
            },
            'overcommit_ratio': {
                'path': '/proc/sys/vm/overcommit_ratio',
                'text': 'Percentage of physical RAM (plus swap) available when overcommit_memory=2.\nRecommended: 60',
                'is_dynamic': False
            },
            'admin_reserve_kbytes': {
                'path': '/proc/sys/vm/admin_reserve_kbytes',
                'text': 'Memory reserved for root processes during OOM conditions. Default: min(3% of RAM, 8MB).\nRecommended: 8192 (8GB+ RAM), 4096 (4GB RAM)',
                'is_dynamic': False
            },
            'user_reserve_kbytes': {
                'path': '/proc/sys/vm/user_reserve_kbytes',
                'text': 'Memory reserved for user processes when overcommit_memory=2. Default: min(3% of process size, 128MB).\nRecommended: 131072',
                'is_dynamic': False
            },
            'max_map_count': {
                'path': '/proc/sys/vm/max_map_count',
                'text': 'Maximum memory mappings per process. Essential for applications using many shared libraries and memory-mapped files.\nRecommended: 2147483642 (SteamDeck Value) or 1048576 (Arch Linux)',
                'is_dynamic': False
            },
            'page_lock_unfairness': {
                'path': '/proc/sys/vm/page_lock_unfairness',
                'text': 'Number of times page lock can be stolen from waiter before fair handoff. Higher values favor readers which can improve read performance for asset streaming workloads.\nRecommended: 5',
                'is_dynamic': False
            },
            'percpu_pagelist_high_fraction': {
                'path': '/proc/sys/vm/percpu_pagelist_high_fraction',
                'text': 'Per-CPU page list size as fraction of zone size (0=default kernel algorithm, min value is 8). Higher values reduce contention on multi-core systems.\nRecommended: 8+ or 0 (reverts to the default behavior)',
                'is_dynamic': False
            },
            'zone_reclaim_mode': {
                'path': '/proc/sys/vm/zone_reclaim_mode',
                'text': 'NUMA memory reclaim behavior (bitmask: 0=reclaim off 1=reclaim on, 2=write dirty pages, 4=swap pages). Usually degrades performance due to unnecessary reclaim overhead.\nRecommended: 0',
                'is_dynamic': False
            },
            'min_unmapped_ratio': {
                'path': '/proc/sys/vm/min_unmapped_ratio',
                'text': 'Minimum percentage of unmapped pages before zone reclaim (NUMA only). Higher values delay local reclaim, improving cache locality.\nRecommended: 1',
                'is_dynamic': False
            },
            'min_slab_ratio': {
                'path': '/proc/sys/vm/min_slab_ratio',
                'text': 'Percentage of zone pages that must be reclaimable slab before zone reclaim (NUMA only). Higher values delay expensive remote allocation.\nRecommended: 5 (default), 3-8 range for tuning',
                'is_dynamic': False
            },
            'numa_stat': {
                'path': '/proc/sys/vm/numa_stat',
                'text': 'Enable NUMA statistics collection. Disabling reduces allocation overhead but breaks monitoring tools.\nRecommended: 0 (performance), 1 (monitoring/debugging)',
                'is_dynamic': False
            },
            'nr_hugepages': {
                'path': '/proc/sys/vm/nr_hugepages',
                'text': 'Number of persistent hugepages allocated. Critical for applications requiring guaranteed hugepage memory (databases, VMs, HPC).\nRecommended: 0 (default), or calculated based on application needs',
                'is_dynamic': False
            },
            'nr_overcommit_hugepages': {
                'path': '/proc/sys/vm/nr_overcommit_hugepages',
                'text': 'Maximum number of additional hugepages that can be allocated dynamically beyond nr_hugepages.\nRecommended: 0 (conservative), or set based on peak demand',
                'is_dynamic': False
            },
            'hugetlb_optimize_vmemmap': {
                'path': '/proc/sys/vm/hugetlb_optimize_vmemmap',
                'text': 'Optimize hugepage metadata memory usage (saves ~7 pages per 2MB hugepage). May add overhead during allocation/deallocation.\nRecommended: 1 (enable for memory savings), 0 (disable for allocation speed)',
                'is_dynamic': False
            },
            'stat_interval': {
                'path': '/proc/sys/vm/stat_interval',
                'text': 'VM statistics update interval (seconds). Higher values reduce CPU overhead.\nRecommended: 10',
                'is_dynamic': False
            },
            'thp_enabled': {
                'path': '/sys/kernel/mm/transparent_hugepage/enabled',
                'text': 'Transparent Huge Pages reduce TLB pressure but may cause allocation stalls. "madvise" enables only where beneficial.\nRecommended: madvise',
                'is_dynamic': True
            },
            'thp_shmem_enabled': {
                'path': '/sys/kernel/mm/transparent_hugepage/shmem_enabled',
                'text': 'THP for shared memory segments. "advise" enables only when explicitly requested.\nRecommended: advise',
                'is_dynamic': True
            },
            'thp_defrag': {
                'path': '/sys/kernel/mm/transparent_hugepage/defrag',
                'text': 'THP defragmentation strategy. "defer" prevents allocation stalls during high-priority tasks.\nRecommended: defer',
                'is_dynamic': True
            }
        },
        "Disk": {
            'dirty_ratio': {
                'path': '/proc/sys/vm/dirty_ratio',
                'text': 'Maximum percentage of available memory for dirty pages before synchronous writes. Lower values reduce I/O latency spikes. Mutually exclusive with dirty_bytes.\nRecommended: 10',
                'is_dynamic': False
            },
            'dirty_background_ratio': {
                'path': '/proc/sys/vm/dirty_background_ratio',
                'text': 'Percentage of available memory at which background writeback begins. Should be 1/3 of dirty_ratio. Mutually exclusive with dirty_background_bytes.\nRecommended: 3',
                'is_dynamic': False
            },
            'dirty_bytes': {
                'path': '/proc/sys/vm/dirty_bytes',
                'text': 'Absolute dirty memory limit (bytes). Provides consistent behavior regardless of RAM size. Mutually exclusive with dirty_ratio.\nRecommended: 67108864 (64MB)',
                'is_dynamic': False
            },
            'dirty_background_bytes': {
                'path': '/proc/sys/vm/dirty_background_bytes',
                'text': 'Absolute background writeback threshold (bytes). Should be 50% of dirty_bytes. Mutually exclusive with dirty_background_ratio.\nRecommended: 33554432 (32MB)',
                'is_dynamic': False
            },
            'dirty_expire_centisecs': {
                'path': '/proc/sys/vm/dirty_expire_centisecs',
                'text': 'Maximum time dirty data remains in memory (centiseconds). Shorter intervals improve responsiveness.\nRecommended: 3000',
                'is_dynamic': False
            },
            'dirty_writeback_centisecs': {
                'path': '/proc/sys/vm/dirty_writeback_centisecs',
                'text': 'Interval between periodic writeback wakeups (centiseconds). Longer intervals reduce CPU overhead.\nRecommended: 1500',
                'is_dynamic': False
            },
            'dirtytime_expire_seconds': {
                'path': '/proc/sys/vm/dirtytime_expire_seconds',
                'text': 'Interval for lazy timestamp updates on filesystems with dirtytime mount option (seconds).\nRecommended: 43200 (12 hours)',
                'is_dynamic': False
            },
            'laptop_mode': {
                'path': '/proc/sys/vm/laptop_mode',
                'text': 'Power-saving write delay mechanism. Disable for performance-oriented systems.\nRecommended: 0',
                'is_dynamic': False
            }
        },
        "System": {
            'watchdog': {
                'path': '/proc/sys/kernel/watchdog',
                'text': 'Soft lockup detector. Disable to remove periodic checks that can cause stuttering.\nRecommended: 0',
                'is_dynamic': False
            },
            'nmi_watchdog': {
                'path': '/proc/sys/kernel/nmi_watchdog',
                'text': 'NMI-based hard lockup detection. Disables performance-counter based monitoring.\nRecommended: 0',
                'is_dynamic': False
            },
            'hung_task_timeout_secs': {
                'path': '/proc/sys/kernel/hung_task_timeout_secs',
                'text': 'Timeout for detecting hung tasks (seconds). 0 disables detection to prevent false positives during long sessions.\nRecommended: 0 or 120 (Default)',
                'is_dynamic': False
            },
            'pid_max': {
                'path': '/proc/sys/kernel/pid_max',
                'text': 'Maximum process ID value. Higher values support systems running many concurrent processes.\nRecommended: 4194304',
                'is_dynamic': False
            },
            'file_max': {
                'path': '/proc/sys/fs/file-max',
                'text': 'System-wide maximum open file descriptors. Essential for applications opening many files simultaneously.\nRecommended: 2097152',
                'is_dynamic': False
            },
            'oom_kill_allocating_task': {
                'path': '/proc/sys/vm/oom_kill_allocating_task',
                'text': 'OOM killer targets the task that triggered OOM instead of scanning all tasks. Improves recovery speed.\nRecommended: 1',
                'is_dynamic': False
            },
            'oom_dump_tasks': {
                'path': '/proc/sys/vm/oom_dump_tasks',
                'text': 'Enable task dump when OOM killer is invoked. Useful for debugging but adds overhead on large systems.\nRecommended: 0 (disable for performance), 1 (enable for debugging)',
                'is_dynamic': False
            },
            'panic_on_oom': {
                'path': '/proc/sys/vm/panic_on_oom',
                'text': 'System behavior on OOM: 0=kill process, 1=panic on system OOM, 2=always panic.\nRecommended: 0 (default behavior)',
                'is_dynamic': False
            },
            'max_user_freq': {
                'path': '/sys/class/rtc/rtc0/max_user_freq',
                'text': 'Maximum RTC interrupt frequency (Hz) for userspace. Higher values provide better timer precision.\nRecommended: 64',
                'is_dynamic': False
            }
        },
        "Network": {
            'core_rmem_max': {
                'path': '/proc/sys/net/core/rmem_max',
                'text': 'Maximum socket receive buffer size (bytes) per socket. Higher values improve throughput for high-bandwidth connections.\nRecommended: 268435456 (256MB)',
                'is_dynamic': False
            },
            'core_wmem_max': {
                'path': '/proc/sys/net/core/wmem_max',
                'text': 'Maximum socket send buffer size (bytes) per socket. Should match rmem_max for balanced performance.\nRecommended: 268435456 (256MB)',
                'is_dynamic': False
            },
            'tcp_fastopen': {
                'path': '/proc/sys/net/ipv4/tcp_fastopen',
                'text': 'TCP Fast Open reduces connection establishment latency. Bitmask: 1=client, 2=server.\nRecommended: 3 (enable for both incoming/outgoing)',
                'is_dynamic': False
            },
            'tcp_window_scaling': {
                'path': '/proc/sys/net/ipv4/tcp_window_scaling',
                'text': 'Enable TCP window scaling for high-bandwidth connections.\nRecommended: 1',
                'is_dynamic': False
            },
            'tcp_timestamps': {
                'path': '/proc/sys/net/ipv4/tcp_timestamps',
                'text': 'Enable TCP timestamps for RTT measurement and PAWS protection.\nRecommended: 1',
                'is_dynamic': False
            }
        },
        "Security": {
            'randomize_va_space': {
                'path': '/proc/sys/kernel/randomize_va_space',
                'text': 'Address space layout randomization: 0=disabled, 1=conservative, 2=full. Lower values reduce address translation overhead.\nRecommended: 0 (performance), 2 (security)',
                'is_dynamic': False
            },
            'perf_event_paranoid': {
                'path': '/proc/sys/kernel/perf_event_paranoid',
                'text': 'Performance monitoring access: -1=unrestricted, 0=user+kernel, 1=user only, 2=kernel only, 3=no access.\nRecommended: 2',
                'is_dynamic': False
            },
            'mmap_min_addr': {
                'path': '/proc/sys/vm/mmap_min_addr',
                'text': 'Minimum virtual address for mmap operations. Security feature with minimal performance impact.\nRecommended: 65536',
                'is_dynamic': False
            }
        }
    }

    KERNEL_SETTINGS = {}
    for category in KERNEL_SETTINGS_CATEGORIES.values():
        KERNEL_SETTINGS.update(category)

    @staticmethod
    def get_current_value(setting_path):
        """
        Read and return current value from setting file
        """
        try:
            with open(setting_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None

    @staticmethod
    def get_dynamic_current_value(setting_path):
        """
        Extract current value from dynamic settings (e.g., [current] option1 option2)
        """
        try:
            with open(setting_path, 'r') as f:
                content = f.read().strip()

            match = re.search(r'\[([^\]]+)\]', content)
            if match:
                return match.group(1)
            else:
                values = content.split()
                if values:
                    return values[0]
                else:
                    return None
        except Exception:
            return None

    @staticmethod
    def get_dynamic_possible_values(setting_path):
        """
        Extract all possible values from dynamic settings
        """
        try:
            with open(setting_path, 'r') as f:
                content = f.read().strip()

            clean_content = re.sub(r'[\[\]]', '', content)
            possible_values = clean_content.split()

            if possible_values:
                return possible_values
            else:
                return None
        except Exception:
            return None

    @staticmethod
    def get_available_setting(setting_path):
        """
        Check if setting file is accessible
        """
        try:
            with open(setting_path, 'r') as f:
                f.read()
            return True
        except Exception:
            return False

    @staticmethod
    def create_kernel_tab(main_window):
        """
        Create and return kernel settings tab with all widgets
        """
        kernel_tab = QWidget()
        kernel_layout = QVBoxLayout(kernel_tab)
        kernel_layout.setSpacing(10)
        kernel_layout.setContentsMargins(9, 9, 9, 0)
        widgets = {}

        kernel_subtabs = QTabWidget()
        for category_name, category_settings in KernelManager.KERNEL_SETTINGS_CATEGORIES.items():
            category_tab = QWidget()
            category_layout = QVBoxLayout(category_tab)
            category_layout.setContentsMargins(0, 0, 0, 0)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            scroll_widget = QWidget()
            scroll_widget.setProperty("scrollContainer", True)
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            scroll_layout.setContentsMargins(10, 10, 10, 0)

            for setting_name, setting_info in category_settings.items():
                KernelManager.create_setting_section(scroll_layout, widgets, setting_name, setting_info)

            scroll_layout.addStretch(1)
            scroll_area.setWidget(scroll_widget)
            category_layout.addWidget(scroll_area)
            kernel_subtabs.addTab(category_tab, category_name)

        kernel_layout.addWidget(kernel_subtabs)
        KernelManager.create_kernel_apply_button(kernel_layout, widgets, main_window)

        widgets['kernel_settings_applied'] = False
        widgets['is_process_running'] = False
        widgets['process'] = None

        return kernel_tab, widgets

    @staticmethod
    def create_setting_section(kernel_layout, widgets, setting_name, setting_info):
        """
        Create GUI section for individual kernel setting
        """
        setting_container = QWidget()
        setting_container.setProperty("settingContainer", True)
        setting_layout = QVBoxLayout(setting_container)
        setting_layout.setContentsMargins(0, 10, 0, 0)

        label = QLabel(f"{setting_info['path']}:")
        label.setWordWrap(True)
        setting_layout.addWidget(label)

        current_value_label = QLabel("Updating...")
        setting_layout.addWidget(current_value_label)

        is_accessible = KernelManager.get_available_setting(setting_info['path'])
        input_widget = QLineEdit()
        input_widget.setPlaceholderText("enter value")

        if is_accessible:
            tooltip_text = setting_info['text']
            if setting_info['is_dynamic']:
                possible_values = KernelManager.get_dynamic_possible_values(setting_info['path'])
                if possible_values:
                    values_text = " ".join(possible_values)
                    tooltip_text += f"\nPossible values: {values_text}"
                else:
                    tooltip_text += "\nPossible values: Unable to read from system"

            input_widget.setToolTip(tooltip_text)
        else:
            input_widget.setEnabled(False)
            input_widget.setToolTip(f"Setting file is not available - {setting_info['path']} disabled")

        setting_layout.addWidget(input_widget)

        widgets[f'{setting_name}_input'] = input_widget
        widgets[f'{setting_name}_current_value'] = current_value_label
        kernel_layout.addWidget(setting_container)

    @staticmethod
    def create_kernel_apply_button(kernel_layout, widgets, main_window):
        """
        Create apply button for kernel settings
        """
        button_container = QWidget()
        button_container.setProperty("buttonContainer", True)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 0)

        widgets['kernel_apply_button'] = QPushButton("Apply")
        widgets['kernel_apply_button'].setMinimumSize(100, 30)
        widgets['kernel_apply_button'].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        button_layout.addStretch(1)
        button_layout.addWidget(widgets['kernel_apply_button'])
        button_layout.addStretch(1)

        kernel_layout.addWidget(button_container)
        kernel_layout.addSpacing(9)

    @staticmethod
    def refresh_kernel_values(widgets):
        """
        Update all kernel setting current values in the GUI and refresh tooltips
        """
        for category in KernelManager.KERNEL_SETTINGS_CATEGORIES.values():
            for name, info in category.items():
                if not KernelManager.get_available_setting(info['path']):
                    widgets[f'{name}_current_value'].setText("current value: not available")
                    continue

                if info['is_dynamic']:
                    current = KernelManager.get_dynamic_current_value(info['path'])
                    tooltip_text = info['text']
                    possible_values = KernelManager.get_dynamic_possible_values(info['path'])
                    if possible_values:
                        values_text = " ".join(possible_values)
                        tooltip_text += f"\nPossible values: {values_text}"
                    else:
                        tooltip_text += "\nPossible values: Unable to read from system"
                    widgets[f'{name}_input'].setToolTip(tooltip_text)
                else:
                    current = KernelManager.get_current_value(info['path'])

                if current is not None:
                    widgets[f'{name}_current_value'].setText(f"current value: {current}")
