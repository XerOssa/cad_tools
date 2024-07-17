import math
from typing import List, Tuple
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLineEdit, QFileDialog
from connect_points import connect_points_with_lwpolyline
from create_profiles import read_coordinates

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setup()

    def setup(self):
        self.file_choice = QLineEdit('                              - plik txt -', self)
        self.file_choice.setFixedWidth(250)
        self.file_choice.move(25, 20)

        choose_file_btn = QPushButton("Wybierz plik", self)
        choose_file_btn.move(110, 50)
        choose_file_btn.clicked.connect(self.choose_file)

        connect_points = QPushButton("Połącz punkty o tym samym kodzie ", self)
        connect_points.move(20, 150)
        connect_points.clicked.connect(self.connect_points)

        create_profiles = QPushButton("Utwórz profile ", self)
        create_profiles.move(20, 180)
        create_profiles.clicked.connect(self.create_profiles)

        quit_btn = QPushButton("Wyjście", self)
        quit_btn.move(220, 270)
        quit_btn.clicked.connect(QApplication.instance().quit)

        self.setFixedSize(300, 300)
        self.setWindowTitle("Autocad")

        self.show()

    def choose_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Wybierz plik txt", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            self.file_choice.setText(file_name)

    def connect_points(self):
        input_file_path = self.file_choice.text()
        if input_file_path == '- plik txt -':
            QMessageBox.warning(self, "Brak pliku", "Proszę wybrać plik tekstowy przed utworzeniem pliku dxf.")
            return
        
        try:
            points = read_coordinates(input_file_path)
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            output_dxf_path, _ = QFileDialog.getSaveFileName(self, "Zapisz jako DXF", "", "DXF Files (*.dxf)", options=options)
            if output_dxf_path:
                # Tutaj możesz wywołać funkcję tworzenia pliku DXF z punktami
                # create_dxf_file(points, output_dxf_path, ...)
                QMessageBox.information(self, "Konwersja zakończona", f"Plik DXF został zapisany jako {output_dxf_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd konwersji", f"Wystąpił błąd podczas konwersji pliku: {str(e)}")

    def create_profiles(self):
        input_file_path = self.file_choice.text()
        if input_file_path == '- plik txt -':
            QMessageBox.warning(self, "Brak pliku", "Proszę wybrać plik tekstowy przed utworzeniem pliku dxf.")
            return
        
        try:
            points = read_coordinates(input_file_path)
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            output_dxf_path, _ = QFileDialog.getSaveFileName(self, "Zapisz jako DXF", "", "DXF Files (*.dxf)", options=options)
            if output_dxf_path:
                # Tutaj możesz wywołać funkcję tworzenia pliku DXF z punktami
                # create_dxf_file(points, output_dxf_path, ...)
                QMessageBox.information(self, "Konwersja zakończona", f"Plik DXF został zapisany jako {output_dxf_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd konwersji", f"Wystąpił błąd podczas konwersji pliku: {str(e)}")

    def closeEvent(self, event: QCloseEvent):
        should_close = QMessageBox.question(self, "Zamknięcie aplikacji",  "Czy na pewno chcesz zamknąć?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if should_close == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication([])

    login_window = LoginWindow()

    app.exec()
