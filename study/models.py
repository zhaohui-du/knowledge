from django.db import models

# Create your models here.


# 制造系统
class ManufactureSystem(models.Model):
    system_name = models.CharField(max_length=200)
    system_path = models.CharField(max_length=200)
    system_comment = models.CharField(max_length=200)

    def __str__(self):
        return self.system_name


# PDF 文件
class PdfFile(models.Model):
    manufacture_system = models.ForeignKey(ManufactureSystem, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=200)
    file_url = models.CharField(max_length=200)
    file_datetime = models.DateTimeField(auto_now=True)
    file_comment = models.CharField(max_length=200)

    def __str__(self):
        return self.file_name


# 用户
class User(models.Model):
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    authority = models.IntegerField
    user_comment = models.CharField(max_length=200)

    def __str__(self):
        return self.username
