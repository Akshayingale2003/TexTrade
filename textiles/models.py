from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name
    
class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.FileField(upload_to='images/')
    address = models.CharField(max_length=50)
    contact = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

class Vendor(models.Model):
    id = models.AutoField(primary_key=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_vendor = models.BooleanField(default=True)
    address = models.CharField(max_length=50, null=True)
    contact = models.CharField(max_length=10, null=True)
    image = models.FileField(upload_to='images/', null=True)

    def __str__(self):
        return self.user.username
    

    
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    image = models.FileField(upload_to='images/', null=True)
    name = models.CharField(max_length=30, null=True)
    price = models.IntegerField(null=True)
    desc = models.TextField(null=True)

    def __str__(self):
        return self.category.name+"--"+self.name


    
class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    dob = models.DateField(null=True)
    city = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=50, null=True)
    contact = models.CharField(max_length=10, null=True)
    image = models.FileField(upload_to='images/', null=True)
    role = models.CharField(
        max_length=20,
        choices=[('user', 'User'), ('vendor', 'Vendor'), ('admin', 'Admin')],
        default='user'
    )

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role='user')  # Default role is 'user'

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()



class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1,null=True) 
    
    def __str__(self):
        return self.profile.user.username + " . " + self.product.name
    
class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"


class Booking(models.Model): 
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=30,null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    booking_id = models.CharField(max_length=200, unique=True, blank=True) 
    book_date = models.CharField(max_length=30, null=True) 
    total = models.IntegerField(null=True) 
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True) 

    def save(self, *args, **kwargs):
        if not self.booking_id:
            import uuid
            while True:
                new_booking_id = f"BKG-{uuid.uuid4().hex[:10]}"
                if not Booking.objects.filter(booking_id=new_booking_id).exists():
                    self.booking_id = new_booking_id
                    break
        super().save(*args, **kwargs)

class BookingItem(models.Model):
    id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True,blank=True)
    product_name = models.CharField(max_length=100 , null=True) 
    product_price = models.IntegerField(default=0) 
    product_image = models.ImageField(upload_to='images/', null=True, blank=True) 
    product_desc = models.TextField(null=True)      
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name} ({self.quantity}) - Booking {self.booking.booking_id}"



    

class Send_Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    message1 = models.TextField(null=True)
    date = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.profile.user.username


# adding reviews to the order
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"
