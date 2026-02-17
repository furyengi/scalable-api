from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.email_tasks.send_welcome_email")
def send_welcome_email(user_id: int, email: str):
    """Send welcome email after registration."""
    print(f"📨 Sending welcome email to {email} (user_id={user_id})")
    # Add real email logic here e.g. SendGrid, Resend, etc.
    return {"status": "sent", "to": email}


@celery_app.task(name="app.tasks.email_tasks.send_due_date_reminder")
def send_due_date_reminder(user_id: int, task_id: int, task_title: str):
    """Send reminder when a task is approaching its due date."""
    print(f"⏰ Reminder: task '{task_title}' is due soon (user_id={user_id})")
    return {"status": "sent", "task_id": task_id}
