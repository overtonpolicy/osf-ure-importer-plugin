import mistune
import pprint 

#document = Document(os.path.abspath(args.template)) if args.template else Document()
with open("math_example.md") as fh:
    text = fh.read()

markdown_analyzer = mistune.create_markdown(
    plugins=[
        'math' 
    ]
)

html = markdown_analyzer(text)

#print(html)

ast_analyzer = mistune.create_markdown(
    renderer = 'ast',
    plugins=[
        'math' 
    ]
)

ast = ast_analyzer(text)

print("\n\n---- AST ----\n\n" + pprint.pformat(ast, indent=4, width=120).replace("'", '"'))