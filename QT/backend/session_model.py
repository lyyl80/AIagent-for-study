from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot, Signal, QObject
from core.agent.memory import Memory
import os


class SessionListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sessions = []
        self.refresh()

    # ====== 角色定义 ======
    def roleNames(self):
        return {
            Qt.UserRole + 1: b"filename",
            Qt.UserRole + 2: b"summary",
            Qt.UserRole + 3: b"created_time",
            Qt.UserRole + 4: b"message_count",
        }

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._sessions):
            return None
        s = self._sessions[index.row()]
        mapping = {
            Qt.UserRole + 1: s.get("filename", ""),
            Qt.UserRole + 2: s.get("summary", ""),
            Qt.UserRole + 3: s.get("created_time", "")[:19],
            Qt.UserRole + 4: s.get("message_count", 0),
        }
        return mapping.get(role)

    def rowCount(self, parent=QModelIndex()):
        return len(self._sessions)

    @Slot()
    def refresh(self):
        self.beginResetModel()
        self._sessions = Memory.list_sessions()
        self.endResetModel()

    @Slot(str)
    def deleteSession(self, filename):
        session_path = os.path.join("session", filename)
        if os.path.exists(session_path):
            os.remove(session_path)
        self.refresh()