import os
import pythoncom
import win32com.client as win32

def send_email(subject, validation_results, log_file_path, environment):
    email_body = (
        "<html>"
        "<body style='font-family: Arial, sans-serif;'>"
        f"<p>Hi Team,</p>"
        f"<p>Please find the validation result of <strong>FPA {environment.upper()} Environment Validation</strong>:</p>"
        "<pre style='font-size: 14px; color: #333;'>"
    )

    for result, status in validation_results:
        email_body += f"{result}\n"

    email_body += "</pre>"
    if all([status == "Success" for result, status in validation_results]):
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
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = 'Pratik_Bhongade@keybank.com'  # Replace with the recipient email addresses
    mail.Subject = subject
    mail.HTMLBody = email_body
    mail.Attachments.Add(log_file_path)  # Attach the log file
    mail.Send()
    pythoncom.CoUninitialize()
