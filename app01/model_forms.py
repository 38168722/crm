#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render,redirect,HttpResponse
from app01 import models
from django.forms import Form,ModelForm
from django.forms import fields
from django.forms import widgets as wd

class naireModelForm(ModelForm):
    class Meta:
        model = models.Questionnaire
        fields=['name','cls']


class OptionModelForm(ModelForm):
    class Meta:
        model = models.Option
        fields=['id','name','score']
        widgets = {
            "name": wd.TextInput(attrs={"optionName":"option"}),
            "score": wd.TextInput(attrs={"optionScore":"score"})
        }


class QuestionModelForm(ModelForm):
    class Meta:
        model = models.Question
        fields = ["id","name",'type','Questionnaire']
        widgets={
            "name":wd.TextInput(attrs={"questionName":"name"}),
            "type":wd.Select(attrs={"questionType":"type"}),
        }
        

