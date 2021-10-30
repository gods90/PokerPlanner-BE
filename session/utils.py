from pokerboard.models import Ticket


def move_ticket_to_last(ticket_id,pokerboard):
    all_non_estimated_tickets = Ticket.objects.filter(pokerboard__id=pokerboard,status=Ticket.NOTESTIMATED).order_by("order")
    print(all_non_estimated_tickets)