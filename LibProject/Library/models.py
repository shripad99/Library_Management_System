from django.db import models


# Create your models here.
class Book(models.Model):
    objects = None
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    publisher = models.CharField(max_length=255)
    num_pages = models.CharField(max_length=255)
    rent_price = models.IntegerField(default=0)


class Member(models.Model):
    objects = None
    name = models.CharField(max_length=255)
    email = models.EmailField()
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Transaction(models.Model):
    objects = None
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issued_date = models.DateField(auto_now_add=True)
    returned_date = models.DateField(null=True, blank=True)
    rent_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expected_return_date = models.DateField()


class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
