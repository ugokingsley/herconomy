from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from knox.auth import AuthToken
from rest_framework import status
from django.db.models import Avg, Min, Max, Count, Exists, OuterRef
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from . serializers import *
from .helpers import *
from .tasks import send_notification_mail

@api_view(['POST'])
def register_api(request):
    data = request.data
    user = RegisterSerializer(data=data)
    if user.is_valid():
        if not User.objects.filter(username=data['email']).exists():
           user = User.objects.create(
               username = data['username'],
               email = data['email'],
               password = make_password(data['password'])
           )
           _,token = AuthToken.objects.create(user) 
           return Response({
                'message': 'User registered',
                'email': user.email,
                'token':token
                
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response({
                'error': 'User already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(user.errors)


@api_view(['POST'])
def login_api(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    _, token = AuthToken.objects.create(user)
    if token:
        return Response({
        'id': user.id,
        'email': user.email,
        'token':token  
        })
    else:
        return Response({'error':'Cannot Log In'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user_api(request):
    user = request.user

    if user.is_authenticated:
        return Response({
            'id': user.id,
            'email': user.email,
            'balance':user.account_balance
        })
    return Response({
        'error': 'Not Authenticated',
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    user = request.user
    recipient = request.data['recipient_email']
    user_recipient = User.objects.get(email=recipient)
    try:
        with transaction.atomic(): 
            if user_recipient: # check if the recipient exists
                if user.account_balance > 0 and user.account_balance >= int(request.data['amount']):
                    if user_recipient.flagged == False: # check if the recipient is not a flagged user
                        user.account_balance-=int(request.data['amount'])
                        user_recipient.account_balance+=int(request.data['amount'])
                        user.save()
                        user_recipient.save()
                        instance = Transaction(
                                    user=request.user,
                                    transaction_type = 'Transfer',
                                    transaction_ref = now + str(random.randint(1000, 9999)),
                                    amount = request.data['amount'],
                                    narration = f"Transferred {request.data['amount']} to {user_recipient.email}",
                                    device_signature = request.META['HTTP_USER_AGENT'],
                                    ip_address =  get_client_ip(request),
                                )
                        instance.save()
                        
                        data = {
                                    'transaction_type':'Transfer',
                                    'user': request.user.email,
                                    'amount': request.data['amount'],
                                    'date': datetime.datetime.now()
                                }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        # trigger email sending if the user is transacting with a flagged recipient
                        send_notification_mail.delay(target_mail=request.user.email, message=f"Transaction Failed, {user_recipient.email} is flagged.")
                        return Response({'error':f"Transaction Failed, {user_recipient.email} is flagged."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error':'Insufficient account balance'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error':'Recipient does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        #raise
        return Response({'error':'something went wrong, try again later'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdrawal(request):
    user = request.user
    newuser = User.objects.latest('date_created')
    latest_transaction_time = user.last_transaction_time

    # trigger email sending if transaction amount is greater than 5000000
    if int(request.data['amount']) > 5000000:
        send_notification_mail.delay(target_mail=request.user.email, message='Withdrawal amount is greater than 5000000')

    # trigger email sending if the user is a new user
    if request.user.email == newuser.email:
        send_notification_mail.delay(target_mail=request.user.email, message='Welcome New user, enjoy your first transaction')

    # trigger email sending if transaction amount is above tier limit
    if request.user.transaction_tier.amount < int(request.data['amount']):
        send_notification_mail.delay(target_mail=request.user.email, message='You cannot do transaction above Tier limit')
    

    try:
        with transaction.atomic():
            if user.account_balance > 0 and user.account_balance >= int(request.data['amount']):
                user.account_balance-=int(request.data['amount'])
                #user.last_transaction_time = now1
                user.save()
                instance = Transaction(
                            user=request.user,
                            transaction_type = 'Withdrawal',
                            transaction_ref = now + str(random.randint(1000, 9999)),
                            amount = request.data['amount'],
                            narration = f"{user.email} withdraws {request.data['amount']}",
                            device_signature = request.META['HTTP_USER_AGENT'],
                            ip_address =  get_client_ip(request),
                        )
                instance.save()
                
                # Trigger email sending if Transaction  occurs within a timing window of less than 1 minute
                transaction_time_diff = now1 - latest_transaction_time
                transaction_time_diff_minutes = transaction_time_diff.total_seconds() / 60
                if transaction_time_diff_minutes < 1:
                    send_notification_mail.delay(target_mail=request.user.email, message='Transaction interval is less than 1 minute')

                data = {
                            'transaction_type':'Withdrawal',
                            'user': request.user.email,
                            'amount': request.data['amount'],
                            'date': datetime.datetime.now()
                        }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'error':'Insufficient account balance'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        raise
        return Response({'error':'something went wrong, try again later'}, status=status.HTTP_400_BAD_REQUEST)

