def get_launch_settings() -> dict:
    return {
        "_tab_metadata": (True,),
        "launch_options": {
            "label": "Launch Options",
            "description": "Additional launch command prefix.",
            "inputs": "e.g. gamemoderun=e.g. gamemoderun",
            "output": ("argument", "", "", "", ""),
        },
    }
