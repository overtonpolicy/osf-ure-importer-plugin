import pytest
import os,sys,re
import pdb,warnings
import textwrap, pprint

sys.path.insert(0, os.path.dirname(__file__) + '/..')
import ure
input_dir = os.path.dirname(__file__) + '/input'
md_dir = os.path.dirname(__file__) + '/md'


def test_basic_formatting():
    compare_import_to_markdown("Basic Formatting.docx")

def test_tables():
    compare_import_to_markdown("Tables.docx")


""" In the following tests, we test that the different types of breaks and headings work based on the docx file "Component and Wiki Breaks.docx", in particular:

- Text prior to the first heading doesn't lead to weirdness
- Text between a page/section break and a heading still render good wiki/component names
- breaks occur sensibly
"""

def compare_headings(md, reference):
    refiter = iter(reference)
    i = 0
    for node_title, *node_data in md:
        refnode = next(refiter)        
        assert node_title == refnode[0], f"Node {i} title does not match: Expected '{refnode[0]}', received '{node_title}'"

        refwiki = refnode[1]
        assert len(node_data) == len(refwiki), f"Node {i} does not match on wiki count. Markdown has {len(node_data)} wikis and the reference has {len(refwiki)}:\n\tMarkdown wiki titles: {[n[0] for n in node_data]}\n\tReference  wiki titles: {refwiki}"
        w = 0
        for wiki_title, wiki_text in node_data:
            assert wiki_title == refwiki[w], f"Node {i}, Wiki {w} title does not match: Expected '{refwiki[w]}', received '{wiki_title}'"
            w += 1
        i += 1



def test_default_break_options():
    # the default break options currently will create 
    # component breaks on section breaks and wiki breaks
    # on new "Heading 1" styles. 
    # 
    # I originally considered using a page break as a default,
    # but page breaks are frequently used for layout/formatting
    # to simply move tables or segments that would be split 
    # onto the next page, and the annoyance of accidentally 
    # creating components based on that seemed bad.
    #
    # OTOH, there is an argument that section breaks should 
    # also not create components by default becuse section 
    # breaks may be used to change between single and multiple
    # columns; however, as markdown doesn't support multiple 
    # columns and will completely change the formatting, 
    # this seems less likely to significantly impair use, and 
    # may even be seen as valuable because column changes likely
    # come with their own conceptual differences that may be 
    # suitable for a new component.

    importer = ure.importer.from_file(input_dir + "/Component and Wiki Breaks.docx")
    imported_md = importer.markdown

    reference_data = [
        [
            'First Heading 1: Abstract 1.1.1',
            [
                'home_wiki',
                'Heading 1, Section 2.1.1',
                'Heading 1, After Page Break 1, Section 3.1.1',
                'Heading 1, Section 4.1.1',
            ],
        ],
        [
            'Heading 1, After section break, Section 5.1.1',
            [ 'home_wiki' ],
        ],
        [
            'Heading 1, After section break, Section 6.1.1',
            [
                'home_wiki',
                'Heading 1, Section 7.1.0',
                'Heading 1, Section 8.1.0 immediately after 7.1.0',
            ],
        ],
        [
            'Heading 1, After Section + Page + Spaces, Section 7.1.1',
            [ 'home_wiki' ],
        ],
    ]

    compare_headings(imported_md, reference_data)

    explicit_importer = ure.importer.from_file(
        input_dir + "/Component and Wiki Breaks.docx",
        h1_break='wiki', 
        h2_break=None, 
        section_break='component', 
        page_break=None,

    )
    compare_headings(explicit_importer.markdown, reference_data)

def test_ignore_section_breaks():

    explicit_importer = ure.importer.from_file(
        input_dir + "/Component and Wiki Breaks.docx",
        h1_break='wiki', 
        h2_break=None, 
        section_break=None, 
        page_break='component',

    )

    reference_data = [
        [
            'First Heading 1: Abstract 1.1.1',
            [
                'home_wiki',
                'Heading 1, Section 2.1.1',
            ],
        ],
        [
            'Heading 1, After Page Break 1, Section 3.1.1',
            [ 'home_wiki' ],
        ],
        [
            'Heading 1, Section 4.1.1',
            [
                'home_wiki',
                'Heading 1, After section break, Section 5.1.1',
                'Heading 1, After section break, Section 6.1.1',
                'Heading 1, Section 7.1.0',
                'Heading 1, Section 8.1.0 immediately after 7.1.0',
            ],
        ],
        [
            'Heading 1, After Section + Page + Spaces, Section 7.1.1',
            [ 'home_wiki' ],
        ],
    ]
    compare_headings(explicit_importer.markdown, reference_data)



def test_h1_component_h2_wiki_breaks():

    explicit_importer = ure.importer.from_file(
        input_dir + "/Component and Wiki Breaks.docx",
        h1_break='component', 
        h2_break='wiki', 
        section_break=None, 
        page_break=None,
    )
    reference_data = [
        [
            '(No Title)',
            ['home_wiki'],
        ],
        [
            'First Heading 1: Abstract 1.1.1',
            [
                'home_wiki',
                'Heading 2, Section 1.1.2',
                'Heading 2, Section 1.1.3',
            ],
        ],
        [
            'Heading 1, Section 2.1.1',
            [
                'home_wiki',
                'Heading 2, Section 2.1.2',
            ],
        ],
        [
            'Heading 1, After Page Break 1, Section 3.1.1',
            [
                'home_wiki',
                'Heading 2, Section 3.1.2',
            ],
        ],
        [
            'Heading 1, Section 4.1.1',
            [ 'home_wiki' ],
        ],
        [
            'Heading 1, After section break, Section 5.1.1',
            [ 'home_wiki' ],
        ],
        [
            'Heading 1, After section break, Section 6.1.1',
            [ 'home_wiki' ],
        ],
        [
            'Heading 1, Section 7.1.0',
            [ 'home_wiki' ],
        ],
        [
            'Heading 1, Section 8.1.0 immediately after 7.1.0',
            [
                'home_wiki',
                'Heading 2, Section 8.2.0, immediately after 8.1.0',
            ],
        ],
    ]

    compare_headings(explicit_importer.markdown, reference_data)


def test_new_break_options():

    importer = ure.importer.from_file(
        input_dir + "/Component and Wiki Breaks.docx",
        h1_break='component', 
        h2_break='wiki', 
        section_break=None, 
        page_break=None,

    )
    imported_md = importer.markdown

    # For advanced debugging, set PRINT_FULL to True
    # to include the text in the debugging output
    PRINT_FULL = False

    nodes = []
    i = 0
    print("\n\n    reference_data = [")
    for node_title, *node_data in imported_md:
        print(" "*8 + "[")
        print(" "*12 + f"'{node_title}',")
        wikis = []
        w = 0        
        if len(node_data) == 1 and not PRINT_FULL:
            print(" "*12 + f"[ '{node_data[0][0]}' ],")
        else:
            print(" "*12 + "[")
            for wiki_title, wiki_text in node_data:
                wikis.append(wiki_title)
                print(" "*16 + f"'{wiki_title}',")
                if PRINT_FULL:
                    print(textwrap.indent(pprint.pformat(wiki_text, width = 80), " "*20))
                w += 1
            print(" "*12 + "],")
        print(" "*8 + "],")
        nodes.append([node_title, wikis])
        i += 1
    print("    ]")
    




def test_new_test():
    # Use this to see what the markdown output will be for a new file to import.

    #print_rendered_markdown("Basic Formatting.docx")
    pass

def compare_import_to_markdown(filename):
    """ Helper function to compare the markdown rendered by an importer to expected markdown output.
    
    This imports the markdown from the proivded filename, which is expected to be in the t/input 
    directory, to saved markdown output, which is expected to be in the t/md directory and 
    will be loaded by calling `load_md_file`     
    """

    importer = ure.importer.from_file(input_dir + '/' + filename)
    assert importer, f"Importer created for {filename}"
    imported_md = importer.markdown
    assert imported_md, f"markdown created from document {filename}"
    
    actual_md = load_md_file(filename)
    assert actual_md, f"raw markdown comparison files found"
    markdown_iter = iter(actual_md)

    i = 0
    for node_title, *node_data in imported_md:
        actual_node = next(markdown_iter)
        assert node_title == actual_node[0], f"Node {i} title is '{node_title}', but the comparison data thinks it should be '{actual_node[0]}'"

        actual_wiki_iter = iter(actual_node[1:])
        w = 0
        for wiki_title, wiki_text in node_data:
            actual_wiki_title, actual_text = next(actual_wiki_iter)
            assert wiki_title == actual_wiki_title, f"Node {i}, Wiki {w} title is '{wiki_title}', but the comparison data thinks it should be '{actual_wiki_title}'"
            wiki_text = wiki_text.strip()
            actual_text = actual_text.strip()
            if wiki_text == actual_text:
                assert wiki_text == actual_text
                continue
            # find out specifically what is different, ignoring whitespace
            wiki_lines = [z.strip() for z in wiki_text.splitlines()]
            actual_lines = [z.strip() for z in wiki_text.splitlines()]
            decomposed = []            
            errors = 0
            for i in range(len(wiki_lines)):
                if wiki_lines[i] == actual_lines[i]:
                    decomposed.append(f"{i:03d}: {wiki_lines[i]}")
                else:
                    errors += 1
                    decomposed.append(f"Line {i+1}:\n  Expected: {wiki_lines[i]}\n    Actual: {actual_lines[i]}")

            if errors:
                pytest.fail("\n".join(decomposed))
            w += 1
        i += 1

def load_md_file(test_file):
    """ takes a filename with any extension and loads the structure from the t/md file.
    
    This is intended to be shorthand to load the file or files from t/md based on an input document.

    The files saved in t/md can be in one of several formats:
        - just a single `filename.md` if there's only one wiki output to compare
        - a series `filename.0.md`, `filename.1.md` if there are multiple wikis
        - a series `filename.0.0.md`, `filename.0.1.md` if there are multiple nodes and wikis 

    Args:
        test_file: the filename to constuct a base from. This is expected to be an input filename,
            and the extension will be stripped.
    
    Returns:
        A parallel nested list structure like what will be returned by the ure.importer  
    """

    base_filename = re.sub(r'\.[^\.]+$', '', test_file)
    
    if os.path.exists(f"{md_dir}/{base_filename}.0.0.md"):
        # files are broken down by project-component AND multiple wikis
        nodes = []
        iprj = 0        
        while os.path.exists(f"{md_dir}/{base_filename}.{iprj}.0.md"):
            node_title = None
            iwiki = 0
            wikis = []
            while os.path.exists(f"{md_dir}/{base_filename}.{iprj}.{iwiki}.md"):
                with open(f"{md_dir}/{base_filename}.{iprj}.{iwiki}.md") as fh:
                    if iwiki == 0:
                        node_title = fh.readline().strip()
                    wiki_title = fh.readline().strip()
                    text = fh.read().strip()
                    wikis.append([wiki_title, text])        
                iwiki += 1
            nodes.append([node_title, *wikis])
            iprj += 1
            return(nodes)

    elif os.path.exists(f"{md_dir}/{base_filename}.0.md"):
        node_wikis = []
        node_title = None
        iwiki = 0
        while os.path.exists(f"{md_dir}/{base_filename}.{iwiki}.md"):
            with open(f"{md_dir}/{base_filename}.{iwiki}.md") as fh:
                if iwiki == 0:
                    node_title = fh.readline().strip()
                wiki_title = fh.readline().strip()
                text = fh.read().strip()
                node_wikis.append([wiki_title, text])        
            iwiki += 1
        return([node_title, *node_wikis])

    elif os.path.exists(f"{md_dir}/{base_filename}.md"):
        node_wikis = []
        node_title = None
        with open(f"{md_dir}/{base_filename}.md") as fh:
            node_title = fh.readline().strip()
            wiki_title = fh.readline().strip()
            text = fh.read().strip()
        return([node_title, [wiki_title, text]])
    else:
        raise Exception(f"Cannot find a file with a base name {test_file}")


def print_rendered_markdown(test_file):
    """ Prints out the markdown generated by a file in the t/input directory

    This is used when writing new tests. It will print out the text as currently rendered, 
    which can be reified into a test easily.

    Remember to run pytest `t/test_ure_importer.py -s -vv`

    Args:
        test_file: the fileanme within the t/input folder that will get parsed.
    
    
    """

    importer = ure.importer.from_file(input_dir + '/' + test_file)
    md = importer.markdown
    
    m = re.fullmatch(r'(.*)\.([^\.]+)', test_file)
    test_func = m.group(1)
    ext = m.group(2)

    print(f"""
    \ndef test_{test_func}():
    ''' Test {ext} -> markdown import of features from t/input/{test_file}'''

    importer = ure.importer.from_file(input_dir + '/' + "{test_file}")
    md = importer.markdown
    
    assert md[0][0] == '{md[0][0]}', "Project title is correct"
    """)
    i = 0
    for wiki_title, wiki_text in md[0][1]:
        print(f"""
    # Check Wiki {i}
    wiki_{i} = md[0][1][0]
    assert wiki_{i}[0] == '{wiki_title}', "Wiki {i} title is correct\"
    assert wiki_{i}[1] == textwrap.dedent('''\n""" \
            + textwrap.indent(wiki_text, '        ') \
            + f"\n        ''').strip(), \"Wiki {i} text is correct\"")
