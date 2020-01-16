from django import forms


class UploadPdfFileForm(forms.Form):
    # catalogue = forms.CharField(max_length=80)
    file = forms.FileField()

    def __str__(self):
        return self.catalogue


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class DeletePdfFileForm(forms.Form):
    file_name = forms.CharField(max_length=200)

    def __str__(self):
        return self.file_name


class DeletePdfFilesForm(forms.Form):
    delete_pdf_list = forms.CharField(max_length=200)

    def __str__(self):
        return self.delete_pdf_list


class AddManufactureSystem(forms.Form):
    system_name = forms.CharField(max_length=200)

    def __str__(self):
        return self.system_name


class DeleteManufactureSystem(forms.Form):
    system_name = forms.CharField(max_length=200)

    def __str__(self):
        return self.system_name


class DeleteManufactureSystems(forms.Form):
    system_name = forms.CharField(max_length=200)

    def __str__(self):
        return self.system_name


class SearchPdfFileForm(forms.Form):
    file_name = forms.CharField(max_length=200)

    def __str__(self):
        return self.file_name


class UserForm(forms.Form):
    email = forms.CharField(max_length=200)
    password = forms.CharField(max_length=200)

    def __str__(self):
        return self.username
