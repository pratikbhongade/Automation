import os
import pythoncom
import win32com.client as win32

def send_email(subject, validation_results, success, log_file_path):
    email_body = (
        "<html>"
        "<body style='font-family: Arial, sans-serif;'>"
        "<p>Hi Team,</p>"
        "<p>Please find the validation result of <strong>FPA IT Application</strong>:</p>"
        "<pre style='font-size: 14px; color: #333;'>"
    )

    for result, status in validation_results:
        email_body += f"{result}\n"

    email_body += "</pre>"
    if success:
        email_body += "<p style='font-size: 18px; color: green;'><strong>Validation Successful</strong></p>"
    else:
        email_body += "<p style='font-size: 18px; color: red;'><strong>Validation Failed</strong></p>"
    
    email_body += (
        "<p>Best regards,</p>"
        "<p><strong>Your Name</strong><br>"
        "Your Position<br>"
        "Your Contact Information</p>"
        "</body>"
        "</html>"
    )

    pythoncom.CoInitialize()
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = 'Pratik_Bhongade@keybank.com'  # Replace with the recipient email addresses
        mail.Subject = subject
        mail.HTMLBody = email_body

        # Check if the log file exists before attaching it
        if os.path.exists(log_file_path):
            mail.Attachments.Add(log_file_path)  # Attach the log file
        else:
            print(f"Log file not found: {log_file_path}")

        mail.Send()
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        pythoncom.CoUninitialize()
