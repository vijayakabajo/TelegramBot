from telegram.ext import Updater, CommandHandler, JobQueue
import datetime
import pytz
import json

def start(update, context):
    # Cancel the existing job if it exists
    if 'class_job' in context.chat_data:
        context.chat_data['class_job'].schedule_removal()
    if 'exam_job' in context.chat_data:
        context.chat_data['exam_job'].schedule_removal()

    with open('class_schedule.pdf', 'rb') as pdf:
        # Send the PDF file
        context.bot.send_document(chat_id=update.effective_chat.id, document=pdf)
    with open('Exam_schedule.xlsx', 'rb') as xlsx:
        # Send the XLSX file
        context.bot.send_document(chat_id=update.effective_chat.id, document=xlsx)
    # Send a welcome message to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I will also remind you about your Classes, Exams and Holidays.")

    # Schedule the send_class_reminder function to run every 60 seconds for classes
    class_job = context.job_queue.run_repeating(send_class_reminder, interval=60, first=0, context=update.effective_chat.id)
    # Store the class job in context for future reference
    context.chat_data['class_job'] = class_job

    # Schedule the send_exam_reminder function to run every 60 seconds for exams
    exam_job = context.job_queue.run_repeating(send_exam_reminder, interval=60, first=0, context=update.effective_chat.id)
    # Store the exam job in context for future reference
    context.chat_data['exam_job'] = exam_job

def send_class_reminder(context):
    # Get the current date and time
    now = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
    current_day = now.weekday()

    with open('schedule.json') as file:
        data = json.load(file)

    # Check if there's a class scheduled for the current day and time
    for cls in data['classes']:
        if current_day in cls['days'] and now.strftime('%H:%M') == cls['time']:
            # Send a reminder message to the user
            context.bot.send_message(chat_id=context.job.context, text=f"Reminder: Your {cls['name']} class is about to start.")

def send_exam_reminder(context):
    # Get the current date and time
    now = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))

    with open('exam_schedule.json') as file:
        data = json.load(file)

    # Check if there's an exam scheduled for the current date and time
    for exam in data:
        exam_date = datetime.datetime.strptime(exam['Date'], '%d-%m-%Y')
        exam_time_start, exam_time_end = exam['Timing'].split('-')
        exam_time_start = datetime.datetime.strptime(exam_time_start.strip(), '%I:%M%p')
        exam_time_end = datetime.datetime.strptime(exam_time_end.strip(), '%I:%M%p')

        # Check if the current date matches the exam date and the current time is within the exam time range
        if now.date() == exam_date.date() and exam_time_start.time() <= now.time() <= exam_time_end.time():
            # Send a reminder message to the user
            context.bot.send_message(chat_id=context.job.context, text=f"Reminder: {exam['Title']}")

def main():
    with open('schedule.json') as file:
        data = json.load(file)

    # Create an Updater and pass in your Telegram bot's API token
    updater = Updater('6031113864:AAGDZQYQTAtmtuQHAaxuXqe7KbivRLkOQCM', use_context=True)
    dp = updater.dispatcher

    # Register the start command handler
    dp.add_handler(CommandHandler('start', start))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
