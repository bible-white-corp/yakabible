from django import forms

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
    promotion_image_path = forms.CharField(required=False, label='f_img',
                                           max_length=128,
                    widget=forms.TextInput(attrs={'class': 'custom-file-input'}))
