from pathlib import Path


def config_loggers() -> None:
    project_dir = Path(__file__).parents[2]
    (project_dir / "logs").mkdir(parents=True, exist_ok=True)
    # config_file_path = project_dir / "logging.ini"
    # config.fileConfig(config_file_path)
