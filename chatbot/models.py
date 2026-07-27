import os
import uuid
from django.db import models
from django.utils.text import slugify
from .rag_service import index_pdf_document, delete_document_from_index


class Company(models.Model):
    """
    Tenant model for Multi-Tenant SaaS platform.
    Each company gets an isolated knowledge base, RAG vector collection, and API Key.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Company or Business Name")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL friendly identifier")
    api_key = models.CharField(max_length=64, unique=True, blank=True, help_text="API Key for widget integration")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Active tenant status")

    class Meta:
        verbose_name = "Company (Tenant)"
        verbose_name_plural = "Companies (Tenants)"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.api_key:
            self.api_key = f"key_{uuid.uuid4().hex}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.slug})"


class PDFDocument(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="pdf_documents",
        null=True,
        blank=True,
        help_text="Company (Tenant) owning this document"
    )
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
        tenant = f"{self.company.name} • " if self.company else ""
        status = "Indexed" if self.is_processed else "Pending"
        return f"{tenant}{self.title} [{status} - {self.chunk_count} chunks]"

    def process_and_index(self) -> int:
        """Extracts text via PyMuPDF, chunks, embeds with Gemini, and stores in ChromaDB with company_id metadata."""
        if self.pdf_file and os.path.exists(self.pdf_file.path):
            company_id = self.company.id if self.company else None
            count = index_pdf_document(self.id, self.title, self.pdf_file.path, company_id=company_id)
            self.chunk_count = count
            self.is_processed = True
            self.save(update_fields=['chunk_count', 'is_processed'])
            return count
        return 0

    def delete(self, *args, **kwargs):
        """Remove document vectors from ChromaDB when model instance is deleted."""
        delete_document_from_index(self.id)
        super().delete(*args, **kwargs)
