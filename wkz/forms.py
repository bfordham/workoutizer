from django import forms

from wkz.models import Activity, Settings, Sport, UserProfile

DATETIMEPICKER_FORMAT = "%m/%d/%Y %I:%M %p"


def set_field_attributes(visible_fields):
    for visible in visible_fields:
        if visible.name == "date":  # because it would overwrite the required 'datetimepicker' class
            continue
        else:
            visible.field.widget.attrs["class"] = "form-control"


class AddSportsForm(forms.ModelForm):
    class Meta:
        model = Sport
        exclude = ("created", "modified", "user")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddSportsForm, self).__init__(*args, **kwargs)
        set_field_attributes(self.visible_fields())
        
    def save(self, commit=True):
        sport = super().save(commit=False)
        if self.user:
            sport.user = self.user
        if commit:
            sport.save()
        return sport


class AddActivityForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=[DATETIMEPICKER_FORMAT],
        widget=forms.DateTimeInput(attrs={"class": "form-control datetimepicker"}),
    )

    class Meta:
        model = Activity
        exclude = ("trace_file", "created", "modified", "is_demo_activity", "evaluates_for_awards", "user")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddActivityForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["sport"] = forms.ModelChoiceField(
                queryset=Sport.objects.filter(user=self.user).exclude(name="unknown")
            )
        else:
            self.fields["sport"] = forms.ModelChoiceField(queryset=Sport.objects.all().exclude(name="unknown"))
        set_field_attributes(self.visible_fields())
        
    def save(self, commit=True):
        activity = super().save(commit=False)
        if self.user:
            activity.user = self.user
        if commit:
            activity.save()
        return activity


class EditActivityForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=[DATETIMEPICKER_FORMAT],
        widget=forms.DateTimeInput(attrs={"class": "form-control datetimepicker"}),
    )

    class Meta:
        model = Activity
        exclude = ("trace_file", "created", "modified", "is_demo_activity", "user")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditActivityForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields["sport"] = forms.ModelChoiceField(
                queryset=Sport.objects.filter(user=self.user).exclude(name="unknown")
            )
        else:
            self.fields["sport"] = forms.ModelChoiceField(queryset=Sport.objects.all().exclude(name="unknown"))
        set_field_attributes(self.visible_fields())


class EditSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ("number_of_days", "created", "modified", "user")

    def __init__(self, *args, **kwargs):
        super(EditSettingsForm, self).__init__(*args, **kwargs)
        set_field_attributes(self.visible_fields())
