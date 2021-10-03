import os,sys,re
import textwrap

from .baseclass import BaseImporter

class GoogleDoc(BaseImporter):

    def __init__(self, google_document_id, access_token, **kwargs):
        super().__init__(**kwargs)
        self.document_id = google_document_id
        self.access_token = access_token

    def process_source(self):

        document = get_document(self.document_id)

        