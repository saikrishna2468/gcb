from django.urls import path
from app.views import add_category, add_to_cart, admin_delete_user, admin_edit_user, admin_feedback_list, admin_login, admin_dashboard, add_product, admin_payment_history, admin_product_list, admin_user_list, admin_view_referrals, cart_page, complete_order, delete_product, edit_product, feedback_history, feedback_success, home, login_view, logout_admin, membership_page, payment_history,  payment_page,  product_list, referral_profit_view, remove_from_cart, reply_to_feedback, send_referral, signup_view, submit_feedback, user_portal, user_profit_history, view_received_referrals, view_sent_referrals,index
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/add_product/', add_product, name='add_product'),
    path('admin/delete_product/<int:product_id>/', delete_product, name='delete_product'),
    path('admin/logout/', logout_admin, name='logout_admin'),
    path('admin/edit-product/<int:product_id>/', edit_product, name='edit_product'),
    path('admin/delete-product/<int:product_id>/', delete_product, name='delete_product'),
    path('admin/add-category/', add_category, name='add_category'),
    path('admin/add-user-list/', admin_user_list, name='admin_user_list'),
    path('admin/add-product-list/', admin_product_list, name='admin_product_list'),
    path('admin/referrals/', admin_view_referrals, name='admin_view_referrals'),
    # user
    path('', index, name='index'),
    path('signup', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_admin, name='logout'),  # Assuming you have a logout_admin view
    path('membership/', membership_page, name='membership_page'),
    path('user/portal/', user_portal, name='user_portal'),
    path('products/', product_list, name='product_list'),
    path('products/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_page, name='cart_page'),
     path('remove-from-cart/<int:order_id>/', remove_from_cart, name='remove_from_cart'),
    path('payment/', payment_page, name='payment_page'),
     path('send-referral/', send_referral, name='send_referral'),
    path('sent-referrals/', view_sent_referrals, name='view_sent_referrals'),
    path('received-referrals/', view_received_referrals, name='view_received_referrals'),
    path('payment-history/', payment_history, name='payment_history'),
    path('admin/users/edit/<int:user_id>/', admin_edit_user, name='admin_edit_user'),
    path('admin/users/delete/<int:user_id>/', admin_delete_user, name='admin_delete_user'),
    path('home/',home,name="home"),
      # URL for completing an order (after purchase)
    path('complete-order/', complete_order, name='complete_order'),

    # URL for the user's profit history
    path('profit-history/', user_profit_history, name='profit_history'),

    # Admin URL for viewing payment history
    path('admin_payment-history/', admin_payment_history, name='admin_payment_history'),
    path('admin_referral-profits/', referral_profit_view, name='referral_profits'),
     path('feedback/submit/', submit_feedback, name='submit_feedback'),
    path('admin/feedback/', admin_feedback_list, name='admin_feedback_list'),
    path('admin/feedback/reply/<int:feedback_id>/', reply_to_feedback, name='reply_to_feedback'),
    path('feedback/success/', feedback_success, name='feedback_success'),
    path('feedback/history/', feedback_history, name='feedback_history'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
