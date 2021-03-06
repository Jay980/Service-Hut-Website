#A view function, or “view” for short, is simply a Python function that takes a web request 
#and returns a web response. This response can be the HTML contents of a Web page, or a redirect,
#or a 404 error, or an XML document, or an image, etc. Example: You use view to create web pages, 
#note that you need to associate a view to a URL to see it as a web page.

from unicodedata import category
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm ,PasswordChangeForm
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.forms import modelformset_factory
from django.urls import reverse


from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage

User=get_user_model()




########################################################### Authentication ###########################################################

def testing(request):
        return render(request,'main/home1.html')


class register_as_company(View):
    ''' This view is used for regisitering the company '''
    
    form_class = CompanySignUpForm
    initial={'key':'value'}
    template_name="company/Employer-Signup.html"
    
    def get(self,request):
        form = self.form_class(initial=self.initial)
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form=self.form_class(request.POST or None,request.FILES or None)
        # for field in form:
        #     print("Field Error:", field.name,  field.errors)
        if form.is_valid():      
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            phone_no = form.cleaned_data.get('phone_no')
            print(phone_no)
            user = User.objects.create_user(email, password)

            user.active = False
            user.name = form.cleaned_data.get('name')
            user.is_company = True
            user.save()

            company = Company.objects.create(user = user)

            company.save()

            
            current_site = get_current_site(request)
            mail_subject = 'Verify your email to activate your account.'
            message = render_to_string('main/acc_active_email.html', {
                   'user': user,
                   'domain': current_site.domain,
                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                   'token': account_activation_token.make_token(user),
                })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return HttpResponse('Please confirm your email address to complete the registration') 

        else:      
            print("ERROR")                                                         
            # for msg in form.error_messages:                   
            #     print(msg)
            #     messages.error(request, f"{msg}: {form.error_messages[msg]}")  
            for field, items in form.errors.items():
                for item in items:
                    print(field)
                    print(item)
                    messages.error(request, f"{field}: {item}")

            form=self.form_class(initial=self.initial)
            return render(request ,self.template_name,{'form':form})


class register_as_student(View):
    ''' This view is for registering the student '''
    form_class=StudentSignUpForm
    initial={'key':'value'}
    template_name="Users/homepage.html"

    def get(self,request):
        form=self.form_class(initial=self.initial)
        return render(request,self.template_name,{'form':form})
    
    def post(self,request):
        form=self.form_class(request.POST or None,request.FILES or None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(email, password)
        
            user.active = False
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.is_normal = True
            user.save()

            student = Student.objects.create(user = user)
            student.save()

            current_site = get_current_site(request)
            mail_subject = 'Verify your email to activate your account.'
            message = render_to_string('main/acc_active_email.html', {
                   'user': user,
                   'domain': current_site.domain,
                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                   'token': account_activation_token.make_token(user),
                })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration') 
            
        else:
            return redirect("main:homepage")


def activate(request, uidb64, token):
    ''' View for activating the user after email verification '''
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.active = True
        user.save()
        login(request, user)

        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

class login_request(View):
    form_class = AuthenticationForm
    initial={'key':'value'}
    template_name="Users/homepage.html"
    
    def get(self,request):
        print("Breakpointget")

        form=self.form_class(initial=self.initial)
        return render(request,self.template_name,{'form':form})
    
    def post(self,request):
        print("Breakpointpost")
        form=self.form_class(request=request,data=request.POST)
        if form.is_valid():                                                  
            email = form.cleaned_data.get('username')                     
            password = form.cleaned_data.get('password')    
            user = authenticate(email = email, password = password)
            
            if user is not None:
                login(request, user)                                         
                
                if user.is_normal:
                  return redirect("main:student")
                else:
                  return redirect("main:company")                               
            else:                                                            
                messages.error(request, "Invalid username or password.")     
                form=self.form_class(initial=self.initial)
                return render(request ,self.template_name,{'form':form})

        else:
            email = form.cleaned_data.get('username')                     
            password = form.cleaned_data.get('password')                     
            user = authenticate(email = email, password=password)
            
            try:
                user=User.objects.get(email = email)
                if user.is_active is False:
                    current_site = get_current_site(request)
                    mail_subject = 'Verify your email to activate your account.'
                    message = render_to_string('main/acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                        })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.send()
                    return HttpResponse("Verify your Email first")
            except:                                                                    
                messages.error(request, "Invalid username or password.")         
            
            form=self.form_class(initial=self.initial)
            return render(request ,self.template_name,{'form':form})


class logout_request(View):
    def get(self,request):
        logout(request)
        return redirect("main:homepage") 


class change_password(View):
    ''' View to change the password '''
    def get(self, request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        try :
            form = PasswordChangeForm(user=request.user)
        except:
            return redirect("main:homepage")
        args = {'form': form}
        return render(request, 'main/change_password.html', args)

    def post(self, request):
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, form.user)

            messages.success(request, 'Password Changed Successfully!!')

            if user.is_normal:
                return redirect(reverse('main:student'))
            else:
                return redirect(reverse('main:company'))

        else:
            messages.error(request, 'Invaild Details. Re-enter the details !!')
            return redirect(reverse('main:change_password'))


#view for homepage of our website
class homepage(View):
    ''' View for homepage of our website '''
    def get(self,request):
        service=Service.objects.all().order_by('-date_published')
        internship1=[]

        for i in service :
            print("----------------------------")
            print(i)  
        context={
            'Service':internship1
        }    
        if request.user.is_authenticated:
            if request.user.is_company:
                return redirect("main:company")
        return render(request=request,context=context, template_name="users/homepage.html")


########################################################### Company Profile ###########################################################

class company_profile(View):
    ''' view for company profile '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        
        try :      
            company = Company.objects.get(user = request.user)
        except Company.DoesNotExist :
            if request.user.is_normal :
                messages.error(request, "Access Denied")
                return redirect("main:student") 
            return redirect("main:homepage")

        return render(request=request, template_name="company/admin_home.html", context={"jobs":Service.objects.all(), "company" : company})


class edit_company_profile(View):
    ''' View for the Company to edit profile '''
    def get(self, request):
        if request.user.is_anonymous:
            return redirect("main:homepage")

        form = EditEmployerProfileForm(instance=request.user)
        try :
            company = Company.objects.get(user = request.user)
        except Company.DoesNotExist:
            if request.user.is_normal:
                return redirect("main:edit_student_profile")
            return redirect("main:homepage")

        args = {'form': form, 'company' : company}
        return render(request, 'company/edit_profile.html', args)

    def post(self, request):
        form = EditEmployerProfileForm(request.POST,request.FILES or None,instance=request.user)

        if form.is_valid():
            try :
                company = Company.objects.get(user = request.user)
                phone=request.POST.get('phone_no')
                print(phone)

            except Company.DoesNotExist:
                if request.user.is_normal:
                    return redirect("main:edit_student_profile")
                return redirect("main:homepage")

            city = form.cleaned_data.get('head_office_location')
            company.head_office_location = city
            company.phone_no=phone
            company.save()
            user=form.save()
            
            if 'image' in request.FILES:  
                company.image = request.FILES['image']
                company.save()

            messages.success(request, 'Profile updated successfully!!')
            if user.is_normal:
                return redirect("main:student")
            else:
                return redirect("main:company")


class post_service(View):
    ''' View for posting the Service '''
    def get(self, request):
        if request.user.is_anonymous:
            return redirect("main:homepage")

        if request.user.is_normal:
            messages.error(request, "Access Denied")
            return redirect("main:student")

        form = Service_Post(request.user)
        categories = Category.objects.all()
        locations = Location.objects.all()
        return render(request = request, template_name = "company/post_service.html", context={"form":form, "categories" : categories, "locations" : locations}) 

    def post(self, request):
        form = Service_Post(request.user, request.POST)
        print("dsjferfbkjsdf----------------------------------------------------")
        #imageurl= request.FILES['Service_image']
       # print(imageurl)
        if form.is_valid():
            job_profile = form.save(commit=False)
            company = Company.objects.get(user = request.user)  
            job_profile.company = company  
            job_profile.save()                
            title = form.cleaned_data.get('role')
            print("-------------------sndn cds ck---------")
            messages.success(request, f"New Service posted : {title}")   
            return redirect("main:company")
        else :
            print(form.errors)
            return redirect("main:company")


def edit_this_internship(request, pk):
    ''' View for the company to Edit an Service '''
    categories = Category.objects.all()
    locations = Location.objects.all()

    if request.user.is_anonymous:
            return redirect("main:homepage")

    try:
        job = Service.objects.get(company__user = request.user.id, pk = pk)
        print("Internship Founnnnnnnnnnnnnnnnnnnnnnnnnnd====================")
    except Service.DoesNotExist :
        messages.error(request, "Access Denied")
        if request.user.is_company :
            return redirect("main:internship_list")
        else :
            return redirect("main:student")

    if request.method=='POST':
        form=EditService(request.POST,instance=job)
        print("wg ewejkfwgedbjwkdw dwedbw dkwed.ds vsjad Founnnnnnnnnnnnnnnnnnnnnnnnnnd====================")
        category=request.POST.get('category')
        print("==============================================================================")
        print(form.errors)
        print(category)
        print("==============================================================================")
        if form.is_valid():
            print("wg ewejkfwgedbjwkdw dwedbw dkwed.ds vsjad Founnnnnnnnnnnnnnnnnnnnnnnnnnd====================")

            job=form.save()
            messages.success(request,"Service Edited successfully!!")
            return redirect("main:internship_list")

    else:
        form = EditService(instance = job)

    return render(request,"main/edit_this_internship.html",{'form':form,'i':job, "categories" : categories, "locations" : locations})


def delete_internship(request, pk):
    if request.user.is_anonymous:
            return redirect("main:homepage")
    if request.user.is_normal:
            messages.error(request, "Access Denied")
            return redirect("main:student")
    try:
        service = Service.objects.get(company__user = request.user.id, pk = pk)
    except service.DoesNotExist :
        messages.error(request, "No Service found")
        return redirect("main:service_posted")

    service.delete()
    messages.success(request, "Successfully deleted the Service")
    return redirect("main:company")

class service_posted(View):
    ''' View for company to display the internships posted '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        if request.user.is_normal:
                messages.error(request, "Access Denied")
                return redirect("main:student")
        
        try :
            company = Company.objects.get(user = request.user)
        except Company.DoesNotExist :
            return redirect("main:homepage")
        internships = Service.objects.filter(company = company)
        return render(request, 'company/posted_internship.html', {'internships': internships})


class interns_applied(View):
    ''' View for the company to see the list of applicants for the posted internships '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        if request.user.is_normal:
                messages.error(request, "Access Denied")
                return redirect("main:student")
        try : 
            applicant = Application.objects.filter(Service__company__user = request.user.id) 
        except Application.DoesNotExist :
            messages.error(request, "No Applications Found")
            return redirect("main:company")
        return render(request=request, template_name = "company/interns_applied.html",context={"applicant" : applicant})        


def application_detail(request, application_id):
    ''' View for the company to see the details of a particular application'''
    if request.user.is_anonymous:
            return redirect("main:homepage")
    if request.user.is_normal:
        messages.error(request, "Access Denied")
        return redirect("main:student")
    
    try : 
        applicant = Application.objects.get(id = application_id, Service__company__user = request.user.id)
    except Application.DoesNotExist :
        messages.error(request, "No such application exist")
        return redirect("main:company")
    return render(request,"main/intern_details.html",{'applicant' : applicant})


class accept(View):
    ''' View for accepting the Application '''
    def get(self,request, application_id):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        if request.user.is_normal:
            messages.error(request, "Access Denied")
            return redirect("main:student")
        
        try : 
            application = Application.objects.get(Service__company__user = request.user.id, id = application_id)
        except Application.DoesNotExist :
            messages.error(request, "No such application exist")
            return redirect("main:company")
        
        application.is_accept = True
        application.is_reject = False

        subject= 'Application Accepted'
        message='Hello '+ application.student.user.first_name + " " + application.student.user.last_name + ', Your application for '+ application.Service.role +' role has been accepted by '+ application.Service.company.user.name + "."
        from_email = settings.EMAIL_HOST_USER
        to_email=[application.student.user.email]
       
        #send_mail(subject,message,from_email,to_email,fail_silently=False,)
        application.save()
        
        return redirect("main:company")        


class reject(View):
    ''' View for rejecting the Application '''
    def get(self,request,application_id):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        if request.user.is_normal:
            messages.error(request, "Access Denied")
            return redirect("main:student")

        try : 
            application = Application.objects.get(Service__company__user = request.user.id, id = application_id)
        except Application.DoesNotExist :
            messages.error(request, "No such application exist")
            return redirect("main:company")
        application.is_accept = False
        application.is_reject = True

        subject= 'Application Rejected'
        message='Hello '+ application.student.user.first_name + " " + application.student.user.last_name + ', Sorry your application for '+ application.Service.role +' role has been rejected by '+ application.Service.company.user.name + "."
        from_email = settings.EMAIL_HOST_USER
        to_email=[application.student.user.email]

        #send_mail(subject,message,from_email,to_email,fail_silently=False,)
        application.save()

        return redirect("main:company")    


class accepted_interns(View):
    ''' View for the company to see the application of accepted interns '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        if request.user.is_normal:
            messages.error(request, "Access Denied")
            return redirect("main:student")

        application = Application.objects.filter(Service__company__user = request.user.id, is_accept = True)
        return render(request=request,template_name="company/accepted_interns.html",context={"application" : application},)

class rejected_interns(View):
    ''' View for the company to see the application of rejected interns '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        if request.user.is_normal:
            messages.error(request, "Access Denied")
            return redirect("main:student")

        application = Application.objects.filter(Service__company__user = request.user.id, is_reject = True)
        return render(request=request,template_name="company/rejected_interns.html",context={"application" : application},)





########################################################### Student Profile ###########################################################

class student_profile(View):
    ''' View for student profile '''
    def get(self,request):  
        if request.user.is_anonymous:
            return redirect("main:homepage")    
        try :  
            student = Student.objects.get(user = request.user)
        except Student.DoesNotExist:
            return redirect("main:homepage")                                        
        return redirect("main:homepage")          

class edit_student_profile(View):
    ''' View for student to edit profile '''
    def get(self, request):
        if request.user.is_anonymous:
            return redirect("main:homepage")
        form = EditStudentProfileForm(instance=request.user)
        
        try :
            student = Student.objects.get(user = request.user)
        except Student.DoesNotExist:
            if request.user.is_company : 
                return redirect("main:edit_company_profile")
            return redirect("main:homepage")
        args = {'form': form, 'student' : student}
        return render(request, 'Users/edit_profile.html', args)

    def post(self, request):
        form = EditStudentProfileForm(request.POST,request.FILES or None, instance=request.user)
        user = Student.objects.get(user = request.user)

        if form.is_valid():
            try :
                student = Student.objects.get(user = request.user)
            except Student.DoesNotExist:
                if request.user.is_company : 
                    return redirect("main:edit_company_profile")
                return redirect("main:homepage")


            student.phone_no = form.cleaned_data.get('phone_no')
            student.city = form.cleaned_data.get('city')
            student.save()
            user = form.save()

 
            
            messages.success(request, 'Profile updated successfully!!')

            if user.is_normal:
                return redirect("main:student")
            else:
                return redirect("main:company")
            
        print("Here HTTP ==========================")


def service_detail(request,internship_id):
    ''' View for applying to the Service '''
    if request.user.is_anonymous:
            return redirect("main:homepage")

    if request.user.is_company : 
        messages.error(request, "Access Denied")
        return redirect("main:company")

    service = Service.objects.get(pk = internship_id)
    applicant = Student.objects.get(user = request.user)
    if request.method == 'POST':
        form = Comment_form(request.POST, request.FILES or None)
        print("}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}")
        comment=form.save(commit=False)
        comment.comment_id=internship_id
        comment.save()


    form = Comment_form()
    service = get_object_or_404(Service, pk=internship_id)
    comments = Comment_model.objects.filter(comment_id=internship_id)
    return render(request,"student/service_details.html",{'Service' : service, 'student' : applicant,'comments':comments,'form':form})


class filter_internship(View):
    ''' View to show the filter Service page where the locations and category are seen '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")

        if request.user.is_company :
            messages.error(request, "Access Denied")
            return redirect("main:company")
        return render(request, template_name="main/Internship_filter.html", context={"filter":Service.objects.all()},)


class all_services(View):
    categories=['Computer','Automobile','Car Wash','Cleaning','Construction','Plumbing']
    ''' View to show all the internships posted on Internpedia '''
    def get(self,request):
        print("---------Get------------------")
        if request.user.is_anonymous is False and request.user.is_company:
            messages.error(request, "Access Denied")
            return redirect("main:company")
        categories=['Computer','Automobile','Car Wash','Cleaning','Construction','Plumbing']

        return render(request=request,
                      template_name="student/internship_list.html",
                      context={"jobs":Service.objects.all().order_by('-date_published'),'categories':categories},
                    )  
    def post(self,request):
        print("---------Post------------------")

        if request.user.is_anonymous is False and request.user.is_company:
            messages.error(request, "Access Denied")
            return redirect("main:company")
        result=Service.objects.all()
        cat= request.POST.get('category')
        loc= request.POST.get('location')
        if(cat is not None):
            print('==================================================')
            print(cat)
            print('==================================================') 
            result=result.filter(category__category_name=cat)
            print(result)
            print(loc)
        if loc == " ":
            result=result.filter(location__location_name=loc)
            print(result)
        if cat and loc is None:
            result=Service.objects.all()
        clear=True
        categories=['Computer','Automobile','Car Wash','Cleaning','Construction','Plumbing']

        return render(request=request,
                      template_name="student/internship_list.html",
                      context={"jobs":result,'clear':clear,'loc':loc,'cat':cat,'categories':categories},
                    ) 


class internships_by_location(View):
    ''' View to show internships based on the location '''
    def get(self, request, location_id):
        if request.user.is_anonymous is False and request.user.is_company:
            messages.error(request, "Access Denied")
            return redirect("main:company")
        d = Service.objects.filter(location = location_id)
        return render(request=request,template_name="main/jobs_list.html",context={"jobs":d})

class internships_by_category(View):
    ''' View to show internships based on the category '''
    def get(self, request, category_id):
        if request.user.is_anonymous is False and request.user.is_company:
            messages.error(request, "Access Denied")
            return redirect("main:company")
        d = Service.objects.filter(category = category_id)
        return render(request=request,template_name="main/jobs_list.html",context={"jobs":d})    

class myapplication(View):
    ''' View for Student to check the status of his application '''
    def get(self,request):
        if request.user.is_anonymous:
            return redirect("main:homepage")

        if request.user.is_company : 
            messages.error(request, "Access Denied")
            return redirect("main:company")

        try :
            application = Application.objects.filter(student__user = request.user.id)
        except Application.DoesNotExist :
            messages.error(request, "No Applications Found")
            return redirect("main:student")
        return render(request=request,template_name="student/myapplication.html",context={"application" : application})
