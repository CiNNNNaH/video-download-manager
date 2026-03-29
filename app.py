from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.analyzer import Analyzer
from core.bootstrap_manager import BootstrapManager
from core.dependency_check import DependencyChecker
from core.downloader import Downloader
from core.environment import EnvironmentPaths
from core.install_manager import InstallManager
from core.path_manager import PathManager
from gui.main_window import MainWindow
from services.history_service import HistoryService
from services.i18n_service import I18nService
from services.log_service import LogService
from services.settings_service import SettingsService
from services.theme_service import ThemeService


class VDMApplication:
    def __init__(self):
        self.root = Path(__file__).resolve().parent
        self.env_paths = EnvironmentPaths(self.root)

        self.settings_service = SettingsService(self.env_paths.data_dir / "settings.json")
        self.settings = self.settings_service.load()
        self.history_service = HistoryService(self.env_paths.data_dir / "history.json")
        self.history = self.history_service.load()

        self.log_service = LogService(self.root / "log.txt", self.env_paths.logs_dir / "app.log")
        self.i18n = I18nService(self.root / "locales", self.settings.language)
        self.log_service.start_session(self.settings, self.root, self.env_paths)
        self.log_service.trace_paths(
            "application",
            root=self.root,
            data_dir=self.env_paths.data_dir,
            logs_dir=self.env_paths.logs_dir,
            tools_dir=self.env_paths.tools_dir,
        )
        self.log_service.trace_settings_snapshot(self.settings)
        self.theme_service = ThemeService()
        self.path_manager = PathManager(self.env_paths, self.settings)
        self.dependency_checker = DependencyChecker(self.settings, self.path_manager)
        self.install_manager = InstallManager(self.path_manager)
        self.bootstrap_manager = BootstrapManager(self.dependency_checker, self.install_manager)
        self.analyzer = Analyzer(self.settings, self.path_manager, self.log_service)
        self.downloader = Downloader(self.settings, self.path_manager, self.log_service)

    def run(self) -> int:
        self.log_service.trace_step("application", "run.enter")
        app = QApplication([])
        self.log_service.trace_step("application", "qapplication.created")
        self.theme_service.apply_theme(app, self.settings.theme)
        self.log_service.trace_step("application", "theme.applied", theme=self.settings.theme)

        try:
            window = MainWindow(
                settings=self.settings,
                history=self.history,
                history_service=self.history_service,
                analyzer=self.analyzer,
                downloader=self.downloader,
                log_service=self.log_service,
                dependency_checker=self.dependency_checker,
                bootstrap_manager=self.bootstrap_manager,
                path_manager=self.path_manager,
                theme_service=self.theme_service,
                settings_service=self.settings_service,
                app=app,
                i18n=self.i18n,
            )
            self.log_service.trace_step("application", "mainwindow.created")
            window.show()
            self.log_service.trace_step("application", "mainwindow.shown")

            exit_code = app.exec()
            self.log_service.trace_step("application", "qapplication.exec.exit", exit_code=exit_code)
            self.settings_service.save(self.settings)
            self.history_service.save(self.history)
            self.log_service.trace_step(
                "application",
                "state.saved",
                settings_path=str(self.env_paths.data_dir / "settings.json"),
                history_path=str(self.env_paths.data_dir / "history.json"),
            )
            self.log_service.info(f"VDM session closing | exit_code={exit_code}")
            return exit_code
        except Exception as exc:
            self.log_service.trace_exception("application.run", exc)
            raise
        finally:
            self.log_service.close()
