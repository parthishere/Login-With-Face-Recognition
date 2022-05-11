from django import forms

from recognizer.models import TeacherProfileModel, LectrueModel


class TeacherUpdateForm(forms.ModelForm):
    class Meta():
        model = TeacherProfileModel
        exclude = ['user', 'login_proceed']
        
    def __init__(self, *args, **kwargs):
        super(TeacherUpdateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        
        
class IpAddress(forms.ModelForm):
    class Meta():
        model = TeacherProfileModel
        fields = ['ip1', 'ip2']
        
    def __init__(self, *args, **kwargs):
        super(IpAddress, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
            
class LectureForm(forms.ModelForm):
    class Meta():
        model = LectrueModel
        fields = ['lecture_name', 'branch', 'semester']
        
    def __init__(self, *args, **kwargs):
        super(LectureForm, self).__init__(*args, **kwargs)
        self.fields['lecture_name'].required = True
        self.fields['branch'].required = True
        self.fields['semester'].required = True
 
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'