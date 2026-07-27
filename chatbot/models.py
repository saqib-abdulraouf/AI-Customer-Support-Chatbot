import os
from django.db import models
from .rag_service import index_pdf_document, delete_document_from_index


class PDFDocument(models.Model):
    title = models.CharField(max_length=255, help_text="Title or description of the PDF document")
    pdf_file = models.FileField(upload_to="pdfs/", help_text="Upload PDF file to index for RAG")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, help_text="Status indicating whether PDF was indexed into ChromaDB")
    chunk_count = models.IntegerField(default=0, help_text="Number of vector text chunks stored in ChromaDB")

    class Meta:
        verbose_name = "PDF Document (RAG Knowledge)"
        verbose_name_plural = "PDF Documents (RAG Knowledge)"
        ordering = ['-uploaded_at']

    def __str__(self):
        status = "Indexed" if self.is_processed else "Pending"
        return f"{self.title} [{status} - {self.chunk_count} chunks]"

    def process_and_index(self) -> int:
        """Extracts text via PyMuPDF, chunks, embeds with Gemini, and stores in ChromaDB."""
        if self.pdf_file and os.path.exists(self.pdf_file.path):
            count = index_pdf_document(self.id, self.title, self.pdf_file.path)
            self.chunk_count = count
            self.is_processed = True
            self.save(update_fields=['chunk_count', 'is_processed'])
            return count
        return 0

    def delete(self, *args, **kwargs):
        """Remove document vectors from ChromaDB when model instance is deleted."""
        delete_document_from_index(self.id)
        super().delete(*args, **kwargs)
