from pokerplanner import settings
import requests
from rest_framework import serializers, status
from pokerboard.models import Ticket

def ticket_responses(issues):
        from pokerboard.serializers import TicketsSerializer
        jira = settings.JIRA
        data = dict(issues)
        ticket_responses = []

        myJql = ""
        # If sprint, then fetch all tickets in sprint and add
        if 'sprint_id' in data.keys():
            myJql = "Sprint = " + data['sprint_id']

        # Adding tickets
        if 'tickets' in data.keys():
            tickets = data['tickets']
            serializer = TicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)

            if len(myJql) != 0:
                myJql += " OR "
            myJql += "issueKey in ("
            for ticket in tickets:
                myJql = myJql + ticket + ','
            myJql = myJql[:-1] + ')'

        # Adding jql
        if 'jql' in data.keys():
            if(len(myJql) != 0):
                myJql += " OR "
            myJql += data['jql']

        jql = myJql
        try:
            if len(jql) == 0:
                raise requests.exceptions.RequestException
            issues = jira.jql(jql)['issues']
            for issue in issues:
                ticket_response = {}
                key = issue['key']
                obj = Ticket.objects.filter(ticket_id=key)
                if obj.exists():
                    ticket_response['message'] = 'Ticket part of another pokerboard.'
                    ticket_response['status_code'] = status.HTTP_400_BAD_REQUEST
                else:
                    ticket_response['estimate'] = issue['fields']['customfield_10016']
                    ticket_response['status_code'] = status.HTTP_200_OK
                ticket_response['key'] = key
                ticket_responses.append(ticket_response)
        except requests.exceptions.RequestException as e:
            raise serializers.ValidationError("Invalid Query")
        return ticket_responses
