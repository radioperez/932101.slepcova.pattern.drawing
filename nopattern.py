import sys
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtWidgets import ( 
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QToolBar,
    QColorDialog,
)
from PyQt6.QtGui import (
    QAction,
    QIcon,
    QPixmap,
    QPainter,
    QPen,
    QColor,
)
class Canvas(QWidget):
    HISTORY_LEN = 10
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.setFixedSize(680, 480)
        self.canvas = QPixmap(self.size())
        self.canvas.fill(QColor("white"))

        self.last_pos = None
        self.painter = QPainter()
        self.pen = QPen(QColor("black"),1)
        self.history = []
        self.history.append(self.canvas.copy())

    def paintEvent(self, e):
        with QPainter(self) as painter:
            painter.drawPixmap(0,0, self.canvas)
    def mousePressEvent(self, e):
        if len(self.history) == self.HISTORY_LEN: self.history = self.history[1:]
        self.history.append(self.canvas.copy())
        self.last_pos = e.pos()
        QWidget.mousePressEvent(self, e)
    def mouseMoveEvent(self, e):
        # TODO check for eraser toggle
        self.painter.begin(self.canvas)
        self.painter.setPen(self.pen)
        self.painter.drawLine(self.last_pos, e.pos())
        self.painter.end()

        self.last_pos = e.pos()
        self.update()

        QWidget.mouseMoveEvent(self, e)
    def mouseReleaseEvent(self, e):
        self.last_pos = None
        QWidget.mouseReleaseEvent(self, e)
    
    def restoreCanvas(self):
        if self.history:
            self.canvas = self.history.pop()
            self.update()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.setGeometry(100, 100, 800, 600)

        self.setWindowTitle("Drawing app")

        # Toolbar
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)
        undo = QAction("Undo", self)
        toolbar.addAction(undo)
        self.get_color = QAction("Color #000000", self)
        self.color = QColor("black")
        toolbar.addAction(self.get_color)
        self.show_size = QAction("Size 1", self)
        inc_size = QAction("+", self)
        dec_size = QAction("-", self)
        self.pen_size = 1
        toolbar.addAction(self.show_size)
        toolbar.addAction(inc_size)
        toolbar.addAction(dec_size)

        # Canvas
        self.canvas_widget = Canvas()
        undo.triggered.connect(self.canvas_widget.restoreCanvas)
        self.get_color.triggered.connect(self.set_color)
        inc_size.triggered.connect(self.inc_size)
        dec_size.triggered.connect(self.dec_size)

        self.setCentralWidget(self.canvas_widget)
    def set_color(self):
        color = QColorDialog.getColor(self.color, self)
        if color:
            self.color = color
            self.canvas_widget.pen.setColor(color)
            self.get_color.setText("Color "+QColor(self.color).name())
    def inc_size(self):
        self.pen_size = abs(self.pen_size + 1) % 100
        self.canvas_widget.pen.setWidth(self.pen_size)
        self.show_size.setText("Size "+str(self.pen_size)) 
    def dec_size(self):
        self.pen_size = abs(self.pen_size - 1) % 100
        self.canvas_widget.pen.setWidth(self.pen_size)
        self.show_size.setText("Size "+str(self.pen_size)) 

app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec()