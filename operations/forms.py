from django import forms
from .models import (
    RailwaySection,
    Train,
    TrainSchedule,
    MaintenanceRequest
)


class RailwaySectionForm(forms.ModelForm):
    class Meta:
        model = RailwaySection
        fields = [
            'section_code',
            'name',
            'from_station',
            'to_station',
            'distance_km',
            'is_active'
        ]
        widgets = {
            'section_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section code'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section name'
            }),
            'from_station': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Starting station'
            }),
            'to_station': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Destination station'
            }),
            'distance_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distance in KM',
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class TrainForm(forms.ModelForm):
    class Meta:
        model = Train
        fields = ['train_number', 'train_name']
        widgets = {
            'train_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter train number'
            }),
            'train_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter train name'
            }),
        }

class TrainScheduleForm(forms.ModelForm):
    class Meta:
        model = TrainSchedule
        fields = [
            'train',
            'section',
            'start_time',
            'end_time',
            'direction'
        ]

        widgets = {
            'train': forms.Select(attrs={
                'class': 'form-select'
            }),
            'section': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'direction': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Up or Down'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_time'].input_formats = [
            '%Y-%m-%dT%H:%M'
        ]
        self.fields['end_time'].input_formats = [
            '%Y-%m-%dT%H:%M'
        ]

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError(
                'End time must be later than start time.'
            )

        return cleaned_data

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = [
            'section',
            'work_type',
            'description',
            'duration_minutes',
            'priority',
            'preferred_start',
            'status'
        ]

        widgets = {
            'section': forms.Select(attrs={
                'class': 'form-select'
            }),

            'work_type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the maintenance work'
            }),

            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in minutes',
                'min': '1'
            }),

            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),

            'preferred_start': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),

            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['preferred_start'].input_formats = [
            '%Y-%m-%dT%H:%M'
        ]