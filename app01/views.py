from django.shortcuts import render
# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from app01 import models
from app01 import forms
from app01.model_forms import *
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
    user = forms.UserForm(request,request.POST)
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
    Questionnaire_list = models.Questionnaire.objects.all()
    return render(request,"index.html",{"Questionnaire_list":Questionnaire_list})

def questionEditor(request):
    QuestionnaireId=request.GET.get("QuestionnaireId")
    request.session["Questionnaire_Id"]=QuestionnaireId
    Question_list=models.Question.objects.filter(Questionnaire_id=QuestionnaireId)
    types = models.Question.question_types
    return render(request,"questionEditor.html",{"types":types,"QuestionnaireId":QuestionnaireId,"Question_list":Question_list})

def questionnaireAdd(request):
    if request.is_ajax():
        result=json.loads(request.body.decode("utf8"))
        print("最终的结果是什么%s"%result)
        #问卷ID
        Questionnaire_id = result["result"][0]["Questionnaire_id"]

        #查出现有问卷中所有的问题
        question_list = models.Question.objects.filter(Questionnaire_id=Questionnaire_id)

        #用户提交的所有问题ID
        post_id_list = [i.get("question_id") for i in result["result"] if i.get("question_id")]

        #数据库中获取已有的问题ID
        question_id_list = [ i.id for i in question_list]

        #数据库中的哪些id需要删除
        del_id_list = set(question_id_list).difference(post_id_list)

        # 循环ajax提交过来的所有问题信息
        print("过来这边了没=====")
        for item in result["result"]:
            #item就是用户提交过来的一个问题
            qid=item.get("question_id")
            name=item.get("name")
            type=item.get("type")
            options=item.get("options")
            if qid not in question_id_list:
                #要新增
                print("options里有啥%s"%options)
                new_question_obj=models.Question.objects.create(name=name,type=type,Questionnaire_id=Questionnaire_id)
                if type=="2":
                    for op in options:
                        models.Option.objects.create(question=new_question_obj,name=op.get("optionName"),score=op.get("optionScore"))
            else:
                #要更新
                models.Question.objects.filter(id=qid).update(name=name,type=type)
                print("选项里都有什么%s"%options)
                if not options:
                    #为了更新不管有没有选项删了再说!
                    models.Option.objects.filter(question_id=qid).delete()
                else:
                    #不推荐
                    models.Option.objects.filter(question_id=qid).delete()
                    for op in options:
                        models.Option.objects.create(name=op.get("optionName"),score=op.get("optionScore"),question_id=qid)
        #删除与提交问题id不同的问题
        models.Question.objects.filter(id__in=del_id_list).delete()
        return JsonResponse({"status":"ok"})

    if request.method =="POST":
        QuestionnaireName=request.POST.get("QuestionnaireName")
        userid=request.POST.get("userid")
        classid=request.POST.get("classid")
        models.Questionnaire.objects.create(name=QuestionnaireName,creator_id=userid,cls_id=classid)
        return HttpResponse("true")
    else:
        user_list = models.UserInfo.objects.all()
        class_list = models.ClassList.objects.all()
        return render(request,"questionnaireAdd.html",{"user_list":user_list,"class_list":class_list})

def question(request,pid):
    print("pid过来了没%s"%pid)
    def inner():
        que_list = models.Question.objects.filter(Questionnaire_id=pid)
        if not que_list:
            #新创建的问卷,其中还么有创建问题
            form = QuestionModelForm()
            yield {"form":form,"obj":None,"option_class":"hide","options":None}
        else:
            #含问题的问卷
            for que in que_list:
                form = QuestionModelForm(instance=que)
                temp = {'form':form,"obj":que,"option_class":"hide","options":None}
                if que.type == 2:
                    temp["option_class"] = ''
                    #获取当前问题的所有选项? que
                    def inner_loop(quee):
                        option_list=models.Option.objects.filter(question=quee)
                        for v in option_list:
                            yield {"form":OptionModelForm(instance=v),"obj":v}
                    temp["options"]=inner_loop(que)
                yield temp
    return render(request,"questionEditor.html",{'form_list':inner(),"Questionnaire_id":pid})

def student_login(request):
    if request.is_ajax():
        student_name=request.POST.get("student_name")
        student_pass=request.POST.get("student_pass")
        print("进来了没有=====")
        obj=models.Student.objects.filter(name=student_name,pwd=student_pass).first()
        if not obj:
            return redirect("/student_login/")
        request.session["student_info"]={"id":obj.id,"user":obj.name}
        return HttpResponse("true")
    return render(request,"slogin.html")

from django.core.exceptions import ValidationError

def func(val):
    if len(val)<15:
        raise ValidationError("内容不能小于15个字符")

def score(request,class_id,qn_id):
    if not request.session.get("student_info"):
        return redirect("/student_login/")
    student_id = request.session["student_info"]["id"]
    #1,当前登录用户是否是要评论的班级学生
    ct1 = models.Student.objects.filter(id=student_id,classes_id=class_id).count()
    if not ct1:
        return HttpResponse("你只能评论自己班级的问卷")

    ct2 = models.Answer.objects.filter(student_id=student_id,question__Questionnaire_id=qn_id).count()

    if ct2:
        return HttpResponse("你已经参与过调查，无法再次进行")

    #展示当前问卷下的所有问题
    from django.forms import Form
    from django.forms import fields
    from django.forms import widgets

    question_list=models.Question.objects.filter(Questionnaire_id=qn_id)
    field_dict={}
    for que in question_list:
        if que.type == 1:
            field_dict['val_%s'%que.id]= fields.ChoiceField(
                label=que.name,
                error_messages={'required':'必填'},
                widget=widgets.RadioSelect,
                choices=[(i,i) for i in range(1,11)]
            )
        elif que.type == 2:
            field_dict['option_id_%s'%que.id]=fields.ChoiceField(
                label=que.name,
                widget=widgets.RadioSelect,
                choices=models.Option.objects.filter(
                    question_id=que.id).values_list("id","name"))
        else:
            from django.core.exceptions import ValidationError
            from django.core.validators import RegexValidator
            field_dict['content_%s'%que.id]=fields.CharField(
                label=que.name,widget=widgets.Textarea,validators=[func, ]
            )

    MyTestForm = type("MyTestForm",(Form,),field_dict)

    if request.method=="GET":
        form = MyTestForm()
        return render(request,"score.html",{'question_list':question_list,'form':form,"classId":class_id,"qn_id":qn_id})
    else:
        #15字验证
        #不允许为空
        form = MyTestForm(request.POST)
        print("requestpost里有哪些数据%s"%request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            objs=[]
            for key,v in form.cleaned_data.items():
                k,qid=key.rsplit('_',1)
                print("k==%s v==%s"%(k,v))
                answer_dict={'student_id':student_id,'question_id':qid,k:v}
                objs.append(models.Answer(**answer_dict))
            models.Answer.objects.bulk_create(objs)
            return HttpResponse("感谢您的参与!!!")
        return render(request,"score.html",{'question_list':question_list,'form':form})



















