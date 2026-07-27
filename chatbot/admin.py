from django.contrib import admin
from .models import PDFDocument


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'pdf_file', 'uploaded_at', 'is_processed', 'chunk_count')
    list_filter = ('is_processed', 'uploaded_at')
    search_fields = ('title',)
    actions = ['reindex_documents']

    def save_model(self, request, obj, form, change):
        """Auto-index PDF document into ChromaDB upon save."""
        super().save_model(request, obj, form, change)
        try:
            count = obj.process_and_index()
            self.message_user(
                request,
                f"Successfully extracted text via PyMuPDF, generated Gemini embeddings, "
                f"and indexed {count} text chunks into ChromaDB for '{obj.title}'."
            )
        except Exception as exc:
            self.message_user(
                request,
                f"Document saved, but indexing failed: {exc}",
                level='ERROR'
            )

    @admin.action(description="Re-index selected PDF documents into ChromaDB")
    def reindex_documents(self, request, queryset):
        total_chunks = 0
        for doc in queryset:
            total_chunks += doc.process_and_index()
        self.message_user(
            request,
            f"Successfully re-indexed {queryset.count()} document(s) into ChromaDB ({total_chunks} total chunks)."
        )
