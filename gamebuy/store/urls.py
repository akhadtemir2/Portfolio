from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.game_list, name='game_list'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('main/', views.main_page, name='main_page'),
    path('bin_basket/', views.bin_basket, name='bin_basket_view'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('bin/', views.bin_basket, name='bin_basket'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('payment/', views.payment, name='payment'),
    path('profile/', views.profile, name='profile'),
    path('profile/history/', views.profile_history, name='profile_history'),
    path('signup2/', views.signup2, name='signup2'),
    path('gamepage/', views.gamepage, name='gamepage'),
    path('accounts/login/', views.login_view, name='accounts_login'),
]
