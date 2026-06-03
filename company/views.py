from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages as flash
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from .models import Customer
from .forms import CustomerForm

# Create your views here.
def home_view(request):
    return render(request, "company/index.html", {"today": datetime.utcnow()})

def customers_list_view(request):
    q = (request.GET.get("q") or "").strip()        # terme de recherche

    customers = Customer.objects.order_by("-id")     # trier AVANT de paginer
    if q:                                            # on filtre seulement si on a tapé qqch
        customers = customers.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )

    paginator = Paginator(customers, 30)              # 5 clients par page
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "company/customers.html", {"page": page, "q": q})

def customers_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():               # ← remplace tes 5 "if not ..."
            form.save()                   # ← remplace Customer.objects.create(...)
            flash.success(request, "Nouveau client créé ✅")
            return redirect("company.customers")
    else:
        form = CustomerForm()             # GET : formulaire vide

    return render(request, "company/customer_add.html", {"form": form})

def customer_detail_view(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, "company/customer_detail.html", {"customer": customer})

def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    flash.success(request, f"Le client #{id} a été bien supprimé")
    return redirect("company.customers")

def customer_update(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)   # instance = objet à modifier
        if form.is_valid():
            form.save()                                        # UPDATE (pas INSERT)
            flash.success(request, "Client mis à jour ✅")
            return redirect("company.customerDetail", customer.id)
    else:
        form = CustomerForm(instance=customer)                 # GET : pré-rempli

    return render(request, "company/customer_update.html", {"form": form, "customer": customer})