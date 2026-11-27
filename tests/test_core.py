import fitz, hashlib
from guild_ai.core import Project

def test_import_marks_export(tmp_path):
    src=tmp_path/'drawing.pdf'
    with fitz.open() as d:
        for rotation in (0,90):
            p=d.new_page(width=400,height=300); p.insert_text((40,40),'E201'); p.set_rotation(rotation)
        d.save(src)
    before=hashlib.sha256(src.read_bytes()).hexdigest(); project=Project(tmp_path/'project')
    assert project.import_pdf(src)==2; assert project.import_pdf(src)==0
    for s in project.sheets():
        mid=project.add_mark(s['id'],'Duplex',50,80); assert len(project.marks(s['id']))==1
        dest=project.root/'exports'/f'{s["id"]}.pdf'; project.export_pdf(s['id'],dest)
        with fitz.open(dest) as d:
            p=d[0]; a=next(p.annots()); assert a.info['content']=='Duplex'; assert abs(a.rect.x0-45)<2
        project.delete_mark(mid); assert not project.marks(s['id'])
    assert hashlib.sha256(src.read_bytes()).hexdigest()==before
    project.close(); assert len(Project(tmp_path/'project').sheets())==2
