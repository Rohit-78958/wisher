from winotify import Notification, audio

def show_notification(title, message):
    try:
        notification = Notification(
            app_id="Daily Greetings",
            title=title,
            msg=message,
            duration="long"
        )
        notification.set_audio(audio.Default, loop=False)
        notification.show()
    except Exception as e:
        print(f"Failed to show notification: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python notify_helper.py <title> <message>")
    else:
        title = sys.argv[1]
        message = sys.argv[2]
        show_notification(title, message)
