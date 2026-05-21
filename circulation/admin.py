from django.contrib import admin
from .models import Borrowing, BorrowedItem

class BorrowedItemInline(admin.TabularInline):
    model = BorrowedItem
    extra = 0

@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'borrow_date', 'due_date', 'status', 'fine')
    list_filter = ('status', 'borrow_date')
    search_fields = ('user__username',)
    inlines = [BorrowedItemInline]

@admin.register(BorrowedItem)
class BorrowedItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'borrowing', 'book', 'is_returned')