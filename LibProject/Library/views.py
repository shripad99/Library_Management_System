from django.utils import timezone
from datetime import timedelta, datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Member, Transaction, BookCopy
from .forms import BookForm, MemberForm, TransactionForm
from django.http import JsonResponse
import requests


def import_books_from_api(request):
    api_url = "https://frappe.io/api/method/frappe-library?page=2&title=and"
    print(api_url)

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json().get("message", [])
            print(data)
            for book_data in data:
                book = Book(
                    title=book_data.get("title", ""),
                    authors=book_data.get("authors", ""),
                    isbn=book_data.get("isbn", ""),
                    num_pages=book_data.get("  num_pages", ""),
                    publisher=book_data.get("publisher", "")
                )
                print(book)
                book.save()
            return JsonResponse({"message": "Books imported successfully"})
        else:
            return JsonResponse({"error": "Error fetching data from the API"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})


def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')

    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})


def member_list(request):
    member = Member.objects.all()
    return render(request, 'library/member_list.html', {'member': member})


def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'library/member_form.html', {'form': form})


def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'library/member_form.html', {'form': form})


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return render(request, 'library/book_confirm_delete.html', {'member': member})


def calculate_expected_return_date():
    current_date = timezone.now().date()
    expected_return_date = current_date + timedelta(days=14)
    return expected_return_date


def issue_book(request, book_id, member_id):
    book = get_object_or_404(Book, pk=book_id)
    member = get_object_or_404(Member, pk=member_id)

    if request.method == 'POST':
        transaction_form = TransactionForm(request.POST)
        if transaction_form.is_valid():
            transaction = transaction_form.save(commit=False)
            transaction.book = book
            transaction.member = member
            transaction.expected_return_date = calculate_expected_return_date()
            transaction.save()
            return redirect('book_list')
    else:
        transaction_form = TransactionForm()

    return render(request, 'library/issue_book_form.html', {'transaction_form': transaction_form, 'book': book})


def calculate_rent_fee(issued_date, rent_price, returned_date=None):
    rent_rate_per_day = 10

    if returned_date is None:
        returned_date = timezone.now()

    if not isinstance(issued_date, datetime):
        issued_date = datetime.combine(issued_date, datetime.min.time())
        issued_date = timezone.make_aware(issued_date, timezone.get_current_timezone())

    if not returned_date.tzinfo:
        returned_date = timezone.make_aware(returned_date, timezone.get_current_timezone())

    days_rented = (returned_date - issued_date).days
    rent_fee = days_rented * rent_rate_per_day * rent_price

    return rent_fee


def return_book(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    print("Transaction ID:", transaction.id)
    print("Returned Date (Type):", type(transaction.returned_date))

    if transaction.returned_date:
        transaction.returned_date = timezone.now()
        transaction.rent_fee = calculate_rent_fee(transaction.issued_date, transaction.book.rent_price,
                                                  transaction.returned_date)
        transaction.save()

        book = transaction.book
        book.is_available = True
        book.save()
        return redirect('book_list')
    else:
        return render(request, 'library/return_book_error.html', {'transaction': transaction})


def search_books(request):
    query = request.GET.get('query', '')
    if query:
        books = Book.objects.filter(title__icontains=query) | Book.objects.filter(authors__icontains=query)
    else:
        books = Book.objects.all()
    return render(request, 'library/search_books.html', {'books': books, 'query': query})


def charge_rent_fee(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    overdue_transactions = Transaction.objects.filter(member=member, returned_date__lt=timezone.now())
    total_rent_fee = 0

    for transaction in overdue_transactions:
        if not transaction.rent_fee:
            rent_fee = calculate_rent_fee(transaction.issued_date, transaction.book.rent_price)
            total_rent_fee += rent_fee
            transaction.rent_fee = rent_fee
            transaction.save()
            print(f"Transaction ID: {transaction.id}, Rent Fee: {rent_fee}")

    total_rent_fee = min(total_rent_fee, 500)

    member.outstanding_debt += total_rent_fee
    member.save()

    return render(request, 'library/charge_rent_fees.html', {'member': member, 'total_rent_fee': total_rent_fee})