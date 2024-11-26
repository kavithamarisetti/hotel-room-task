from django.db import models 
from django.contrib.auth.models import User
 # Create your models here. 

class Room(models.Model): 
  ROOM_TYPES = [ ('Single', 'Single'), ('Double', 'Double'), ('Suite', 'Suite'), ] 
  room_number = models.CharField(max_length=10, unique=True) 
  type = models.CharField(max_length=10, choices=ROOM_TYPES) 
  price = models.DecimalField(max_digits=10, decimal_places=2) 
  
  def _str(self): 
     return f"{self.room_number} - {self.type} (${self.price})" 
  
class Booking(models.Model): 
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings') 
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    check_in_date = models.DateField() 
    check_out_date = models.DateField() 
    class Meta: 
        unique_together = ('room', 'check_in_date', 'check_out_date') 
    def __str_(self): 
       return f"Booking by {self.user} for {self.room} from {self.check_in_date} to {self.check_out_date}"
    
