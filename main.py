import sys
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtWidgets import ( 
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QToolBar,
    QColorDialog,
    QHBoxLayout,
    QFormLayout,
    QPushButton
)
from PyQt6.QtGui import (
    QAction,
    QIcon,
    QPixmap,
    QPainter,
    QPen,
    QColor,
)

class Memento:
    def __init__(self, state):
        self.state = state

class Canvas:
    def __init__(self, width, height):
        self.state = QPixmap(width, height)
        self.state.fill(QColor("white"))
    def save_state(self):
        return Memento(self.state.copy())
    def restore_state(self, memento: 'Memento'):
        self.state = memento.state.copy()

class Caretaker:
    HISTORY_LEN = 20
    def __init__(self):
        self.history = []
    def add(self, memento):
        if len(self.history) == self.HISTORY_LEN: self.history = self.history[1:]
        self.history.append(memento)
    def get_last(self):
        try:
            last = self.history.pop()
        except IndexError:
            return
        return last

class Canvas_widget(QWidget):
    idx = None
    def __init__(self, idx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idx = idx
        self.setFixedSize(680, 480)
        self.canvas = Canvas(500,500)
        self.caretaker = Caretaker()
        
        self.last_pos = None
        self.painter = QPainter()
        self.pen = QPen(QColor("black"),1)
        self.eraser = QPen(QColor("white"),1)
    def paintEvent(self, e):
        with QPainter(self) as painter:
            painter.drawPixmap(0,0,self.canvas.state)
    def mousePressEvent(self, e):
        savestate = self.canvas.save_state()
        self.caretaker.add(savestate)

        self.last_pos = e.pos()
        QWidget.mousePressEvent(self, e)
    def mouseMoveEvent(self, e):
        self.painter.begin(self.canvas.state)
        if e.buttons() == Qt.MouseButton.RightButton:
            self.painter.setPen(self.eraser)
        elif e.buttons() == Qt.MouseButton.LeftButton:
            self.painter.setPen(self.pen)
        self.painter.drawLine(self.last_pos, e.pos())
        self.painter.end()

        self.last_pos = e.pos()
        self.update()
        QWidget.mouseMoveEvent(self, e)
    def mouseReleaseEvent(self, e):
        self.last_pos = None
        QWidget.mouseReleaseEvent(self,e)

class Database:
    index = 0
    items = {}
    def create(self) -> Canvas_widget:
        self.index += 1
        canvas = Canvas_widget(self.index)
        self.items[self.index] = canvas
        return canvas
    def read(self, idx) -> Canvas_widget:
        return self.items[idx]
    def update(self, object) -> Canvas_widget:
        object.canvas.state.save(f'canvas{object.idx}.png')
        self.items[object.idx] = object
        return self.items[object.idx]
    def delete(self, object) -> Canvas_widget:
        return self.items.pop(object.idx)

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
        save = QAction("Save", self)
        new = QAction("New", self)
        toolbar.addAction(self.show_size)
        toolbar.addAction(inc_size)
        toolbar.addAction(dec_size)
        toolbar.addAction(save)
        toolbar.addAction(new)

        self.root = QWidget()
        self.layout = QHBoxLayout()
        self.canvas_list = QFormLayout()

        self.db = Database()
        # Canvas
        self.canvas_widget = Canvas_widget(0)
        self.on_new()
        self.current_index = self.canvas_widget.idx

        undo.triggered.connect(self.undo)
        self.get_color.triggered.connect(self.set_color)
        inc_size.triggered.connect(self.inc_size)
        dec_size.triggered.connect(self.dec_size)
        
        new.triggered.connect(self.on_new)
        save.triggered.connect(lambda: self.db.update(self.canvas_widget))

        self.layout.addWidget(self.canvas_widget)
        self.layout.addLayout(self.canvas_list)
        self.root.setLayout(self.layout)

        self.setCentralWidget(self.root)

    def on_new(self):
        canvas = self.db.create()
        self.set_canvas(canvas)
        canvas_button = QPushButton(f"Canvas {canvas.idx}")
        canvas_button.clicked.connect(lambda: self.set_canvas(self.db.read(canvas.idx)))
        x_button = QPushButton("x")
        x_button.clicked.connect(lambda: self.on_x(canvas_button, canvas))
        self.canvas_list.addRow(canvas_button, x_button)
    
    def on_x(self, button, canvas):
        if len(self.db.items) == 1: return
        self.db.delete(canvas)
        self.canvas_list.removeRow(button)
   
    def undo(self):
        savestate = self.canvas_widget.caretaker.get_last()
        if savestate: 
            self.canvas_widget.canvas.restore_state(savestate)
            self.canvas_widget.update()
    
    def set_canvas(self, canvas: Canvas_widget):
        self.canvas_widget.hide()
        canvas.hide()
        self.layout.replaceWidget(self.canvas_widget, canvas)
        self.canvas_widget = canvas
        self.layout.replaceWidget(canvas, self.canvas_widget)
        self.canvas_widget.show()
    
    def set_color(self):
        color = QColorDialog.getColor(self.color, self)
        if color:
            self.color = color
            self.canvas_widget.pen.setColor(color)
            self.get_color.setText("Color "+QColor(self.color).name())
    def inc_size(self):
        self.pen_size = abs(self.pen_size + 1) % 100
        self.canvas_widget.pen.setWidth(self.pen_size)
        self.canvas_widget.eraser.setWidth(self.pen_size)
        self.show_size.setText("Size "+str(self.pen_size)) 
    def dec_size(self):
        self.pen_size = abs(self.pen_size - 1) % 100
        self.canvas_widget.pen.setWidth(self.pen_size)
        self.canvas_widget.eraser.setWidth(self.pen_size)
        self.show_size.setText("Size "+str(self.pen_size)) 

app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec()