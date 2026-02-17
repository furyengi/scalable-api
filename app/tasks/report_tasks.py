from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.report_tasks.generate_weekly_report")
def generate_weekly_report(user_id: int):
    """Generate and email a weekly task summary."""
    print(f"📊 Generating weekly report for user {user_id}")
    return {"status": "generated", "user_id": user_id}


@celery_app.task(name="app.tasks.report_tasks.archive_old_tasks")
def archive_old_tasks():
    """Daily job: archive tasks completed more than 30 days ago."""
    print("🗄️  Archiving old completed tasks...")
    return {"status": "done"}
