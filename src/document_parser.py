import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


class DocumentParser:
    def __init__(self, file_path):
        self._loader = PyPDFLoader(file_path)
        self._document = self._loader.load()

    def clean_documents(self, overwrite: bool = True):
        cleaned_docs = []
        for doc in self._document:
            cleaned_text = re.sub(r"\s+", " ", doc.page_content).strip()
            if cleaned_text:
                doc.page_content = cleaned_text
                cleaned_docs.append(doc)

        if overwrite:
            self._document = cleaned_docs

        return cleaned_docs

    def split_documents(self, chunk_size=1000, chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        split_docs = text_splitter.split_documents(self._document)
        print(f"Split into {len(split_docs)} chunks.")
        return split_docs

    @property
    def document(self):
        return self._document