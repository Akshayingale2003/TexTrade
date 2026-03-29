from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from django.contrib import messages
from .models import *
from datetime import date
from django.conf import settings
import razorpay
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Sum, Q, F
from django.db import transaction
from django.views.decorators.http import require_POST
import uuid
from django.contrib.auth.decorators import login_required

# Create your views here.

PENDING_CHECKOUT_SESSION_KEY = "pending_checkout"


def _pending_reviews_for_booking_items(booking, items, reviewed_product_ids):
    """
    Products in this booking the user can still review (delivered + not yet reviewed).
    Returns (list of {name, url}, has_any_reviewable_product).
    """
    pending = []
    has_reviewable = False
    if (booking.status or "").strip().lower() != "delivered":
        return pending, has_reviewable
    for item in items:
        if not item.product:
            continue
        has_reviewable = True
        if item.product.id not in reviewed_product_ids:
            name = (item.product_name or item.product.name or "Product")[:100]
            pending.append(
                {
                    "name": name,
                    "url": reverse(
                        "add_review",
                        kwargs={
                            "booking_id": booking.booking_id,
                            "product_id": item.product.id,
                        },
                    ),
                }
            )
    return pending, has_reviewable


def Home(request):
    cat = ""
    pro = ""
    cat = ""
    num = 0
    num1 = 0
    cat = Category.objects.all()
    pro = Product.objects.all()
    num = []
    num1 = 0
    try:
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user=user)
        cart = Cart.objects.filter(profile=profile)
        for i in cart:
            num1 += 1

    except:
        pass
    a = 1
    li = []

    for j in pro:
        b = 1
        for i in cat:
            if i.name == j.category.name:
                if not j.category.name in li:
                    li.append(j.category.name)
                    if b == 1:
                        num.append(a)
                        b = 2
        a += 1


    d = {'pro': pro, 'cat': cat,'num':num,'num1':num1}
    return render(request, 'all_product.html', d)
	

def About(request):
    return render(request, 'about.html')

def Contact(request):
    return render(request, 'contact.html')	
	

#user signup

def Signup(request):
    error = ""
    if request.method == "POST":
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        p = request.POST['pwd']
        d = request.POST['date']
        c = request.POST['city']
        ad = request.POST['add']
        e = request.POST['email']
        i = request.FILES['img']
        con = request.POST['contact']
        
        if User.objects.filter(username=u).exists():
            error = "user_exists"
    
        elif User.objects.filter(email=e).exists():
            error = "email_exists"
        else:
            user = User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'dob': d,
                    'city': c,
                    'address': ad,
                    'contact': con,
                    'image': i
                 }
              )
    return render(request, "signup.html", {'error': error})

def Login(request):
    error = None  # Default state

    if request.method == "POST":
        username = request.POST.get('username', '') 
        password = request.POST.get('password', '') 
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'profile'):  # Ensures only normal users log in
                login(request, user)
                error = "yes"  # Login success
                return render(request, "login.html", {"error": error})
            else:
                error = "not_allowed"  # Not allowed for admin/vendor
        else:
            error = "not"  # Invalid credentials

    return render(request, "login.html", {"error": error})


def Admin_Login(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        
        if user is not None:
            if user.is_superuser:  # ✅ Only superusers can log in
                login(request, user)
                error = "yes"
            else:
                error = "not_allowed"  # ✅ Vendors & normal users are blocked
        else:
            error = "not"  # Invalid credentials

    return render(request, 'loginadmin.html', {'error': error})

def signupvender(request):
    error = None
    success = False

    if request.method == 'POST':
        try:
            firstname = request.POST['fname']
            lastname = request.POST['lname']
            username = request.POST['uname']
            password = request.POST['pwd']
            address = request.POST['add']
            email = request.POST['email']
            image = request.FILES['img']
            contact = request.POST['contact']

            if User.objects.filter(username=username).exists():
                error = "Username already taken. Try another."
            elif User.objects.filter(email=email).exists():
                error = "Email already registered. Use another email."
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password,
                    first_name=firstname, last_name=lastname, is_staff=True
                )
                Vendor.objects.create(user=user, address=address, contact=contact, image=image)
                success = True

        except Exception as e:
            error = f"Error: {str(e)}"

    return render(request, "signupvender.html", {'error': error, 'success': success})

def loginvender(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('pwd')   
        user = authenticate(request, username=username, password=password)  

        if user is not None:
            if user.is_staff and not user.is_superuser:  # ✅ Only vendors allowed
                login(request, user)
                error = 'yes'
            else:
                error = "not"  
        else:
            error = "not"  # Invalid credentials

    return render(request, "loginvender.html", {'error': error})

def Logout(request):
    logout(request)
    return redirect('home')

# vendor homepage logic
def vendor_home(request):
    if not request.user.is_authenticated:
        return redirect('login_vendor')
    vendor = Vendor.objects.get(user=request.user)
    num1 = Product.objects.filter(vendor=vendor).count()
    num2 = Booking.objects.filter(items__product__vendor=vendor).distinct().count()
    return render(request, "vendor_home.html", {'num1': num1, 'num2': num2})


def View_user(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    users = Profile.objects.filter(user__is_staff = False)

    # Pass the correct variable name to the template
    return render(request, 'view_user.html', {'users': users})


def view_vendors(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Vendor.objects.all()
    d = {'user':pro}
    return render(request,'view_vendors.html',d)



def Add_Product(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    cat = Category.objects.all()
    error=False
    if request.method=="POST":
        c = request.POST['cat']
        p = request.POST['pname']
        pr = request.POST['price']
        i = request.FILES['img']
        d = request.POST['desc']
        ct = Category.objects.get(name=c)
        v=Vendor.objects.get(user=request.user.id)
        
        Product.objects.create(category=ct, name=p,vendor=v, price=pr, image=i, desc=d)
        error=True
    d = {'cat': cat,'error':error}
    return render(request, 'add_product.html', d)


def All_product(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)
    num1=0
    for i in cart:
        num1 += 1
    cat = Category.objects.all()
    pro = Product.objects.all()
    d ={'pro':pro,'cat':cat,'num1':num1}
    return render(request,'all_product.html',d)



def View_feedback(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    feed = Send_Feedback.objects.all()
    d = {'feed': feed}
    return render(request, 'view_feedback.html', d)

def View_product(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    user = profile = cart = pro1 = cat1 = None
    num1 = 0

    # If user is not staff, get user cart
    if not request.user.is_staff:
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user=user)
        cart = Cart.objects.filter(profile=profile)
        num1 = cart.count()  # Count cart items

    # Fetch products based on category
    if pid == 0:
        cat = "All Product"
        pro1 = Product.objects.all()
    else:
        cat1 = Category.objects.get(id=pid)
        pro1 = Product.objects.filter(category=cat1)

    # Get all categories
    categories = Category.objects.all()

    context = {
        'pro1': pro1,
        'cat': categories,
        'cat1': cat1,
        'num1': num1
    }
    return render(request, 'view_product.html', context)




def Add_Categary(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    error=False
    if request.method=="POST":
        n = request.POST['cat']
        Category.objects.create(name=n)
        error=True
    d = {'error':error}
    return render(request, 'add_category.html', d)


def View_Categary(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Category.objects.all()
    d = {'pro': pro}
    return render(request,'view_category.html', d)


# def view_orders(request):
#     if not request.user.is_authenticated or not request.user.is_staff:
#         return redirect('login_vender') 

#     vendor = Vendor.objects.get(user=request.user)  
#     products = Product.objects.filter(vendor=vendor)
#     return render(request, 'view_orders.html')


def Feedback(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    error = False
    user1 = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user1)
    cart = Cart.objects.filter(profile=profile)
    num1 =0
    for i in cart:
        num1 += 1
    date1 = date.today()
    user = User.objects.get(id=pid)
    pro = Profile.objects.filter(user=user).first()
    if request.method == "POST":
        d = request.POST['date']
        u = request.POST['uname']
        e = request.POST['email']
        con = request.POST['contact']
        m = request.POST['desc']
        user = User.objects.filter(username=u, email=e).first()
        pro = Profile.objects.filter(user=user, contact=con).first()
        Send_Feedback.objects.create(profile=pro, date=d, message1=m)
        error = True
    d = {'pro': pro, 'date1': date1,'num1':num1,'error':error}
    return render(request, 'feedback.html', d)

from django.contrib.auth import update_session_auth_hash

def Change_Password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    num1=0
    user = request.user
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)
    for i in cart:
        num1 += 1
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']

        if user.check_password(o):
            if c == n:
                
                user.set_password(n)
                user.save()
                update_session_auth_hash(request,user) 
                error = "yes"
                return redirect('change_password')
        else:
            error = "not"
    d = {'error':error,'num1':num1}
    return render(request,'change_password.html',d)


def vendor_change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    num1=0
    user = request.user
    # cart = Cart.objects.filter(profile=vendor1)  # Replace 'profile' with the correct field in the Cart model
    # for i in cart:
    #     num1 += 1
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']

        if  user.check_password(o):
            if c == n:
                user.set_password(n)
                user.save()
                update_session_auth_hash(request, user)
                error = "yes"
                return redirect('vendor_change_password')
        else:
            error = "not"
    d = {'error':error,'num1':num1}
    return render(request,'vendor_change_password.html',d)

def Add_Cart(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method=="POST":
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user=user)
        product = Product.objects.get(id=pid)
        quantity = request.POST.get('quantity')
        if quantity:
             quant = quantity
        else:
            quant = 1
        Cart.objects.create(profile=profile, product=product,quantity=quant)
        return redirect('cart')

def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart =  Cart.objects.filter(profile=profile).all()
    for i in cart:
        if i.quantity == 0:
           i.delete()
           return redirect('cart')
    total=0
    num1=0
    book_id=request.user.username
    message1="Here ! No Any Product"
    for i in cart:
        total+=i.product.price * i.quantity
        num1+=1
        book_id = book_id+"."+str(i.product.id)
    d = {'profile':profile,'cart':cart,'total':total,'num1':num1,'book':book_id,'message':message1}
    return render(request,'cart.html',d)

def plus_cart(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    cart = Cart.objects.get(id=id)
    cart.quantity += 1
    cart.save()
    return redirect('cart')

def minus_cart(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    cart = Cart.objects.get(id=id)
    cart.quantity -= 1
    cart.save()
    return redirect('cart')


def remove_cart(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    cart = Cart.objects.get(id=id)
    cart.delete()
    return redirect('cart')



def Booking_order(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')

    data1 = get_object_or_404(User, id=request.user.id)
    data = get_object_or_404(Profile, user=data1)  

    cart = Cart.objects.filter(profile=data).all()

    total = sum(i.product.price * i.quantity for i in cart)
    num1 = cart.count()
    date1 = date.today()

    if request.method == "POST":
        d = request.POST['date1']
        c = request.POST['name']
        c1 = request.POST['city']
        ad = request.POST['add']
        e = request.POST['email']
        con = request.POST['contact']
        t = request.POST['total']

        if c != request.user.username:
            messages.error(request, "Invalid checkout.")
            return redirect("cart")

        profile = data
        cart = Cart.objects.filter(profile=profile)
        if not cart.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        try:
            posted_total = int(float(t))
        except (TypeError, ValueError):
            messages.error(request, "Invalid total.")
            return redirect("booking_order", pid=pid)

        computed_total = sum(ci.product.price * ci.quantity for ci in cart)
        if posted_total != int(computed_total):
            messages.error(request, "Your cart changed. Please review and try again.")
            return redirect("cart")

        checkout_id = uuid.uuid4().hex
        items = []
        for cart_item in cart:
            items.append(
                {
                    "product_id": cart_item.product_id,
                    "quantity": cart_item.quantity,
                    "product_name": cart_item.product.name,
                    "product_price": cart_item.product.price,
                    "product_desc": cart_item.product.desc or "",
                }
            )

        request.session[PENDING_CHECKOUT_SESSION_KEY] = {
            "checkout_id": checkout_id,
            "profile_id": profile.id,
            "book_date": d,
            "total": posted_total,
            "status": "processing",
            "items": items,
        }
        request.session.modified = True

        return redirect("payment")

    context = {
        'data': data,
        'data1': data1,
        'book_id': pid,
        'date1': date1,
        'total': total,
        'num1': num1
    }

    return render(request, 'booking.html', context)


def View_Booking(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)
    book = list(
        Booking.objects.filter(profile=profile)
        .prefetch_related("items__product")
        .order_by("-id")
    )
    reviewed_product_ids = set(
        Review.objects.filter(user=user).values_list("product_id", flat=True)
    )
    for b in book:
        pending, has_rev = _pending_reviews_for_booking_items(
            b, b.items.all(), reviewed_product_ids
        )
        b.pending_review_items = pending
        b.has_reviewable_products = has_rev

    num1 = cart.count()
    d = {"book": book, "num1": num1}
    return render(request, "view_booking.html", d)


def view_orders_vendor(request):
    if not request.user.is_authenticated:
        return redirect('login_vendor')

    vendor = Vendor.objects.get(user=request.user)
    item_vendor_q = Q(items__product__vendor=vendor)
    book = (
        Booking.objects.filter(item_vendor_q)
        .annotate(
            vendor_qty=Sum('items__quantity', filter=Q(items__product__vendor=vendor)),
            vendor_subtotal=Sum(
                F('items__product_price') * F('items__quantity'),
                filter=Q(items__product__vendor=vendor),
            ),
        )
        .order_by('-id')
    )

    cart = Cart.objects.filter(profile__user=request.user).count()
    d = {'book': book, 'num1': cart}
    return render(request, "view_orders_vendor.html", d)


# def delete_admin_booking(request, pid,bid):
#     if not request.user.is_authenticated:
#         return redirect('login_admin')
#     book = Booking.objects.get(booking_id=pid,id=bid)
#     book.delete()
#     return redirect('admin_viewBooking')

def delete_booking(request, pid,bid):
    if not request.user.is_authenticated:
        return redirect('login')
    book = Booking.objects.get(booking_id=pid,id=bid)
    book.delete()
    return redirect('view_booking')

def delete_user(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    user = User.objects.get(id=pid)
    user.delete()
    return redirect('view_user')

def delete_feedback(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    feed = Send_Feedback.objects.get(id=pid)
    feed.delete()
    return redirect('view_feedback')


def Admin_View_Booking(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    book = Booking.objects.all().order_by('-id')
    d = {'book': book}
    return render(request, 'admin_viewBokking.html', d)


@login_required
def booking_detail(request, pid, bid):
    if not request.user.is_authenticated:
        return redirect('login')
    booking = get_object_or_404(
        Booking, booking_id=pid, id=bid, profile__user=request.user
    )
    bookitem = BookingItem.objects.filter(booking=booking)

    li = []
    for i in bookitem:
        li.append(i.product)

    total_price = booking.total
    reviewed_product_ids = set(
        Review.objects.filter(user=request.user).values_list("product_id", flat=True)
    )
    pending_review_items, has_reviewable_products = _pending_reviews_for_booking_items(
        booking, bookitem, reviewed_product_ids
    )

    context = {
        "book": li,
        "booking": booking,
        "product": bookitem,
        "total": total_price,
        "pending_review_items": pending_review_items,
        "has_reviewable_products": has_reviewable_products,
    }
    return render(request, "booking_detail.html", context)


def admin_booking_detail(request,pid,bid,uid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    user = User.objects.get(id=uid)
    profile = Profile.objects.get(user=user)
    cart =  Cart.objects.filter(profile=profile).all()

    booking = get_object_or_404(Booking, booking_id=pid, id=bid)
    bookitem = BookingItem.objects.filter(booking=booking)

    li = []

    for i in bookitem:
        li.append(i.product)
    
    total_price = booking.total

    d = {'profile':profile,'cart':cart,'total':total_price,'book':li,'product':bookitem}
    return render(request,'admin_view_booking_detail.html',d)

def vendor_view_booking_detail(request,pid,bid,uid):
    if not request.user.is_authenticated:
        return redirect('login_vendor')
    vendor = Vendor.objects.get(user=request.user)
    user = User.objects.get(id=uid)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile).all()
    num1 = 0
    booking = get_object_or_404(Booking, booking_id=pid, id=bid)
    bookitem = BookingItem.objects.filter(booking=booking, product__vendor=vendor)
    if not bookitem.exists():
        raise Http404("No products from your store in this order.")
    li = [i.product for i in bookitem if i.product]
    agg = bookitem.aggregate(
        subtotal=Sum(F('product_price') * F('quantity'))
    )
    total_price = agg['subtotal'] or 0

    d = {
        'profile': profile,
        'cart': cart,
        'total': total_price,
        'num1': num1,
        'book': li,
        'product': bookitem,
    }
    return render(request, 'vendor_view_booking_detail.html', d)

def Edit_status(request,pid,bid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    book = Booking.objects.get(booking_id=pid,id=bid)
    if request.method == "POST":
        n = request.POST['book']
        s = request.POST['status']
        book.booking_id = n
        book.status = s
        book.save()
        return redirect('admin_viewBooking')
    d = {'book': book}
    return render(request, 'status.html', d)

def Edit_status_vendor(request,pid,bid):
    book = Booking.objects.get(booking_id=pid,id=bid)
    if request.method == "POST":
        n = request.POST['book']
        s = request.POST['status']
        book.booking_id = n
        book.status = s
        book.save()
        return redirect('view_orders_vendor')
    d = {'book': book }
    return render(request, 'status_vendor.html', d)

def Admin_View_product(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Product.objects.all()
    d = {'pro':pro}
    return render(request,'admin_view_product.html',d)

def vendor_view_product(request):
    if not request.user.is_authenticated:
        return redirect('login_vendor')
    v=Vendor.objects.get(user=request.user.id)
    pro = Product.objects.filter(vendor = v)
    d = {'pro':pro}
    return render(request,'vendor_view_product.html',d)

def delete_product(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Product.objects.get(id=pid)
    pro.delete()
    return redirect('admin_view_product')


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile_id = request.user.id  # Changed variable name to avoid confusion
    cart = Cart.objects.filter(profile=profile_id)
    
    num1 = 0
    total = 0
    for i in cart:
        total += i.product.price
        num1 += 1

    user = User.objects.get(id=request.user.id)
    pro = Profile.objects.get(user=user)

    if not pro.image:
        pro.image = "images/default-profile.png"  # Set a default image path

    context = {'pro': pro, 'user': user, 'num1': num1, 'total': total}
    return render(request, 'profile.html', context)



def Edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    error = False
    user = request.user.id
    pro = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=pro)  # Use filter() instead of get()
    
    num1 = 0
    total = 0
    for i in cart:
        total += i.product.price
        num1 += 1
    
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        c = request.POST['city']
        ad = request.POST['add']
        e = request.POST['email']
        con = request.POST['contact']
        d = request.POST['date']

        try:
            i = request.FILES['img']
            pro.image = i
            pro.save()
        except:
            pass

        if d:
            try:
                pro.dob = d
                pro.save()
            except:
                pass
        else:
            pass

        pro.user.username = u
        pro.user.first_name = f
        pro.user.last_name = l
        pro.user.email = e
        pro.contact = con
        pro.city = c
        pro.address = ad
        pro.save()
        error = True
    
    d = {'error': error, 'pro': pro, 'num1': num1, 'total': total}
    return render(request, 'edit_profile.html', d)



# vendor edit profile
def Vendor_Edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = False
    user = request.user.id
    pro = Profile.objects.get(user=user)
    num1 = 0
    total = 0

    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        address = request.POST['address']
        email = request.POST['email']
        contact = request.POST['contact']
        image = request.FILES.get('img')
            

        pro.user.username = username
        pro.user.first_name = firstname
        pro.user.last_name = lastname
        pro.user.email = email
        pro.image = image
        pro.contact = contact
        pro.address = address 
        pro.save()
        error = True
    
    d = {'error': error, 'pro': pro, 'num1': num1, 'total': total}
    return render(request, 'vendor_edit_profile.html', d)

   

def Admin_Home(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    book = Booking.objects.all()
    customer = Profile.objects.all()
    pro = Product.objects.all()
    total_book = 0
    total_customer = 0
    total_pro = 0
    for i in book:
        total_book+=1
    for i in customer:
        total_customer+=1
    for i in pro:
        total_pro+=1
    d = {'total_pro':total_pro,'total_customer':total_customer,'total_book':total_book}
    return render(request,'admin_home.html',d)


def Admin_profile(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Admin.objects.get(user__id=request.user.id)
    return render(request, 'admin_profile.html',{'pro':pro})

def Admin_edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Admin.objects.get(user=request.user)
    error = False
    if request.method =='POST':
        uname = request.POST['uname']
        fname = request.POST['fname']
        lname = request.POST['lname']
        contact = request.POST['contact']
        address = request.POST['address']
        image = request.FILES.get('image') 
        
        pro.user.username = uname
        pro.user.first_name = fname
        pro.user.last_name = lname
        pro.contact = contact
        pro.address = address
        if image:
            pro.image = image
        pro.user.save()
        pro.save()
        error = True

    return render(request, 'admin_edit_profile.html',{'pro':pro,'error': error})


def admin_edit_user(request,id):
    pro = Profile.objects.get(id = id)
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        uname = request.POST['uname']
        city = request.POST['city']
        address = request.POST['add']
        contact = request.POST['contact']
        dob = request.POST.get('date')
        img = request.FILES.get('img')

        pro.user.first_name = fname
        pro.user.last_name = lname
        pro.user.email = email
        pro.user.username = uname
        pro.city = city
        pro.address = address
        pro.contact = contact
        if dob :
            pro.dob = dob
        if img :
            pro.image = img
        pro.user.save()
        pro.save()

    context= {
        'pro' : pro
    }
    return render(request , 'admin_edit_user.html' , context)

def admin_edit_vendor(request,id):
    pro = Vendor.objects.get(id = id)
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        uname = request.POST['uname']
        address = request.POST.get('address')
        contact = request.POST['contact']
        img = request.FILES.get('img')

        pro.user.first_name = fname
        pro.user.last_name = lname
        pro.user.email = email
        pro.user.username = uname
        pro.address = address
        pro.contact = contact
        if img :
            pro.image = img
        pro.user.save()
        pro.save()

    context= {
        'pro' : pro
    }
    return render(request , 'admin_edit_vendor.html' , context)

def delete_vendor(request,id):
    ven = User.objects.get(id = id)
    ven.delete()
    redirect(request,'/')
 
def Admin_change_password(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = User.objects.get(id=request.user.id)
    return render(request, 'change_password.html',{'pro':pro})

def delete_category(request,pid): 
    if not request.user.is_authenticated:
        return redirect('login_admin')
    cat = Category.objects.get(id=pid)
    cat.delete()
    return redirect('view_categary')
	
def edit_product(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    cat = Category.objects.all()
    product = Product.objects.get(id=pid)
    error=""
    if request.method=="POST":
        c = request.POST['cat']
        p = request.POST['pname']
        pr = request.POST['price']
        d = request.POST['desc']
        ct = Category.objects.get(name=c)
        product.category = ct
        product.name = p
        product.price = pr
        product.desc = d
        try:
            product.save()
            error = "no"
        except:
            error = "yes"
        try:
            i = request.FILES['img']
            product.image = i
            product.save()
        except:
            pass 

    d = {'cat': cat,'error':error,'product':product}
    return render(request, 'edit_product.html', d)


def edit_category(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    category = Category.objects.get(id=pid)
    error=""
    if request.method=="POST":
        c = request.POST['cat']
        category.name = c
        try:
            category.save()
            error = "no"
        except:
            error = "yes"
    d = {'error':error,'category':category}
    return render(request, 'edit_category.html', d)

# payment


@login_required
def payment(request):
    """
    Razorpay checkout for a pending order stored in session (created on booking form).
    The Booking row is created only after successful payment or COD in payment_success.
    """
    pending = request.session.get(PENDING_CHECKOUT_SESSION_KEY)
    if not pending:
        return render(
            request,
            "error.html",
            {"error": "No checkout in progress. Please confirm your booking again."},
        )
    if pending.get("profile_id") != request.user.profile.id:
        return render(
            request,
            "error.html",
            {"error": "Invalid checkout session."},
        )

    total = pending.get("total")
    if total is None:
        return render(request, "error.html", {"error": "Invalid checkout total."})

    items = pending.get("items") or []
    computed = sum(int(i["product_price"]) * int(i["quantity"]) for i in items)
    if int(total) != int(computed):
        return render(
            request,
            "error.html",
            {"error": "Checkout total does not match items. Return to cart."},
        )

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    data = {
        "amount": int(total) * 100,
        "currency": "INR",
        "payment_capture": "1",
    }

    try:
        order = client.order.create(data)
    except razorpay.errors.BadRequestError:
        return render(request, "error.html", {"error": "Authentication failed. Check API keys."})

    context = {
        "amount": total,
        "order_id": order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "checkout_id": pending["checkout_id"],
    }

    return render(request, "payment.html", context)


def create_order(request):
    """Legacy entrypoint; checkout now uses session + /payment/."""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        return redirect("payment")

    return render(request, "payment_form.html")

# payment
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def process_booking(request):
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        total = request.POST.get("total")

        pending_status, created = "Pending"

        with transaction.atomic():  
            booking, created = Booking.objects.get_or_create(
                profile=profile,
                total=total,
                payment=None, 
                defaults={"status": pending_status}  
            )

            if not created and booking.status != pending_status:
                booking.status = pending_status
                booking.save()

        return redirect("success_page")


@login_required
@require_POST
def payment_success(request):
    """
    Create Booking + BookingItems + Payment after Razorpay success or COD.
    Cart is cleared here. Requires matching session from the booking form (checkout_id).
    """
    checkout_id = (request.POST.get("checkout_id") or "").strip()
    payment_mode = (request.POST.get("payment_mode") or "").strip()

    if not checkout_id:
        return JsonResponse(
            {"status": "error", "message": "Missing checkout_id"},
            status=400,
        )

    rz_payment_id = ""
    rz_order_id = ""
    if payment_mode != "COD":
        rz_payment_id = (request.POST.get("razorpay_payment_id") or "").strip()
        rz_order_id = (request.POST.get("razorpay_order_id") or "").strip()
        if not rz_payment_id or not rz_order_id:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing Razorpay payment details",
                },
                status=400,
            )

    pending = request.session.get(PENDING_CHECKOUT_SESSION_KEY)
    if not pending or pending.get("checkout_id") != checkout_id:
        return JsonResponse(
            {"status": "error", "message": "Invalid or expired checkout."},
            status=400,
        )
    if pending.get("profile_id") != request.user.profile.id:
        return JsonResponse(
            {"status": "error", "message": "Invalid session."},
            status=403,
        )

    items = pending.get("items") or []
    try:
        computed = sum(int(i["product_price"]) * int(i["quantity"]) for i in items)
    except (KeyError, TypeError, ValueError):
        return JsonResponse(
            {"status": "error", "message": "Invalid checkout items."},
            status=400,
        )
    if int(pending["total"]) != int(computed):
        return JsonResponse(
            {"status": "error", "message": "Amount mismatch."},
            status=400,
        )

    try:
        with transaction.atomic():
            profile = Profile.objects.select_for_update().get(
                pk=pending["profile_id"],
                user=request.user,
            )

            booking = Booking.objects.create(
                profile=profile,
                book_date=pending["book_date"],
                total=pending["total"],
                status=pending.get("status", "processing"),
            )

            for it in items:
                product = Product.objects.get(pk=it["product_id"])
                BookingItem.objects.create(
                    booking=booking,
                    product=product,
                    product_name=it.get("product_name") or product.name,
                    product_price=it["product_price"],
                    quantity=it["quantity"],
                    product_image=product.image,
                    product_desc=it.get("product_desc") or product.desc or "",
                )

            if payment_mode == "COD":
                payment = Payment.objects.create(
                    payment_id="COD",
                    order_id=f"COD-{uuid.uuid4().hex[:10]}",
                    amount=float(booking.total or 0),
                    status="Pending",
                )
            else:
                payment = Payment.objects.create(
                    payment_id=rz_payment_id,
                    order_id=rz_order_id,
                    amount=float(booking.total or 0),
                    status="Paid",
                )

            booking.payment = payment
            booking.save(update_fields=["payment"])

            Cart.objects.filter(profile=profile).delete()
            request.session.pop(PENDING_CHECKOUT_SESSION_KEY, None)
            request.session.modified = True

    except Product.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "A product is no longer available."},
            status=400,
        )
    except Profile.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Invalid profile."},
            status=400,
        )
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Could not record payment"},
            status=500,
        )

    return JsonResponse({"status": "success", "booking_id": booking.booking_id})

# confirmation


@login_required
def booking_confirmation(request):
    booking_id = request.GET.get("booking_id")
    total_amount = request.GET.get("total_amount")
    payment_id = request.GET.get("payment_id")

    get_object_or_404(
        Booking,
        booking_id=booking_id,
        profile=request.user.profile,
    )

    context = {
        "booking_id": booking_id,
        "total_amount": total_amount,
        "payment_id": payment_id,
        "order_status": "Confirmed",
    }

    return render(request, "booking_confirmation.html", context)

from .forms import ReviewForm

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(profile=request.user.profile, status__status="Completed")  # Show completed bookings
    return render(request, 'booking_history.html', {'bookings': bookings})


# reviews


def _booking_status_is_delivered(booking):
    st = (booking.status or "").strip().lower()
    return st == "delivered"


@login_required(login_url="login")
def add_review(request, booking_id, product_id):
    profile = get_object_or_404(Profile, user=request.user)
    booking = get_object_or_404(Booking, booking_id=booking_id, profile=profile)

    if not _booking_status_is_delivered(booking):
        messages.warning(
            request,
            "You can review products only after the order is marked delivered.",
        )
        return redirect("view_booking")

    if not BookingItem.objects.filter(booking=booking, product_id=product_id).exists():
        raise Http404("This product is not part of this order.")

    product = get_object_or_404(Product, id=product_id)

    if Review.objects.filter(user=request.user, product=product).exists():
        messages.info(request, "You have already reviewed this product.")
        return redirect("view_booking")

    if request.method == "POST":
        comment = (request.POST.get("comment") or "").strip()
        rating_raw = request.POST.get("rating")
        try:
            rating = int(rating_raw)
        except (TypeError, ValueError):
            rating = 0
        if not comment or rating < 1 or rating > 5:
            messages.error(request, "Please choose a rating and write a short review.")
            return redirect(
                "add_review", booking_id=booking.booking_id, product_id=product.id
            )

        Review.objects.create(
            product=product,
            user=request.user,
            comment=comment,
            rating=rating,
        )
        messages.success(request, "Thanks — your review was submitted.")
        return redirect("view_booking")

    return render(request, "add_review.html", {"booking": booking, "product": product})


# product details

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews,
        "form": form
    })
