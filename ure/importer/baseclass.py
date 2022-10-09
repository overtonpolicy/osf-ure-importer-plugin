import re

class BaseImporter():
    """ 
    """

    def __init__(self, h1_break='wiki', h2_break=None, section_break='component', page_break=None):
        self._markdown = None
        self.break_policy = {}
        self.set_break_policy(1, h1_break)
        self.set_break_policy(2, h2_break)
        self.set_break_policy('section break', section_break)
        self.set_break_policy('page break', page_break)

    @staticmethod 
    def check_break_type(break_type):
        """ Verify a break type is valid. """
        if break_type is None:
            return(True)
        if break_type in ('wiki', 'component'):
            return(True)
        raise Exception(f"break type '{break_type}' is not recognized")

    @staticmethod 
    def check_style_type(style_type):
        """ Verify a style type is valid. """
        if style_type in range(1,6):
            return(True)
        if style_type in ('section break', 'page break'):
            return(True)
        raise Exception(f"component type '{style_type}' is not recognized - it must be 'section break', 'page break', or 1-6 to indicate a heading level")

    def set_break_policy(self, style_type, break_type):
        self.check_style_type(style_type)
        self.check_break_type(break_type)
        self.break_policy[style_type] = break_type

    @property
    def markdown(self):
        """ The markdown text translate from the document. 
        
        Note that `postprocess_markdown` is run by the setter to allow for simpler subclass 
        overrides and to translate raw markdown text into the multi-component, multi-wiki 
        structure supported by OSF. 

        The final data structure will be a multi-level list following this structure:

            [
                [ 'Node 0_Title', [
                    ['Wiki_0_Title', 'Wiki_0_Text'],
                    ['Wiki_1_Title', 'Wiki_1_Text'],
                    ...,
                ]],
                [ 'Component_1_Title', [ ... ]],
                ...
            ]

        """
        if not self._markdown:
            self.markdown = self.process_source()
        return(self._markdown)

    @markdown.setter
    def markdown(self, mkd):
        # we don't presently do any validation to verify that the parameter is valid markdown
        # but we do run the processor so that it 
        # does the additional datastructure creation that we use for everything here
        self._markdown = self.postprocess_markdown(mkd)

    def process_source(self):
        raise Exception("process_source must be defined in the subclass to return a ure-markdown datastructure")

    def postprocess_markdown(self, mkdtext):
        """ Do additional processing based on the parameters provided 
        to create the datastructure to import into osf.

        The baseclass postprocess uses the page break and section break policy to identify and break 
        up the document appropriately to generate the correct structure.

        """

        mkdtext = mkdtext.strip()

        policies = self.break_policy.copy()

        if 'page break' in policies:
            policy = policies['page break']
            del policies['page break']
            if policy == 'wiki':
                mkdtext = mkdtext.replace("\n\n# |||NEWPAGE|||", "\n&&&&&&")
                #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWPAGE\|\|\|", "\n&&&&&&")
            elif policy == 'component':
                mkdtext = mkdtext.replace("\n\n# |||NEWPAGE|||", "\n%%%%%%")
                #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWPAGE\|\|\|", "\n%%%%%%")
            else:
                mkdtext = mkdtext.replace("\n\n# |||NEWPAGE|||", '')
                #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWPAGE\|\|\|", '')
        else:
            mkdtext = mkdtext.replace("\n\n# |||NEWPAGE|||", '')
            #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWPAGE\|\|\|", '')

        if 'section break' in policies:
            policy = policies['section break']
            del policies['section break']
            if policy == 'wiki':
                mkdtext = mkdtext.replace("\n\n# |||NEWSECTION|||", "\n&&&&&&")
                #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWSECTION\|\|\|", "\n&&&&&&")
            elif policy == 'component':
                mkdtext = mkdtext.replace("\n\n# |||NEWSECTION|||", "\n%%%%%%")
                #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWSECTION\|\|\|", "\n%%%%%%")
            else:
                mkdtext = mkdtext.replace("\n\n# |||NEWSECTION|||", '')
                #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWSECTION\|\|\|", '')
        else:
            mkdtext = mkdtext.replace("\n\n# |||NEWSECTION|||", '')
            #mkdtext = mkdtext.replace("\n\n# \|\|\|NEWSECTION\|\|\|", '')

        # -- go through all of the style types and apply our custom markups 
        for style, break_type in policies.items():
            if not break_type:
                continue
            if break_type == 'wiki':
                metabreak = '&&&&&&'
            elif break_type == 'component':
                metabreak =  '%%%%%%'

            mkdtext = re.sub(r'\n\n+\s{0,3}' + ('#'*style) + r'\s+([^\n]+)', lambda m: "\n"+metabreak+"\n" +('#' * style)+ " " + m.group(1), mkdtext)
     
        # -- now we go through and separate out the metabreak 
        headingre = re.compile(r'\n*\s{0,3}#+\s+([^\n]+)')
        component_mkds = re.split(r"%%%%%%", mkdtext)
        nodes = []
        for component_mkd in [mkd.strip() for mkd in component_mkds]:
            #
            # So here we split on the wiki break field and make up the wiki landscape.
            # The importer demands a heading in each new wiki, and so if it encouter 
            # a wiki with no heading, it will add it to the previous wiki page.
            # 
            # If the home wiki has no heading, it will assume it is some sort of preamble note 
            # possibly describing the current draft, and so following pages will be appended until 
            # there is indeed a heading

            if not re.search(r'\w', component_mkd):
                continue
            
            home_wiki, *other_mkd = filter(lambda m: m, [wiki.strip() for wiki in component_mkd.split("&&&&&&")])

            # This is a little bit roundabout.  
            # We look for a heading in the home wiki.
            # If there isn't one, we use that to suggest this is a preamble block of text, and we concatenate the next wiki to it until we run out.
            # If we run out of wikis and still have no title, we assign '(No Title)' to the heading.
            # HOWEVER, the processed title/heading from the home wiki becomes the component title because the home wiki is, obviously, 'Home'.
            headmatch = headingre.search(home_wiki)
            while other_mkd and not headmatch:
                print("*** Appending subpage to HOME")
                home_wiki += "\n\n" + other_mkd.pop(0)
                headmatch = headingre.search(home_wiki)

            if headmatch:
                title = headmatch.group(1)
            else:
                # this if there are no headings for the entire document.
                title = '(No Title)'
            wiki_pages = [
                ['home_wiki', home_wiki],
            ]
            
            # process all wikis after the home wiki.  
            # We again require a wiki to have a heading. But here we consider
            # any heading-less wikis as epilogues to the prior wiki, and add 
            # it the *prior* text, which we already processed.
            while other_mkd:
                wiki_mkd = other_mkd.pop(0)
                # -- first try to identify the heading that we name the wiki page after
                m = headingre.search(wiki_mkd)   
                if not m:
                    # -- so there is no heading in this segment. We add it to the previous wiki page.
                    print("*** Appending subpage to " + wiki_pages[-1][0])
                    wiki_pages[-1][1] += "\n\n" + wiki_mkd
                else:
                    wiki_pages.append([self.sanitize_title(m.group(1)), wiki_mkd])
            # Now append the full data structure to nodes, with the title of the home wiki as the title for the node. 
            nodes.append([self.sanitize_title(title), *wiki_pages])

        return(nodes)

    @classmethod
    def sanitize_title(cls, text):
        """ Remove characters or strings that are invalid from the wiki/node titles. 

            Page names cannot include foreward slashes, carriage returns, or newlines.

            Args:
                text: The text to sanitize.
            Returns:
                The sanitized text.
        """
        text = re.sub(r'\/', '-', text.strip()) # change slash to hyphens
        text = re.sub(r'\n', ' ', text) # change newlines to spaces
        text = re.sub(r'\r', '', text) # remove carriage returns 
        return(text)


    ulmd_re = re.compile(r'\[([^\]]+)\]\{\.(underline|ul)\}', flags=re.MULTILINE | re.I)
    boldline_re = re.compile(r'^(#+\s+)\*\*(.+)\*\*\s*$', flags=re.MULTILINE )
    supmd_re = re.compile(r'\^([^\^]+)\^', flags=re.MULTILINE | re.I)
    
    # ~i~ is subscript, but ~~i~~ is strikethrough, so the regex is more complicated
    submd_re = re.compile(r'(?<!~)~([^\~]+)~(?!~)', flags=re.MULTILINE | re.I) 
    
    @classmethod
    def clean_pandoc_markdown(cls, mkdtext):
        """ Cleans formatting that comes out of pandoc to handle the slightly different dialect
        that OSF  """

        # pandoc formats underlining as [text]{.underline}, which isn't standard.
        # OSF does not support underline at all (i.e., not even html <u> tags).
        # Current function is to just remove the pandoc underline markup and print the inner text.
        # Consideration: possibly italicize it, but quasi-links or link-like objects can end up with 
        #      underline characteristics, and that is not appropriate to italicize.
        mkdtext = cls.ulmd_re.sub(lambda m: m.group(1), mkdtext)
               
        # remove bold from headings (if the entire heading is bolded) as it leads to weird markdown
        mkdtext = cls.boldline_re.sub(lambda m: m.group(1) + m.group(2), mkdtext)

        # superscript: markdown superscript is ^{text}^, i.e. 3^2^, but this is not supported by OSF.
        # translate it to html <sup>{text}</sup>, which OSF allows.
        mkdtext = cls.supmd_re.sub(lambda m: '<sup>' + m.group(1) + '</sup>', mkdtext)

        # subscript: markdown subscript is ~{text}~, i.e. Z~i~, but this is not supported by OSF.
        # translate it to html <sub>{text}</sub>, which OSF allows.
        mkdtext = cls.submd_re.sub(lambda m: '<sub>' + m.group(1) + '</sub>', mkdtext)

        return(mkdtext)
