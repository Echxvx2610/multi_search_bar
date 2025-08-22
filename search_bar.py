import sys
import webbrowser
import os
import subprocess
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QPainter, QPainterPath, QColor

class UniversalSearchBar(QWidget):
    def __init__(self):
        super().__init__()
        
        # Estados de la ventana
        self.is_expanded = False
        self.notch_width = 120
        self.notch_height = 30
        self.expanded_width = 600
        self.expanded_height = 60
        
        # Configuración de la ventana
        self.setWindowTitle("Universal Search Bar")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Estilo base
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        self.setup_ui()
        self.setup_animations()
        
        # Iniciar en modo notch
        self.resize(self.notch_width, self.notch_height)
        self.center_on_top()
        
        # Variable para mover la ventana
        self.drag_position = QPoint()

    def setup_ui(self):
        # Crear la barra de búsqueda
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Escribe tu comando... (-nav, -exp, -sys, -app)")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 220);
                color: white;
                border: 2px solid rgba(80, 80, 80, 150);
                border-radius: 25px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid rgba(100, 149, 237, 180);
                background-color: rgba(50, 50, 50, 240);
            }
        """)
        self.search_bar.returnPressed.connect(self.on_search)
        self.search_bar.hide()  # Inicialmente oculto
        
        # Crear botón de cierre (X)
        self.close_button = QPushButton("×", self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 20, 20, 200);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: rgba(255, 30, 30, 220);
            }
            QPushButton:pressed {
                background-color: rgba(180, 15, 15, 200);
            }
        """)
        self.close_button.clicked.connect(self.collapse)
        self.close_button.hide()  # Inicialmente oculto
        
        # Layout principal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.search_bar)
        self.main_layout.addWidget(self.close_button)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear notch (elemento clickeable)
        self.notch_widget = QWidget(self)
        self.notch_widget.setStyleSheet("""
            background-color: rgba(20, 20, 20, 200);
            border-radius: 15px;
        """)
        self.notch_widget.setCursor(Qt.PointingHandCursor)
        
        # Agregar efecto de sombra
        self.add_shadow_effect()

    def add_shadow_effect(self):
        # Efecto de sombra para darle profundidad
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def setup_animations(self):
        # Animación para el tamaño
        self.size_animation = QPropertyAnimation(self, b"geometry")
        self.size_animation.setDuration(300)
        self.size_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.size_animation.finished.connect(self.animation_finished)

    def center_on_top(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = 5  # Pequeño margen desde el borde superior
        self.move(x, y)

    def paintEvent(self, event):
        if not self.is_expanded:
            # Dibujar el notch
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Crear el path del notch con bordes redondeados
            path = QPainterPath()
            rect = self.rect().adjusted(2, 2, -2, -2)
            path.addRoundedRect(rect, 15, 15)
            
            # Rellenar con color semi-transparente
            painter.fillPath(path, QColor(20, 20, 20, 200))
        
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.is_expanded:
                self.expand()
            else:
                self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_position and self.is_expanded:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_position = QPoint()

    def expand(self):
        if self.is_expanded:
            return
            
        self.is_expanded = True
        screen_geometry = QApplication.primaryScreen().geometry()
        
        # Calcular nueva posición centrada
        new_x = (screen_geometry.width() - self.expanded_width) // 2
        new_y = 20
        
        # Configurar animación
        start_rect = QRect(self.x(), self.y(), self.width(), self.height())
        end_rect = QRect(new_x, new_y, self.expanded_width, self.expanded_height)
        
        self.size_animation.setStartValue(start_rect)
        self.size_animation.setEndValue(end_rect)
        self.size_animation.start()

    def collapse(self):
        if not self.is_expanded:
            return
            
        self.is_expanded = False
        self.search_bar.clear()
        self.search_bar.hide()
        self.close_button.hide()
        
        screen_geometry = QApplication.primaryScreen().geometry()
        
        # Calcular posición del notch
        new_x = (screen_geometry.width() - self.notch_width) // 2
        new_y = 5
        
        # Configurar animación
        start_rect = QRect(self.x(), self.y(), self.width(), self.height())
        end_rect = QRect(new_x, new_y, self.notch_width, self.notch_height)
        
        self.size_animation.setStartValue(start_rect)
        self.size_animation.setEndValue(end_rect)
        self.size_animation.start()

    def animation_finished(self):
        if self.is_expanded:
            # Mostrar elementos de búsqueda
            self.search_bar.show()
            self.close_button.show()
            self.search_bar.setFocus()
        self.update()  # Forzar repintado

    def on_search(self):
        search_text = self.search_bar.text().strip()
        if not search_text:
            return
            
        # Procesar comandos
        if search_text.startswith("-nav "):
            query = search_text[5:].strip()
            if query:
                self.search_browser(query)
        elif search_text.startswith("-exp "):
            query = search_text[5:].strip()
            if query:
                self.search_files(query)
        elif search_text.startswith("-sys "):
            query = search_text[5:].strip()
            if query:
                self.search_system(query)
        elif search_text.startswith("-app "):
            query = search_text[5:].strip()
            if query:
                self.launch_application(query)
        else:
            # Búsqueda web por defecto
            self.search_browser(search_text)
        
        # Auto-colapsar después de la búsqueda
        QTimer.singleShot(500, self.collapse)

    def search_browser(self, query):
        """Realiza una búsqueda en el navegador web predeterminado."""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        print(f"🌐 Buscando en navegador: {query}")

    def search_files(self, query):
        """Abre el explorador de archivos y busca un archivo o carpeta."""
        try:
            if sys.platform == "win32":
                # Para Windows, buscar archivos o abrir carpetas
                if os.path.exists(query):
                    os.startfile(query)
                else:
                    # Buscar en el sistema
                    subprocess.run(["explorer", f"/select,{query}"], check=False)
            elif sys.platform == "darwin":
                subprocess.run(["open", "-a", "Finder", query])
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", query])
            print(f"📁 Buscando archivos: {query}")
        except Exception as e:
            print(f"❌ Error al abrir explorador: {e}")

    def search_system(self, query):
        """Abre las configuraciones del sistema."""
        try:
            if sys.platform == "win32":
                # Mapear comandos comunes de Windows
                system_commands = {
                    "wifi": "ms-settings:network-wifi",
                    "bluetooth": "ms-settings:bluetooth",
                    "sonido": "ms-settings:sound",
                    "pantalla": "ms-settings:display",
                    "actualizaciones": "ms-settings:windowsupdate",
                    "cuentas": "ms-settings:accounts",
                    "privacidad": "ms-settings:privacy"
                }
                
                command = system_commands.get(query.lower(), f"ms-settings:{query}")
                subprocess.run(["start", command], shell=True)
            elif sys.platform == "darwin":
                subprocess.run(["open", "-b", "com.apple.systempreferences"])
            elif sys.platform == "linux":
                subprocess.run(["gnome-control-center", query], check=False)
            print(f"⚙️ Abriendo configuración: {query}")
        except Exception as e:
            print(f"❌ Error al abrir configuración: {e}")

    def launch_application(self, app_name):
        """Lanza una aplicación específica."""
        try:
            if sys.platform == "win32":
                # Aplicaciones comunes de Windows
                common_apps = {
                    "notepad": "notepad.exe",
                    "calc": "calc.exe",
                    "paint": "mspaint.exe",
                    "cmd": "cmd.exe",
                    "powershell": "powershell.exe",
                    "explorer": "explorer.exe"
                }
                
                app_command = common_apps.get(app_name.lower(), app_name)
                subprocess.run([app_command])
            elif sys.platform == "darwin":
                subprocess.run(["open", "-a", app_name])
            elif sys.platform == "linux":
                subprocess.run([app_name])
            print(f"🚀 Lanzando aplicación: {app_name}")
        except Exception as e:
            print(f"❌ Error al lanzar {app_name}: {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.collapse()
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar la aplicación para que no se cierre al cerrar la última ventana
    app.setQuitOnLastWindowClosed(False)
    
    window = UniversalSearchBar()
    window.show()
    
    sys.exit(app.exec())
