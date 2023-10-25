import datetime
#from axes.models import AccessAttempt
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from .models import *
from django.shortcuts import  get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
#from rest_framework.authtoken.serializers import AuthTokenSerializer
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
    #user_check = AccessAttempt.objects.get(user=request.data['username'])
    #user_check = get_object_or_404(AccessAttempt, user=request.data['username'])

    #if AccessAttempt.objects.filter(user=request.data['username']).exists():
    try:
        if User.objects.filter(email=request.data['username']).exists():
            user_check = AccessAttempt.objects.get(user=request.data['username'])
            user_check.attempt_count = user_check.attempt_count + 1
            user_check.save()

            if not user and (user_check.attempt_count == 2):
                return Response({'error':'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

            if not user and (user_check.attempt_count >= 3 and user_check.attempt_count < 5):
                return Response({'error':'3 failed login attempts, try again in 3 minutes'}, status=status.HTTP_400_BAD_REQUEST)

            if not user and user_check.attempt_count >= 5:
                return Response({'error':'5 failed login attempts, try again in 5 minutes'}, status=status.HTTP_400_BAD_REQUEST)

            if user:
                login_time_diff = now1 - user_check.time_last_unsuccessful_login
                login_time_diff_minute = login_time_diff.total_seconds() / 60

                print('time-diff',login_time_diff_minute)
                if user_check.attempt_count >= 3 and login_time_diff_minute <= 3:
                    return Response({'error':'3 failed login attempts, try again in 3 minutes'}, status=status.HTTP_400_BAD_REQUEST)
                elif user_check.attempt_count >= 5 and login_time_diff_minute <= 5:
                    return Response({'error':'5 failed login attempts, try again in 5 minutes'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    _, token = AuthToken.objects.create(user)

                    return Response({
                    'id': user.id,
                    'email': user.email,
                    'token':token  
                    })
                    user_check.delete()
                
            #else:
            #    return Response({'error':'Cannot Log In after 5 minutes'}, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response({'error':'Invalid Login Details'}, status=status.HTTP_400_BAD_REQUEST)
    except AccessAttempt.DoesNotExist:
        if user:
            _, token = AuthToken.objects.create(user)
            return Response({
                'id': user.id,
                'email': user.email,
                'token':token  
            })
        else:
            AccessAttempt.objects.create(user = request.data['username'],attempt_count =+ 1)
            return Response({'error':'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
    
        
'''
def timeout(request):
    try:
        loginview = login_api(request)
        username = request.data['username'],
        ip_address = request.axes_ip_address
        account = AccessAttempt.objects.filter(username=username).filter(ip_address=ip_address)
        
        current_time = datetime.datetime.now()
        number_of_attempts = account.failures_since_start
        threshold = (number_of_attempts / 5) * 5
       
        error = {'message':f"Access attempts exceeded. Please wait {threshold} minutes"}
'''        
       # result = AccessAttempt.objects.raw(
        #    '''
        #    SELECT axes_accessattempt.id, login_accessattemptaddons.expiration_date
        #    FROM axes_accessattempt
        #    INNER JOIN login_accessattemptaddons
        #    ON axes_accessattempt.id = login_accessattemptaddons.accessattempt_id
        #    WHERE axes_accessattempt.username = %s and axes_accessattempt.ip_address = %s
       #     ''', #[username, ip_address]
       # )[0]
'''

        if(current_time < result.expiration_date):
            return Response(error)
        else:
            account.delete()
            account_page = loginview.post(request)
            return account_page

    except IndexError:
        expiration_date = current_time + datetime.timedelta(minutes=threshold)
        id = AccessAttempt.objects.filter(username=username, ip_address=ip_address)[0].id
        addons = AccessAttemptAddons(expiration_date=expiration_date, accessattempt_id=id)
        addons.save()
        return Response(error)
'''

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

