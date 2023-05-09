from django import forms
from .models import OrderedCall
from doctors.models import Review

class CreateCallForm(forms.ModelForm):

    def __init__(self, max_time=60, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordered_time'] = forms.IntegerField(
            label = 'Продолжительность звонка',
            # help_text= '''Если ваше заказаное время меньше
            # половины максимального времени назначеного доктором,
            # то вы платите половину суммы.''',
            max_value=max_time,
            widget=forms.NumberInput(attrs={'max':max_time}))

    def save(self, client, visiting_time, commit=True):
        call = super().save(commit=False)
        call.visiting_time = visiting_time
        visiting_time.is_booked = True
        visiting_time.save()
        call.save()
        call.participants.set([visiting_time.doctor.user, client])
        return call

    class Meta:
        model = OrderedCall
        fields = ['ordered_time']