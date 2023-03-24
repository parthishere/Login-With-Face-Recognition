from django import forms

from login_details.models import LoginDetails

from .models import LectrueModel, UserProfile

class UserCreateForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(required=False)
    enrollment_number = forms.NumberInput()
    gender = forms.CharField(max_length=1)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    

class AuthenticationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    
        
    
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        
        
        
class FirstTimeUserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(widget = forms.SelectDateWidget())
    class Meta():
        model = UserProfile
        fields = ['image', 'enrollment_number', 'about', 'gender', 'birth_date',
                  'phone_number', 'website', 'github_username',
                  'twitter_handle', 'instagram_username', 'facebook_username', "college", "company", "branch", "city","district", "semester"]

        
    def __init__(self, *args, **kwargs):
        super(FirstTimeUserProfileForm, self).__init__(*args, **kwargs)
        self.fields['enrollment_number'].required = True
        self.fields['college'].required = True
        self.fields['branch'].required = True
        self.fields['semester'].required = True
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
class SecondTimeUserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(widget = forms.SelectDateWidget())
    class Meta():
        model = UserProfile 
        fields = ['about', 'birth_date',
                  'phone_number', 'website', 'github_username',
                  'twitter_handle', 'instagram_username', 'facebook_username']

        
    def __init__(self, *args, **kwargs):
        super(SecondTimeUserProfileForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
class UserProfileImageForm(forms.ModelForm):

    class Meta():
        model = UserProfile
        fields = ['image', 'enrollment_number', "college", "company", "branch", "city","district", "semester"]
    
    def __init__(self, *args, **kwargs):
        super(UserProfileImageForm, self).__init__(*args, **kwargs)
        self.fields['enrollment_number'].required = True
        self.fields['college'].required = True
        self.fields['branch'].required = True
        self.fields['semester'].required = True
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
            
class LectureDetailsForm(forms.ModelForm):
    
    class Meta():
        model = LoginDetails
        fields = ['teacher', 'lecture']
    
    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop('user_profile')
        
        
        super().__init__(*args, **kwargs)
        self.fields['teacher'].required = True
        self.fields['lecture'].required = True
        user_p = UserProfile.objects.prefetch_related("user").filter(college=self.user_profile.college, branch=self.user_profile.branch, user__is_teacher=True)
        self.fields['teacher'].queryset = user_p
        self.fields['teacher'].widget.attrs.update({'class':'form-control', 'required':'true'})
        self.fields['lecture'].widget.attrs.update({'class':'form-control'})
    
        self.fields['lecture'].queryset = LectrueModel.objects.none()

        
        if 'teacher' in self.data:
            try:
                teacher_id = int(self.data.get('teacher'))
                
                self.fields['lecture'].queryset =LectrueModel.objects.filter(teacher_id=teacher_id).order_by('-id')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['lecture'].queryset = self.instance.teacher.lectures.order_by('-id')

            
            
    