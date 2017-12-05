#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.forms import Form
from app01.views import models
from django.forms import widgets
from django.forms import fields
from django.core.validators import RegexValidator
from django.core.exceptions import NON_FIELD_ERRORS,ValidationError

class UserForm(Form):

    def __init__(self,request,*args,**kwargs):
        super(UserForm, self).__init__(*args,**kwargs)
        self.request=request

    name=fields.CharField(
        label="Your name",
        max_length=100,
        required=True,
        error_messages={"required":"用户名不能为空"},
        widget=widgets.TextInput(attrs={"class":"form-control input-lg","id":"username"})
    )
    pwd=fields.CharField(
        label="Your password",
        max_length=100,
        required=True,
        error_messages={"required": "密码不能为空"},
        widget=widgets.PasswordInput(attrs={"class": "form-control input-lg", "id": "password"})
    )

    validCode=fields.CharField(
        label="Your valiCode",
        max_length=100,
        required=True,
        error_messages={"required": "验证码不能为空"},
    )

    def clean_validCode(self):
        v = self.cleaned_data['validCode']
        if v.upper() != self.request.session["keepValidCode"].upper():
            raise ValidationError("验证码有误")
        return v

    def clean_username(self):
        v=self.cleaned_data['name']
        if not models.UserInfo.objects.filter(name=v):
            raise ValidationError("用户名不存在")
        return v

    def clean(self):
        value_dict=self.cleaned_data
        v1 = value_dict.get('name')
        v2 = value_dict.get('pwd')
        print("用户名%s 密码%s"%(v1,v2))
        if not v2:
            raise ValidationError("密码不能为空")
        elif not models.UserInfo.objects.filter(name=v1,pwd=v2):
            raise ValidationError("密码错误")
        return self.cleaned_data

