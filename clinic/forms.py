from django import forms

class MDBFileUploadForm(forms.Form):
    file = forms.FileField(label="Upload .mdb File", allow_empty_file=False)
