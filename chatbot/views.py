from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from .models import User, LeaveRequest, Task, Project
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
import re
import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

# Helper functions
def extract_dates(message):
    return re.findall(r'\d{2}-\d{2}-\d{4}', message)

def validate_password(password):
    if len(password) < 8:
        return "Password must be 8+ characters"
    if not any(c.isdigit() for c in password):
        return "Password must contain a number"
    return None

def check_permission(user, permission):
    if permission == "approve_leave":
        return user.is_hr
    elif permission == "assign_tasks":
        return user.is_manager
    return False

def generate_main_menu(user):
    menu = "📋 Main Menu:\n"
    menu += "• Leave requests (type 'leave')\n"
    menu += "• Task management (type 'task')\n"
    if user.is_hr or user.is_manager:
        menu += "• HR functions (type 'hr')\n"
    menu += "• Update profile (type 'update')\n"
    menu += "• Logout (type 'logout')"
    return menu

# Authentication handlers
def handle_unauthenticated(user, message):
    try:
        if user.auth_state == 'awaiting_username':
            if len(message) < 3:
                return "❌ Username must be 3+ characters"
            
            if User.objects.filter(username=message).exists():
                return "❌ Username taken. Try another"
            
            user.temp_username = message
            user.auth_state = 'awaiting_password'
            user.save()
            return "🔒 Please enter your password (8+ chars with a number)"
        
        elif user.auth_state == 'awaiting_password':
            error = validate_password(message)
            if error:
                return f"❌ {error}"
                
            user.username = user.temp_username
            user.set_password(message)
            user.auth_state = 'authenticated'
            user.temp_username = ''
            user.save()
            return f"👋 Welcome {user.username}! Type 'menu' for options"
    
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        return "⚠️ System error. Please start over."
    
    return "❌ Invalid state. Send 'hello' to restart."

def handle_authenticated(user, message):
    user.last_activity = timezone.now()
    user.save()
    
    message = message.lower().strip()
    
    if message == 'logout':
        user.auth_state = 'awaiting_username'
        user.save()
        return "👋 Logged out successfully"
    
    elif message == 'menu':
        return generate_main_menu(user)
    
    elif 'leave' in message:
        return handle_leave_request(user, message)
    
    elif 'task' in message:
        return handle_task_command(user, message)
    
    elif 'update' in message:
        return handle_profile_update(user, message)
    
    elif message in ('hello', 'hi'):
        return f"👋 Hello {user.username}! How can I help?"
    
    elif 'my name is ' in message:
        new_name = message[11:].strip().title()
        user.first_name = new_name
        user.save()
        return f"👍 I'll call you {new_name} from now on!"
    
    return "🤔 I didn't understand. Send 'menu' for options."

# Command handlers
def handle_leave_request(user, message):
    try:
        if "apply leave" in message:
            dates = extract_dates(message)
            if len(dates) == 2:
                LeaveRequest.objects.create(
                    employee=user,
                    start_date=dates[0],
                    end_date=dates[1],
                    leave_type="annual"
                )
                return "✅ Leave request submitted!"
            return "❌ Format: apply leave DD-MM-YYYY to DD-MM-YYYY"
        
        elif "approve leave" in message and check_permission(user, "approve_leave"):
            return "✅ Leave approved!"  # Implement actual approval logic
        
        return "📅 Leave commands:\n• apply leave [dates]\n• approve leave [ID]"
    
    except Exception as e:
        logger.error(f"Leave error: {str(e)}")
        return "⚠️ Error processing leave request"

def handle_task_command(user, message):
    try:
        if "assign task" in message and check_permission(user, "assign_tasks"):
            parts = message.split(' to ')
            project_part = parts[0].replace('assign task ', '').strip()
            rest = parts[1].split(': ')
            employee_part = rest[0].strip()
            desc_date = rest[1].split(' due ')
            
            Task.objects.create(
                project=Project.objects.get(name=project_part),
                assigned_to=User.objects.get(username=employee_part),
                description=desc_date[0].strip(),
                due_date=desc_date[1].strip()
            )
            return f"✅ Task assigned to {employee_part}"
        
        elif "my tasks" in message:
            tasks = Task.objects.filter(assigned_to=user)
            if tasks.exists():
                return "📌 Your tasks:\n" + "\n".join(
                    f"- {t.description} (Due: {t.due_date})" 
                    for t in tasks
                )
            return "📌 You have no tasks"
        
        return "📝 Task commands:\n• assign task [details]\n• my tasks"
    
    except Exception as e:
        logger.error(f"Task error: {str(e)}")
        return "⚠️ Error processing task"

def handle_profile_update(user, message):
    try:
        if "update phone" in message:
            new_phone = message.split('phone ')[1].strip()
            if not re.match(r'^\+?[\d\s-]{10,15}$', new_phone):
                return "❌ Invalid phone format"
            user.phone = new_phone
            user.save()
            return "✅ Phone updated!"
        
        return "📱 Profile commands:\n• update phone [number]"
    
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return "⚠️ Error updating profile"

# Main view
@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        try:
            sender_phone = request.POST.get('From', '').replace('whatsapp:', '')
            message = request.POST.get('Body', '').strip()
            
            logger.info(f"Message from {sender_phone}: {message}")
            
            # Get or create user
            try:
                user = User.objects.get(phone=sender_phone)
                # Check session timeout (30 minutes)
                if (timezone.now() - user.last_activity) > timedelta(minutes=30):
                    user.auth_state = 'awaiting_username'
                    user.save()
            except ObjectDoesNotExist:
                user = User.objects.create(
                    phone=sender_phone,
                    auth_state='awaiting_username'
                )
            
            # Process message
            if user.auth_state != 'authenticated':
                response = handle_unauthenticated(user, message)
            else:
                response = handle_authenticated(user, message)
            
            # Send response
            twiml = MessagingResponse()
            twiml.message(response)
            return HttpResponse(str(twiml), content_type="text/xml")
        
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            twiml = MessagingResponse()
            twiml.message("⚠️ System error. Please try again later.")
            return HttpResponse(str(twiml), content_type="text/xml", status=500)
    
    return HttpResponse("Invalid method", status=405)