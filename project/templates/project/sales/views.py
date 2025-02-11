from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import *  # ต้องนำเข้าโมเดลที่เกี่ยวข้อง
from django.contrib.auth.models import User
import re
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django_ratelimit.decorators import ratelimit
from .forms import *
from django.db import IntegrityError
from django.db.models import Sum, Count


def home(request):
    return render(request, "sales/home.html")


def is_valid_email(email):
    """Simple regex-based email validation"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# def register(request):
#     context = {}

#     if request.method == "POST":
#         data = request.POST.copy()
#         name = data.get("name", "").strip()
#         email = data.get("email", "").strip()
#         password = data.get("password", "").strip()

#         # Check if all required fields are filled
#         if not name or not email or not password:
#             messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วน")
#             return render(request, "sales/register.html", context)

#         # Validate email format
#         if not is_valid_email(email):
#             messages.error(request, "กรุณากรอกอีเมล์ให้ถูกต้อง")
#             return render(request, "sales/register.html", context)

#         # Check if user exists
#         if User.objects.filter(username=email).exists():
#             messages.error(request, "อีเมล์นี้ถูกใช้งานไปแล้ว กรุณาใช้ที่อยู่อีเมล์อื่น")
#             return render(request, "sales/register.html", context)

#         # Create new user
#         new_user = User.objects.create_user(
#             username=email, first_name=name, email=email, password=password
#         )

#         # Create user profile
#         customuser = CustomUser.objects.create(user=new_user)
#         customuser.save()

#         messages.success(request, "สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
#         return redirect("login-page")  # Redirect to login page

#     return render(request, "sales/register.html", context)


def register(request):

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Extract cleaned data
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Create new user
            try:
                new_user = User.objects.create_user(
                    username=email, first_name=name, email=email, password=password
                )
                customuser, created = CustomUser.objects.get_or_create(user=new_user)
                if created:
                    customuser.save()
                messages.success(request, "สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
                return redirect("login-page")  # Redirect to login page
            except IntegrityError:
                messages.error(request, "อีเมล์นี้ถูกใช้งานไปแล้ว กรุณาใช้ที่อยู่อีเมล์อื่น")
                return render(request, "sales/register.html", {"form": form})
        else:
            # Form is invalid, render the form with errors
            return render(request, "sales/register.html", {"form": form})
    else:
        form = RegistrationForm()
    return render(request, "sales/register.html", {"form": form})


# @ratelimit(key="ip", rate="5/m", block=True)  # Allow 5 login attempts per minute
# def user_login(request):
#     if request.method == "POST":
#         data = request.POST.copy()
#         email = data.get("email", "").strip()
#         password = data.get("password", "").strip()

#         # Validate input
#         if not email or not password:
#             messages.error(request, "กรุณากรอกอีเมล์และรหัสผ่าน")
#             return render(request, "sales/login.html")

#         user = authenticate(request, username=email, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect("home-page")
#         else:
#             messages.error(request, "อีเมล์หรือรหัสผ่านไม่ถูกต้อง!")

#     return render(request, "sales/login.html")


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Authenticate user
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)

                    # Redirect based on user role
                    try:
                        custom_user = CustomUser.objects.get(user=user)
                        if custom_user.user_type == "sales":
                            return redirect("home-page")
                        elif custom_user.user_type == "account":
                            return redirect("sales-dashboard-page")
                        elif custom_user.user_type == "admin":
                            return redirect("sales-dashboard-page")
                    except CustomUser.DoesNotExist:
                        messages.error(request, "โปรไฟล์ผู้ใช้ไม่สมบูรณ์ กรุณาติดต่อผู้ดูแลระบบ")
                        return redirect("login-page")
                else:
                    messages.error(request, "บัญชีของคุณถูกระงับ กรุณาติดต่อผู้ดูแลระบบ")
            else:
                messages.error(request, "อีเมล์หรือรหัสผ่านไม่ถูกต้อง!")
        else:
            # Form is invalid, render the form with errors
            return render(request, "sales/login.html", {"form": form})
    else:
        form = LoginForm()
    return render(request, "sales/login.html", {"form": form})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "คุณได้ออกจากระบบแล้ว")
    else:
        messages.warning(request, "คุณยังไม่ได้เข้าสู่ระบบ")

    return redirect("login-page")


@login_required
def create_sale_record(request):
    if request.method == "POST":
        data = request.POST.copy()
        customer_id = data.get("customer")
        product_id = data.get("product")
        quantity = int(data.get("quantity"))
        transfer_amount = data.get("transfer_amount")
        po_document = request.FILES.get("po_document")
        payment_slip = request.FILES.get("payment_slip")
        remarks = data.get("remarks")
        user = request.user

        try:
            customer = Customer.objects.get(id=customer_id)
            product = Product.objects.get(id=product_id)

            sale_record = SaleRecord.objects.create(
                user=user,
                customer=customer,
                product=product,
                quantity=quantity,
                transfer_amount=transfer_amount,
                po_document=po_document,
                payment_slip=payment_slip,
                remarks=remarks,
            )

            sale_record.save()

            messages.success(request, "บันทึกข้อมูลสำเร็จ!")
            return redirect("orders:list_orders")
        except Customer.DoesNotExist:
            messages.error(request, "ไม่พบลูกค้าในระบบ")
        except Product.DoesNotExist:
            messages.error(request, "ไม่พบสินค้าในระบบ")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")

    customers = Customer.objects.all()
    products = Product.objects.all()

    context = {"customers": customers, "products": products}

    return render(request, "sales/create-sale-record.html", context)


def edit_sale_record(request, sale_id):
    sale_record = get_object_or_404(
        SaleRecord, id=sale_id
    )  # Get sale record or return 404

    if request.method == "POST":
        data = request.POST.copy()
        customer_id = data.get("customer")
        product_id = data.get("product")
        quantity = int(data.get("quantity"))
        transfer_amount = data.get("transfer_amount")
        po_document = request.FILES.get("po_document") or sale_record.po_document
        payment_slip = request.FILES.get("payment_slip") or sale_record.payment_slip
        remarks = data.get("remarks")

        try:
            customer = Customer.objects.get(id=customer_id)
            product = Product.objects.get(id=product_id)

            # Update sale record
            sale_record.customer = customer
            sale_record.product = product
            sale_record.quantity = quantity
            sale_record.transfer_amount = transfer_amount
            sale_record.po_document = po_document
            sale_record.payment_slip = payment_slip
            sale_record.remarks = remarks
            sale_record.save()

            messages.success(request, "อัปเดตข้อมูลสำเร็จ!")
            return redirect("create-sale-record-page")
        except Customer.DoesNotExist:
            messages.error(request, "ไม่พบลูกค้าในระบบ")
        except Product.DoesNotExist:
            messages.error(request, "ไม่พบสินค้าในระบบ")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")

    customers = Customer.objects.all()
    products = Product.objects.all()

    context = {
        "sale_record": sale_record,
        "customers": customers,
        "products": products,
    }

    return render(request, "sales/edit-sale-record.html", context)


@login_required
def table_product(request):
    try:
        # Try to get the CustomUser instance for the current user
        custom_user = CustomUser.objects.get(user=request.user)
        user = request.user  # No need to query the User model again

    except ObjectDoesNotExist:
        # If CustomUser does not exist, return an appropriate response
        return HttpResponse(
            "Unauthorized: CustomUser profile does not exist.", status=401
        )

    # Determine which records the user can access based on their role
    if custom_user.user_type == "sales":
        # Sales can only view their own records
        records = SaleRecord.objects.filter(user=custom_user.user)
    elif custom_user.user_type == "account":
        # Account can view all records and confirm them
        records = SaleRecord.objects.all()
    elif (
        custom_user.user_type == "admin"
        or user.is_staff
        or user.is_superuser
        or user.active
    ):
        # Admin can view all records and edit/confirm them
        records = SaleRecord.objects.all()
    else:
        return HttpResponse("Unauthorized: Invalid user type.", status=401)

    # Prepare context for rendering the template
    context = {
        "records": records,
        "user": user,
        "user_type": custom_user.user_type,  # Optional: Pass user type to the template
    }
    return render(request, "sales/table-product.html", context)


def confirm_sale(request, order_id):
    # Get the SaleRecord instance or return a 404 if not found
    sale_record = get_object_or_404(SaleRecord, id=order_id)

    # Confirm the sale by updating the status
    sale_record.status = "confirmed"  # Change to 'confirmed' as per your status choices
    sale_record.save()

    # Redirect to a page where you want to show the updated order
    return redirect(
        "table-product-page"
    )  # Change to the name of your dashboard or the page to redirect to


def cancel_sale(request, order_id):
    # Get the SaleRecord instance or return a 404 if not found
    sale_record = get_object_or_404(SaleRecord, id=order_id)

    # Cancel the sale by setting the status back to 'pending'
    sale_record.status = "pending"
    sale_record.save()

    # Redirect to a page where you want to show the updated order
    return redirect(
        "table-product-page"
    )  # Change to the name of your dashboard or the page to redirect to


def delete_sale(request, order_id):
    sale_record = get_object_or_404(SaleRecord, id=order_id)
    sale_record.delete()
    return redirect("dashboard-page")  # Or wherever you want to redirect after deletion


@login_required
def customer_list_dashboard(request):
    customers = Customer.objects.all()
    context = {"customers": customers}
    return render(request, "sales/customer-list-dashboard.html", context)


def add_customer(request):
    # if (
    #     not hasattr(request.user, "customuser")
    #     or request.user.customuser.user_type != "admin"
    # ):
    #     return redirect("home-page")
    if request.method == "POST":
        data = request.POST.copy()
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        customer = Customer.objects.create(first_name=first_name, last_name=last_name)

        customer.save()

        messages.success(request, "เพิ่มลูกค้าสำเร็จ")
        return redirect("customer-list-dashboard-page")

    return render(request, "sales/add-customer.html")


def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        data = request.POST.copy()
        customer.first_name = data.get("first_name")
        customer.last_name = data.get("last_name")
        customer.save()

        messages.success(request, "แก้ไขข้อมูลลูกค้าสำเร็จ")
        return redirect(
            "customer-list-dashboard-page"
        )  # Redirect to customer list page

    context = {"customer": customer}
    return render(request, "sales/edit-customer.html", context)


def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer.delete()
        messages.success(request, "ลบลูกค้าสำเร็จ")
        return redirect("customer-list-dashboard-page")

    context = {"customer": customer}
    return render(request, "sales/delete-customer.html", context)


def sales_dashboard(request):
    total_sales = (
        SaleRecord.objects.aggregate(total_amount=Sum("transfer_amount"))[
            "total_amount"
        ]
        or 0
    )
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_orders = SaleRecord.objects.count()

    sales_data = SaleRecord.objects.values("product__name").annotate(
        total_sales=Sum("transfer_amount")
    )

    context = {
        "total_sales": total_sales,
        "total_products": total_products,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "sales_data": list(sales_data),
    }

    return render(request, "sales/sales-dashboard.html", context)
