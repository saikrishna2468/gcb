from itertools import count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from .models import CompletedOrder, Payment, Product, CustomUser, Category
def index(request):
    return render(request,"user/index.html")
# Helper function to check if the user is admin
def is_admin(user):
    return user.username == 'admin'

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username == 'admin' and password == 'admin':
            user = CustomUser.objects.filter(username='admin').first()
            if not user:
                user = CustomUser.objects.create_user(username='admin', password='admin')
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, './admin/admin_login.html', {'error': 'Invalid Credentials'})
    return render(request, './admin/admin_login.html')
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        Category.objects.create(name=name)
        return redirect('admin_dashboard')  # Redirect to the admin dashboard or category list page
    return render(request, './admin/add_category.html')
@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.category = Category.objects.get(id=request.POST['category'])
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        return redirect('admin_dashboard')  # Redirect to the admin dashboard or product list page

    return render(request, './admin/edit_product.html', {
        'product': product,
        'categories': categories
    })
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('admin_dashboard')  # Redirect to the admin dashboard or product list page

from django.contrib.auth import get_user_model
from .models import Category, Product
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .models import Category, Product, Payment, Referral
from django.db.models import Sum, Count
from django.db.models import Count, Sum
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers.json import DjangoJSONEncoder
import json

@user_passes_test(is_admin)
def admin_dashboard(request):
    User = get_user_model()

    # Count total users, categories, products
    user_count = User.objects.count()
    category_count = Category.objects.count()
    product_count = Product.objects.count()

    # Count total referrals
    referral_count = Referral.objects.count()

    # Referral profits (Assume 100 INR profit per referral)
    referral_profits = referral_count * 100

    # Group payments by payment method
    payments_by_method = Payment.objects.values('payment_method').annotate(count=Count('id'))

    # Prepare payments data in a suitable format
    payment_labels = [payment['payment_method'] for payment in payments_by_method]
    payment_data = [payment['count'] for payment in payments_by_method]

    # Context data to pass to the template
    context = {
        'user_count': user_count,
        'category_count': category_count,
        'product_count': product_count,
        'referral_profits': referral_profits,
        'payment_labels': json.dumps(payment_labels, cls=DjangoJSONEncoder),  # JSON-safe format
        'payment_data': json.dumps(payment_data, cls=DjangoJSONEncoder),  # JSON-safe format
    }

    return render(request, 'admin/admin_dashboard.html', context)



@user_passes_test(is_admin)
def admin_product_list(request):
    products = Product.objects.all()
    return render(request, './admin/admin_product-list.html', {'products': products})
@user_passes_test(is_admin)
def admin_user_list(request):
    users = CustomUser.objects.filter(is_superuser=False)  # Exclude admin user from the list
    return render(request, './admin/admin_user_list.html', {'users': users})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import CustomUser

@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)  # Fetch the user by ID

    if request.method == 'POST':
        user.username = request.POST['username']
        user.mobile_number = request.POST['mobile_number']
        user.email = request.POST['email']
        user.age = request.POST['age']
        user.save()  # Save changes
        return redirect('admin_user_list')  # Redirect back to the user list

    return render(request, './admin/edit_user.html', {'user': user})
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()  # Delete the user
    return redirect('admin_user_list')  # Redirect back to the user list

@user_passes_test(is_admin)
def add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        category_id = request.POST['category']
        image = request.FILES['image']
        
        category = Category.objects.get(id=category_id)
        Product.objects.create(name=name, description=description, price=price, category=category, image=image)
        return redirect('admin_dashboard')
    return render(request, './admin/add_product.html', {'categories': categories})

@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('admin_dashboard')


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Referral, Membership

@user_passes_test(is_admin)
def admin_view_referrals(request):
    # Get all referrals
    referrals = Referral.objects.all().order_by('-sent_at')  # Order by most recent
    
    context = {
        'referrals': referrals
    }
    
    return render(request, './admin/admin_view_referrals.html', context)


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import CompletedOrder, Payment

@user_passes_test(is_admin)
def admin_payment_history(request):
    completed_orders = CompletedOrder.objects.all()  # Fetch all completed orders
    payments = Payment.objects.all()  # Fetch all payment records

    # Add pagination (optional)
    paginator_orders = Paginator(completed_orders, 10)  # Show 10 orders per page
    paginator_payments = Paginator(payments, 10)  # Show 10 payments per page

    page_number_orders = request.GET.get('page_orders')
    page_number_payments = request.GET.get('page_payments')

    page_orders = paginator_orders.get_page(page_number_orders)
    page_payments = paginator_payments.get_page(page_number_payments)

    order_count = completed_orders.count()
    payment_count = payments.count()

    return render(request, 'admin/payment_history.html', {
        'completed_orders': page_orders,
        'payments': page_payments,
        'order_count': order_count,
        'payment_count': payment_count,
    })


@user_passes_test(is_admin)
def logout_admin(request):
    logout(request)
    return redirect('admin_login')
# user
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import Product, Order, CustomUser, Category
from django.contrib.auth.decorators import login_required

# Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        age = request.POST.get('age')

        # Check if username or email already exists
        if CustomUser.objects.filter(username=username).exists():
            return render(request, './user/signup.html', {'error': 'Username already exists.'})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, './user/signup.html', {'error': 'Email already exists.'})

        # Create the user
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            mobile_number=mobile_number,
            age=age
        )
        # Automatically log in the user after signup
        login(request, user)
        # Redirect to the membership page immediately after signup
        return redirect('login')

    return render(request, './user/signup.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to the membership page after login
            return redirect('home')  # Change to 'membership_page'
        else:
            return render(request, './user/login.html', {'error': 'Invalid Credentials'})

    return render(request, './user/login.html')

@login_required
def home(request):
    return render(request,"user/home.html")
# Membership Page with Referral Code Input
from django.shortcuts import redirect, render
from .models import CustomUser
from django.contrib.auth.decorators import login_required

@login_required
def membership_page(request):
    user = request.user

    if request.method == 'POST':
        referral_code = request.POST.get('referral_code')
        address = request.POST.get('address')
        referral_user = None

        # Check for referral code logic
        if referral_code:
            referral_user = CustomUser.objects.filter(referral_code=referral_code).first()
            if referral_user and referral_user != user:
                # Save referral user and address to session before payment
                request.session['referral_user'] = referral_user.id
                request.session['address'] = address
                request.session['membership_amount'] = 10000  # Membership fee
                return redirect('payment_page')  # Redirect to payment page
            else:
                return render(request, './user/membership.html', {'error': 'Invalid referral code.'})

        # Standard membership without referral
        if not user.is_member:
            request.session['address'] = address
            request.session['membership_amount'] = 10000  # Membership fee
            return redirect('payment_page')  # Redirect to payment page
    return render(request, './user/membership.html')


# payment
@login_required
def payment_page(request):
    if request.method == 'POST':
        user = request.user
        membership_amount = request.session.get('membership_amount')
        address = request.session.get('address')
        referral_user_id = request.session.get('referral_user')

        # Mark the user as a member and update wallet balance
        user.wallet_balance += membership_amount
        user.is_member = True
        user.address = address
        if referral_user_id:
            referral_user = CustomUser.objects.get(id=referral_user_id)
            user.referral_user = referral_user
            referral_user.wallet_balance += 20  # Referral bonus
            referral_user.save()

        user.save()

        # Clear session data after transaction
        request.session.pop('membership_amount', None)
        request.session.pop('address', None)
        request.session.pop('referral_user', None)

        return redirect('user_portal')  # Redirect to user portal after payment

    return render(request, './user/payment.html')


# Product List View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Product

@login_required
def product_list(request):
    if not request.user.is_member:
        return redirect('membership_page')  # Redirect to membership page if not a member

    categories = Category.objects.all()  # Get all categories

    # Check if a category is selected via query parameters
    selected_category_id = request.GET.get('category')
    if selected_category_id:
        # Filter products by the selected category
        products = Product.objects.filter(category_id=selected_category_id)
    else:
        # Show all products if no category is selected
        products = Product.objects.all()

    return render(request, './user/products.html', {
        'categories': categories,
        'products': products,
        'selected_category_id': selected_category_id,  # Pass the selected category for the template
    })



# User Portal (Display user details)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def user_portal(request):
    user = request.user
    return render(request, './user/user_portal.html', {
        'username': user.username,
        'email': user.email,
        'mobile_number': user.mobile_number,
        'wallet_balance': user.wallet_balance,
        'is_member': user.is_member,
        'referral_user': user.referral_user,
        'referral_code': user.referral_code,  # Include referral code
    })


# Add to Cart View
@login_required
def add_to_cart(request, product_id):
    user = request.user
    if not user.is_member:
        return redirect('membership_page')  # Redirect to membership page if user is not a member

    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST['quantity'])
        total_price = product.price * quantity

        # Ensure user has enough wallet balance
        if user.wallet_balance >= total_price:
            # Create an order and update user wallet
            order = Order.objects.create(user=user, product=product, quantity=quantity, total_price=total_price)
            user.wallet_balance -= total_price
            user.save()
            return redirect('product_list')

    return render(request, './user/add_to_cart.html', {'product': product})



# Cart Page View
@login_required
def cart_page(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, './user/cart.html', {'orders': orders})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Order

@login_required
def remove_from_cart(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()  # Remove the order from the cart
    messages.success(request, "Item removed from cart.")
    return redirect('cart_page')  # Redirect back to cart page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from decimal import Decimal
from .models import Order, Payment, CompletedOrder
@login_required
def cart_page(request):
    orders = Order.objects.filter(user=request.user)

    # Ensure that total_cart_price is calculated using Decimal
    total_cart_price = sum(Decimal(order.total_price) for order in orders)

    if request.method == 'POST':
        payment_method = request.POST['payment_method']
        address = request.POST['address']  # Get the address input

        # Create a new Payment record with Decimal
        payment = Payment.objects.create(
            user=request.user,
            total_amount=total_cart_price,
            payment_method=payment_method,
            address=address  # Save address
        )

        # Save orders to CompletedOrder and clear the user's cart
        for order in orders:
            CompletedOrder.objects.create(
                user=request.user,
                product=order.product,
                quantity=order.quantity,
                total_price=Decimal(order.total_price),  # Ensure total_price is Decimal
                payment_method=payment_method,
                payment_reference=payment.id,  # Optionally save the payment ID
                address=address  # Save address
            )
            order.delete()

        # Save payment method-specific details
        if payment_method == 'Card':
            payment.card_number = request.POST.get('card_number')
        elif payment_method == 'UPI':
            payment.upi_id = request.POST.get('upi_id')
        elif payment_method == 'Net Banking':
            payment.bank_name = request.POST.get('bank_name')

        # Save the payment details
        payment.save()

        messages.success(request, "Payment was successful! Your cart is now empty.")
        return redirect('payment_history')  # Redirect to order history

    return render(request, 'user/cart.html', {'orders': orders, 'total_cart_price': total_cart_price})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CompletedOrder

@login_required
def payment_history(request):
    completed_orders = CompletedOrder.objects.filter(user=request.user)
    return render(request, 'user/payment_history.html', {'completed_orders': completed_orders})

# referral
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Referral
from django.core.mail import send_mail
from django.contrib import messages

@login_required
def send_referral(request):
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        recipient_username = request.POST.get('recipient_username')

        # Find the recipient user by email or username
        try:
            recipient = CustomUser.objects.get(email=recipient_email) or CustomUser.objects.get(username=recipient_username)
        except CustomUser.DoesNotExist:
            messages.error(request, "Recipient user does not exist.")
            return redirect('send_referral')

        # Create a referral entry
        Referral.objects.create(sender=request.user, recipient=recipient)

        # Send referral email (now only prints to console in dev mode)
        send_mail(
            'Referral from ' + request.user.username,
            f"Hi, you have been referred by {request.user.username}. Use their referral code: {request.user.referral_code}",
            'noreply@example.com',
            [recipient_email],
            fail_silently=False,
        )

        messages.success(request, f"Referral sent to {recipient_username}!")
        return redirect('view_sent_referrals')

    return render(request, './user/send_referral.html')

@login_required
def view_sent_referrals(request):
    # Get all referrals sent by the logged-in user
    sent_referrals = Referral.objects.filter(sender=request.user)
    
    context = {
        'sent_referrals': sent_referrals
    }
    
    return render(request, './user/view_sent_referrals.html', context)
@login_required
def view_received_referrals(request):
    # Get all referrals received by the logged-in user
    received_referrals = Referral.objects.filter(recipient=request.user)
    
    context = {
        'received_referrals': received_referrals
    }
    
    return render(request, './user/view_received_referrals.html', context)


# ==========================

    
from django.shortcuts import render
from .models import ReferralProfit
from django.shortcuts import render, redirect
from .models import ReferralProfit
from django.db.models import Sum

def user_profit_history(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect if not logged in

    # Get all profits related to the logged-in user
    profit_history = ReferralProfit.objects.filter(user=request.user)

    # Calculate the total profit for the logged-in user
    total_profit = profit_history.aggregate(total=Sum('amount'))['total'] or 0  # Default to 0 if None

    return render(request, 'user/profit_history.html', {
        'profit_history': profit_history,
        'total_profit': total_profit,
    })


from django.shortcuts import render, redirect
from .models import CompletedOrder, Product
from app.utils import distribute_referral_profit  # Import the function

def complete_order(request):
    if request.method == 'POST':
        # Get the product ID from the POST request
        product_id = request.POST.get('product_id')  # Assume you are sending product ID from the form
        quantity = int(request.POST.get('quantity'))  # Get quantity from the form
        payment_method = request.POST.get('payment_method')  # Get payment method from the form
        shipping_address = request.POST.get('address')  # Get shipping address from the form

        # Fetch the selected product from the database
        try:
            selected_product = Product.objects.get(id=product_id)  # Get the product instance using the ID
        except Product.DoesNotExist:
            return render(request, 'user/error_page.html', {'message': 'Product not found.'})

        # Calculate the total price
        total_price = selected_product.price * quantity

        # Create the completed order
        order = CompletedOrder.objects.create(
            user=request.user,
            product=selected_product,
            quantity=quantity,
            total_price=total_price,
            payment_method=payment_method,
            address=shipping_address
        )
        
        # Distribute referral profits
        distribute_referral_profit(order)

        return redirect('order_success_page')  # Redirect to a success page

    return render(request, 'user/error_page.html', {'message': 'Invalid request method.'})

from django.shortcuts import render
from .models import ReferralProfit

def referral_profit_view(request):
    profits = ReferralProfit.objects.all()  # Get all referral profits
    return render(request, 'admin/referral_profits.html', {'profits': profits})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Feedback

# views.py
from django.shortcuts import render, redirect
from .models import Feedback
from django.contrib import messages
from django.utils import timezone

# views.py
from django.shortcuts import render, redirect
from .models import Feedback
from django.contrib import messages

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Feedback, FeedbackReply

# View for submitting feedback
@login_required
def submit_feedback(request):
    if request.method == 'POST':
        feedback_message = request.POST.get('message')
        
        # Save the feedback to the database using the correct field name
        feedback = Feedback(user=request.user, text=feedback_message)  # Use 'text' instead of 'message'
        feedback.save()
        
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('feedback_success')  # Redirect to the feedback success page
    
    return render(request, 'user/submit_feedback.html')  # Render the feedback form template

# View for admin to see all feedback
@user_passes_test(is_admin)
def admin_feedback_list(request):
    feedbacks = Feedback.objects.all()  # Get all feedback for the admin
    return render(request, './admin/admin_feedback_list.html', {'feedbacks': feedbacks})

# View for admin to reply to feedback
@user_passes_test(is_admin)
def reply_to_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)

    if request.method == 'POST':
        reply_text = request.POST['reply']
        feedback_reply = FeedbackReply(feedback=feedback, admin=request.user, reply_text=reply_text)
        feedback_reply.save()  # Save the reply
        
        messages.success(request, 'Reply sent successfully!')
        return redirect('admin_feedback_list')  # Redirect to feedback list after replying

    return render(request, './admin/reply_feedback.html', {'feedback': feedback})

# Success view after feedback submission
def feedback_success(request):
    return render(request, 'user/feedback_success.html')

# View for users to see their feedback history
@login_required
def feedback_history(request):
    # Fetch all feedback submitted by the logged-in user
    user_feedbacks = Feedback.objects.filter(user=request.user).prefetch_related('replies')
    
    return render(request, 'user/feedback_history.html', {'feedbacks': user_feedbacks})
