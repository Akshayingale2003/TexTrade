from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from .models import *
from datetime import date
from django.conf import settings
import razorpay
from django.http import JsonResponse ,HttpResponse
from django.db import transaction
import uuid
from django.contrib.auth.decorators import login_required

# Create your views here.

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
    
    return render(request,"vendor_home.html")


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


def view_orders(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login_vender') 

    vendor = Vendor.objects.get(user=request.user)  
    products = Product.objects.filter(vendor=vendor)
    return render(request, 'view_orders.html')


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

        user = get_object_or_404(User, username=c)
        profile = get_object_or_404(Profile, user=user)
        status = "processing"

        # ✅ Generate a unique booking ID
        new_booking = Booking.objects.create(
            profile=profile,
            book_date=d,
            total=t,
            status=status
        )



        for cart_item in cart:
            BookingItem.objects.create(
                booking=new_booking,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
                product_image = cart_item.product.image,
                product_desc = cart_item.product.desc

            )

        cart.delete()

        return redirect('payment', new_booking.total)

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
    book = Booking.objects.filter(profile=profile)
    num1=0
    for i in cart:
        num1 += 1
    d = {'book': book,'num1':num1}
    return render(request, 'view_booking.html', d)


def view_orders_vendor(request):
    if not request.user.is_authenticated:
        return redirect('login_vendor')
    
    cart = Cart.objects.all()
    vendor = Vendor.objects.get(user=request.user)
    book = BookingItem.objects.filter(product__vendor = vendor)
    num1=0
    for i in cart:
        num1 += 1
    d = {'book': book,'num1':num1}
    return render(request,"view_orders_vendor.html",d)


def payment(request,total):
    if not request.user.is_authenticated:
        return redirect('login')
    error = False
    user = User.objects.get(id=request.user.id)
    profile= Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile = profile).all()
    if request.method=="POST":
        error=True
    d ={'total':total,'error':error}
    return render(request,'payment2.html',d)


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



@login_required
def booking_detail(request, pid, bid):
    if not request.user.is_authenticated:
        return redirect('login')
    booking = get_object_or_404(Booking, booking_id=pid, id=bid)
    products = booking.products.all()
    order_status = booking.status.name if booking.status else "Pending"
    total_price = sum(product.price for product in products)
    context = {
        'booking': booking,
        'products': products,
        'total_price': total_price,
        'order_status': order_status,  
    }

    return render(request, 'booking_detail.html', context)

def Admin_View_Booking(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    book = BookingItem.objects.all()
    d = {'book': book}
    return render(request, 'admin_viewBokking.html', d)


def admin_booking_detail(request,pid,bid,uid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    user = User.objects.get(id=uid)
    profile = Profile.objects.get(user=user)
    cart =  Cart.objects.filter(profile=profile).all()
    product = Product.objects.all()

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
    user = User.objects.get(id=uid)
    profile = Profile.objects.get(user=user)
    cart =  Cart.objects.filter(profile=profile).all()
    num1=0
    booking = get_object_or_404(Booking, booking_id=pid, id=bid)
    bookitem = BookingItem.objects.filter(booking=booking)
    li = []

    for i in bookitem:
        li.append(i.product)

    total_price = booking.total

    d = {'profile':profile,'cart':cart,'total':total_price,'num1':num1,'book':li ,'product':bookitem}
    return render(request,'vendor_view_booking_detail.html',d)

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
        dob = request.POST['date']
        img = request.FILES.get('img')

        pro.user.first_name = fname
        pro.user.last_name = lname
        pro.user.email = email
        pro.user.username = uname
        pro.city = city
        pro.address = address
        pro.contact = contact
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

def payment(request, total=None):
    if total is None:
        return render(request, "error.html", {"error": "Invalid total amount."})

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    profile = request.user.profile
    latest_booking = Booking.objects.filter(profile=profile).order_by('-book_date').first()
    
    if not latest_booking:
        return render(request, "error.html", {"error": "No booking found."})

    data = {
        "amount": int(total) * 100, 
        "currency": "INR",
        "payment_capture": "1"
    }

    try:
        order = client.order.create(data)
    except razorpay.errors.BadRequestError:
        return render(request, "error.html", {"error": "Authentication failed. Check API keys."})

    return render(request, "payment.html", {
        "amount": total,
        "order_id": order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
         "booking_id": latest_booking.booking_id  
    })


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_order(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount")) * 100  
        order_currency = "INR"
        
        # Create a Razorpay Order
        order = razorpay_client.order.create({
            "amount": amount,
            "currency": order_currency,
            "payment_capture": "1"
        })

        # Save order to database
        payment = Payment(order_id=order["id"], amount=amount/100, status="Created")
        payment.save()

        return render(request, "payment.html", {
            "order_id": order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": amount
        })

    return render(request, "payment_form.html")

# payment
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def process_booking(request):
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        total = request.POST.get("total")

        # ✅ Ensure "Pending" status exists
        pending_status, created = Status.objects.get_or_create(name="Pending")

        print(f"Using status: {pending_status.name}, Created new status: {created}")  # ✅ Debugging output

        with transaction.atomic():  # ✅ Prevents race conditions
            booking, created = Booking.objects.get_or_create(
                profile=profile,
                total=total,
                payment=None,  # ✅ Ensures we only check unpaid bookings
                defaults={"status": pending_status}  # ✅ Set status when creating
            )

            # ✅ If the booking already exists, ensure status is "Pending"
            if not created and booking.status != pending_status:
                booking.status = pending_status
                booking.save()

            print(f"Booking created: {created}, Status assigned: {booking.status.name}")  # ✅ Debugging output

        return redirect("success_page")


def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        booking_id = request.POST.get("booking_id")  # ✅ Get booking_id from request

        try:
            # Find the corresponding booking
            booking = Booking.objects.get(booking_id=booking_id)

            # Create Payment entry
            payment = Payment.objects.create(
                payment_id=razorpay_payment_id,
                order_id=razorpay_order_id,
                amount=booking.total,
                status = 'paid'
            )

            # Link the payment to the booking
            booking.payment = payment
            booking.save()

            return JsonResponse({"status": "success"})
        except Booking.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Booking not found"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

# confirmation

def booking_confirmation(request):
    booking_id = request.GET.get("booking_id")
    total_amount = request.GET.get("total_amount")
    payment_id = request.GET.get("payment_id")

    try:
        booking = Booking.objects.get(booking_id=booking_id)
    except Booking.DoesNotExist:
        return render(request, "error.html", {"error": "Booking not found."})

    return render(request, "booking_confirmation.html", {
        "booking_id": booking_id,
        "total_amount": total_amount,
        "payment_id": payment_id,
        "order_status": "Confirmed"
    })

from .forms import ReviewForm

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(profile=request.user.profile, status__status="Completed")  # Show completed bookings
    return render(request, 'booking_history.html', {'bookings': bookings})


# reviews 

def add_review(request, booking_id, product_id):
    booking = Booking.objects.get(booking_id=booking_id)  # Get Booking
    product = Product.objects.get(id=product_id)  # Get Product

    if request.method == "POST":
        comment = request.POST.get("comment")  # Match "comment" field
        rating = request.POST.get("rating")

        # ✅ Ensure Review object is created with correct field names
        review = Review.objects.create(
            product=product,
            user=request.user,  # Assuming user is logged in
            comment=comment,  # Use "comment" instead of "review_text"
            rating=int(rating)  # Convert rating to integer
        )
        review.save()

        return redirect("view_booking")  # Redirect after review submission

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
