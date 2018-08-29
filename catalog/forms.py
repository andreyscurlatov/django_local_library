from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from catalog.models import BookInstance

import datetime

class RenewBookModelForm(ModelForm):

    def clean_due_back(self):
        data=self.cleaned_data['due_back']

        if bool(data) == False:
            pass

        elif data<datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        elif data>datetime.date.today()+datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data
        
    class Meta:
        model=BookInstance
        fields=['due_back','status','borrower']
        
