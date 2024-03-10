from django import forms

class ImageUploadForm(forms.Form):
    files_field = forms.FileField(widget = forms.TextInput(attrs={
            "name": "images",
            "type": "File",
            "class": "form-control",
            "multiple": "True",
        }), label = "", required=False)