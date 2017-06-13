from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email ID", max_length=100, help_text="Enter your email id", label_suffix=":")
    password = forms.CharField(label="Password", help_text="Enter your password", widget=forms.PasswordInput(), label_suffix=":")


class SignUpForm(forms.Form):
    firstname = forms.CharField(label="First Name", max_length=100, label_suffix=":")
    lastname = forms.CharField(label="Last Name", max_length=100, label_suffix=":")
    email = forms.EmailField(label="Email ID", max_length=100, label_suffix=":")
    contact = forms.CharField(label="Contact", max_length=15, label_suffix=":")
    password = forms.CharField(label="Password", widget=forms.PasswordInput(), label_suffix=":")
    repass = forms.CharField(label="Retype Password", widget=forms.PasswordInput(), label_suffix=":")

class CartForm(forms.Form):
    quantity = forms.FloatField(label="Quantity", help_text="Specify quantity", label_suffix=":")


