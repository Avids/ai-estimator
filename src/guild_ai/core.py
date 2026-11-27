from pathlib import Path
import hashlib, sqlite3, shutil, uuid, re
import fitz

SCHEMA = '''
CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, filename TEXT NOT NULL, path TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sheets(id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id), page INTEGER NOT NULL, path TEXT NOT NULL, title TEXT, rotation INTEGER NOT NULL, width REAL, height REAL, UNIQUE(document_id,page));
CREATE TABLE IF NOT EXISTS marks(id TEXT PRIMARY KEY, sheet_id TEXT NOT NULL REFERENCES sheets(id), kind TEXT NOT NULL, x REAL NOT NULL, y REAL NOT NULL);
'''
class Project:
    def __init__(self, root):
        self.root = Path(root).resolve(); self.root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root/'project.db'); self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON'); self.db.executescript(SCHEMA)
        for folder in ('originals','pages','exports'): (self.root/folder).mkdir(exist_ok=True)
    def import_pdf(self, source):
        source = Path(source); digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if self.db.execute('SELECT 1 FROM documents WHERE id=?',(digest,)).fetchone(): return 0
        with fitz.open(source) as doc:
            if doc.needs_pass or not doc.is_pdf or not len(doc): raise ValueError('Expected an unlocked, nonempty PDF')
            original = self.root/'originals'/f'{digest}.pdf'; shutil.copyfile(source,original)
            with self.db:
                self.db.execute('INSERT INTO documents VALUES(?,?,?)',(digest,source.name,str(original.relative_to(self.root))))
                for i,p in enumerate(doc):
                    sid=f'{digest}-{i+1:04}'; dest=self.root/'pages'/f'{sid}.pdf'
                    with fitz.open() as out:
                        out.insert_pdf(doc,from_page=i,to_page=i); out.save(dest)
                    text=p.get_text(); matches=set(re.findall(r'\bE[- ]?\d{3,4}(?:\.\d+)?\b',text,re.I)); title=next(iter(matches))+' (candidate)' if len(matches)==1 else f'{source.name} / page {i+1}'
                    self.db.execute('INSERT INTO sheets VALUES(?,?,?,?,?,?,?,?)',(sid,digest,i+1,str(dest.relative_to(self.root)),title,p.rotation,p.rect.width,p.rect.height))
            return len(doc)
    def sheets(self): return self.db.execute('SELECT * FROM sheets ORDER BY document_id,page').fetchall()
    def marks(self,sid): return self.db.execute('SELECT * FROM marks WHERE sheet_id=? ORDER BY rowid',(sid,)).fetchall()
    def add_mark(self,sid,kind,x,y):
        if not kind.strip(): raise ValueError('Type required')
        row=self.db.execute('SELECT * FROM sheets WHERE id=?',(sid,)).fetchone()
        with fitz.open(self.root/row['path']) as d:
            p=d[0]; bounds=p.rect * p.derotation_matrix
            if not bounds.contains(fitz.Point(x,y)): raise ValueError('Point outside drawing')
        mid=uuid.uuid4().hex
        with self.db: self.db.execute('INSERT INTO marks VALUES(?,?,?,?,?)',(mid,sid,kind.strip(),x,y))
        return mid
    def delete_mark(self,mid):
        with self.db: self.db.execute('DELETE FROM marks WHERE id=?',(mid,))
    def export_pdf(self,sid,dest):
        row=self.db.execute('SELECT * FROM sheets WHERE id=?',(sid,)).fetchone(); dest=Path(dest).resolve()
        if dest.parent != (self.root/'exports').resolve(): raise ValueError('Export must be inside project exports folder')
        with fitz.open(self.root/row['path']) as doc:
            p=doc[0]
            for m in self.marks(sid):
                x,y=m['x'],m['y']; a=p.add_circle_annot(fitz.Rect(x-5,y-5,x+5,y+5)); a.set_colors(stroke=(0,0.6,0.2)); a.set_info(content=m['kind'],subject=m['id']); a.update()
            doc.save(dest)
    def close(self): self.db.close()
