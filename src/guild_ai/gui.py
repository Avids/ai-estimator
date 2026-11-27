import sys, csv
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QPushButton,QListWidget,QGraphicsView,QGraphicsScene,QFileDialog,QInputDialog,QMessageBox,QLabel
from PySide6.QtGui import QPixmap,QImage,QPen,QColor
from PySide6.QtCore import Qt
import fitz
from .core import Project
class Canvas(QGraphicsView):
    def __init__(self,window): super().__init__(); self.window=window; self.setScene(QGraphicsScene(self)); self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    def wheelEvent(self,event): self.scale(1.2 if event.angleDelta().y()>0 else 1/1.2,1.2 if event.angleDelta().y()>0 else 1/1.2)
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.RightButton and self.window.sheet is not None:
            pt=self.mapToScene(event.position().toPoint()); self.window.add(pt.x(),pt.y()); return
        super().mousePressEvent(event)
class Window(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Guild Electrical AI - prototype'); self.resize(1200,800); self.project=None; self.sheet=None; self.rows=[]
        central=QWidget(); self.setCentralWidget(central); layout=QHBoxLayout(central); left=QVBoxLayout(); layout.addLayout(left,1); self.canvas=Canvas(self); layout.addWidget(self.canvas,4)
        for text,fn in [('Open / create project',self.open_project),('Import PDF',self.import_pdf),('Delete selected mark',self.delete),('Export current PDF',self.export),('Export counts CSV',self.counts)]:
            b=QPushButton(text); b.clicked.connect(fn); left.addWidget(b)
        left.addWidget(QLabel('Drawings')); self.list=QListWidget(); left.addWidget(self.list); self.list.currentRowChanged.connect(self.show_sheet)
        left.addWidget(QLabel('Marks (right-click drawing to add)')); self.marklist=QListWidget(); left.addWidget(self.marklist)
    def open_project(self):
        path=QFileDialog.getExistingDirectory(self,'Select project folder');
        if not path:return
        if self.project:self.project.close()
        self.project=Project(path); self.refresh()
    def refresh(self):
        self.sheet=None; self.canvas.scene().clear(); self.marklist.clear(); self.rows=self.project.sheets(); self.list.clear()
        for r in self.rows:self.list.addItem(r['title'])
        if self.rows:self.list.setCurrentRow(0)
    def import_pdf(self):
        if not self.project:return
        path,_=QFileDialog.getOpenFileName(self,'Import PDF','','PDF (*.pdf)')
        if path:
            try:self.project.import_pdf(path); self.refresh()
            except Exception as e: QMessageBox.warning(self,'Import failed',str(e))
    def show_sheet(self,i):
        if i<0:return
        self.sheet=self.rows[i]; self.draw(); self.canvas.resetTransform(); self.canvas.fitInView(self.canvas.scene().sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
    def draw(self):
        scene=self.canvas.scene(); scene.clear(); self.marklist.clear()
        with fitz.open(self.project.root/self.sheet['path']) as d:
            p=d[0]; pix=p.get_pixmap(alpha=False); img=QImage(pix.samples,pix.width,pix.height,pix.stride,QImage.Format.Format_RGB888).copy(); scene.addPixmap(QPixmap.fromImage(img)); self.derotation=p.derotation_matrix
            for m in self.project.marks(self.sheet['id']):
                pt=fitz.Point(m['x'],m['y'])*p.rotation_matrix; scene.addEllipse(pt.x-5,pt.y-5,10,10,QPen(QColor('green'),2)); self.marklist.addItem(m['kind']+' | '+m['id'])
        scene.setSceneRect(0,0,pix.width,pix.height)
    def add(self,x,y):
        kind,ok=QInputDialog.getText(self,'Count item','Device type:')
        if ok and kind.strip():
            pt=fitz.Point(x,y)*self.derotation
            try:self.project.add_mark(self.sheet['id'],kind,pt.x,pt.y); self.draw()
            except Exception as e: QMessageBox.warning(self,'Mark failed',str(e))
    def delete(self):
        item=self.marklist.currentItem()
        if item:self.project.delete_mark(item.text().rsplit(' | ',1)[1]); self.draw()
    def export(self):
        if self.sheet is not None:
            dest=self.project.root/'exports'/f"{self.sheet['id']}-marked.pdf"; self.project.export_pdf(self.sheet['id'],dest); QMessageBox.information(self,'Exported',str(dest))
    def counts(self):
        if not self.project:return
        dest=self.project.root/'exports'/'counts.csv'
        with dest.open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f); w.writerow(['Sheet ID','Drawing','Device type','Count']); w.writerows(self.project.db.execute('SELECT s.id,s.title,m.kind,COUNT(*) FROM marks m JOIN sheets s ON s.id=m.sheet_id GROUP BY s.id,m.kind'))
        QMessageBox.information(self,'Exported',str(dest))
def run():
    app=QApplication(sys.argv); w=Window(); w.show(); sys.exit(app.exec())
