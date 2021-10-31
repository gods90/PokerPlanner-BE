from pokerboard.models import Ticket


def move_ticket_to_last(ticket_id,pokerboard):
    all_non_estimated_tickets = Ticket.objects.filter(pokerboard__id=pokerboard,status=Ticket.NOTESTIMATED).order_by("order")
    print(all_non_estimated_tickets)

def checkEstimateValue(deck_type, estimateValue):
    if not isinstance(estimateValue,int):
        return False
    if deck_type == 1:
        return (estimateValue>0 and estimateValue<11)
    if deck_type == 2:
        return (estimateValue>0 and estimateValue<21 and estimateValue%2 == 0)
    if deck_type == 3:
        return (estimateValue>0 and estimateValue<20 and estimateValue%2 != 0)
    if deck_type == 4:
        deck = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        return estimateValue in deck
