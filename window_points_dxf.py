from PySide6.QtGui import QCloseEvent
from ezdxf import new as new_dxf
from ezdxf.document import Drawing
from typing import List, Tuple
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLineEdit, QFileDialog, QLabel


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()


    def setup(self):
        self.file_choice = QLineEdit('- plik txt -', self)
        self.file_choice.setFixedWidth(250)
        self.file_choice.move(25, 120)
        example_label = QLabel("Format danych:\n1    5000000.54  7000000.89  135.78  KOD", self)
                               
        example_label.move(25, 90)  # Ustawienie pozycji etykiety
        choose_file_btn = QPushButton("Wybierz plik", self)
        choose_file_btn.move(50, 150)
        choose_file_btn.clicked.connect(self.choose_file)
        create_dxf = QPushButton("Stwórz dxf z punktami", self)
        create_dxf.move(150, 150)
        create_dxf.clicked.connect(self.generate_dxf_file)
        quit_btn = QPushButton("Wyjście", self)
        quit_btn.move(220, 270)
        quit_btn.clicked.connect(QApplication.instance().quit)
        self.setFixedSize(300, 300)
        self.setWindowTitle("DXF Points")
        self.show()


    def choose_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Wybierz plik txt", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            self.file_choice.setText(file_name)


    def read_coordinates(self, file_path: str) -> List[Tuple[int, float, float, float, str]]:
        measurements = []
        with open(file_path) as stream:
            content = stream.read()
            cleaned_lines = ["\t".join(line.split()) for line in content.split('\n')]
            measurements.extend(cleaned_lines)
        return [(int(''.join(filter(str.isdigit, line.split('\t')[0]))),
                float(line.split('\t')[2]),
                float(line.split('\t')[1]),
                float(line.split('\t')[3]),
                str(line.split('\t')[4])) for line in measurements if len(line) > 3]


    def generate_dxf_file(self):
        file_path = self.file_choice.text()
        if file_path == '- plik txt -':
            QMessageBox.warning(self, "Błąd", "Proszę wybrać plik!")
            return
        try:
            points = self.read_coordinates(file_path)
            if not points:
                QMessageBox.warning(self, "Błąd", "Brak punktów do zapisania!")
                return
            doc = new_dxf(dxfversion='R2010')  # Upewniamy się, że obiekt doc to Drawing
            self.create_points(points, doc)
            save_path, _ = QFileDialog.getSaveFileName(self, "Zapisz plik DXF", "", "DXF Files (*.dxf)")
            if save_path:
                doc.saveas(save_path)
                QMessageBox.information(self, "Sukces", "Plik DXF został pomyślnie zapisany!")
            else:
                QMessageBox.warning(self, "Błąd", "Nie zapisano pliku.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd: {e}")


    def create_points(self, points: List[Tuple[int, float, float, float, str]], doc: Drawing) -> None:
        msp = doc.modelspace()  # Używamy doc.modelspace() prawidłowo
        sorted_points = sorted(points, key=lambda x: x[0])  # Sortujemy punkty po numerze
        for nr, x, y, z, desc in sorted_points:
            msp.add_point(location=(x, y, z), dxfattribs={'layer': 'POINTS'})
            msp.add_text(f'{nr}', dxfattribs={'insert': (x-0.4, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})
            msp.add_text(desc, dxfattribs={'insert': (x+0.1, y+0.1, z + 0.2), 'style': 'Standard', 'height': 0.1})


    def closeEvent(self, event: QCloseEvent):
        should_close = QMessageBox.question(self, "Zamknięcie aplikacji", "Czy na pewno chcesz zamknąć?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if should_close == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication([])
    login_window = LoginWindow()
    app.exec()
