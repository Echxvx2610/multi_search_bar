import sys
import webbrowser
import os
import subprocess
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout

class SearchBar(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("Barra de búsqueda")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Establecer el fondo negro para la aplicación
        self.setStyleSheet("background-color: black; color: white;")

        # Crear la barra de búsqueda
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Buscar...")
        self.search_bar.setStyleSheet("""
            background-color: white;
            color: black;
            border: 2px solid #555;
            border-radius: 10px;
            padding: 5px;
        """)

        # Crear botón de búsqueda
        self.search_button = QPushButton("Buscar", self)
        self.search_button.setStyleSheet("""
            background-color: #555;
            color: white;
            border-radius: 10px;
            padding: 5px 10px;
        """)
        self.search_button.clicked.connect(self.on_search)

        # Crear botón de cierre
        self.close_button = QPushButton("Cerrar", self)
        self.close_button.setStyleSheet("""
            background-color: red;
            color: white;
            border-radius: 10px;
            padding: 5px 10px;
        """)
        self.close_button.clicked.connect(self.close)

        # Diseño horizontal para la barra de búsqueda, el botón de búsqueda y el de cierre
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.close_button)

        # Diseño principal para la barra de búsqueda y botones
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(search_layout)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Espacio para mover la ventana

        # Tamaño de la ventana
        self.resize(500, 50)

        # Posicionar la ventana en la parte superior central
        self.center_on_top()

        # Variable para mover la ventana
        self.drag_position = QPoint()

    def center_on_top(self):
        # Obtener el tamaño de la pantalla
        screen_geometry = QApplication.primaryScreen().geometry()

        # Calcular la posición central en la parte superior de la pantalla
        x = (screen_geometry.width() - self.width()) // 2
        y = 0  # En la parte superior de la pantalla

        # Mover la ventana a esa posición
        self.move(x, y)

    def mousePressEvent(self, event):
        # Guardamos la posición inicial cuando el usuario hace clic para mover la ventana
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        # Mover la ventana mientras arrastramos el mouse
        if self.drag_position:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        # Limpiar la posición cuando el mouse se suelta
        self.drag_position = QPoint()

    def on_search(self):
        # Obtener el texto de la barra de búsqueda
        search_text = self.search_bar.text()

        # Verificar el comando y ejecutar la acción correspondiente
        if search_text.startswith("-nav"):
            query = search_text[5:].strip()  # Obtener la búsqueda después de -nav
            if query:
                self.search_browser(query)
            else:
                print("Error: Escribe un término para buscar en el navegador.")
        elif search_text.startswith("-exp"):
            query = search_text[5:].strip()  # Obtener la búsqueda después de -exp
            if query:
                self.search_files(query)
            else:
                print("Error: Escribe un término para buscar en el explorador de archivos.")
        elif search_text.startswith("-sys"):
            query = search_text[5:].strip()  # Obtener la búsqueda después de -sys
            if query:
                self.search_system(query)
            else:
                print("Error: Escribe un término para buscar en la configuración del sistema.")
        else:
            print("Comando no reconocido. Usa '-nav', '-exp' o '-sys'.")

    def search_browser(self, query):
        """Realiza una búsqueda en el navegador web predeterminado."""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        print(f"Buscando en el navegador: {query}")

    def search_files(self, query):
        """Abre el explorador de archivos y busca un archivo o carpeta."""
        try:
            if sys.platform == "win32":  # Para Windows
                os.startfile(query)  # Abre la búsqueda en el explorador de archivos
            elif sys.platform == "darwin":  # Para macOS
                subprocess.run(["open", "-a", "Finder", query])
            elif sys.platform == "linux":  # Para Linux
                subprocess.run(["xdg-open", query])
            print(f"Buscando archivos: {query}")
        except Exception as e:
            print(f"Error al abrir el explorador de archivos: {e}")

    def search_system(self, query):
        """Abre las configuraciones del sistema dependiendo del sistema operativo."""
        try:
            if sys.platform == "win32":  # Para Windows
                subprocess.run(["ms-settings:", query])  # Intentamos abrir la configuración del sistema
            elif sys.platform == "darwin":  # Para macOS
                subprocess.run(["open", f"System Preferences/{query}"])
            elif sys.platform == "linux":  # Para Linux
                subprocess.run(["gnome-control-center", query])
            print(f"Buscando en configuraciones del sistema: {query}")
        except Exception as e:
            print(f"Error al abrir configuraciones del sistema: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SearchBar()
    window.show()

    sys.exit(app.exec())
