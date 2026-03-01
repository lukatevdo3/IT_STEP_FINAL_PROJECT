from django.urls import path
from . import views

urlpatterns = [
    path('', views.SearchPage.as_view(), name='index'),
    path('routes/', views.TrainPage.as_view(), name='routes'),
    path('tickets/', views.TicketPage.as_view(), name='tickets'),
    path('tickets/user_info/', views.UserPage.as_view(), name='user'),
    path('tickets/user_info/payment/', views.PaymentPage.as_view(), name='payment'),
    path('tickets/user_info/payment/payment_info/', views.PaymentInfoPage.as_view(), name='payment-info'),
    path('info/', views.ViewAndReturnPage.as_view(), name='info'),
]
