"""Point d'entree de Pystart.

Lance l'application Qt, charge la configuration et ouvre la fenetre
principale. C'est aussi ici qu'on decide de verifier les mises a jour au
demarrage (en tache de fond, sans bloquer).

Usage :
    python -m app          # depuis les sources
    pystart                # une fois installe (voir pyproject.toml)
"""

from __future__ import annotations

import logging
import sys

from app import __version__
from app.core import paths
from app.core.config import AppConfig
from app.progress.store import ProgressStore


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(paths.logs_dir() / "pystart.log", encoding="utf-8"),
            logging.StreamHandler(sys.stderr),
        ],
    )


def main(argv: list[str] | None = None) -> int:
    _setup_logging()
    logging.info("Demarrage de Pystart %s", __version__)

    # Import de Qt le plus tard possible : les modules `core` restent
    # testables sans interface graphique.
    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow
    from app.ui.theme import apply_theme

    app = QApplication(argv if argv is not None else sys.argv)
    app.setApplicationName("Pystart")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Pystart")

    config = AppConfig.load()
    apply_theme(app, config.theme)

    store = ProgressStore()
    window = MainWindow(config, store)
    window.show()

    if config.check_updates_on_startup:
        _schedule_background_update_check(window)

    exit_code = app.exec()
    store.close()
    return exit_code


def _schedule_background_update_check(window) -> None:
    """Verifie discretement s'il existe une nouvelle version, 3s apres le demarrage."""
    from PySide6.QtCore import QThread, QTimer

    from app.ui.updates_dialog import _CheckWorker

    def start_check() -> None:
        worker = _CheckWorker()
        thread = QThread(window)
        worker.moveToThread(thread)
        worker.setParent(window)
        thread.started.connect(worker.run)

        def handle(info) -> None:
            thread.quit()
            if info.update_available:
                window.statusBar().showMessage(
                    f"🚀 Nouvelle version disponible : {info.latest_version} "
                    f"(menu Aide > Mises a jour)",
                    15000,
                )

        worker.done.connect(handle)
        worker.failed.connect(lambda _msg: thread.quit())
        window._update_check_thread = thread  # garde une reference
        thread.start()

    QTimer.singleShot(3000, start_check)


if __name__ == "__main__":
    raise SystemExit(main())
