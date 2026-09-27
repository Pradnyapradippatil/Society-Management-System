from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import Complaint, Notice, SocietyUser


def bootstrapize(field, *, css_class="form-control", placeholder=None):
    existing = field.widget.attrs.get("class", "")
    field.widget.attrs["class"] = f"{existing} {css_class}".strip()
    if placeholder is not None:
        field.widget.attrs["placeholder"] = placeholder


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapize(self.fields["username"], placeholder="name@example.com")
        bootstrapize(self.fields["password"], placeholder="Password")
        self.fields["username"].widget.attrs.update({"autocomplete": "email"})
        self.fields["password"].widget.attrs.update({"autocomplete": "current-password"})

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password,
            )
            if self.user_cache is None:
                raise ValidationError("Please enter a correct email and password.")
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class ResidentRegistrationForm(UserCreationForm):
    class Meta:
        model = SocietyUser
        fields = ["full_name", "email", "flat_number", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapize(self.fields["full_name"], placeholder="Full name")
        bootstrapize(self.fields["email"], placeholder="name@example.com")
        bootstrapize(self.fields["flat_number"], placeholder="Flat number")
        bootstrapize(self.fields["phone"], placeholder="Phone number")
        bootstrapize(self.fields["password1"], placeholder="Create password")
        bootstrapize(self.fields["password2"], placeholder="Confirm password")
        self.fields["full_name"].widget.attrs.update({"autocomplete": "name"})
        self.fields["email"].widget.attrs.update({"autocomplete": "email"})
        self.fields["flat_number"].widget.attrs.update({"autocomplete": "off"})
        self.fields["phone"].widget.attrs.update({"autocomplete": "tel"})

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if SocietyUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower().strip()
        user.role = SocietyUser.Role.RESIDENT
        user.is_staff = False
        if commit:
            user.save()
        return user


class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = SocietyUser
        fields = ["full_name", "email", "flat_number", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapize(self.fields["full_name"], placeholder="Admin full name")
        bootstrapize(self.fields["email"], placeholder="admin@example.com")
        bootstrapize(self.fields["flat_number"], placeholder="Flat number")
        bootstrapize(self.fields["phone"], placeholder="Phone number")
        bootstrapize(self.fields["password1"], placeholder="Create password")
        bootstrapize(self.fields["password2"], placeholder="Confirm password")

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if SocietyUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower().strip()
        user.role = SocietyUser.Role.ADMIN
        user.is_staff = True
        if commit:
            user.save()
        return user


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["category", "title", "description"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Complaint title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe the issue clearly"}),
        }


class ComplaintStatusForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["status"]
        widgets = {"status": forms.Select(attrs={"class": "form-select"})}


class ComplaintSearchForm(forms.Form):
    query = forms.CharField(required=False, label="Search", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Resident name, title, category"}))
    status = forms.ChoiceField(required=False, choices=[("", "All statuses")] + list(Complaint.Status.choices), widget=forms.Select(attrs={"class": "form-select"}))
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Notice title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Notice description"}),
        }