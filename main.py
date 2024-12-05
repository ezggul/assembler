import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget, QLabel, QFrame, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QProcess

class SICXEAssemblerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.initUI()
        self.process = QProcess(self)
        self.process.finished.connect(self.assembler_finished)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

    def initUI(self):
        self.setWindowTitle("SIC Assembler by Ezgi")
        self.setGeometry(100, 100, 800, 600)

        
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

       
        self.title_label = QLabel('SIC/XE Assembler by Ezgi')
        self.title_label.setFont(QFont('Arial', 24))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.line)

        
        self.select_file_btn = QPushButton('Dosya Seç', self)
        self.select_file_btn.setFont(QFont('Arial', 14))
        self.select_file_btn.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.select_file_btn, alignment=Qt.AlignCenter)

        
        self.info_label = QLabel('Dosya seçilmedi.', self)
        self.info_label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.info_label, alignment=Qt.AlignCenter)

        
        self.run_assembler_btn = QPushButton('Assembler Çalıştır', self)
        self.run_assembler_btn.setFont(QFont('Arial', 14))
        self.run_assembler_btn.clicked.connect(self.run_assembler)
        self.layout.addWidget(self.run_assembler_btn, alignment=Qt.AlignCenter)

        
        self.output_area = QTextEdit(self)
        self.output_area.setFont(QFont('Arial', 12))
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        self.setCentralWidget(self.central_widget)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Bir txt dosyası seçin", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            self.selected_file = file_name
            self.info_label.setText(f'Seçilen Dosya: {file_name}')
        else:
            self.selected_file = None
            self.info_label.setText('Dosya seçilmedi.')

    def run_assembler(self):
        if self.selected_file:
            #Seçilen dosyayı input.txt olarak kopyalama
            shutil.copy(self.selected_file, "input.txt")
            #assembler.py dosyasını çalıştırma
            assembler_path = os.path.join(os.path.dirname(__file__), 'assembler.py')
            print(f"Running assembler: python {assembler_path}")
            self.process.start("python3", [assembler_path])
        else:
            self.info_label.setText('Lütfen bir dosya seçin.')

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print("STDOUT:", stdout)
        self.output_area.append(f"STDOUT:\n{stdout}")

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        print("STDERR:", stderr)
        self.output_area.append(f"STDERR:\n{stderr}")

    def assembler_finished(self):
        if self.process.exitCode() == 0:
            self.info_label.setText('Assembler başarıyla çalıştırıldı.')
            # object.txt dosyasının içeriğini okuma ve gösterme
            with open("object.txt", "r") as file:
                object_code = file.read()
            self.output_area.setPlainText(object_code)
        else:
            self.info_label.setText('Assembler çalıştırılırken bir hata oluştu.')
            error_output = self.process.readAllStandardError().data().decode()
            self.output_area.setPlainText(f'Hata:\n{error_output}')
            print(f"Process error output: {error_output}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SICXEAssemblerApp()
    ex.show()
    sys.exit(app.exec_())
