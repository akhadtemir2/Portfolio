from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Game, Cart, CartItem, Order, OrderItem


def home(request):
    """Главная страница - показывает все игры"""
    games = Game.objects.filter(in_stock=True)
    context = {'games': games}
    return render(request, 'store/home.html', context)


def main_page(request):
    """Статическая главная витрина"""
    games = Game.objects.filter(in_stock=True)[:10]
    context = {'games': games}
    return render(request, 'store/main-page.html', context)


def game_list(request):
    """Список всех игр"""
    games = Game.objects.all()
    context = {'games': games}
    return render(request, 'store/all_games.html', context)


def game_detail(request, game_id):
    """Детальная страница игры"""
    game = get_object_or_404(Game, id=game_id)
    context = {'game': game}
    return render(request, 'store/gamepage.html', context)


def gamepage(request):
    """Страница детальной информации о игре (первая игра как пример)"""
    game = Game.objects.first()
    if not game:
        messages.error(request, "Игры не найдены")
        return redirect('home')
    context = {'game': game}
    return render(request, 'store/gamepage.html', context)


@login_required
def add_to_cart(request, game_id):
    """Добавление игры в корзину"""
    game = get_object_or_404(Game, id=game_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        game=game, 
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        message = f"Количество {game.title} увеличено в корзине"
    else:
        message = f"{game.title} добавлена в корзину"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total': cart.get_total_items()
        })
    
    messages.success(request, message)
    return redirect('game_detail', game_id=game_id)


@login_required
def cart_view(request):
    """Просмотр корзины"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    context = {'cart': cart}
    return render(request, 'store/cart.html', context)


def bin_basket(request):
    """Статическая страница корзины"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        context = {'cart': cart}
    else:
        context = {'cart': None}
    return render(request, 'store/bin_basket.html', context)


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Количество обновлено")
    else:
        cart_item.delete()
        messages.success(request, "Товар удален из корзины")
    return redirect('cart_view')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Товар удален из корзины")
    return redirect('cart_view')


@login_required
def checkout(request):
    """Оформление заказа"""
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.error(request, "Ваша корзина пуста")
        return redirect('cart_view')
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user, 
            total_price=cart.get_total_price()
        )
        for item in cart.items.all():
            price = item.game.get_discounted_price() if item.game else 0
            OrderItem.objects.create(
                order=order, 
                game=item.game, 
                price=price, 
                quantity=item.quantity
            )
        cart.items.all().delete()
        messages.success(request, f"Заказ #{order.id} успешно оформлен!")
        return redirect('order_detail', order_id=order.id)
    
    context = {'cart': cart}
    return render(request, 'store/checkout.html', context)


@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_detail.html', context)


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Cart.objects.get_or_create(user=user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Неверное имя пользователя или пароль")
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, "Вы вышли из системы")
    return redirect('home')


@login_required
def payment(request):
    """Страница оплаты"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Перенаправляем на checkout для создания заказа
        return redirect('checkout')
    
    context = {'cart': cart}
    return render(request, 'store/payment.html', context)


@login_required
def profile(request):
    """Страница профиля"""
    if request.method == 'POST':
        # Обработка обновления профиля
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        request.user.save()
        
        messages.success(request, "Профиль обновлен!")
        return redirect('profile')
    
    return render(request, 'store/profile.html')


@login_required
def profile_history(request):
    """Страница истории покупок"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'store/profile-history.html', context)


def signup2(request):
    """Второй этап регистрации"""
    if not request.user.is_authenticated:
        return redirect('register')
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        # Здесь можно сохранить дополнительные данные в профиль
        messages.success(request, "Данные обновлены!")
        return redirect('home')
    
    return render(request, 'store/signup2.html')