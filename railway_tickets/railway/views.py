from django.shortcuts import render,redirect
from django.views.generic import ListView, FormView, View
from .models import Station, Seat, User, Ticket, Payment
from datetime import datetime, date
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm 
from django.contrib import messages
from django import forms
import re

class SearchPage(View):
    '''
    '''
    def get(self, request, *args, **kwargs):
        from_place = request.GET.get('from_place')
        to_place = request.GET.get('to_place')
        day = request.GET.get('day')
        

        if from_place and to_place and day:
            weekday = datetime.strptime(day, '%Y-%m-%d').strftime('%A') # აგენერირებს კვირის დღეს რომელსაც მივიღებთ კონკრეტული თარიღიდან
            return redirect(f"{reverse_lazy('routes')}?from_place={from_place}&to_place={to_place}&day={weekday}&travel_date={day}") ###

        return render(request, 'railway_tickets/index.html', {'today': date.today().strftime('%Y-%m-%d')})
    
class TrainPage(ListView):
    '''
    '''
    model = Station
    context_object_name = 'stations'
    template_name = 'railway_tickets/trains_page.html'

    def get(self, request, *args, **kwargs):
        from_place = request.GET.get('from_place')
        to_place = request.GET.get('to_place')
        day = request.GET.get('day')
        travel_date = request.GET.get('travel_date') ###

        stations = Station.objects.filter(from_place = from_place.strip().title(), to_place = to_place.strip().title(), day = day.strip().title())

        return render(request, 'railway_tickets/trains_page.html', {'stations' : stations, 'travel_date' : travel_date}) ###
    
    def post(self, request, *args, **kwargs):
        train_id = request.POST.get('train_id')
        station_id = request.POST.get('station_id')
        count = request.POST.get('count')
        travel_date = request.POST.get('travel_date') ###
        return redirect(f"{reverse_lazy('tickets')}?train_id={train_id}&station_id={station_id}&count={count}&travel_date={travel_date}")


class TicketPage(ListView):
    '''
    '''
    model = Seat
    template_name = 'railway_tickets/trains_tickets_page.html'
    context_object_name = 'seats'

    def get_queryset(self):
        train_id = self.request.GET.get('train_id')
        return Seat.objects.filter(train_id = train_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        train_id = self.request.GET.get('train_id')
        station_id = self.request.GET.get('station_id')
        travel_date = self.request.GET.get('travel_date') ###
        count = int(self.request.GET.get('count', 1))
        context['count'] = count
        context['travel_date'] = travel_date
        context['count_range'] = range(count)
        context['station'] = Station.objects.get(id=station_id)
        context['wagons'] = Seat.objects.filter(train_id=train_id).values('wagon_num').distinct()
        context['seats'] = Seat.objects.filter(train_id=train_id)
        taken_seat_ids = list(Ticket.objects.filter(station_id=station_id, travel_date = travel_date, paid=True).values_list('seat_id', flat=True)) ###
        selected_seats = self.request.session.get('selected_seats', [])
        taken_seat_ids += selected_seats
        context['taken_seat_ids'] = list(taken_seat_ids)
        return context
    
    def post(self, request, *args, **kwargs):
        seat_id = request.POST.get('seat_id')
        train_id = request.POST.get('train_id')
        station_id = request.POST.get('station_id')
        travel_date = request.POST.get('travel_date') ###
        count = int(request.POST.get('count', 1))
        count -= 1

        selected_seats = request.session.get('selected_seats', [])
        selected_seats.append(int(seat_id))
        request.session['selected_seats'] = selected_seats

        seat = Seat.objects.get(id=seat_id)
        seat.taken = True
        seat.save()
        if count > 0:
            return redirect(f"{reverse_lazy('user')}?seat_id={seat_id}&station_id={station_id}&train_id={train_id}&count={count}&travel_date={travel_date}") ###
        else:
            request.session['selected_seats'] = []
            return redirect(f"{reverse_lazy('user')}?seat_id={seat_id}&station_id={station_id}&train_id={train_id}&count=0&travel_date={travel_date}") ###

    

class UserPage(View):
    template_name = 'railway_tickets/trains_tickets_trains.html'

    def get(self, request, *args, **kwargs):
        seat_id = request.GET.get('seat_id')
        station_id = request.GET.get('station_id')
        train_id = request.GET.get('train_id')
        travel_date = request.GET.get('travel_date') ###
        count = int(request.GET.get('count', 0))
        seat = Seat.objects.get(id=seat_id)
        station = Station.objects.get(id=station_id)
        return render(request, 'railway_tickets/trains_tickets_user.html', {'seat' : seat, 'station': station, 'train_id' : train_id, 'count' : count, 'travel_date' : travel_date}) ###
    
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone-number')
        seat_id = request.POST.get('seat_id')
        station_id = request.POST.get('station_id')
        train_id = request.POST.get('train_id')
        travel_date = request.POST.get('travel_date') ###
        count = int(request.POST.get('count', 0))

        

        seat = Seat.objects.get(id=seat_id)
        station = Station.objects.get(id=station_id)
        user = User.objects.create(id=id, name=name, surname=surname, email=email, phone_number=phone_number)
        user.save()

        ticket = Ticket.objects.create(user_id=user, seat_id=seat, station_id=station, travel_date=travel_date) ###

        #ეს გვეხმარება რომ მოვითხოვოთ უკვე დაკავებული ადგილები და დაავამატოთ ახალი იმ შემთხვევაში თუ ახალი შეიქმნა და ეს ადგილი არ არის დაკავებული
        ticket_ids = request.session.get('ticket_ids', [])
        ticket_ids.append(ticket.id)
        request.session['ticket_ids'] = ticket_ids

        
        if count > 0:
            return redirect(f"{reverse_lazy('tickets')}?train_id={train_id}&station_id={station_id}&count={count}&travel_date={travel_date}")
        else:
            ticket_ids_str = ','.join(str(id) for id in ticket_ids) #აერთებს ბილეთების ID-ებს 
            request.session['ticket_ids'] = []
            return redirect(f"{reverse_lazy('payment')}?ticket_ids={ticket_ids_str}")
        
    

class PaymentPage(View):
    template_name = 'railway_tickets/trains_tickets_payments.html'

    def get(self, request, *args, **kwargs):
        ticket_ids = request.GET.get('ticket_ids').split(',')
        ticket = Ticket.objects.get(id=ticket_ids[0])  # უბრალოდ რომ გამოისახოს
        return render(request, 'railway_tickets/trains_tickets_payments.html', {'ticket': ticket, 'ticket_ids': request.GET.get('ticket_ids')})
        
    def post(self, request, *args, **kwargs):        
        card_number = request.POST.get('card-number')
        cvv = request.POST.get('cvv')
        date = request.POST.get('date')
        ticket_ids = request.POST.get('ticket_ids').split(',')# რომ მივიღოთ ორი ID რომელიც იქნება გადახდილი ერთი ბარათით

        for ticket_id in ticket_ids:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.paid = True
            ticket.save()
            payment = Payment.objects.create(card_num=card_number, cvv=cvv, date=date, user_id=ticket.user_id)
            payment.save()
        
        return redirect(f"{reverse_lazy('payment-info')}?ticket_ids={request.POST.get('ticket_ids')}")
    
class PaymentInfoPage(View):
    template_name = 'railway_tickets/payment_info_page.html'

    def get(self, request, *args, **kwargs):
        ticket_ids = request.GET.get('ticket_ids').split(',')
        tickets = Ticket.objects.filter(id__in=ticket_ids)
        user = tickets.first().user_id
        return render(request, 'railway_tickets/payment_info_page.html', {'tickets' : tickets, 'user' : user})

class ViewAndReturnPage(View):
    template_name = 'railway_tickets/return_page.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'railway_tickets/return_page.html')

    def post(self, request, *args, **kwargs):
        qr_code = request.POST.get('qr-code')
        id_num = request.POST.get('id')
        submit = request.POST.get('button')

        if not Ticket.objects.filter(qr_code=qr_code).exists():
            return render(request, 'railway_tickets/return_page.html', {'error': 'Please enter a correct QR code'})
        
        if not User.objects.filter(id=id_num).exists():
            return render(request, 'railway_tickets/return_page.html', {'error': 'Please enter a correct phone number'})

        ticket = Ticket.objects.get(qr_code=qr_code)
        user = User.objects.get(id=id_num)

        if submit == 'return':
            if ticket.paid:
                return render(request, 'railway_tickets/return_page.html', {'ticket': ticket, 'user': user, 'show_return_modal': True})                           
            else:
                messages.error(request, 'This ticket has not been paid yet!')
                return render(request, 'railway_tickets/return_page.html')
        elif submit == 'information':
            if ticket.paid:
                return render(request, 'railway_tickets/return_page.html', {
                    'ticket': ticket,
                    'user': user,
                    'show_modal': True
                })
            else:
                return render(request, 'railway_tickets/return_page.html')
        elif submit == 'pay':
            if ticket.paid:
                messages.error(request, 'This ticket has already been paid!')
                return render(request, 'railway_tickets/return_page.html')
            else:
                return redirect(f"{reverse_lazy('payment')}?ticket_ids={ticket.id}")
        elif submit == 'confirm_return':
            ticket = Ticket.objects.get(qr_code=request.POST.get('qr-code'))
            user = User.objects.get(id=request.POST.get('id'))
            user.delete()
            messages.success(request, 'Ticket successfully returned!')
            return redirect('index')

                

        





    

    
        

        



    
    



    
