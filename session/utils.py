from django.db.models import Max

from pokerboard.models import Pokerboard, Ticket
from session.models import UserEstimate
from user.models import User

def move_ticket_to_last(pokerboard, pk):
    highest_order_of_all_non_estimated_tickets = Ticket.objects.filter(pokerboard__id=pokerboard,status=Ticket.NOTESTIMATED).aggregate(Max('order'))
    ticket = Ticket.objects.get(id=pk)
    ticket.order = highest_order_of_all_non_estimated_tickets["order__max"] + 1
    ticket.save()
    
def check_estimate_value(deck_type, estimateValue):
    if not isinstance(estimateValue,int):
        return False
    if deck_type == Pokerboard.SERIES:
        return 0 < estimateValue < 11
    if deck_type == Pokerboard.EVEN:
        return 0 < estimateValue < 21 and estimateValue % 2 == 0
    if deck_type == Pokerboard.ODD:
        return 0 < estimateValue < 21 and estimateValue % 2 != 0
    if deck_type == Pokerboard.FIBONACCI:
        deck = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        return estimateValue in deck

def set_user_estimates(user_estimates, ticket_key):    
    users_estimates_data = []
    user_estimate_data = {}
    for user,data in user_estimates.items():
        user_estimate_data['user'] = User.objects.get(email=user)
        user_estimate_data['ticket'] = Ticket.objects.get(ticket_id=ticket_key)
        user_estimate_data['estimate'] = data[0]
        user_estimate_data['estimation_duration'] = data[1]
        users_estimates_data.append(user_estimate_data)
    UserEstimate.objects.bulk_create(
            [
                UserEstimate(
                    user=user_estimate_data['user'], ticket=user_estimate_data['ticket'],
                    estimate=user_estimate_data['estimate'], estimation_duration=user_estimate_data['estimation_duration']
                ) for ind, user_estimate_data in enumerate(users_estimates_data)
            ]
        )