from __future__ import unicode_literals
from django.shortcuts import render, redirect ,HttpResponse
from .models import *
from django.contrib import messages
import re
import bcrypt
from datetime import date
import time


############ REGEX #####################

NAME_REGEX = re.compile(r'^[a-zA-z]')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
PASSWORD_REGEX = re.compile(r'^((?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,15})')

############ Login/Registration Page ##############
def register_login(request):
    if "user" in request.session:
        del request.session['user']
    return render(request,"belt_exam2_app/login_register.html")
    

########## Register Validation ############
def register(request):
    if request.method == 'POST':
        if 'register' in request.POST:
            is_valid = True
            if len(request.POST['fname']) < 2 or not NAME_REGEX.match(request.POST['fname']):
                messages.error(request, "First Name must contain at least two letters and contain only letters")
                is_valid = False
            if len(request.POST['lname']) < 2 or not NAME_REGEX.match(request.POST['lname']):
                messages.error(request, "Last Name must contain at least two letters and contain only letters")
                is_valid = False
            if not EMAIL_REGEX.match(request.POST['email']):
                messages.error(request, "Invalid email address")
                is_valid = False
            if User.objects.filter(email=request.POST['email']).exists()==True:
                messages.error(request, "Email address is already Taken")
                is_valid = False
            if not PASSWORD_REGEX.match(request.POST['pw']):
                messages.error(request, "Password must contain a number, a capital letter, and at least 8-15 characters")
                is_valid = False
            if request.POST['pw'] != request.POST['pwc']:
                messages.error(request, "Passwords need to match")
                is_valid = False
            
            if is_valid:
                new_fname = request.POST['fname']
                new_lname = request.POST['lname']
                new_email = request.POST['email']
                new_pw = request.POST['pw']
                hash1 = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
                new_user = User.objects.create(first_name = new_fname, last_name = new_lname, email = new_email, password = hash1.decode())
                messages.success(request, "Successfully created your account!")
                return redirect('/')

            else:
                return redirect('/')

############## Login validation #########
def login(request):
    if request.method == "POST":
        if 'login' in request.POST:
            if User.objects.filter(email=request.POST['login_email']).exists()==False:
                messages.error(request, "Email doesn't exist")
                return redirect('/')
            else:
                user = User.objects.get(email = request.POST['login_email'])
                if bcrypt.checkpw(request.POST['login_pw'].encode(), user.password.encode()) == False:
                    messages.error(request, "Wrong Password")
                    return redirect('/')
                else:
                    request.session['user'] = user.id
                    return redirect('/dashboard')

############# Dashboard ##############
def dashboard(request):
    if not 'user' in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id = request.session['user'])
        trips = Trip.objects.all()
        context = {
            'user': user,
            'trips': trips,
        }
        return render(request, 'belt_exam2_app/dashboard.html', context)

########### Create Trip Page #############
def new_trip(request):
    if not 'user' in request.session:
        return redirect('/')
    else:

        context = {

        }
        return render(request, 'belt_exam2_app/new_trip.html', context)

######### New trip process / validations ###########
def create_trip(request):
    is_valid = True

    if len(request.POST['dn']) < 3:
        messages.error(request, "Destination should be at least 3 characters.")
        is_valid = False

    if len(request.POST['plan']) < 3:
        messages.error(request, "Plan should be at least 3 characters.")
        is_valid = False
    
    current = date.today()
    current = current.strftime("%Y-%m-%d")
    start_date = request.POST['sd']

    if current > start_date:
        messages.error(request, "Time travel is not allowed")
        is_valid = False

    a = request.POST['sd']
    b = request.POST['ed']
    if a > b:
        messages.error(request, "Start Date should be past than End Date")
        is_valid = False
    
    if is_valid == True:
        if request.method == 'POST':
            if 'submit' in request.POST:
                new_dn = request.POST['dn']
                new_sd = request.POST['sd']
                new_ed = request.POST['ed']
                new_plan = request.POST['plan']
                user = User.objects.get(id = request.session['user'])
                new_trip = Trip.objects.create(destination = new_dn, start_date = new_sd, end_date = new_ed, plan = new_plan, posted_by = user)
            return redirect('/dashboard')
    else:
        return redirect('/trips/new')

############ Trip Delete ###########
def delete_trip(request, id):
    this_trip = Trip.objects.get(id = id)
    this_trip.delete()
    return redirect('/dashboard')

########### Edit Page ###############
def edit_trip(request, id):
    if not 'user' in request.session:
        return redirect('/')
    else:
        this_trip = Trip.objects.get(id = id)
        user = User.objects.get(id = request.session['user'])
        context = {
            'user': user,
            'trip':this_trip,
        }

        return render(request, 'belt_exam2_app/edit_trip.html', context)

############# Edit process ##############
def edit_trip_process(request, id):
    is_valid = True
    if len(request.POST['edit_dn']) < 3 or len(request.POST['edit_plan']) < 3:
        messages.error(request, "Destination and Plan should be at least 3 characters.")
        is_valid = False

    current = date.today()
    current = current.strftime("%Y-%m-%d")
    start_date = request.POST['edit_sd']

    if current > start_date:
        messages.error(request, "Time travel is not allowed")
        is_valid = False

    a = request.POST['edit_sd']
    b = request.POST['edit_ed']
    if a > b:
        messages.error(request, "Start Date should be past than End Date")
        is_valid = False

    if is_valid == True:
        if request.method == 'POST':
            if 'edit' in request.POST:
                new_dn = request.POST['edit_dn']
                new_sd = request.POST['edit_sd']
                new_ed = request.POST['edit_ed']
                new_plan = request.POST['edit_plan']
                this_trip = Trip.objects.get(id = id)
                this_trip.destination = new_dn
                this_trip.start_date = new_sd
                this_trip.end_date = new_ed
                this_trip.plan = new_plan
                this_trip.save()
            return redirect('/dashboard')
    else:
        return redirect(f'/trips/edit/{id}')

####### Join/unjoin the trip #######
def join_trip(request,id):
    user = request.session['user']
    this_trip = Trip.objects.get(id = id)
    this_trip.joined_user.add(user)
    return redirect('/dashboard')

def unjoin_trip(request,id):
    user = request.session['user']
    this_trip = Trip.objects.get(id = id)
    this_trip.joined_user.remove(user)
    return redirect('/dashboard')

def trip_info(request,id):
    if not 'user' in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id = request.session['user'])
        this_trip = Trip.objects.get(id = id)
        context = {
            'trip': this_trip,
            'user': user,
        }
        return render(request, 'belt_exam2_app/trip_info.html', context)