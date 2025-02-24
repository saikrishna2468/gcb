from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid

from django.conf import settings

class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    age = models.IntegerField(null=True, blank=True)
    is_member = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    referral_user = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_users')
    referral_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4()).replace('-', '')[:8]
        super().save(*args, **kwargs)

    def get_upline_profit(self, level=0):
        if level >= 5 or not self.referral_user:
            return 0
        return self.referral_user.wallet_balance + self.referral_user.get_upline_profit(level + 1)



    groups = models.ManyToManyField(Group, related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions', blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Other fields as needed...
    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.product.name}"


class ReferralProfit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    referred_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='profit_references')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profit {self.amount} from {self.referred_user.username} to {self.user.username}"


from django.db import models
from django.conf import settings
from decimal import Decimal

class CompletedOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_reference = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return f"Completed Order {self.id} - {self.user.username} - {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Calculate profit sharing for referrals
        self.share_profit()

    def share_profit(self):
        referral_user = self.user.referral_user
        profit_percentage = Decimal(0.01)  # Convert percentage to Decimal
        profit = self.total_price * profit_percentage  # Ensure profit is calculated correctly
        level = 0

        while referral_user and level < 5:
            # Distribute profit to the referring user
            ReferralProfit.objects.create(user=referral_user, amount=profit, referred_user=self.user)

            # Update wallet balance
            referral_user.wallet_balance += profit
            referral_user.save()

            referral_user = referral_user.referral_user  # Move to the next upline
            level += 1
            
class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    upi_id = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment {self.id} - {self.user.username}'
class Membership(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    membership_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)

class Referral(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_referrals')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_referrals')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral from {self.sender.username} to {self.recipient.username} on {self.sent_at}"
# models.py
from django.db import models
from django.conf import settings

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class FeedbackReply(models.Model):
    feedback = models.ForeignKey(Feedback, related_name='replies', on_delete=models.CASCADE)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Assuming admin is a user
    reply_text = models.TextField()
    replied_at = models.DateTimeField(auto_now_add=True)

