from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    """Простая модель игры для магазина"""
    title = models.CharField(max_length=200, verbose_name="Название игры")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Цена", 
        blank=True, 
        null=True
    ) 
    image = models.ImageField(upload_to='games/', verbose_name="Изображение")
    description = models.TextField(verbose_name="Описание", blank=True)
    platform = models.CharField(max_length=100, verbose_name="Платформа", blank=True)
    genre = models.CharField(max_length=100, verbose_name="Жанр", blank=True)
    release_date = models.DateField(verbose_name="Дата выхода", null=True, blank=True)
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    
    # Новые поля для скидок
    discount_percentage = models.IntegerField(
        default=0, 
        verbose_name="Скидка (%)",
        help_text="Процент скидки (0-100)"
    )
    is_free = models.BooleanField(default=False, verbose_name="Бесплатная игра")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def get_discounted_price(self):
        """Расчет цены со скидкой"""
        if self.is_free:
            return 0
        if self.price and self.discount_percentage > 0:
            discount = self.price * (self.discount_percentage / 100)
            return self.price - discount
        return self.price if self.price else 0
    
    def get_display_price(self):
        """Получить цену для отображения"""
        if self.is_free:
            return "FREE"
        if self.price:
            return f"{self.price:,.0f} KZT"
        return "Скоро"
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        ordering = ['-created_at']


class Cart(models.Model):
    """Корзина пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Корзина пользователя {self.user.username}"
    
    def get_total_price(self):
        """Подсчет общей стоимости корзины с учетом скидок"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        """Подсчет количества товаров в корзине"""
        return sum(item.quantity for item in self.items.all())
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    """Товар в корзине"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.game.title} x {self.quantity}"
    
    def get_total_price(self):
        """Подсчет стоимости этого товара с учетом скидок"""
        if not self.game:
            return 0
        price = self.game.get_discounted_price()
        return price * self.quantity
    
    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"
        unique_together = ('cart', 'game')


class Order(models.Model):
    """Модель заказа"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Товар в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.game.title} x {self.quantity}"
    
    def get_total_price(self):
        """Подсчет стоимости позиции"""
        return self.price * self.quantity
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"