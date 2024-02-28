import sys
import os
from os.path import basename
import cv2
import csv

from PySide6 import QtCore


# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
from modules.process_image import process_image
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None
IMAGES = {}

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Deteccion Micro Plasticos"
        description = "Deteccion Micro Plasticos"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.setColumnCount(6)
        widgets.tableWidget.setHorizontalHeaderLabels(["ID", "IMAGENES","Nº FIBRAS", "PROB. DE ACIERTO", "TAMAÑO", "COLOR"])

        # COMBO BOX
        widgets.comboBox_filtro.addItem("Filtro de Vidrio")
        widgets.comboBox_escala.addItems(["350","500","750", "1000"])
        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_images.clicked.connect(self.buttonClick)
        widgets.btn_dashboard.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.setVisible(False)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.setVisible(True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # IMAGE WIDGET BUTTONS
        widgets.bttn_import_images.clicked.connect(self.import_images)
        widgets.spinbox_n_imagenes.valueChanged.connect(lambda: UIFunctions.update_image_widget(self, widgets.spinbox_n_imagenes.value(), widgets.scroll_area_for_images, widgets.grid_layout_images, widgets.scrollAreaWidgetContents_2))

        # RIGHT SIDE SETTINGS MENU BUTTONS
        widgets.btn_logout.setVisible(False)
        widgets.btn_save_images.setDisabled(True)
        widgets.btn_save_images.setStyleSheet('background-image: url(:/icons/images/icons/cil-image-plus.png); color: grey;')
        widgets.btn_save_images.clicked.connect(lambda: UIFunctions.save_images(self, IMAGES))
        widgets.btn_export_csv.setDisabled(True)
        widgets.btn_export_csv.setStyleSheet('background-image: url(:/icons/images/icons/cil-file.png);color: grey;')
        widgets.btn_export_csv.clicked.connect(lambda: UIFunctions.export_csv(self, widgets.tableWidget))

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()


        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_images":
            widgets.stackedWidget.setCurrentWidget(widgets.images)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_dashboard":
            widgets.stackedWidget.setCurrentWidget(widgets.dashboard) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition().toPoint()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')


    def update_table(self):
        table = widgets.tableWidget
        table.clearContents()
        if table.rowCount() < len(IMAGES):
            table.setRowCount(len(IMAGES)+1)
        for i, (path, data) in enumerate(IMAGES.items()):
            table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            table.setItem(i, 1, QTableWidgetItem(basename(path)))
            table.setItem(i, 2, QTableWidgetItem(str(data["Fibres_detected"])))
            table.setItem(i, 3, QTableWidgetItem(str(data["Scores"])))
            table.setItem(i, 4, QTableWidgetItem(str(data["Size"])))
            table.setItem(i, 5, QTableWidgetItem(str(data["Color"])))
        
        print("Table updated")

    # IMPORT IMAGES
    def import_images(self):
        print("Importing images message box")
        msg = QMessageBox(self)
        msg.setStyleSheet("color:white;background:#21252B")
        msg.setText("Cuidado")
        msg.setInformativeText('Importar nuevas imagenes sobreescribira las imagenes actuales')
        msg.setWindowTitle("Importar Imagenes")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        botonCancelar = msg.button(QMessageBox.StandardButton.No)
        botonCancelar.setText("Cancelar")
        botonAceptar = msg.button(QMessageBox.StandardButton.Yes)
        botonAceptar.setText("Aceptar")
        msg.exec()

        if msg.clickedButton() == botonCancelar:
            print("Message box closed without importing images")
            return
        if msg.clickedButton() == botonAceptar:
            print("Importing images")
            file_dialog = QFileDialog()
            image_path, _ = file_dialog.getOpenFileNames(self, 'Open Image', '', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
            # Display all chosen images
            if image_path:
                loading_window = Load_Window(self)
                loading_window.show()
                global IMAGES
                IMAGES.clear()
                scroll_area = widgets.scroll_area_for_images
                width = scroll_area.width()
                image_size = width // 2
                image_layout = widgets.grid_layout_images
                #for i in reversed(range(image_layout.count())):
                #    image_layout.removeWidget(image_layout.itemAtPosition(i).widget())                    
                clearLayout(image_layout)
                image_widget = widgets.scrollAreaWidgetContents_2
                total_fibre_count = 0
                for i, path in enumerate(image_path):
                    QApplication.processEvents() # To prevent the GUI from freezing
                    result_img, mask, scores, size, color = process_image(path, widgets.comboBox_filtro.currentText(), widgets.comboBox_escala.currentText())
                    IMAGES[path] = {"Image":result_img,"Mask": mask,"Fibres_detected": len(scores), "Scores":scores, "Size":size, "Color":color}
                    total_fibre_count += len(scores)
                    vbox = QVBoxLayout()
                    height, width, channel = result_img.shape
                    bytesPerLine = 3 * width
                    #image_mask_overlay = cv2.addWeighted(result_img, 0.7, mask, 0.3, 0)
                    qImg = QImage(result_img, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
                    pixmap = QPixmap.fromImage(qImg)
                    pixmap = pixmap.scaled(image_size, image_size, Qt.AspectRatioMode.KeepAspectRatio)
                    label = QLabel()
                    label.setPixmap(pixmap)
                    vbox.addWidget(label)
                    file_name_label = QLabel(basename(path))
                    vbox.addWidget(file_name_label)
                    row = i // 2
                    col = i % 2
                    if len(image_path) == 1:
                        row = 0
                        col = 0
                    image_layout.addLayout(vbox, row, col)
                
                self.update_table()
                widgets.n_fibras_detectadas.setText(str(total_fibre_count))
                loading_window.close()
                image_widget.setLayout(image_layout)
                scroll_area.setWidget(image_widget)
                widgets.scroll_area_for_images
                widgets.spinbox_n_imagenes.setMaximum(len(image_path))
                widgets.spinbox_n_imagenes.blockSignals(True)
                if len(image_path) == 1:
                    widgets.spinbox_n_imagenes.setValue(1)
                else:
                    widgets.spinbox_n_imagenes.setValue(1) #Should be 2
                widgets.spinbox_n_imagenes.blockSignals(False)
                widgets.spinbox_n_imagenes.setMinimum(1)
                widgets.btn_save_images.setEnabled(True)
                widgets.btn_save_images.setStyleSheet('background-image: url(:/icons/images/icons/cil-image-plus.png); color: white;')
                widgets.btn_export_csv.setEnabled(True)
                widgets.btn_export_csv.setStyleSheet('background-image: url(:/icons/images/icons/cil-file.png); color: white;')
                print("Images imported")

    # CHANGES THE NUMBER OF IMAGES DISPLAYED IN A ROW
    def update_image_widget(self, n_images, scroll_area, image_layout, image_widget):
        print(f"Updating image widget to display {n_images} images")
        print(image_layout)
        for i in reversed(range(image_layout.count())):
            image_layout.itemAt(i).widget().setParent(None)
        for i, image in enumerate(IMAGES):
            row = i // n_images + 1  # +1 to account for the spin box
            col = i % n_images
            label = QLabel(self)
            label.setPixmap(QPixmap(image["Image"]))
            image_layout.addWidget(label, row, col)
        image_widget.setLayout(image_layout)
        scroll_area.setWidget(image_widget)
    
    # SAVES PROCESSED IMAGES IN GIVEN DIRECTORY
    def save_images(self, images):
        print("Saving images")
        file_dialog = QFileDialog()
        if file_dialog.exec_():
            folder_path = file_dialog.getExistingDirectory(self)
            for image in images:
                path= image.split("/")[-1]
                cv2.imwrite(os.path.join(folder_path,path), images[image]["Image"])
            print("Images saved in " + folder_path)

    # EXPORTS TABLE TO CSV FORMAT
    def export_csv(self, table):
        print(table)  
        print("Exporting to csv")
        file_dialog = QFileDialog()
        if file_dialog.exec_():
            folder_path = file_dialog.getExistingDirectory(self)
            file_path = os.path.join(folder_path, "csv_images.csv")
            with open(file_path, 'w') as stream:
                    writer = csv.writer(stream)
                    for row in range(table.rowCount()):
                        rowdata = []
                        for column in range(table.columnCount()):
                            item = table.item(row, column)
                            if item is not None:
                                rowdata.append(item.text())
                            else:
                                rowdata.append('')
                        writer.writerow(rowdata)
            
def clearLayout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            else:
                clearLayout(child.layout())


class Load_Window(QDialog):
    def __init__(self, parent=None):
        super(Load_Window, self).__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.setFixedSize(200, 100)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(33, 37, 43)) 
        self.setPalette(p)
        layout = QVBoxLayout()
        label = QLabel("Loading...")
        label.setStyleSheet("color:white")
        layout.addWidget(label)
        self.setLayout(layout)

                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
