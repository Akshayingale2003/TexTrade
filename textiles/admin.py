from django.contrib import admin
from .models import Category, Product, Booking, Profile, Vendor, Send_Feedback, Cart , Admin , BookingItem , Payment, Review # Import models explicitly

# Register models normally
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(Vendor)
admin.site.register(Admin)
admin.site.register(Send_Feedback)
admin.site.register(Cart)
admin.site.register(BookingItem)
admin.site.register(Payment)
admin.site.register(Review)

# Register Booking model with custom admin configuration
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'profile', 'total', 'book_date')  # Fields to display in admin
    search_fields = ('booking_id', 'profile__user__username')  # Search by booking ID or user
    list_filter = ('book_date',)  # Filter bookings by date
