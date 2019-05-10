from django import forms
from django.forms import formset_factory
from .models import *

class Event_Form(forms.Form):
    title = forms.CharField(label='f_title', max_length=128,
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='f_desc',
                    widget=forms.Textarea(attrs={'class': 'form-control',
                                                 'rows': 5}))
    begin = forms.DateTimeField(label='f_date_start',
                    input_formats=['%d/%m/%Y %H:%M'],
                    widget=forms.TextInput(attrs={'class': 'form-control datetimepicker-input date-pick',
                                 'data-toggle': 'datetimepicker',
                                 'data-target': '#id_begin'}))
    end = forms.DateTimeField(label='f_date_end',
                    input_formats=['%d/%m/%Y %H:%M'],
                    widget=forms.TextInput(attrs={'class': 'form-control datetimepicker-input date-pick',
                                 'data-toggle': 'datetimepicker',
                                 'data-target': '#id_end'}))
    begin_register = forms.DateTimeField(label='f_insc_start',
                    input_formats=['%d/%m/%Y %H:%M'],
                    widget=forms.TextInput(attrs={'class': 'form-control datetimepicker-input date-pick',
                                 'data-toggle': 'datetimepicker',
                                 'data-target': '#id_begin_register'}))
    end_register = forms.DateTimeField(label='f_insc_end',
                    input_formats=['%d/%m/%Y %H:%M'],
                    widget=forms.TextInput(attrs={'class': 'form-control datetimepicker-input date-pick',
                                 'data-toggle': 'datetimepicker',
                                 'data-target': '#id_end_register'}))
    place = forms.CharField(label='f_place', max_length=128,
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    price_ionis = forms.FloatField(label='f_price_int',
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01'}))
    price = forms.FloatField(label='f_price_ext',
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01'}))
    ext_capacity = forms.IntegerField(label='f_limit_ext',
                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    int_capacity = forms.IntegerField(label='f_limit_int',
                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    promotion_image_path = forms.ImageField(required=False, label='f_img',
                    widget=forms.FileInput(attrs={'class': 'custom-file-input'}))
    show_capacity = forms.BooleanField(label='f_show_capacity', required=False,
                    initial=False,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class Asso_Form(forms.Form):
    name = forms.CharField(label='f_name', max_length=64,
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    logo_path = forms.ImageField(label='f_img',
                    widget=forms.FileInput(attrs={'class': 'custom-file-input'}))
    email = forms.EmailField(label='f_email', max_length=64,
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='f_desc',
                    widget=forms.Textarea(attrs={'class': 'form-control',
                                                  'rows': 5}))

class Staff_Form(forms.Form):
    association_name = forms.ModelChoiceField(label='f_association_name', widget=forms.Select(attrs={'class': 'form-control'}), queryset=Association.objects.all(), required=False, help_text="Company")
    capacity = forms.IntegerField(label='f_capacity',
               widget=forms.NumberInput(attrs={'class': 'form-control'}))

Staff_Form_Set = formset_factory(Staff_Form)

class Connection_Form(forms.Form):
    username = forms.CharField(label='f_pseudo',
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='f_pwd',
                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class Inscription_Form(forms.Form):
    email = forms.EmailField(label='f_email',
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    firstname = forms.CharField(label='f_firstname',
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    lastname = forms.CharField(label='f_lastname',
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='f_pseudo',
                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    pwd = forms.CharField(label='f_pwd',
                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    pwd_conf = forms.CharField(label='f_pwd_conf',
                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))
