from django.shortcuts import render,redirect
from home.models import *
from home.forms import *
from django.contrib.auth import authenticate, login, logout
from nocaptcha_recaptcha.fields import NoReCaptchaField
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import datetime
import os
import json
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

def err_404(request):
	return render(request,'404.html')

def err_500(request):
	return render(request,'500.html')	
	
def get_by_bday():
	upc=[]
	mnt_srt=[]
	for x in range(12):
		mnt_srt.append([])
	today=datetime.date.today()
	for x in Friend.objects.all():#order_by('date_of_birth'):
		mnt_srt[x.date_of_birth.month-1].append(x)
	curr_mnt=today.month-1
	last=[]
	for y in range(12):
		# insertion sort
		x=mnt_srt[curr_mnt]
		l=len(x)
		if l>1:
			j,i=1,0
			while j<l:
				i=j-1
				tmp=x[j]
				while i>=0 and tmp.date_of_birth.day<x[i].date_of_birth.day:
					x[i+1]=x[i]
					i-=1
				x[i+1]=tmp
				j+=1
		upc.extend(x)
		if curr_mnt==today.month-1:# in first loop only
			k=0
			while k<len(upc) and upc[k].date_of_birth.day<today.day:
				k+=1
			last=upc[:k]
			upc=upc[k:]
		curr_mnt+=1
		if curr_mnt==12:
			curr_mnt=0
	upc.extend(last)
	return upc
	
# Create your views here.

def do_logout(request):
	if request.method=='POST':
		data={}
		logout(request)
		data['success']='successfully sign out'
		return HttpResponse(json.dumps(data),content_type="application/json")
	else:
		return HttpResponseRedirect("/")

def do_login(request):
	data={}
	if request.method=='POST':
		print 'post request',data
		username=request.POST['username']
		password=request.POST['password']
		user=authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request,user)
				print 'active'
				data['success']='Welcome !!'
				data['full_name']=user.get_full_name()
				data['username']=user.username
				data['email']=user.email
				data['post_count']=user.friend.post_set.count()
				data['image_url']=user.friend.image.url
				data['date_of_birth']=user.friend.date_of_birth.strftime('%d-%B-%Y')
				print data
			else:
				print 'inactive'
				data['error']='Your account is inavtive contact admin'
		else:
			print 'Login Failed'
			data['error']='Login attemp failed! check username and password'
		return HttpResponse(json.dumps(data),content_type="application/json")
	else:
		return HttpResponseRedirect("/")

def index(request):
	submit_status=False
	sidebar_msg=''
	user_enroll_form=''
	login_form=''
	if request.method=='POST':
		if 'login_button' in request.POST:
			print 'login attempt'
			data['msg']='hello'
			return HttpResponse(json.dumps(data),content_type="application/json")
			username=request.POST['username']
			password=request.POST['password']
			user=authenticate(username=username, password=password)
			if user:
				if user.is_active:
					login(request,user)
					print 'active'
					sidebar_msg='Welcome !!'
				else:
					print 'inactive'
					sidebar_msg='Your account is inavtive contact admin'
			else:
				print 'Login Failed'
				sidebar_msg='Login attemp failed! check username and password'
		elif 'logout_button' in request.POST:
			logout(request)
			sidebar_msg='Successfully logged out'
		elif 'request_button' in request.POST:			
			user_enroll_form=UserEnrollForm(request.POST,request.FILES);
			if user_enroll_form.is_valid():
				user_enroll_form.save()
				submit_status=True
	if not user_enroll_form:
		user_enroll_form=UserEnrollForm()
	if not login_form:
		login_form=LoginForm()
	friends=get_by_bday()
	primary_friends=[]
	for x in friends:
		if x.date_of_birth.month==datetime.date.today().month and x.date_of_birth.day==datetime.date.today().day:
			primary_friends.append(x)
		else:
			break;
	for x in primary_friends:
		friends.remove(x)
	return render(request,'home/index.html',{'sidebar_msg':sidebar_msg,'submit_status':submit_status,'is_index':True,'form':user_enroll_form,'friends':friends,'primary_friends':primary_friends,'login_form':login_form})

def listPosts(request,username):
	#user=User.objects.get(username=username)
	friend=Friend.objects.get(user=User.objects.get(username=username))
	if request.method=='POST':
		author=Friend.objects.get(user=request.user)
		if 'post_button' in request.POST and request.user.is_authenticated():
			post_form=PostForm(request.POST,request.FILES)
			if post_form.is_valid():
				post=post_form.save(commit=False)
				post.author=author
				post.friend=friend
				post.save()
				post_form=PostForm()
		elif 'comment_button' in request.POST and request.user.is_authenticated():
			comment_form=CommentForm(request.POST)
			if comment_form.is_valid():
				print 'comment valid'
				comment=comment_form.save(commit=False)
				comment.author=author
				comment.save()
			else:
				print 'comment invalid'
			post_form=PostForm()
	else:
		post_form=PostForm()
	data={'friend':friend,'posts':friend.post_set.all(),'login_form':LoginForm(),'post_form':post_form,'comment_form':CommentForm(),}
	data['today']=datetime.date.today()
	return render(request,'home/list_posts.html',data)
	
def delPost(request,username,post_id):
	if request.user.is_authenticated():
		try:
			post=Post.objects.get(pk=post_id)
			if post.author.user==request.user:
				path=post.image.url
				print path
				os.remove(path)
				post.delete()
		except:
			pass
	return redirect('/posts/'+username)
	
def delComment(request,username,comment_id):
	if request.user.is_authenticated():
		try:
			comment=Comment.objects.get(pk=comment_id)
			if comment.author.user == request.user:
				comment.delete()
		except:
			pass
	return redirect('/posts/'+username)
	
