from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RideForm, UserSelectionForm, UserSignUpForm, DriverUserForm
from .models import Ride, DriverUser
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail

USER_TYPES = [('ride owner', 'Ride Owner'), ('ride sharer', 'Ride Sharer'), ('driver', 'Driver')]

def home(request):
    return render(request, "home.html", {})

def request_new_ride(request):
    if not request.user.is_authenticated:
        print("Unable to authenticate user in request")
        return redirect('/users/login/')
    if request.session.get('user_type') != 'ride owner':
        # if the user has not specified a session type, redirect them to the session selection screen
        return redirect('/users/select/')
    form = RideForm(request.POST or None)
    context = {'form': form}
    return render(request, "request_new_ride.html", context)


def ride_selection(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    # if not request.session.get('user_type') == 'ride owner' or not request.session.get('user_type') == 'ride sharer':
    if request.session.get('user_type') != 'ride owner':
        # if the user has not specified a session type, redirect them to the session selection screen
        return redirect('/users/select/')
    print("Here is the user_session_type: {}".format(request.session.get('user_type')))
    # allow selection of any open or confirmed rides for that user (but not COMPLETE rides)
    open_or_confirmed_rides = Ride.objects.filter(rider_owner_user_id=request.user.id).exclude(status='complete')
    context = {'open_or_confirmed_rides': open_or_confirmed_rides}
    return render(request, "ride_selection.html", context)

def ride_detail(request, ride_id):
    selected_ride = Ride.objects.get(id=ride_id)
    selected_driver = DriverUser.objects.get(user__id=selected_ride.driver_user_id)
    context = {'selected_ride': selected_ride, 'selected_driver': selected_driver }
    return render(request, 'ride_detail.html', context)

def ride_sharer_view(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    # if not request.session.get('user_type') == 'ride owner' or not request.session.get('user_type') == 'ride sharer':
    if request.session.get('user_type') != 'ride sharer':
        # if the user has not specified a session type, redirect them to the session selection screen
        return redirect('/users/select/')
    print("Here is the user_session_type: {}".format(request.session.get('user_type')))
    # allow selection of any open or confirmed rides for that user (but not COMPLETE rides)
    open_or_confirmed_rides = Ride.objects.filter(rider_sharer_user_id=request.user.id).exclude(status='complete')
    available_drivers = DriverUser.objects.filter(user=request.user.id)
    context = {'open_or_confirmed_rides': open_or_confirmed_rides, 'available_drivers': available_drivers}
    return render(request, "ride_sharer_view.html", context)


def ride_sharer_search(request):
    # specify destination, arrival window (earliest and latest time for arrival) and number of passengers in our party
    if not request.user.is_authenticated:
        return redirect('/accounts/login')
    if request.session.get('user_type') != 'ride sharer':
        # if the user has not specified a session type, redirect them to the session selection screen
        return redirect('/users/select/')
    if request.method == "POST":
        data = request.POST.copy()
        print("Here are all of the existing rides: {}".format(Ride.objects.all()))
        print("Here is what our data looks like: {}".format(data))
        matching_rides = Ride.objects.filter(destination=data['destination'],
                                             arrival_time__gte=data['arrival_time_start'],
                                             arrival_time__lte=data['arrival_time_end'],
                                             shareable=True,
                                             status='open')
        context = { 'matching_rides': matching_rides }
        return render(request, "ride_sharer_search_results.html", context)
    else:
        return render(request, "ride_sharer_search.html", {})

def ride_sharer_join(request, ride_to_join_id):
    ride_to_share = Ride.objects.filter(id=ride_to_join_id)
    ride_to_share.update(rider_sharer_user_id=request.user.id)
    return redirect("/rides/sharer/view/")

def driver_ride_status_viewing(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    if request.session.get('user_type') != 'driver':
        # if the user has not specified a session type, redirect them to the session selection screen
        messages.error(request, "You must register as a driver before you can search for rides")
        return redirect('/users/select/')
    confirmed_rides = Ride.objects.filter(status='confirmed', driver_user_id=request.user.id)
    print("Here are the confirmed_rides: {}".format(confirmed_rides))
    my_drivers = DriverUser.objects.filter(user=request.user.id) # should only return a single driver, consider reworking HTML display
    context = {'confirmed_rides' : confirmed_rides, 'my_drivers' : my_drivers}
    return render(request, "driver_ride_status_viewing.html", context)


def driver_ride_searching(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    if request.session.get('user_type') != 'driver':
        # if the user has not specified a session type, redirect them to the session selection screen
        messages.error(request, "You must register as a driver before you can search for rides")
        return redirect('/users/select/')
    my_drivers = DriverUser.objects.filter(user=request.user.id) # there should only be one driver found after our query
    available_seats = my_drivers[0].passenger_seats_in_car
    vehicle_type = my_drivers[0].vehicle_model
    rides = Ride.objects.filter(Q(status='open', passengers_requested__lte=available_seats, vehicle_type_requested=vehicle_type) |
                                Q(status='open', passengers_requested__lte=available_seats, vehicle_type_requested="") |
                                Q(status='open', passengers_requested__lte=available_seats, vehicle_type_requested=None)).exclude(rider_owner_user_id=my_drivers[0].user.id)
    print("Here are the existing drivers: {}".format(DriverUser.objects.all()))
    print("Here are the existing rides: {}".format(Ride.objects.all()))
    context = { 'rides' : rides, 'my_drivers' : my_drivers }
    return render(request, "driver_ride_searching.html", context)


def register(request):
    form = UserSignUpForm
    if request.method == "POST":
        form = UserSignUpForm(request.POST or None)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print("User is being saved")
            messages.success(request, "Registration successful.")
            return redirect("/users/login/")
    context = { 'form': form, 'messages': messages }
    return render(request, "register.html", context)


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.info(request, f"Logged in as {username}.")
                return redirect("select_user_session")
            else:
                messages.error(request, "Incorrect Username or Password")
        else:
            messages.error(request, "Incorrect Username or Password")
    form = AuthenticationForm(request, data=request.POST)
    return render(request=request, template_name="login_user.html", context={"login_form": form})


def logout_user(request):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            messages.success(request, "You have successfully logged out")
            logout(request)
        else:
            messages.error(request, "Bad request. Please login again")
    return redirect("/users/login/")



def select_user_session(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    request.session['user_type'] = None # reset the user_type session value
    form = UserSelectionForm(request.POST or None)
    if form.is_valid():
        user_session_type = form.cleaned_data['user_type']
        request.session['user_type'] = user_session_type
        if user_session_type == 'driver':
            my_driver = DriverUser.objects.filter(user=request.user.id)
            if not my_driver:
                # if the user hasn't previously registered as a driver, then make sure that they do so before continuing
                return redirect('/users/register/driver/')
            else:
                return redirect('/rides/driver/view/')
        elif user_session_type == 'ride sharer':
            return redirect('/rides/sharer/view/')
        return redirect('ride_selection')
    context = { 'form' : form }
    return render(request, "select_user_session.html", context)



def new_ride_submit(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/')
    form = RideForm(request.POST or None)
    if form.is_valid():
        new_ride = form.save(commit=False)
        new_ride.rider_owner_user_id = request.user.id
        new_ride.save()
        return redirect('ride_selection')


def driver_registration(request):
    form = DriverUserForm(request.POST or None)
    context = {'form': form}
    if request.method == "POST":
        if form.is_valid():
            new_driver_user = form.save(commit=False)
            new_driver_user.user = request.user
            new_driver_user.save()
            return redirect('/rides/driver/view/')
    return render(request, 'driver_registration.html', context)

def ride_edit(request, ride_edit_id):
    if request.method != "POST":
        ride = Ride.objects.get(id=ride_edit_id)
        ride_form = RideForm(instance=ride)
        context = {'ride_id': ride_edit_id, 'form': ride_form}
        return render(request, 'ride_edit.html', context)
    else:
        # this will be reached when the user presses the save button
        form = RideForm(request.POST or None)
        if form.is_valid():
            existing_ride = Ride.objects.get(id=ride_edit_id)
            ride_form = RideForm(request.POST, instance=existing_ride)
            ride_form.save()
            return redirect('/rides/rider/view/')


def ride_confirm(request, ride_confirm_id):
    ride_to_confirm = Ride.objects.filter(id=ride_confirm_id)
    ride_to_confirm.update(status='confirmed')
    ride_to_confirm.update(driver_user_id=request.user.id)
    ride_details = Ride.objects.get(id=ride_confirm_id)
    rider_owner = User.objects.get(id=ride_details.rider_owner_user_id)
    emails = [rider_owner.email]
    if ride_details.rider_sharer_user_id:
        print("found a ride sharer user id!")
        emails.append(User.objects.get(id=ride_details.rider_sharer_user_id).email)
    driver_details = DriverUser.objects.get(user__id=ride_details.driver_user_id)
    arrival_time = ride_details.arrival_time.strftime("%I:%M %p")
    print("Here are the emails that we will ping: {}".format(emails))

    send_mail(
        'Ride Sharing Service Confirmation',
        f'Hello!\n\n'
        f'Your {arrival_time} trip to {ride_details.destination} with {ride_details.passengers_requested} passengers(s) has been confirmed.\n '
        f'Be on the lookout for a {driver_details.vehicle_model} with license plate number: {driver_details.license_plate_num}\n\n\n'
        f'Please enjoy your ride and stay safe!',
        'suryanshluisece568@gmail.com',
        emails,
        auth_user='suryanshluisece568@gmail.com',
        auth_password='BrianRogersRoxx'
    )
    return redirect("/rides/driver/open/")


def ride_complete(request, ride_complete_id):
    ride_to_complete = Ride.objects.filter(id=ride_complete_id)
    ride_to_complete.update(status='complete')
    messages.info(request, "Ride successfully completed!")
    return redirect("/rides/driver/view/")


def driver_profile_edit(request, driver_id):
    if request.method != "POST":
        existing_driver_profile = DriverUser.objects.get(user__id=driver_id)
        new_driver_form = DriverUserForm(instance=existing_driver_profile)
        context = {'driver_id': driver_id, 'form': new_driver_form}
        return render(request, 'driver_profile_edit.html', context)
    else:
        # this will be reached when the user presses the save button
        form = DriverUserForm(request.POST or None)
        if form.is_valid():
            existing_driver_profile = DriverUser.objects.get(user__id=driver_id)
            new_driver_form = DriverUserForm(request.POST, instance=existing_driver_profile)
            new_driver_form.save()
            return redirect('/rides/driver/view/')

