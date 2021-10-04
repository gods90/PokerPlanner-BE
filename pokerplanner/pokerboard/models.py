from django.db import models

from pokerplanner.group.models import Group
from pokerplanner.user.models import User

class Pokerboard(models.Model):
    """ Model to store Pokerboard settings."""
    SERIES = 1
    EVEN = 2
    ODD = 3
    FIBONACCI = 4
    ESTIMATION_CHOICES = (
        (SERIES, 'Series'),
        (EVEN, 'Even'),
        (ODD, 'Odd'),
        (FIBONACCI, 'Fibonacci'),
    )
    
    CREATED = 1
    STARTED = 2
    ENDED = 3
    STATUS_CHOICES = (
        (CREATED, 'Created'),
        (STARTED, 'Started'),
        (ENDED, 'Ended')
    )
    manager=models.ForeignKey(User,on_delete=models.CASCADE,help_text='Owner of pokerboard.')
    title = models.CharField(max_length=50, help_text='Name of Pokerboard.')
    description = models.CharField(max_length=100, help_text='Description of POkerboard.')
    configuration = models.IntegerField(choices=ESTIMATION_CHOICES, default=SERIES, help_text='Estimation type.')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=CREATED,help_text='Default pokerboard status is created.')
    
    def __str__(self) -> str:
        return self.title


class PokerboardUserMapping(models.Model):
    """
    Model to store mappings of pokerboards to users.
    """

    PLAYER = 0
    MANAGER = 1
    SPECTATOR = 2

    ROLE_CHOICES = (
        (PLAYER, 'PLAYER'),
        (MANAGER, 'MANAGER'),
        (SPECTATOR, 'SPECTATOR'),
    )
    
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.IntegerField(
        choices=ROLE_CHOICES,
        default=PLAYER,
        help_text='Default user role is player.',
    )

    def __str__(self):
        return f'${self.pokerboard}->${self.user}'
    
    
class Ticket(models.Model):
    """
    Model to store ticket detail
    """
    NOTSTARTED=0
    ONGOING = 0
    HASENDED = 1

    
    STATUS_CHOICES = (
        (NOTSTARTED,'notstarted'),
        (ONGOING, 'ongoing'),
        (HASENDED, 'hasended'),
    )
    
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE, help_text='Pokerboard to which ticket belongs.')
    ticket_id = models.CharField(max_length=100,help_text='Ticket ID imported from JIRA.')
    order = models.PositiveSmallIntegerField(help_text='Rank of ticket.')
    estimation_date=models.DateField()
    status=models.IntegerField(
        choices=STATUS_CHOICES,
        default=NOTSTARTED,
        help_text='Default ticket status is not started.',
    )
    
    def __str__(self):
        return f'{self.ticket_id} -> {self.pokerboard}'
  
    
class UserEstimate(models.Model):
    """
    Model to store user estimates
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,help_text='User which has estimated the ticket.')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,help_text='Ticket to which estimate belongs.')
    time_taken_to_estimate = models.IntegerField(default=0,help_text='Duration for voting(in secs)')
    estimate = models.PositiveIntegerField(help_text='Value of estimate done by the user.')
    
    def __str__(self):
        return f"${self.ticket}->${self.user}->${self.estimate}"


class Invite(models.Model):
    """
    Model to store invites
    """

    PLAYER = 0
    MANAGER = 1
    SPECTATOR = 2

    ROLE_CHOICES = (
        (PLAYER, 'PLAYER'),
        (MANAGER, 'MANAGER'),
        (SPECTATOR, 'SPECTATOR'),
    )

    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE,help_text='Pokerboard of which invite has been sent.')
    user = models.ForeignKey(User, on_delete=models.CASCADE,help_text='User which is invited.')
    user_role = models.IntegerField(
        choices=ROLE_CHOICES,
        default=PLAYER,
        help_text='Default user role is player',
    )
    is_accepted = models.BooleanField(default=False)
    group = models.ForeignKey(
        Group,null=True,on_delete=models.CASCADE,help_text='Group which is invited.'
    )
    
    def __str__(self):
        if self.group!=None:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard} -> Group: {self.group}'
        else:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard}'
        