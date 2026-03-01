from django.db import models
import uuid

class Train(models.Model):
    '''
    ეს არის მატარებლების ცხრილი რომელშიც იქნება ასახული მატარებლების სახელები თავისი ID მისამართით
    და ეს მისამართები გამოყენებული იქნება შემდეგ ცხრილებში Foreign Key-ს სახით
    '''
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Station(models.Model):
    '''
    ეს არის განრიგებისა და ამავდროულად სადგურების ცხრილი რომელიც გვიჩვენებს შემდეგ მონაცემებს. გამოყენებულია მომხმარებლის
    მიერ თავისი სასურველი სადგურის მოძებნისა და შემდეგ ბილეთის ყიდვისთვის. ეს ცხრილი განაპირობებს რეისების ძებნას
    '''
    from_place = models.CharField(max_length=200)
    to_place = models.CharField(max_length=200)
    day = models.CharField(max_length=50)
    from_time = models.TimeField()
    to_time = models.TimeField()
    train_id = models.ForeignKey(Train, on_delete=models.CASCADE)

    def __str__(self):
        return self.from_place
    

class Seat(models.Model):
    '''
    ეს არის არსებული ადგილების ცხრილი რომელსაც ექნება კონკრეტული მატარებლის უნიკალური ადგილების მონაცემები და გვიჩვენებს არის თუ არა
    ეს ადგილები დაკავებული
    '''
    train_id = models.ForeignKey(Train, on_delete=models.CASCADE)
    wagon_num = models.IntegerField(verbose_name='wagon')
    seat_num = models.IntegerField(verbose_name='seat')
    taken = models.BooleanField(default=False)

class User(models.Model):
    '''
    ეს არის მომხმარებლის მონაცემები რომელიც თვითონ მომხმარებელს შეჰყავს და ჩვენ ამ ყველაფერს ვიღებთ POST მეთოდით
    view ფაილში, შესაბამისი ვალიდაციები დაცულია html ფაილში patter-ების სახით
    '''
    id = models.CharField(primary_key=True, max_length=50)
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    count_tickets = models.IntegerField(default=1)

class Ticket(models.Model):
    '''
    ეს არის ბილეთების ცხრილი რომელიც უკვე ჩამოყალიბებულ ბილეთებს გვიჩვენებს
    ბილეთი შესაძლოა იყოს გადახდილი მოგვიანებით რომელსაც ასევე აქვს თავისი url აპლიკაციაში, ეს ცხრილი აგენერირებს უნიკალურ
    კოდს რომელიც იქნება ბილეთის ხელმისაწვდომი კოდი მომხმარებლისთვის რათა მომხმარებელს რეგისტრაციის გარეშე შეეძლოს ბილეთის 
    დაბრუნება გადახდა თუ ინფორმაციის ნახვა
    '''
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    seat_id = models.ForeignKey(Seat, on_delete=models.CASCADE)
    station_id = models.ForeignKey(Station, on_delete=models.CASCADE)
    travel_date = models.DateField(null=True)
    qr_code = models.CharField(max_length=20, unique=True, blank=True) #blank=True იმიტომ, რომ მომხმარებელმა შეყვანის გარეშე დააგენერიროს თავისი უნიკალური კოდი save()-ის საშუალებით
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            code = str(uuid.uuid4()).replace('-', '')[:7].upper()
            self.qr_code = f'SI-{code}'

        super().save(*args, **kwargs)

class Payment(models.Model):
    '''
    ეს არის უკვე ფიქტიური გადახდის ცხრილი რომლის ვალიდაციებიც ასევე დაცულია html ფაილში
    გამოიყენება მხოლოდ ერთი მიზნისთვის. იმის გამო რომ გვაქვს ფიქტიური გადახდა ფასები და შემდეგი დეტალები
    არ არის გათვალისწინებული ამ აპლიკაციაში
    '''
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    card_num = models.CharField(max_length=100)
    cvv = models.IntegerField()
    date = models.CharField(max_length=10)









    



