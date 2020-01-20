from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import ManufactureSystem, PdfFile, User
from .forms import UploadPdfFileForm, DeletePdfFileForm, AddManufactureSystem, DeleteManufactureSystem, \
    SearchPdfFileForm, DeletePdfFilesForm, DeleteManufactureSystems, FileFieldForm, UserForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

import os
import shutil
import datetime


# Create your views here.


# 预览首页
def view_index(request):
    return render(request, 'study/view_index.html')


# 管理首页
def admin_index(request):
    return render(request, 'study/admin_index.html')


# 系统预览
def system_view(request):
    if ManufactureSystem.objects.exists():
        system_list = ManufactureSystem.objects.order_by('system_name')
        context = {
            'system_list': system_list
        }
        return render(request, 'study/system_view.html', context)
    else:
        context = {
            'message': '暂无数据...'
        }
        return render(request, 'study/operation_result.html', context)


# 各系统 PDF 文档预览
def system_pdf_view(request, system_name):
    manufacture_system = get_object_or_404(ManufactureSystem, system_name=system_name)
    if manufacture_system.pdffile_set.exists():
        system_pdf_list = manufacture_system.pdffile_set.order_by('file_name')
        context = {
            'system_pdf_list': system_pdf_list
        }
        return render(request, 'study/system_pdf_view.html', context)
    else:
        context = {
            'message': '暂无数据...'
        }
        return render(request, 'study/operation_result.html', context)


# 系统管理
def system_admin(request):
    if ManufactureSystem.objects.exists():
        system_list = ManufactureSystem.objects.order_by('system_name')
        context = {
            'system_list': system_list,
            'message': ''
        }
        return render(request, 'study/system_admin_new.html', context)
    else:
        context = {
            'system_list': [],
            'message': '暂无数据...'
        }
        return render(request, 'study/system_admin_new.html', context)


# 各系统 PDF 文档管理
def system_pdf_admin(request, system_name):
    manufacture_system = get_object_or_404(ManufactureSystem, system_name=system_name)
    if manufacture_system.pdffile_set.exists():
        system_pdf_list = manufacture_system.pdffile_set.order_by('file_name')
        context = {
            'system_pdf_list': system_pdf_list,
            'message': '',
            'system_name': system_name
        }
        return render(request, 'study/system_pdf_admin_new.html', context)
    else:
        context = {
            'system_pdf_list': [],
            'message': '暂无数据...',
            'system_name': system_name
        }
        return render(request, 'study/system_pdf_admin_new.html', context)


# 跳转到操作界面（上传、删除、添加等）
def to_operation(request, name, operation):
    if name == 'system':
        if operation == 'add':
            return render(request, 'study/system_add.html')
        elif operation == 'delete':
            return render(request, 'study/system_delete.html')
    elif name == 'pdf_file':
        if operation == 'upload':
            return render(request, 'study/pdf_file_upload.html')
        elif operation == 'delete':
            return render(request, 'study/pdf_file_delete.html')


# PDF 文档上传 (支持多文档上传) 须判断文件是否已经存在
def pdf_file_upload(request):
    if request.method == 'POST':
        print(request.POST)
        form = UploadPdfFileForm(request.POST, request.FILES)
        if form.is_valid():
            # 循环解析 file.name 文件命名方式 系统名称-文件名称 [SAP-test1]
            print(request.FILES.getlist('file'))
            for file in request.FILES.getlist('file'):
                print(file.name)
                # f = request.FILES['file']
                path_str = str(file.name.replace('-', '\\'))
                path_list = path_str.split('\\')[:-1]
                # 获取 PDF 文档所属系统名称 [考虑多级嵌套的情况 SAP-SAP1-SAP11-test]
                system_name = path_list[0]
                # 判断文件是否已在数据库中，若不在则增加，若已在则更新
                if not PdfFile.objects.filter(file_name=file.name).exists():
                    path = '\\'.join(s for s in path_list)
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    # 系统文件夹路径
                    path_dir = os.path.join(base_dir, 'static', 'files', path)
                    print(path_dir)
                    # 文件路径
                    file_path = os.path.join(path_dir, file.name)
                    print(file_path)
                    # 写文件
                    with open(file_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    # 'http://127.0.0.1:8000/static/PDF/web/viewer.html?file=http://127.0.0.1:8000/static/PDF/web/' + pdf
                    # 主机ip和port  'origin': '127.0.0.1:8000'
                    # host_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
                    print(request.headers)
                    host = 'http://' + request.headers['Host']
                    print(host)
                    # PDF文件在线预览 url
                    file_url = host + '/static/PDF/web/viewer.html?file=' + host + '/static/files/' + \
                               path.replace('\\','/') + '/' + file.name
                    print(file_url)
                    system = get_object_or_404(ManufactureSystem, system_name=system_name)
                    # 更新PDF时更新上传时间
                    file_datetime = datetime.datetime.now().replace(microsecond=0)
                    # 数据库新增 PDF 文件并保存
                    pdf_file = PdfFile(manufacture_system=system, file_name=file.name, file_path=file_path,
                                       file_url=file_url, file_datetime=file_datetime)
                    pdf_file.save()
                else:
                    # 若文件已存在，则删除本地文件并重新写入
                    pdf_file = PdfFile.objects.get(file_name=file.name)
                    os.remove(pdf_file.file_path)
                    with open(pdf_file.file_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    # 更新PDF时更新上传时间
                    file_datetime = datetime.datetime.now().replace(microsecond=0)
                    pdf_file.file_datetime = file_datetime
                    pdf_file.save()
            system_pdf_list = PdfFile.objects.order_by('file_name')
            context = {
                'system_pdf_list': system_pdf_list,
                'message': '',
                'system_name': system_name,
            }
            return HttpResponseRedirect(reverse('study:system_pdf_admin', args=(system_name,)), context)
        else:
            context = {
                'message': '上传失败'
            }
            return render(request, 'study/operation_result.html', context)
    else:
        system_list = ManufactureSystem.objects.order_by('system_name')
        context = {
            'system_list': system_list,
            'message': ''
        }
        return HttpResponseRedirect(reverse('study:system_admin'), context)


# PDF 文档删除（单个删除，输入文件名称）
@csrf_exempt
def pdf_file_delete(request):
    if request.method == 'POST':
        print(request.POST)
        form = DeletePdfFileForm(request.POST)
        if form.is_valid():
            file_name = request.POST['file_name']
            if PdfFile.objects.filter(file_name=file_name).exists():
                pdf_file = PdfFile.objects.get(file_name=file_name)
                file_path = pdf_file.file_path
                system_name = pdf_file.manufacture_system
                os.remove(file_path)
                pdf_file.delete()
                system_pdf_list = PdfFile.objects.order_by('file_name')
                context = {
                    'system_pdf_list': system_pdf_list,
                    'message': ''
                }
                return HttpResponseRedirect(reverse('study:system_pdf_admin', args=(system_name,)), context)
            else:
                context = {
                    'message': '该文件不存在'
                }
                return render(request, 'study/operation_result.html', context)
        else:
            context = {
                'message': '删除失败'
            }
            return render(request, 'study/operation_result.html', context)
    else:
        system_list = ManufactureSystem.objects.order_by('system_name')
        context = {
            'system_list': system_list,
            'message': ''
        }
        return HttpResponseRedirect(reverse('study:system_admin'), context)


# 跳转到 PDF 文档复选框删除界面
def to_pdf_delete(request, system_name):
    manufacture_system = get_object_or_404(ManufactureSystem, system_name=system_name)
    system_pdf_list = manufacture_system.pdffile_set.order_by('file_name')
    context = {
        'system_pdf_list': system_pdf_list,
    }
    return render(request, 'study/pdf_file_delete_new.html', context)


# PDF 文档复选框删除（多选删除）
def pdf_files_delete(request):
    if request.method == 'POST':
        print(request.POST)
        form = DeletePdfFilesForm(request.POST)
        if form.is_valid():
            delete_pdf_list = request.POST.getlist('delete_pdf_list')
            if delete_pdf_list:
                # 循环删除
                system_name = ''
                for delete_file_name in delete_pdf_list:
                    pdf_file = PdfFile.objects.get(file_name=delete_file_name)
                    file_path = pdf_file.file_path
                    system_name = pdf_file.manufacture_system
                    os.remove(file_path)
                    pdf_file.delete()
                system_pdf_list = PdfFile.objects.order_by('file_name')
                print(delete_pdf_list)
                context = {
                    'system_pdf_list': system_pdf_list,
                    'message': '',
                    'system_name': system_name
                }
                return HttpResponseRedirect(reverse('study:system_pdf_admin', args=(system_name,)), context)
            else:
                context = {
                    'message': '所选文件为空'
                }
                return render(request, 'study/operation_result.html', context)
        else:
            context = {
                'message': '删除失败'
            }
            return render(request, 'study/operation_result.html', context)
    else:
        form = DeletePdfFilesForm()
        return render(request, 'study/pdf_file_delete_new.html', {'form': form})


# 系统添加
def system_add(request):
    if request.method == 'POST':
        print(request.POST)
        form = AddManufactureSystem(request.POST)
        if form.is_valid():
            system_name = request.POST['system_name']
            if not ManufactureSystem.objects.filter(system_name=system_name).exists():
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                system_path = os.path.join(base_dir, 'static', 'files', system_name)
                os.makedirs(system_path)
                system = ManufactureSystem(system_name=system_name, system_path=system_path, system_comment='')
                system.save()
                system_list = ManufactureSystem.objects.order_by('system_name')
                context = {
                    'system_list': system_list,
                    'message': ''
                }
                return HttpResponseRedirect(reverse('study:system_admin'), context)
            else:
                context = {
                    'message': '该系统已存在'
                }
                return render(request, 'study/operation_result.html', context)
        else:
            context = {
                'message': '添加失败'
            }
            return render(request, 'study/operation_result.html', context)
    else:
        system_list = ManufactureSystem.objects.order_by('system_name')
        context = {
            'system_list': system_list,
            'message': ''
        }
        return HttpResponseRedirect(reverse('study:system_admin'), context)


# 系统删除（单个删除，输入系统名称）
# 通过注解暂时跳过 csrf 中间件的保护
@csrf_exempt
def system_delete(request):
    if request.method == 'POST':
        print(request.POST)
        form = DeleteManufactureSystem(request.POST)
        if form.is_valid():
            system_name = request.POST['system_name']
            if ManufactureSystem.objects.filter(system_name=system_name).exists():
                system = ManufactureSystem.objects.get(system_name=system_name)
                system_path = system.system_path
                shutil.rmtree(system_path)
                system.delete()
                system_list = ManufactureSystem.objects.order_by('system_name')
                context = {
                    'system_list': system_list,
                    'message': ''
                }
                return HttpResponseRedirect(reverse('study:system_admin'), context)
            else:
                context = {
                    'message': '该系统不存在'
                }
                return render(request, 'study/operation_result.html', context)
        else:
            context = {
                'message': '删除失败'
            }
            return render(request, 'study/operation_result.html', context)
    else:
        system_list = ManufactureSystem.objects.order_by('system_name')
        context = {
            'system_list': system_list,
            'message': ''
        }
        return HttpResponseRedirect(reverse('study:system_admin'), context)


# 跳转到系统复选框删除界面
def to_system_delete(request):
    system_list = ManufactureSystem.objects.order_by('system_name')
    context = {
        'system_list': system_list,
        'message': ''
    }
    return render(request, 'study/system_delete_new.html', context)


# 系统复选框删除（多选删除）
def systems_delete(request):
    if request.method == 'POST':
        print(request.POST)
        form = DeleteManufactureSystems(request.POST)
        if form.is_valid():
            delete_system_list = request.POST.getlist('delete_system_list')
            if delete_system_list:
                for system_name in delete_system_list:
                    system = ManufactureSystem.objects.get(system_name=system_name)
                    system_path = system.system_path
                    shutil.rmtree(system_path)
                    system.delete()
                    system_list = ManufactureSystem.objects.order_by('system_name')
                    context = {
                        'system_list': system_list,
                        'message': ''
                    }
                    return HttpResponseRedirect(reverse('study:system_admin'), context)
            else:
                context = {
                    'message': '系统不存在'
                }
                return render(request, 'study/operation_result.html', context)
        else:
            context = {
                'message': '删除失败'
            }
            return render(request, 'study/operation_result.html', context)
    else:
        form = DeleteManufactureSystems()
        return render(request, 'study/system_delete_new.html', {'form': form})


# 在线搜索
def pdf_file_search(request):
    if request.method == 'POST':
        print(request.POST)
        print(request.headers)
        form = SearchPdfFileForm(request.POST)
        if form.is_valid():
            file_name = request.POST['file_name']
            print(PdfFile.objects.filter(file_name__icontains=file_name))
            if PdfFile.objects.filter(file_name__icontains=file_name).exists():
                system_pdf_list = PdfFile.objects.filter(file_name__icontains=file_name)
                context = {
                    'system_pdf_list': system_pdf_list,
                    'message': ''
                }
                return render(request, 'study/system_pdf_view.html', context)
            else:
                context = {
                    'system_pdf_list': [],
                    'message': '暂无数据...'
                }
                return render(request, 'study/operation_result.html', context)

    else:
        form = SearchPdfFileForm()
        return render(request, 'study/index.html', {'form': form})


# 登录界面
def to_login(request):
    return render(request, 'study/login.html')


# 用户登录
def user_login(request):
    # 不允许重复登陆
    if request.session.get('is_login', None):
        return render(request, 'study/admin_index.html')

    if request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        message = ''
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            message = '所有字段都必须填写！'
            if username and password:
                username = str(username).strip()
                user = get_object_or_404(User, username=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.username
                    # 分权限跳转页面
                    return render(request, 'study/admin_index.html')
                else:
                    message = '输入密码错误，请重新输入'
                    return render(request, 'study/login.html', {'message': message})

        return render(request, 'study/login.html', {'message': message})

    form = UserForm()
    return render(request, 'study/login.html', {'form': form})


# 用户退出
def user_logout(request):
    request.session['is_login'] = False
    return render(request, 'study/view_index.html')

# 用户注册（管理员权限）
