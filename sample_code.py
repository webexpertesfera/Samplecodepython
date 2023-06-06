from django.views.generic.base import View
from django.shortcuts import render, redirect
from .. import forms
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.core import mail
from .functions import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
import os
class addSalon(View):
    @method_decorator(login_required(login_url='/admin-signin'))
    def get(self,request):
       service_obj = Services.objects.filter(end_date__isnull =True)
       sub_service_obj = []
       if 'service_id' in request.GET:
           sub_service_obj = SubServices.objects.filter(service_id=request.GET.get('service_id'),end_date__isnull = True) 

       return render(request,'add-salon.html',{'service_obj':service_obj,'sub_service_obj':sub_service_obj})
    
    def post(self,request):
        try:
            form = forms.addsalon_form(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                name_en = form.cleaned_data.get('name_en')
                name_dn = form.cleaned_data.get('name_dn')
                description_en = form.cleaned_data.get('description_en')
                description_dn = form.cleaned_data.get('description_dn')
                address = form.cleaned_data.get('address')
                alternate_address = form.cleaned_data.get('alternate_address')
                payment = request.POST.getlist('payment')
                vat_number = form.cleaned_data.get('vat_number')
                price_level = form.cleaned_data.get('price_level')
                contact_number = form.cleaned_data.get('contact_number')
                latitude = form.cleaned_data.get('latitude')
                longitude = form.cleaned_data.get('longitude')
                image_one = request.FILES.get('image_one')
                image_two = request.FILES.get('image_two')
                image_three = request.FILES.get('image_three')
                password = randomStringFunctionForPw()
                # check user
                user_data = User.objects.filter(email=email).first()
                if user_data:
                    messages.error(request, "Email already registred")
                    return redirect('/salon-listing')
                # Create user
                user_data = User.objects.create_user(email=email,password = password)
                user_data.is_salon=True
                user_data.save()

                # Create Salon
                salonObj = Salon.objects.create(user=user_data,email=email,name_en=name_en,description_en=description_en,name_dn=name_dn,description_dn=description_dn,address=address,alternate_address=alternate_address,price_level=price_level)
                salonObj.image_one = str(settings.BASE_URL)+'/'+uploadTheSalonImages(image_one)
                salonObj.image_two = str(settings.BASE_URL)+'/'+uploadTheSalonImages(image_two)
                salonObj.image_three = str(settings.BASE_URL)+'/'+uploadTheSalonImages(image_three)
                payment_str = ','.join(payment)
                salonObj.payment = payment_str
                salonObj.vat_number = vat_number
                salonObj.contact_number = contact_number
                salonObj.latitude = latitude
                salonObj.longitude = longitude
                salonObj.save()

                # Create services
                service_json = request.POST.get('service_json')
                rows_data = json.loads(service_json)
                for row in rows_data:
                    service_select = row['service_select']
                    subservice_select = row['subservice_select']
                    service_obj = Services.objects.filter(id=service_select).first()
                    if service_obj.service_image:
                        image = service_obj.service_image
                    else:
                        image = ""
                    salonservice_obj = SalonServices.objects.create(salon=salonObj,service=service_obj,service_name_en=service_obj.service_name_en,service_name_dn= service_obj.service_name_dn,service_image=image)
                    for sub_service in subservice_select:

                        subservice_obj = SubServices.objects.filter(id=sub_service ).first()
                        SalonSubServices.objects.create(salon=salonObj,service=salonservice_obj,sub_services=subservice_obj,sub_service_name_dn=subservice_obj.sub_service_name_dn,sub_service_name_en=subservice_obj.sub_service_name_en,service_image=subservice_obj.service_image)
                # Salon timing
                salon_timing = request.POST.get('salon_timing')  
                SalonTiming.objects.create(salon=salonObj,theDaysData=salon_timing)
                
                # Create salon bank detail
                account_name = form.cleaned_data.get('account_name')
                bank_name = form.cleaned_data.get('bank_name')
                bank_address = form.cleaned_data.get('bank_address')
                account_number = form.cleaned_data.get('account_number')
                swift_address = form.cleaned_data.get('swift_address')
                swift_code = form.cleaned_data.get('swift_code')
                intermediary = form.cleaned_data.get('intermediary')
                currency = form.cleaned_data.get('currency')
                salonBankObj = SalonBank.objects.create(salon=salonObj,account_name=account_name,bank_name=bank_name,account_number=account_number,swift_address=swift_address,intermediary=intermediary,currency=currency,bank_address=bank_address,swift_code=swift_code)
                html_message = render_to_string('new_customer_email.html',{'password':password,'email':email})
                plain_message = html_message
                from_email = 'easybookr@gmail.com'
                to = email
                subject = 'Login Details'
                mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
                messages.success(request, "Added Succesfully")
                return redirect('/salon-listing')
            else:
                return render(request,'add-salon.html')
        except Exception as e:
            messages.warning(request, "Something went wrong.Please try again.")
            return redirect('admin-dashboard')