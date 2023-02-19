import os,sys,re
import pdb 
import traceback
import ure.exporter


#document = Document(os.path.abspath(args.template)) if args.template else Document()
with open("input/full_markdown_text.md") as fh:
    text = fh.read()
    
md = [
    ['Main Project', [
        ['Wiki', text],
    ]],
]

exporter = ure.exporter.Docx(style_template="conf/APA Double Space.docx")

try:
    doc = exporter.process_markdown([['Main Project', [['Wiki', text]]]])
    doc.save("TestOutput.docx")
except Exception as e:
    extype, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
    raise

