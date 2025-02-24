from .models import CustomUser, CompletedOrder, Referral

def distribute_referral_profit(order):
    # Get the user who made the order
    user = order.user

    # Get the total amount of the order
    total_amount = order.total_price

    # Calculate the profit (1% of the total amount)
    profit = total_amount * 0.01

    # Initialize variables for referral distribution
    referral_user = user.referral_user
    profit_distribution = []

    # Distribute the profit up to 5 users in the referral chain
    for _ in range(5):
        if referral_user:
            referral_user.wallet_balance += profit
            referral_user.save()
            profit_distribution.append(referral_user)
            referral_user = referral_user.referral_user  # Move up the chain
        else:
            break

    return profit_distribution
