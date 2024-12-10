import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import subprocess
from datetime import datetime
import logging
from pathlib import Path
from winotify import Notification, audio


class NotificationService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DailyGreetingsService"
    _svc_display_name_ = "Daily Greetings Notification Service"
    _svc_description_ = "Displays good morning and good night notifications at specified times"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        
        # Create log directory if it doesn't exist
        log_dir = Path("F:\\DailyGreetings")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=log_dir / 'service.log',
            level=logging.DEBUG,  # Changed to DEBUG for more detailed logging
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Log service initialization
        logging.info("Service initialized")

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        logging.info("Service stop requested")

    def SvcDoRun(self):
        """Main service run method"""
        try:
            self.main()
        except Exception as e:
            logging.error(f"Service error: {str(e)}", exc_info=True)
            servicemanager.LogErrorMsg(str(e))

    def show_notification(self, title, message):
        """Call the external notification script."""
        try:
            script_path = "F:\\DailyGreetings\\notify.py"
            result = subprocess.run(
                ["python", script_path, title, message],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logging.info(f"Notification sent: {title} - {message}")
            else:
                logging.error(f"Helper script error: {result.stderr}")
        except Exception as e:
            logging.error(f"Failed to call notification script: {str(e)}", exc_info=True)

    def main(self):
        """Main service logic"""
        logging.info("Service started - sending test notification")
        
        # Send test notification on service start
        self.show_notification(
            "Service Started",
            "Daily Greetings Service is now running!"
        )
        
        last_morning = False
        last_evening = False
        
        while True:
            try:
                current_time = datetime.now()
                time_str = current_time.strftime("%H:%M")
                
                # Log current check
                logging.debug(f"Checking time: {time_str}")
                
                # Morning notification at 9:00 AM
                if time_str == "20:30" and not last_morning:
                    success = self.show_notification(
                        "Hello Master! ☀️",
                        "Let's Code!"
                    )
                    last_morning = True
                    logging.info(f"Morning notification sent: {success}")
                elif time_str != "20:30":
                    last_morning = False
                
                # Evening notification at 6:30 PM
                if time_str == "23:00" and not last_evening:
                    success = self.show_notification(
                        "Good Night! 🌙",
                        "Have a peaceful evening!"
                    )
                    last_evening = True
                    logging.info(f"Evening notification sent: {success}")
                elif time_str != "23:00":
                    last_evening = False
                
                # Check if service should stop
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    logging.info("Stop event received")
                    break
                
                # Wait for 60 seconds before next check
                time.sleep(60)
                
            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}", exc_info=True)
                time.sleep(30)  # Wait before retrying

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(NotificationService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(NotificationService)
