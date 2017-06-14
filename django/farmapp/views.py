from django.shortcuts import render, HttpResponseRedirect
from .forms import LoginForm, SignUpForm,CartForm, AnalyticsForm
from farmapp.models import User,Produce,Machine,Trough,Inventory,Crop,Cart,Cart_session,Order
from django.views.decorators.cache import cache_control
from django.db.models import Sum,Count
from django.db.models import F, Q
from graphos.sources.model import ModelDataSource
from django.db import transaction
from graphos.sources.simple import SimpleDataSource


from graphos.renderers.morris import DonutChart, BarChart, AreaChart
from django.template.defaulttags import register

import datetime


@register.filter
def get_item(dictionary, key):
    print(key)
    print(type(key))
    return dictionary.get(key)

@register.filter
def get_list_item(list, key):
    return list[key]

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def index(request):
    loginform = LoginForm()
    signupform = SignUpForm()
    if request.session.get('logged_in', False):
        if request.session.get('user_type', "") == "Producer":
            return HttpResponseRedirect('/producer/home/')
        else:
            return HttpResponseRedirect('/home/')
    return render(request, 'index.html', {'loginform': loginform, 'signupform': signupform, 'page': 'index'})


def home(request):
    if request.session.get("logged_in", False) and request.session.get('user_type', "").upper() != "PRODUCER":
        if request.session.get('cart_id', False):
            if request.session.get('page',False):
                return HttpResponseRedirect(request.session['page'])
            else:
                return HttpResponseRedirect('/crops')
        else:
            return HttpResponseRedirect('/crops')
    return HttpResponseRedirect('/')


def logout(request):
    if request.session.get('cart_id',False):
        user = User.objects.get(user_id = request.session['user_id'])
        user.last_cart = Cart.objects.get(cart_id = request.session['cart_id'])
        user.save()
        request.session.flush()

        # request.session['cart_id'] = cart_id
        # request.session['cart_count'] = cart_count
        return HttpResponseRedirect('/')
    request.session.flush()
    return HttpResponseRedirect('/')


def login(request):
    print("In LOGIN")
    print(request.session.get("logged_in", False))
    if request.session.get('logged_in', False):
        if request.session.get('user_type', "").upper() == "PRODUCER":
            return HttpResponseRedirect('/producer/home/')
        else:
            return HttpResponseRedirect('/home/')
    if request.method == "POST":
        if request.POST.get("login", ""):
            loginform = LoginForm(request.POST)
            if loginform.is_valid():
                print(loginform.cleaned_data)
                try:
                    user = User.objects.get(email=loginform.cleaned_data['email'], password=loginform.cleaned_data['password'])
                    request.session['logged_in'] = True
                    request.session['user_id'] = user.user_id
                    request.session['email'] = user.email
                    request.session['user_type'] = user.user_type
                    if request.session['user_type'] == "Producer":
                        print("A Producer Logged In")
                        return HttpResponseRedirect('/producer/home/')
                    else:
                        print("A Consumer Logged In")
                        cart = Cart.objects.get(cart_id=user.last_cart.cart_id)
                        print(user.last_cart.cart_id)
                        if request.session.get('cart_id',False):
                            user.last_cart = cart
                            user.save()
                        else:
                            request.session['cart_id'] = cart.cart_id

                        return HttpResponseRedirect('/home/')
                except Exception as e:
                    print(e)
        elif request.POST.get("signup", ""):
            signupform = SignUpForm(request.POST)
            print(signupform)
            if signupform.is_valid():
                print(signupform.cleaned_data)
                return HttpResponseRedirect('/home/')
        else:
            print(request.POST)
    return HttpResponseRedirect('/')


def producer_home(request):
    if request.session.get('logged_in', False) and request.session.get('user_type', "").upper() == "PRODUCER":
        user = User.objects.get(pk=request.session['user_id'])
        machines = Machine.objects.filter(user_id=user)
        produce = list(Produce.objects.filter(machine_id__in=machines))

        print(produce)
        return render(request, 'producer.html', {'page': "home", 'produce': produce})
    return HttpResponseRedirect('/')


def producer_inventory(request):
    if request.session.get('logged_in', False) and request.session.get('user_type', "").upper() == "PRODUCER":
        user = User.objects.get(pk = request.session['user_id'])
        inventory = Inventory.objects.filter(user_id = user)
        return render(request, 'producer_inventory.html', {'page': "inventory",'inventory':inventory})
    return HttpResponseRedirect('/')


def about(request):
    loginform = LoginForm()
    signupform = SignUpForm()
    request.session['page'] = '/about'

    if request.session.get('logged_in', False) and request.session.get('user_type', "").upper() == "CONSUMER":
        context = {'page': 'about'}
        return render(request, 'login/about.html', context)
    else:
        context = {'loginform': loginform, 'signupform': signupform, 'page': 'about'}
        return render(request, 'about.html', context)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def crops(request):
    loginform = LoginForm()
    signupform = SignUpForm()
    request.session['page'] = "/crops"
    if request.session.get('cart_id',False):
        cart = Cart.objects.get(cart_id = request.session['cart_id'])
        cart_items = Cart_session.objects.filter(cart_id = cart)
        id=[]
        print(cart_items)
        for crop in cart_items:
            id.append(crop.crop_id.crop_id)
        print(id)
        added_crops = Crop.objects.filter(crop_id__in=id).order_by('-availability')
        request.session['cart_count'] = added_crops.count()

        crops = Crop.objects.exclude(crop_id__in = id).order_by('-availability')
        print(crops)

    else:
        crops = Crop.objects.all().order_by('-availability')
        added_crops = []
    if request.session.get('logged_in', False) and request.session.get('user_type', "").upper() == "CONSUMER":
        context = {'page':'home','crops': crops,'added_crops': added_crops}
        return render(request, 'login/shop.html', context)
    else:
        context = {'loginform': loginform, 'signupform': signupform, 'page': 'crops', 'crops': crops,'added_crops': added_crops}
        return render(request, 'shop.html', context)

def add_to_cart(request,crop_id):
    try:
        input_crop = Crop.objects.get(crop_id = crop_id)
        cart_session = Cart_session()
        if request.session.get('cart_id', False):
            cart = Cart.objects.get(cart_id = request.session['cart_id'])
            cart_session.cart_id = cart
        else:
            cart = Cart.objects.create()
            cart_session.cart_id = cart
            request.session['cart_id'] = cart.cart_id
        print(request.session['cart_id'])
        cart_session.crop_id = input_crop
        cart_session.save()
        # cart_items = Cart_session.objects.filter(cart_id = cart_session.cart_id)
        # id=[]
        # print(cart_items)
        # for crop in cart_items:
        #     id.append(crop.crop_id.crop_id)
        # print(id)
        # added_crops = Crop.objects.filter(crop_id__in=id).order_by('-availability')
        # crops = Crop.objects.exclude(crop_id__in = id).order_by('-availability')
        # print(crops)
        # context = {'loginform': loginform, 'signupform': signupform, 'page': 'crops', 'crops': crops ,'added_crops':added_crops}
        return HttpResponseRedirect('/crops')
    except:
        return HttpResponseRedirect('/crops')

def remove_from_cart(request,crop_id):
    try:
        input_crop = Crop.objects.get(crop_id = crop_id)
        if request.session.get('cart_id',False):
            cart = Cart.objects.get(cart_id = request.session['cart_id'])
            Cart_session.objects.get(cart_id = cart,crop_id = input_crop).delete()

            # cart_count = Cart_session.objects.filter(cart_id = cart).count()
            # if cart_count == 0:
            #     del request.session['cart_id']
            #     del request.session['cart_count']
        return HttpResponseRedirect(request.session['page'])

    except:
        return HttpResponseRedirect(request.session['page'])

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def view_cart(request):
    request.session['page'] = "/cart"
    loginform = LoginForm()
    signupform = SignUpForm()
    cart = Cart.objects.get(cart_id = request.session['cart_id'])
    cart_session = Cart_session.objects.filter(cart_id = cart)

    id=[]
    for crop in cart_session:
        id.append(crop.crop_id.crop_id)
    added_crops = Crop.objects.filter(crop_id__in=id).order_by('-availability')
    request.session['cart_count'] = added_crops.count()
    if request.session['cart_count']==0:
        return HttpResponseRedirect('/crops')
    if request.session.get('logged_in', False) and request.session.get('user_type', "").upper() == "CONSUMER":
        context = {'page':'cart','crops': crops,'cart_session':cart_session}
        return render(request, 'login/cart.html', context)
    else:
        context = {'loginform': loginform, 'signupform': signupform, 'page': 'cart', 'cart_session': cart_session}
        return render(request, 'cart.html', context)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def checkout(request):
    outerlist = {}
    errors = {}
    error_flag =0
    form_values = {}

    if request.method == "POST":
        cart = Cart.objects.get(cart_id=request.session['cart_id'])
        cart_session = Cart_session.objects.filter(cart_id=cart)
        valid_producers = []
        for item in cart_session:
            producers = Inventory.objects.filter(crop_id=item.crop_id, weight__gte=F('minimum'))
            item_errors =[]
            for producer in producers:
                requested_quantity = request.POST.get(producer.user_id.first_name +  str(producer.crop_id.crop_id))
                form_values[producer.user_id.first_name +  str(producer.crop_id.crop_id)] = int(requested_quantity)
                requested_quantity = float(requested_quantity)
                print(requested_quantity)
                if requested_quantity!= 0:
                    if (producer.weight - producer.sold) < requested_quantity and (producer.weight - producer.sold) >= producer.minimum:
                        message = "Sorry "+producer.crop_id.english_name+" is  unavailable as requested quantity of "\
                                  +str(requested_quantity)+"gm is greater than available quantity of "\
                                  +str(producer.weight - producer.sold)+"gm !"
                        form_values[producer.user_id.first_name +  str(producer.crop_id.crop_id)] = 0
                        error_flag =1
                        item_errors.append(message)
                    elif (producer.weight - producer.sold) < producer.minimum:
                        message = "Sorry "+producer.user_id.first_name+" does not have enough "+producer.crop_id.english_name+"!"
                        form_values[producer.user_id.first_name +  str(producer.crop_id.crop_id)] = 0
                        error_flag =1
                        item_errors.append(message)
                    else:
                        valid_producers.append(producer)
            errors[item.crop_id.crop_id] = item_errors
            print("Crop:"+item.crop_id.english_name)
            print("Producers : "+str(valid_producers))
            print("Errors : "+str(errors))
            print(len(errors))
        if error_flag==0:
            with transaction.atomic():
                user = User.objects.get(user_id = request.session['user_id'])
                for producer in valid_producers:
                    requested_quantity = request.POST.get(producer.user_id.first_name + str(producer.crop_id.crop_id))
                    requested_quantity = float(requested_quantity)
                    if requested_quantity != 0:
                        try:
                            Order.objects.create(user_id = user ,\
                                                 cart_id = cart ,\
                                                 crop_id = producer.crop_id ,\
                                                 seller = producer.user_id ,\
                                                 weight = requested_quantity)

                            producer.sold = producer.sold + requested_quantity
                            producer.save()
                        except Exception as e:
                            print(e)

                return HttpResponseRedirect('/order')



    cart = Cart.objects.get(cart_id=request.session['cart_id'])
    cart_session = Cart_session.objects.filter(cart_id=cart)


    for item in cart_session:
        producers = Inventory.objects.filter(crop_id=item.crop_id, weight__gte=F('minimum'))
        item_list = []
        for producer in producers:
            machines = Machine.objects.filter(user_id = producer.user_id)
            row = Produce.objects.filter(machine_id__in = machines, crop_id = producer.crop_id).order_by('-date_of_produce')[0]
            innerlist = []
            innerlist.append(producer.user_id)
            innerlist.append(producer.crop_id)
            innerlist.append(producer.weight - producer.sold)
            innerlist.append(producer.minimum)
            innerlist.append(producer.maximum)
            innerlist.append(row.image)

            quantity = []
            i = int(producer.minimum)
            max = min(int(producer.maximum),int(producer.weight-producer.sold))
            if i<max:
                while i <= max:
                    quantity.append(i)
                    i= i + int(producer.minimum)
                if quantity[len(quantity)-1] != max:
                    quantity.append(max)
            else:
                quantity.append("Unavailable")
            print(quantity)
            innerlist.append(quantity)
            innerlist.append(producer.user_id.first_name + str(producer.crop_id.crop_id))
            item_list.append(innerlist)
            print(quantity)
        outerlist[item.crop_id.crop_id] = item_list
    context = { 'page': 'checkout', 'cart_session': cart_session , 'outerlist':outerlist ,'errors':errors ,'form_values':form_values}
    return render(request,'login/checkout.html',context)

def order_summary(request):
    cart = Cart.objects.get(cart_id=request.session['cart_id'])
    user = User.objects.get(user_id=request.session['user_id'])
    order = Order.objects.filter(user_id = user , cart_id = cart)
    del request.session['cart_id']
    del request.session['cart_count']

    return render(request,'login/order.html',{'order':order})


class TotalProduce(ModelDataSource):
    def get_data(self):
        data = super(TotalProduce, self).get_data()
        header = data[0]
        data_without_header = data[1:]
        for row in data_without_header:
            row[0] = row[0].english_name
            print(row[1])
            row[1] = str(int(round(row[1])))
            print(row[1])
        data_without_header.insert(0, header)
        return data_without_header


def graph(request):
    queryset = Inventory.objects.all()
    chart = DonutChart(TotalProduce(queryset, fields=['crop_id', 'weight']), html_id='graph', options={'formatter':'function(y){return y+" gm"}'})
    context = {'chart': chart}
    return render(request, 'graph.html', context)

def set_to_list(set_of_dict):
    keys = set_of_dict[0].keys()
    list = []
    list.append(tuple(keys))
    for dict in set_of_dict:
        list.append(tuple(dict.values()))
    return list

def analytics(request):
    context = {}
    if request.session.get('logged_in', False) and request.session.get('user_type', "").upper() == "PRODUCER":
        inventory = Inventory.objects.filter(user_id=request.session['user_id'])
        producer_crops = []
        crop_list = []
        for item in inventory:
            producer_crops.append(Crop.objects.get(crop_id=item.crop_id.pk))
        for crop in producer_crops:
            crop_list.append([str(crop.crop_id), crop.english_name])
        print(crop_list)
        form = AnalyticsForm(crop_list=crop_list)
        if request.method == "POST":
            form = AnalyticsForm(request.POST, crop_list=crop_list)
            print(request.POST)
            if form.is_valid():
                print("Printing Data:"+str(form.cleaned_data))
                selected_crops =  Crop.objects.filter(pk__in=form.cleaned_data['crops'])
                data = []
                for crop in selected_crops:
                    try:
                        user = User.objects.get(pk=request.session['user_id'])
                        machines = Machine.objects.filter(user_id=user)
                        object = Produce.objects.filter(machine_id__in=machines, crop_id=crop)\
                            .exclude(date_of_produce__lte=form.cleaned_data['start_date'])\
                            .exclude(date_of_produce__gte=form.cleaned_data['end_date'])
                        print(object)
                        object = object.aggregate(Sum('weight'))
                        print(object)
                        data.append([crop.english_name, object.weight])
                    except Exception as e:
                        print(e)
                        data.append([crop.english_name, 0])
                sorted_data = list(sorted(data, key=lambda data: data[1], reverse=True))
                sorted_data.insert(0,['Crop Name', 'Weight'])
                data = SimpleDataSource(sorted_data)
                chart = BarChart(data, html_id='graph', options={'formatter': 'function(y){return y+" gm"}'})
                context['chart']=chart
            else:
                print("Not Valid")
        context['analyticsform']=form
        return render(request, 'analytics.html', context)
    return HttpResponseRedirect("/")