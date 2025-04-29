from django.shortcuts import render,redirect
from django.contrib import messages
from Trackart.models import Products,Wishlist
from dashboard.models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden

def not_manager(user):
    return getattr(user, 'role', '').lower() != 'staff'

def block_role(role_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request.user, 'role', None) == role_name:
                return HttpResponseForbidden("You are not allowed to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
# Create your views here.

def home_view(request):
    user_role = getattr(request.user, 'role', None) 
    return render(request,'trackart/home.html',{'user_role': user_role})
def products_view(request):
    products = Products.objects.all()
    user_role = getattr(request.user, 'role', None)  # Safely get the role
    if request.method == 'POST':
        
            # Get form data
        product_category = request.POST.get('category')
        product_sub_category = request.POST.get('sub_category')
        image_link = request.POST.get('image_link')
        description = request.POST.get('description')
        selling_price = request.POST.get('offer_price')
        original_price = request.POST.get('original_price')
        discount = request.POST.get('discount')

        # Validate required fields
        

        # Create product
        Products.objects.create(
            category=product_category,
            sub_category=product_sub_category,
            image_link=image_link,
            description=description,
            offer_price=selling_price,
            original_price=original_price,
            discount=discount
        )
        products = Products.objects.all()

        return render(request, 'products.html', {'products': products,'user_role': user_role}) 
        
        
        
    return render(request, 'products.html', {'products': products,'user_role': user_role})


def delete_product(request, product_id):
    product= Products.objects.get(id=product_id)
    
    product.delete()
   
       
    return redirect('products')   


def productDetail_view(request,product_id):
    user_role = getattr(request.user, 'role', None)
   
    product= Products.objects.get(id=product_id)
        
    return render(request,'productDetail.html',{'product':product,'user_role': user_role})



@login_required
def cart_view(request, product_id):
    user_role = getattr(request.user, 'role', None)

    product = Products.objects.get(id=product_id)
    current_user = CustomUser .objects.get(id=request.user.id)
    product.chooser.add(current_user)
    product.save()

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        item_id = request.POST.get('item_id')
        item = Products.objects.get(id=item_id)
        item.quantity = quantity
        item.save()
        return render(request, 'cart.html', {'user': current_user, 'user_role': user_role})

    return render(request, 'cart.html', {"user": current_user, 'user_role': user_role})

def cart_button(request):
    user_role = getattr(request.user, 'role', None)  # Define user_role at the beginning
    if user_role and user_role.lower() == 'user':
        current_user = CustomUser .objects.get(id=request.user.id)
        if request.method == 'POST':
            quantity = request.POST.get('quantity')
            item_id = request.POST.get('item_id')
            item = Products.objects.get(id=item_id)
            item.quantity = quantity
            item.save()
            return render(request, 'cart.html', {'user': current_user})

        return render(request, 'cart.html', {'user': current_user})
    return HttpResponseForbidden("Access Denied: you are not user.")

def item_quantity(request):
    current_user = CustomUser.objects.get(id=request.user.id)
    if request.method == 'POST':
      
        quantity = request.POST.get('quantity')
        item_id = request.POST.get('item_id')
        item = Products.objects.get(id=item_id)
        item.quantity = quantity
        item.save()
        return render(request, 'cart.html', {'user': current_user})
        
        # Update the quantity of the cart item
       
    current_user = CustomUser.objects.get(id=request.user.id)
    cart_items = Products.objects.filter(chooser=current_user)
    total_price = sum(item.offer_price*item.quantity for item in cart_items)
    return render(request, 'cart.html', {'user': current_user, 'total_price': total_price,"total":total_price+248})

def wishlist_view(request,product_id):
    user_role = getattr(request.user, 'role', None)
    current_user = CustomUser.objects.get(id=request.user.id)
    product = Products.objects.get(id=product_id)
    try:
        existing_item = Wishlist.objects.get(
            description=product.description,
            chooser=current_user
        )
        messages.warning(request, 'Product already exists in your wishlist!')
    except Wishlist.DoesNotExist:
        # Create new wishlist item only if it doesn't exist
        wishlist_product = Wishlist.objects.create(
            category=product.category,
            sub_category=product.sub_category,
            image_link=product.image_link,
            description=product.description,
            offer_price=product.offer_price,
            original_price=product.original_price,
            discount=product.discount,
        )
        wishlist_product.chooser.add(current_user)
        wishlist_product.save()
        messages.success(request, 'Product added to wishlist successfully!')

        return render(request,'wishlist.html', {"user":current_user}) 
    

    return render(request,'wishlist.html', {"user":current_user,'user_role': user_role}) 
      

def wishlist_button(request):      
    user_role = getattr(request.user, 'role', None)  # Define user_role at the beginning

    # Check if the user is a staff member
    if user_role and user_role.lower() == 'staff':
        return HttpResponseForbidden("Access Denied: you are not allowed to access this page.")

    current_user = CustomUser .objects.get(id=request.user.id)

def delete_from_wishlist(request, item_id):
    current_user = CustomUser.objects.get(id=request.user.id)
        
        # Get wishlist item for this specific user
    wishlist_item = Wishlist.objects.filter(id=item_id, chooser=current_user)
        
        # Delete the item
    wishlist_item.delete()
        
        # Get remaining wishlist items for this user
    
        
    return redirect('wishlist_button')
        
def delete_from_cart(request, item_id):
    current_user = CustomUser.objects.get(id=request.user.id)
   
        # Get cart item for this specific user
    cart_item = Products.objects.get(id=item_id)
        
        # Delete the item
    cart_item.chooser.remove(current_user)
        
        # Get remaining cart items for this user
    
        
    return redirect('cart_button')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Validate required fields
        if not username or not password or not email:
            messages.error(request, 'All fields are required.')
            return redirect('signup')

        # Create user
      
        
      
        return redirect('home')

    return render(request, 'signup.html')


def edit_product(request, product_id):
    item = Products.objects.get(id=product_id)
    products= Products.objects.all()
    user_role = getattr(request.user, 'role', None)
    if request.method == 'POST':
        # Get form data
        item.category = request.POST.get('category')
        item.sub_category = request.POST.get('sub_category')
        item.image_link = request.POST.get('image_link')
        item.description = request.POST.get('description')
        item.offer_price = request.POST.get('offer_price')
        item.original_price = request.POST.get('original_price')
        item.discount = request.POST.get('discount')

        # Save the updated product
        item.save()

       

        return render(request, 'products.html', {'product_detail':item,'products': products,"user_role":user_role})
    return render(request, 'products.html', {'product_detail':item,'products': products,"user_role":user_role})

def item_quantity(request):
    if request.method == 'POST':
      
        quantity = request.POST.get('quantity')
        item_id = request.POST.get('item_id')
        item = Products.objects.get(id=item_id)
        item.quantity = quantity
        item.save()

        # Update the quantity of the cart item
       
    current_user = CustomUser.objects.get(id=request.user.id)
    cart_items = Products.objects.filter(chooser=current_user)
    total_price = sum(item.offer_price*item.quantity for item in cart_items)
    return render(request, 'cart.html', {'user': current_user, 'total_price': total_price,"total":total_price+248})


def wishlist_cart_btn(request,product_id):
    try:
        # Get current user
        current_user = CustomUser.objects.get(id=request.user.id)
        
        # Get wishlist item
        wishlist_item = Wishlist.objects.get(id=product_id)
        
        # Find corresponding product in Products table
        product = Products.objects.get(description=wishlist_item.description)
        
        # Add product to user's cart
        product.chooser.add(current_user)
        product.save()
        
        # Remove item from wishlist
       
        
        # Get updated cart items
        
        return redirect('cart_button')
            
     
        
    except Wishlist.DoesNotExist:
        messages.error(request, 'Wishlist item not found!')
        return redirect('wishlist')
    except Products.DoesNotExist:
        messages.error(request, 'Product not found!')
        return redirect('wishlist')

   

def view_furniture(request):
    products=Products.objects.filter(category="furniture")
    user_role = getattr(request.user, 'role', None)

    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_living_room(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="livingroom")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_dining_room(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="dining_room")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_bed_room(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="bedroom")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_outdoor(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="outdoor")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_bathroom_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="bathroom_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_home_office_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="home_office_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def entry_way_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="entry_way_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})

def tabletop_bar(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def dinnerware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="dinnerware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def serveware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="serveware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def drinkware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="drinkware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bar_tools_accessories(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="bar_tools_accessories")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def table_linnens(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="table_linnens")
    return render(request,'products.html',{"products":products,"user_role":user_role})


def kitchen(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def kitchen_appliences_electronics(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="kitchen_appliences_electronics")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def coffee_espresso_tea(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="coffee_espresso_tea")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def cookware_bakeware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="cookware_bakeware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def cutlury_knive(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="cutlury_knive")
    return render(request,'products.html',{"products":products,"user_role":user_role})

def bedding(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bedding")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bedding_essentials(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bedding",sub_category="bedding_essentials")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def Bath(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_linnens_towels(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_linnens_towels")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_accessories_storage(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_accessories_storage")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_hardware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_hardware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_sent(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_sent")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def Decor_Pillow(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def pillows_cushions(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="pillows_cushions")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def wall_art_frames(request):
    products=Products.objects.filter(category="decor_pillow",sub_category="wall_art_frames")
    user_role = getattr(request.user, 'role', None)
    return render(request,'products.html',{"products":products,"user_role":user_role})
def mirrors(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="mirrors")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def botanicals_vases(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="botanicals_vases")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def candles_fragrance(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="candles_fragrance")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def decorative_objects(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="decorative_objects")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def lighting(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="lighting")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def ceiling_lights(request):
    products=Products.objects.filter(category="lighting",sub_category="ceiling_lights")
    user_role = getattr(request.user, 'role', None)
    return render(request,'products.html',{"products":products,"user_role":user_role})
def table_floor_lamps(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="lighting",sub_category="table_floor_lamps")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def wall_light_sconces(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="lighting",sub_category="wall_light_sconces")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def window(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def all_window_curtains(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="all_window_curtains")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def blackout_curtains(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="blackout_curtains")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def sheer_curtains(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="sheer_curtains")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def window_curtain_hardware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="window_curtain_hardware")
    return render(request,'products.html',{"products":products,"user_role":user_role})


