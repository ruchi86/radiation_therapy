from django import forms

class dcmUploadForm(forms.Form):
    dcmZipFile = forms.FileField()

