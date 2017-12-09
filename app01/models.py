from django.db import models
# Create your models here.
from django.db import models

class UserInfo(models.Model):

    name = models.CharField(max_length=32,verbose_name="用户名")
    pwd = models.CharField(max_length=32,verbose_name="密码")

    class Meta:
        verbose_name_plural="用户信息表"
    def __str__(self):
        return self.name

class ClassList(models.Model):

    name = models.CharField(max_length=32,verbose_name="班级")

    class Meta:
        verbose_name_plural="班级表"

    def __str__(self):
        return self.name

class Student(models.Model):

    name = models.CharField(max_length=32,verbose_name="学生名")
    pwd = models.CharField(max_length=32,verbose_name="密码")
    classes = models.ForeignKey(verbose_name="所属班级",to=ClassList)

    class Meta:
        verbose_name_plural="学生表"

    def __str__(self):
        return self.name

class Questionnaire(models.Model):

    name = models.CharField(max_length=32)
    creator = models.ForeignKey(verbose_name="创建者",to=UserInfo)
    cls = models.ForeignKey(verbose_name="所属班级",to=ClassList)

    class Meta:
        verbose_name_plural="调查问卷表"

    def __str__(self):
        return self.name

class Question(models.Model):

    name = models.CharField(max_length=100)
    question_types=(
        (1,"打分(1-10分)"),
        (2,"单选"),
        (3,"建议"),
    )
    type = models.IntegerField(choices=question_types,verbose_name="问题类型")
    Questionnaire=models.ForeignKey(verbose_name="调查问卷",to=Questionnaire)

    class Meta:
        verbose_name_plural="问题表"

    def __str__(self):
        return self.name

class Option(models.Model):

    name = models.CharField(max_length=32,verbose_name="名称")
    score = models.IntegerField(verbose_name="选项对应的分值")
    question = models.ForeignKey(verbose_name="所属问题",to=Question)

    class Meta:
        verbose_name_plural="选项表"

    def __str__(self):
        return self.name

class Answer(models.Model):

    student = models.ForeignKey(verbose_name="学生",to=Student)
    question = models.ForeignKey(verbose_name="所属问题",to=Question)
    val = models.IntegerField(null=True,blank=True,verbose_name="评分值")
    content = models.CharField(max_length=255,null=True,blank=True,verbose_name="评论")
    option = models.ForeignKey(verbose_name="选项",to=Option,null=True,blank=True)

    class Meta:
        verbose_name_plural="回复表"

    def __str__(self):
        return self.content