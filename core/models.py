from django.db import models
from datetime import date, timedelta



class Member(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True)

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=True)  # soft delete
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'date')

    def __str__(self):
        return f"{self.member.name} - {self.date}"

class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    paid_on = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.member.name} - {self.amount}"
    
class GymConfig(models.Model):
    qr_active = models.BooleanField(default=True)
    grace_days = models.IntegerField(default=4)

    def save(self, *args, **kwargs):
        if not self.pk and GymConfig.objects.exists():
            return  # prevent multiple rows
        super().save(*args, **kwargs)

    def __str__(self):
        return "Gym Config"

