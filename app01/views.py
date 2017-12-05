from django.shortcuts import render
# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from app01 import models
from app01 import forms
from django.db.models import Count,Sum
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
import datetime
import json
#滑动模块验证码的包
from app01.geetest import GeetestLib

def login(request):
    if request.method=="POST":
        user = forms.UserForm(request, request.POST)
        if user.is_valid():
            del user.cleaned_data['validCode']
            user_obj=models.UserInfo.objects.filter(**user.cleaned_data).first()
            if not user_obj:
                return HttpResponse("false")
            request.session["username"]=user.cleaned_data.get("name")
            request.session["userid"]=user_obj.id
            return HttpResponse("true")
        return HttpResponse(json.dumps(user.errors))
    else:
        user=forms.UserForm(request)
    user = forms.UserForm(request, request.POST)
    return render(request,"login.html",{"form":user})

def getvalicode(request):
    from io import BytesIO
    import random
    from PIL import Image,ImageDraw,ImageFont
    img = Image.new(mode="RGB",size=(120,40),color=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    draw = ImageDraw.Draw(img,"RGB")
    font=ImageFont.truetype("crm/static/font/kumo.ttf",25)
    valid_list=[]
    for i in range(5):
        random_num=str(random.randint(0,9))
        random_lower_zimu=chr(random.randint(65,90))
        random_upper_zimu=chr(random.randint(97,122))
        random_char=random.choice([random_num,random_lower_zimu,random_upper_zimu])
        draw.text([5+i*24,10],random_char,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),font=font)
        valid_list.append(random_char)
    f=BytesIO()
    img.save(f,"png")
    data=f.getvalue()
    valid_str="".join(valid_list)
    print(valid_str)
    request.session["keepValidCode"]=valid_str
    return HttpResponse(data)

#滑动模块验证码函数
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
mobile_geetest_id = "7c25da6fe21944cfe507d2f9876775a9"
mobile_geetest_key = "f5883f4ee3bd4fa8caec67941de1b903"

def home(request):
    return render(request, "index.html",)

def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)

def mobilegetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(mobile_geetest_id, mobile_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)

def pcajax_validate(request):
    if request.method == "POST":
        login_response = {"is_login": False, "error_msg": None}
        # 验证验证码
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        #扩充验证用户名密码
        user = forms.UserForm(request, request.POST)
        if result:
            if user.is_valid():
                del user.cleaned_data['validCode']
                user_obj = models.UserInfo.objects.filter(**user.cleaned_data).first()
                if not user_obj:
                    return HttpResponse(json.dumps(user.errors))
                request.session["username"] = user.cleaned_data.get("name")
                request.session["userid"] = user_obj.id
                return HttpResponse("true")
        return HttpResponse(json.dumps(user.errors))

def mobileajax_validate(request):
    if request.method == "POST":
        gt = GeetestLib(mobile_geetest_id, mobile_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status":"success"} if result else {"status":"fail"}
        return HttpResponse(json.dumps(result))
    return HttpResponse("error")

def index(request):
    return render(request,"index.html")
