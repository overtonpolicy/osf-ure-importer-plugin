import pytest
import os,sys,re
import textwrap, pprint
import pdb,warnings,traceback


sys.path.insert(0, os.path.dirname(__file__) + '/..')
import ure
import ure.exporter
input_dir = os.path.dirname(__file__) + '/input'

exporter = ure.exporter.Docx()

markdown = [
    ('Woof Project',
     [
         [
             'Woof Project',
             textwrap.dedent("""
             # Formatting Test
             
             ## Introduction
             
             In these sections we test a variety of principles. We\\'ll descend through the 6 headings, and have some text included. We\\'ll also mess around with empty lines before/after the headings to make sure that doesn\\'t impact anything. We also want to test, in particular, repetition of styles, nested styles, and indicators that signal markdown styles in some cases but are actually just plain text.
             
             ### Text Formatting 
             
             Text in paragraph: **Bold** and *italic* and ***bold italic***. Under line. Don\\'t forget ~~strikethrough~~, Superscript in 2<sup>3</sup> and subscript Z<sub>i</sub> and N<sub>b</sub>.
             
             **Make sure bold starting a line isn\\'t confused** with a list.
             
             *Make sure italic starting* a line isn\\'t confused with a list.
             
             #### Unordered Lists
             
             -   item 1
             -   Item **with bold**
             -   **Bold item**
             -   *italic item*
             -   ***bold italic item***
                 -   ***2nd level item***
                     -   third level item\\
                         carriage return
                     -   third level item 2
             -   Back to first level
             
             ##### Ordered lists
             
             1.  Unordered list item 1
             2.  Item **with bold**
             3.  **Bold item**
             4.  *italic item*
             5.  ***bold italic item***
                 1.  ***2nd level item***
                     1.  third level item\\
                         carriage return
                     2.  third level item 2
             6.  Back to first level
             
             ###### Heading 6 with **Format Overrides** in the heading
             
             Here we make sure that a new list continued across sections doesn\\'t continue the same numbering in translation.
             
             1.  Unordered list item 1
             2.  Item **with bold**
             3.  **Bold item**
             4.  *italic item*
             5.  ***bold italic item***
                 1.  ***2nd level item***
                     1.  third level item\\
                         carriage return
                     2.  third level item 2
             6.  Back to first level
             """)
         ],
         [
             'Links',
             textwrap.dedent("""
             # Links
             
             Go to [https://uremethods.org/building-your-protocol/](https://uremethods.org/building-your-protocol/), which should be the same as [our website](https://uremethods.org/).
             
             Text in paragraphs again, to test repetition: **Bold** and *italic* and ***bold italic***. Under line. Don\\'t forget ~~strikethrough~~, Superscript in 2<sup>3</sup> and subscript Z<sub>i</sub> and N<sub>b</sub>.
             
             **Make sure bold starting a line isn\\'t confused** with a list.
             
             *Make sure italic starting* a line isn\\'t confused with a list.
             """),
        ], 
        [
            'New Section, Back to H1', 
            textwrap.dedent("""
            # New Section, Back to H1
             
            Test introducing the next section.
             
            ## Repeat the same formatting test
             
            Just to make sure nothing changes in repeat or in a new section.
             
            Text in paragraphs again, to test repetition: **Bold** and *italic* and ***bold italic***. Under line. Don\\'t forget ~~strikethrough~~, Superscript in 2<sup>3</sup> and subscript Z<sub>i</sub> and N<sub>b</sub>.
             
            **Make sure bold starting a line isn\\'t confused** with a list.
             
            *Make sure italic starting* a line isn\\'t confused with a list.
            """),
        ]
     ]
     )
]


def test_render_docx():
    output_filename = "test.docx"
    doc = exporter.process_markdown(
        markdown,
    )
    assert doc
    doc.save(output_filename)

    pytest.fail(f"Saved output to {output_filename}, but we haven't crafted thorough tests to make sure it is right")

