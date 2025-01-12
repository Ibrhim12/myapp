from kivy.clock import Clock 
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout 
import os
import csv
import webbrowser
import requests
from bs4 import BeautifulSoup
from utils.phishing_detection import predict_phishing_url, predict_phishing_text


# Set window background color
Window.clearcolor = (1, 1, 1, 1)

# Load KV files
Builder.load_file("screens/splash_screen.kv")
Builder.load_file("screens/main_screen.kv")
Builder.load_file("screens/detect_url_screen.kv")
Builder.load_file("screens/detect_text_screen.kv")
Builder.load_file("screens/realtime_detection_screen.kv")
Builder.load_file("screens/view_scrapped_data_screen.kv")


# Screen Classes
class SplashScreen(Screen):
    def on_enter(self):
        # Switch to the main screen after 3 seconds
        Clock.schedule_once(self.switch_to_main_screen, 3)

    def switch_to_main_screen(self, dt):
        self.manager.current = "main"


class MainScreen(Screen):
    pass


class DetectURLScreen(Screen):
    def detect_url(self):
        url = self.ids.url_input.text.strip()
        if not url:
            self.ids.result_label.text = "Please enter a valid URL."
            return
        result = predict_phishing_url(url)
        self.ids.result_label.text = result


class DetectTextScreen(Screen):
    def detect_text(self):
        text = self.ids.text_input.text.strip()
        if not text:
            self.ids.result_label.text = "Please enter valid text."
            return
        result = predict_phishing_text(text)
        self.ids.result_label.text = result

 
class RealTimeDetectionScreen(Screen):
    def __init__(self, **kwargs):
        super(RealTimeDetectionScreen, self).__init__(**kwargs)
        self.scraped_data = ""  # Placeholder for scraped text data

        # Ensure the 'assets' folder exists
        assets_folder = 'assets'
        if not os.path.exists(assets_folder):
            os.makedirs(assets_folder)
        self.data_file = os.path.join(assets_folder, 'scraped_data.csv')

        # Real-time detection variables
        self.realtime_detection_active = False
        self.realtime_detection_event = None

    def toggle_realtime_detection(self):
        url_input = self.ids.url_input
        status_label = self.ids.status_label
        start_stop_button = self.ids.start_stop_button

        self.realtime_detection_active = not self.realtime_detection_active
        if self.realtime_detection_active:
            start_stop_button.text = 'Stop Detection'
            status_label.text = 'Web-Based Detection is Started'
            url = url_input.text.strip()
            if not url:
                status_label.text = 'Please enter a valid URL.'
                self.realtime_detection_active = False
                start_stop_button.text = 'Start Detection'
                return
            webbrowser.open(url)  # Open URL in the browser
            # Start checking and analyzing content every 2 seconds
            self.realtime_detection_event = Clock.schedule_interval(lambda dt: self.detect_phishing_in_realtime(url), 2)
        else:
            start_stop_button.text = 'Start Detection'
            status_label.text = 'Web-Based Detection is Stopped'
            if self.realtime_detection_event:
                self.realtime_detection_event.cancel()
                self.realtime_detection_event = None

    def detect_phishing_in_realtime(self, url):
        url_safe = self.check_url_for_phishing(url)
        page_text_safe = self.scrape_and_analyze_text(url)

        if not url_safe or not page_text_safe:
            self.ids.status_label.text = "Phishing Detected!"
        else:
            self.ids.status_label.text = "No Phishing Detected"

    def check_url_for_phishing(self, url):
        # Use the phishing detection model to check the URL
        return predict_phishing_url(url) == "Safe URL"

    def scrape_and_analyze_text(self, url):
        try:
            # Fetch page content from the provided URL
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text(strip=True)

            # Analyze the text using the phishing detection model
            text_safe = predict_phishing_text(page_text) == "Safe Text"

            # Save the scraped data to a CSV file
            label = "safe" if text_safe else "spam"
            self.save_data(url, page_text, label)

            return text_safe
        except requests.RequestException as e:
            print(f"Failed to retrieve page content: {e}")
            return False

    def save_data(self, url, text_data, label):
        file_exists = os.path.exists(self.data_file)
        with open(self.data_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["URL", "Scraped Text", "Label"])
            writer.writerow([url, text_data, label])

# Screen for displaying scraped data
class ViewScrappedDataScreen(Screen):
    data_file = "assets/scraped_data.csv"  # File path for scraped data

    def on_pre_enter(self, *args):
        self.load_scraped_data()

# Screen for displaying scraped data
class ViewScrappedDataScreen(Screen):
    data_file = "assets/scraped_data.csv"  # File path for scraped data

    def on_pre_enter(self, *args):
        self.load_scraped_data()

    def load_scraped_data(self):
        data_layout = self.ids.data_layout
        data_layout.clear_widgets()

        # Check if the file exists
        if not os.path.exists(self.data_file):
            label = Label(text='No data available', font_size='16sp', color=(1, 1, 1, 1))
            data_layout.add_widget(label)
            return

        # Read the CSV file and add rows to the layout
        with open(self.data_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                url = row.get('URL', 'N/A')
                text = row.get('Scraped Text', 'N/A')
                status = row.get('Status', 'Unknown')  # Add 'Status' column handling

                # Create a container for the URL, text, and status
                container = BoxLayout(
                    orientation="vertical",
                    size_hint_y=None,
                    padding=(10, 10),
                    spacing=10
                )

                # Create URL label
                url_label = Label(
                    text=f"URL: {url}",
                    size_hint_y=None,
                    halign='left',
                    valign='middle',
                    text_size=(self.width * 0.8, None),
                    color=(1, 1, 1, 1)
                )
                url_label.bind(size=url_label.setter('text_size'))

                # Create Scraped Text label
                text_label = Label(
                    text=f"Scraped Text: {text}",
                    size_hint_y=None,
                    halign='left',
                    valign='top',
                    text_size=(self.width * 0.8, None),
                    color=(1, 1, 1, 1)
                )
                text_label.bind(size=text_label.setter('text_size'))

                # Create Status label
                status_label = Label(
                    text=f"Status: {status}",
                    size_hint_y=None,
                    halign='left',
                    valign='middle',
                    text_size=(self.width * 0.8, None),
                    color=(0, 1, 0, 1) if status.lower() == "safe" else (1, 0, 0, 1)
                )
                status_label.bind(size=status_label.setter('text_size'))

                # Add labels to container
                container.add_widget(url_label)
                container.add_widget(text_label)
                container.add_widget(status_label)

                # Calculate the height of the container based on the labels
                container.height = url_label.height + text_label.height + status_label.height + 30  # Add extra space for padding

                # Add container to the data layout
                data_layout.add_widget(container)

    def calculate_label_height(self, text, font_size=16, max_width=800):
        """
        Calculate the height of a label based on the text and font size.
        """
        from kivy.core.text import Label as CoreLabel
        label = CoreLabel(text=text, font_size=font_size)
        label.refresh()
        _, height = label.texture.size
        return height


# App Class
class EZIPhishingDetectionApp(App):
    icon = "assets/icon.png"

    def build(self):
        # Verify if the icon file exists
        if not os.path.exists(self.icon):
            print("Warning: App icon file not found. Default icon will be used.")

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(DetectURLScreen(name="detect_url"))
        sm.add_widget(DetectTextScreen(name="detect_text"))
        sm.add_widget(RealTimeDetectionScreen(name="realtime_detection"))
        sm.add_widget(ViewScrappedDataScreen(name="view_scrapped_data"))
        return sm


if __name__ == "__main__":
    EZIPhishingDetectionApp().run()