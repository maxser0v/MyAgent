from django.shortcuts import render
from .models import *
from django.template import loader
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from collections import Counter
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .parser import (
    convert_price_to_number,
    filter_objects_within_range,
    price_conversion,
    has_numbers,
    parse_controller,
)

# Create your views here.


def parse_all(request):
    password = request.GET.get("password")
    mode = request.GET.get("mode")
    if password == "g7329jd":
        parse_controller(mode)
    return HttpResponse("Invalid Password", 500)


def main(request):
    slider = Slider.objects.filter()[0]
    objects = Property.objects.all()[:6]
    reviews = Reviews.objects.filter()
    gallery = Gallery.objects.filter()[0]
    profile_image = ProfileImage.objects.filter()[0]
    context = {
        "slider_photo": slider,
        "properties": objects,
        "reviews": reviews,
        "gallery": gallery,
        "profile_image": profile_image,
    }
    template = loader.get_template("index.html")
    return HttpResponse(template.render(context, request))


# def get_category(array):
#     category = []
#     for el in array:
#         for cat in el.split(","):
#             category.append(cat.replace(" ", "", 5))
#     category = list(set(category))
#     print(category)


def search_property(request):
    keyword = request.GET.get("keyword")
    property_types = request.GET.getlist("type")
    locations = request.GET.getlist("loc")
    min_price = request.GET.get("minprice")
    max_price = request.GET.get("maxprice")
    developers = request.GET.getlist("developer")
    bedrooms = request.GET.getlist("bed")

    developers_list = list(
        set(Property.objects.values_list("property_developer", flat=True))
    )
    locations_list = list(
        set(Property.objects.values_list("property_location", flat=True))
    )
    type_list = list(
        set(Property.objects.values_list("property_accommodation_type", flat=True))
    )
    # get_category(type_list)
    objects = Property.objects.all()

    if keyword:
        objects = objects.filter(property_name__contains=keyword)
    if min_price:
        objects = objects.filter(property_starting_price_aed__gte=min_price)
    if max_price:
        objects = objects.filter(property_starting_price_aed__lte=max_price)

    q_objects = Q()

    if bedrooms:
        for bedroom in bedrooms:
            q_objects |= Q(property_bed_number__contains=bedroom)

    if developers:
        for developer in developers:
            q_objects |= Q(property_developer__contains=developer)

    if locations:
        for location in locations:
            q_objects |= Q(property_location__contains=location)

    if property_types:
        for prop_type in property_types:
            q_objects |= Q(property_accommodation_type__contains=prop_type)

    if q_objects:
        objects = objects.filter(q_objects)
    # Set the number of items per page
    items_per_page = 6
    paginator = Paginator(objects, items_per_page)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    properties = Property.objects.filter()
    beds = Bed.objects.filter()
    categories = Category.objects.filter()
    gallery = Gallery.objects.filter()[0]
    profile_image = ProfileImage.objects.filter()[0]

    context = {
        "page_obj": page_obj,
        "locations": sorted(locations_list),
        "developers": sorted(developers_list),
        "beds": beds,
        "categories": categories,
        "gallery": gallery,
        "profile_image": profile_image,
    }

    template = loader.get_template("property-list.html")
    return HttpResponse(template.render(context, request))


def search(request):
    keyword = request.GET.get("keyword")
    property_types = request.GET.getlist("type")
    property_status = request.GET.getlist("status")
    locations = request.GET.getlist("loc")
    min_price = float(request.GET.get("minprice"))
    max_price = float(request.GET.get("maxprice"))
    developers = request.GET.getlist("developer")
    bedrooms = request.GET.getlist("bed")

    developers_list = list(
        set(Property.objects.values_list("property_developer", flat=True))
    )
    locations_list = list(
        set(Property.objects.values_list("property_location", flat=True))
    )
    type_list = list(
        set(Property.objects.values_list("property_accommodation_type", flat=True))
    )

    print(type_list)

    objects = Property.objects.all()

    if keyword:
        objects = objects.filter(property_name__contains=keyword)

    q_objects = Q()

    if property_status:
        for status in property_status:
            q_objects |= Q(property_type__contains=status)

    if bedrooms:
        for bedroom in bedrooms:
            q_objects |= Q(property_bed_number__contains=bedroom)

    if developers:
        for developer in developers:
            q_objects |= Q(property_developer__contains=developer)

    if locations:
        for location in locations:
            q_objects |= Q(property_location__contains=location)

    if property_types:
        for prop_type in property_types:
            q_objects |= Q(property_accommodation_type__contains=prop_type)

    if q_objects:
        objects = objects.filter(q_objects)

    objects = filter_objects_within_range(min_price, max_price, objects)
    # Set the number of items per page
    items_per_page = 6
    paginator = Paginator(objects, items_per_page)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    properties = Property.objects.filter()
    context = {
        "page_obj": page_obj,
        "locations": locations_list,
        "developers": developers_list,
    }

    template = loader.get_template("search.html")
    return HttpResponse(template.render(context, request))


def show_property(request):
    id = request.GET.get("id")
    project = Property.objects.get(id=id)
    amenities = project.property_amenities.split("^")
    description = project.property_description.split("^")
    location = project.property_location_description.split("^")
    payment_plan = project.property_payment_plan.split("^")
    highlights = project.property_highlights.split("^")
    units = project.property_units.split("^")
    gallery = Gallery.objects.filter()[0]
    profile_image = ProfileImage.objects.filter()[0]
    context = {
        "property": project,
        "amenities": amenities,
        "description": description,
        "location": location,
        "payment": payment_plan,
        "highlights": highlights,
        "units": units,
        "gallery": gallery,
        "profile_image": profile_image,
    }
    template = loader.get_template("property.html")
    return HttpResponse(template.render(context, request))


def custom_404(request, exception):
    print(exception)
    context = {}
    template = loader.get_template("404.html")
    return HttpResponse(template.render(context, request))
