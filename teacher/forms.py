from django import forms

from recognizer.models import SessionAttendanceModel, UserProfile, LectrueModel, IpAddress


class TeacherUpdateForm(forms.ModelForm):
    class Meta():
        model = UserProfile
        exclude = ['user', 'login_proceed']

    def __init__(self, *args, **kwargs):
        super(TeacherUpdateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class IpAddress(forms.ModelForm):
    class Meta():
        model = IpAddress
        fields = ['ip']

    def __init__(self, *args, **kwargs):
        super(IpAddress, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class LectureForm(forms.ModelForm):
    class Meta():
        model = LectrueModel
        fields = ['lecture_name', "code", "district", "time_to_expire_session",
                  "accepted_user",  "city", "college", 'branch', 'semester']

    def __init__(self, *args, **kwargs):
        super(LectureForm, self).__init__(*args, **kwargs)
        self.fields['lecture_name'].required = True
        self.fields['branch'].required = True
        self.fields['semester'].required = True

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class SessionForm(forms.ModelForm):
    class Meta():
        model = SessionAttendanceModel
        fields = ['name', "lecture", "atendees", "requested_users"]

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        lectures = kwargs.pop('lectures', None)

        super(SessionForm, self).__init__(*args, **kwargs)

        self.fields['atendees'].queryset = user_profile
        self.fields['lecture'].queryset = lectures
        self.fields['requested_users'].queryset = user_profile

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class StudentBulkForm(forms.Form):
    excel = forms.FileField(
        required=True, help_text="Upload in format 'id, name, email, gender, enrollment_number'")
