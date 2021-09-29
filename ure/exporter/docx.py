import os,sys,re
import subprocess
import zipfile
import lxml, lxml.etree
import textwrap
import shutil
import tempfile

from .baseclass import BaseExporter

def print_xml(element):
    print(lxml.etree.tostring(element, encoding='Unicode', pretty_print=True))


class DocX(BaseExporter):

    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        if not os.path.exists(filename):
            raise FileExistsError(f"File '{filename}' does not exist.")
        if not re.search(r'\.docx$', filename, re.I):
            raise Exception(r"File {filename} does no have a docx extension")
        self.filename = filename

    def process_source(self):
        """ Process the source document. We use pandoc to do the primary translation of docx data to markdown (via the markdown_mmd format). However, pandoc absolutely has no ability to process page or section breaks from docx, so we actually go through and hack new headings to indicate page and sections breaks via the hack_docx() method, which returns a tempfile that has the modifications made to it. """
        filepath = os.path.abspath(self.filename)
        moduledir = os.path.dirname(os.path.abspath(__file__))
        tempfile = self.hack_docx(filepath)
        exc = subprocess.run(['pandoc', '-f', 'docx', '-t', 'markdown_mmd', tempfile], capture_output=True, check=True)
        os.remove(tempfile) #clean up the temp file
        return(self.clean_pandoc_markdown(exc.stdout.decode('utf-8')))
        
    def hack_docx(self, filename):
        """ Because pandoc doesn't translate page or section breaks, we create a tempfile and add in keys to later manipulate. docx is an xml format. While the python-docx module reads docx and can do a nominal amount of appending, it can't modify or replace existing content very well, so we have to be very manual and handle it using an lxml parser """
        
        with zipfile.ZipFile(filename) as source:
            # get a temp file, which we primarily use for the filename.
            tmpfd, tmpfilename = tempfile.mkstemp(suffix='.docx')
            os.close(tmpfd)
            # copy the original file to the tempfile
            shutil.copy2(filename, tmpfilename)
            # open the docx, which is a zip of several xml files
            with zipfile.ZipFile(tmpfilename, "w") as dest:
                # Iterate over the input "files", i.e. pieces of the docx
                for sourceinfo in source.infolist():
                    # we only need to modify the document.xml file.  All the rest are straight copy
                    with source.open(sourceinfo) as docpart:
                        if sourceinfo.filename == 'word/document.xml':
                            xml_content = source.read(sourceinfo.filename)
                            tree = lxml.etree.fromstring(xml_content)
                            new_tree = self.update_xml(tree)    
                            dest.writestr(sourceinfo.filename, lxml.etree.tostring(new_tree))
                        else: # Other file, dont want to modify => just copy it
                            dest.writestr(sourceinfo, source.read(sourceinfo.filename))
        return(tmpfilename)


    def update_xml(self, tree):

        nsmap = ' '.join([f'xmlns:{ns}="{path}"' for ns,path in tree.nsmap.items()])                
        for child in tree.iter():
            items = child.items()
            #
            # -- section break!
            #
            if child.tag[-6:] == 'sectPr' and child.prefix == 'w':
                hack_element = lxml.etree.XML(textwrap.dedent(f"""
                    <w:p {nsmap} w:rsidR="001515C9" w:rsidRDefault="001515C9" w:rsidP="001515C9">
                        <w:pPr>
                            <w:pStyle w:val="Heading1"/>
                        </w:pPr>
                        <w:r>
                            <w:t>@@@NEWSECTION@@@</w:t>
                        </w:r>
                    </w:p>
                """))
                wrxml = child.getparent() 
                if len(wrxml.tag) >= 4 and wrxml.tag[-4:] == 'body':
                    # We skip the last section, which is the root section
                    # "For all sections except the last section, the sectPr element is stored as a child element of the last paragraph in the section. For the last section, the sectPr is stored as a child element of the body element" (http://officeopenxml.com/WPsection.php)
                    continue
                
                #print(lxml.etree.tostring(breakcontainer, pretty_print=True, encoding='Unicode'))
                breakcontainer = wrxml.getparent() # the whole page break 
                body = breakcontainer.getparent() # the whole doc, because
                break_index =  body.index(breakcontainer) 
                body.insert(break_index, hack_element)


            if child.tag[-2:] == 'br' and items[0][1] == 'page' and child.prefix == 'w' and child.values and child.values()[0] == 'page':
                #
                # Page Break!
                #
                # XML Info on headers: http://officeopenxml.com/WPheaders.php
                    hack_element = lxml.etree.XML(textwrap.dedent(
                        f"""
                        <w:p {nsmap} w:rsidR="001515C9" w:rsidRDefault="001515C9" w:rsidP="001515C9">
                            <w:pPr>
                                <w:pStyle w:val="Heading1"/>
                            </w:pPr>
                            <w:r>
                                <w:t>@@@NEWPAGE@@@</w:t>
                            </w:r>
                        </w:p>
                        """))

                    wrxml = child.getparent() # -- this is the enclosing piece
                    breakcontainer = wrxml.getparent() # the whole page break 
                    body = breakcontainer.getparent() # the whole doc, because we want to insert the H1 at the top-level
                    break_index =  body.index(breakcontainer) 
                    body.insert(break_index, hack_element)
            
            if child.text:
                pass
        return(tree)

