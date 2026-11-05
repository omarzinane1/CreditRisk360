
import json

from PySide6.QtCore import QObject, QUrl, Signal, QByteArray
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkReply,
    QNetworkRequest
)


class ApiClient(QObject):
    response_received = Signal(str, object)
    request_failed = Signal(str, str)

    def __init__(
        self,
        parent=None,
        base_url="http://127.0.0.1:8000"
    ):
        super().__init__(parent)

        self.base_url = base_url.rstrip("/")
        self.manager = QNetworkAccessManager(self)

    def _preparer_requete(self, path):
        request = QNetworkRequest(
            QUrl(self.base_url + path)
        )

        request.setTransferTimeout(5000)
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader,
            "application/json"
        )

        return request

    def get(self, path):
        request = self._preparer_requete(path)
        reply = self.manager.get(request)
        self._connecter_reponse(path, reply)

    def post(self, path, donnees):
        request = self._preparer_requete(path)

        corps = QByteArray(
            json.dumps(
                donnees,
                ensure_ascii=False,
                allow_nan=False
            ).encode("utf-8")
        )

        reply = self.manager.post(request, corps)
        self._connecter_reponse(path, reply)

    def patch(self, path, donnees):
        request = self._preparer_requete(path)

        corps = QByteArray(
            json.dumps(
                donnees,
                ensure_ascii=False,
                allow_nan=False
            ).encode("utf-8")
        )

        reply = self.manager.sendCustomRequest(
            request,
            QByteArray(b"PATCH"),
            corps
        )

        self._connecter_reponse(path, reply)

    def _connecter_reponse(self, path, reply):
        reply.finished.connect(
            lambda: self._terminer_requete(path, reply)
        )

    def _terminer_requete(self, path, reply):
        try:
            status = reply.attribute(
                QNetworkRequest.Attribute.HttpStatusCodeAttribute
            )

            contenu = bytes(
                reply.readAll()
            ).decode("utf-8", errors="replace")

            try:
                donnees = json.loads(contenu) if contenu else {}
            except json.JSONDecodeError:
                self.request_failed.emit(
                    path, "Réponse JSON invalide."
                )
                return

            if status is not None and status >= 400:
                detail = donnees.get(
                    "detail", "Erreur du serveur"
                ) if isinstance(donnees, dict) else donnees

                self.request_failed.emit(
                    path,
                    f"HTTP {status} : {detail}"
                )
                return

            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.request_failed.emit(
                    path, reply.errorString()
                )
                return

            self.response_received.emit(path, donnees)

        finally:
            reply.deleteLater()
