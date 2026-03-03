"""LegalHigh - Legal document processing and management."""

__version__ = "0.1.0"


class LegalHigh:
    """Main application class for LegalHigh."""

    def __init__(self):
        self.documents = []

    def add_document(self, document):
        """Add a document to the collection.

        Parameters
        ----------
        document : str
            Path to the document file (e.g. ``"contract.pdf"``).

        Returns
        -------
        LegalHigh
            Returns ``self`` to allow method chaining.
        """
        self.documents.append(document)
        return self

    def get_documents(self):
        """Return a copy of all documents.

        Returns
        -------
        list
            A new list containing all document paths added via
            :meth:`add_document`.
        """
        return list(self.documents)

    def run(self):
        """Run the application."""
        print(f"LegalHigh v{__version__}")
        print(f"Documents loaded: {len(self.documents)}")
