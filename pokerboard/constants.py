PLAYER = 0
SPECTATOR = 1

ROLE_CHOICES = (
    (PLAYER, 'PLAYER'),
    (SPECTATOR, 'SPECTATOR'),
)

PENDING = 0
ACCEPTED = 1
DECLINED = 2

INVITE_STATUS = (
    (PENDING, 'PENDING'),
    (ACCEPTED, 'ACCEPTED'),
    (DECLINED, 'DECLINED')
)

ESTIMATED = 0
NOTESTIMATED = 1

TICKET_STATUS_CHOICES = (
    (ESTIMATED, 'estimated'),
    (NOTESTIMATED, 'notestimated'),
)

ONGOING = 0
HASENDED = 1

SESSION_STATUS_CHOICES = (
    (ONGOING, "ongoing"),
    (HASENDED, "hasended"),
)

SESSION_METHOD_CHOICES = [
    'estimate',
    'start_game',
    'skip_ticket',
    'start_timer',
    'final_estimate', 
    'get_ticket_details'
]