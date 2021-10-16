import os,sys,re
import textwrap

from .baseclass import BaseImporter

class GoogleDoc(BaseImporter):

    def __init__(self, google_document_json, access_token, **kwargs):
        super().__init__(**kwargs)
        self.document_json = google_document_json

    def process_source(self):

        docjson = self.google_document_json

        title = docjson['title']

        all_elements = docjson['body']['content']
        while all_elements:
            elem = all_elements.pop(0)
            is_break = False
            if elem.body_type == 'paragraph':
                string = ""
                just_text = ""
                if elem.paragraph_type == 'heading':                    
                    string = '#' * elem.heading_level + ' '
                    html = f'h{elem.heading_level}'
                    if html in self.wiki_breaks:
                        is_break = 'wiki'
                    elif html in self.component_breaks:
                        is_break = 'component'
                elif elem.list_type == 'ordered':
                    string = '1. '
                elif elem.list_type == 'unordered':
                    string = '* '
                elif elem.paragraph_type == 'title':
                    string = '# '
                    if 'title' in self.wiki_breaks:
                        is_break = 'wiki'
                    elif 'title' in self.component_breaks:
                        is_break = 'component'
                elements = elem.elements

                for i, para in enumerate(elements):
                    if para.inline_object_element_id:
                        string = "\n[[ IMAGE OR OBJECT INSERTED HERE - NOT YET SUPPORTED BY googleapps ]]\n"
                    elif para.text:
                        text = ""
                        # -- if the font is in courier/new, we consider that a code block

                        if para.text_style.link:
                            text += f'[{para.text}]({para.text_style.link})'
                        else:
                            text += para.text
                            just_text += para.text

                        if para.text_style.font_family and 'Courier' in para.text_style.font_family:
                            text = re.sub(r'^(\s*)(\S)', lambda m: m.group(1) + '`' + m.group(2), text)


                        if para.text_style.bold:
                            text = re.sub(r'^(\s*)(\S)', lambda m: m.group(1) + '**' + m.group(2), text)

                        if para.text_style.italic:
                            text = re.sub(r'^(\s*)(\S)', lambda m: m.group(1) + '*' + m.group(2), text)


                        # for the closing bits, we ensure that we are on the left side of a newline
                        if para.text_style.italic:
                            text = re.sub(r'(\S)(\s*)$', lambda m: m.group(1) + '*' + m.group(2), text)
                        if para.text_style.bold:
                            text = re.sub(r'(\S)(\s*)$', lambda m: m.group(1) + '**' + m.group(2), text)
                        # -- if the font is in courier/new, we consider that a code block
                        if para.text_style.font_family and 'Courier' in para.text_style.font_family:
                            text = re.sub(r'(\S)(\s*)$', lambda m: m.group(1) + '`' + m.group(2), text)

                        if docframework.is_new_component and alphanum.search(text):
                            docframework.current_component_name = text.strip()
                            docframework.is_new_component = False
                        string += text
                    elif para.element_type == 'horizontal_rule':
                        if string and string[-1] != "\n":
                            string += "\n\n"
                        string += "---\n"
                    elif para.element_type == 'page_break':
                        if 'page-break' in self.component_breaks:
                            docframework.new_component()
                        elif 'page-break' in self.wiki_breaks:
                            docframework.new_wiki()
                        else:
                            string += "\n\n\n"
                        pass
                    else:
                        raise Exception(f"Unknown paragraph eleement type {para.element_type}")

                #
                # Check to see if this element was a valid wiki/component break
                if is_break:
                    if is_break == 'wiki':                        
                        docframework.new_wiki(just_text)
                    elif is_break == 'component':
                        docframework.new_component(just_text)
                    else:
                        raise Exception(f"Unknown break type {is_break}")
                
                if string:
                    docframework.add_text(string)

            elif elem.body_type == 'section break':
                if 'section-break' in self.component_breaks:
                    docframework.new_component()
                elif 'section-break' in self.wiki_breaks:
                    docframework.new_wiki()
            elif elem.body_type == 'table of contents':
                pass
            else:
                pass
        # add the rest of the pages
        docframework.new_component() # -- this is necessary to save any existing components
        return(docframework)

        