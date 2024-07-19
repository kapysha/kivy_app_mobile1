from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivy.uix.popup import Popup
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid, ApiIdInvalid
from kivymd.uix.textfield import MDTextField

number = None
phone_code_hash = None
app = None
popup2 = None
passpopup1 = None


class ContentNavigationDrawer(BoxLayout):
    drawer = ObjectProperty()
    screen_manager = ObjectProperty()


class SendPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = app

    def authorization(self):
        if len(self.ids.code_input.text) == 5:
            try:
                self.dismiss()
                self.app.sign_in(number, phone_code_hash, self.ids.code_input.text)
                MyBoxLayout().MDDialogs(text='Вы успешно вошли!', title='Информация')
            except SessionPasswordNeeded:
                passpopup = PasswordPopup()
                passpopup.open()
                global passpopup1
                passpopup1 = passpopup
            except PhoneCodeInvalid:
                self.dismiss()
                MyBoxLayout().MDDialogs(text='Код неверный! Зарегестрируйтесь заново.')
        else:
            MyBoxLayout().MDDialogs(text="Код должен быть длиной в 5 символов!")


class PasswordPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.size_hint = (0.8, 0.3)
        self.title_size = '25sp'
        self.title = 'Введите пароль'
        self.title_align = 'center'
        layout = BoxLayout(orientation='vertical', padding=16, spacing=12)

        self.pass_input = MDTextField(font_size='18sp', multiline=True, size_hint_y=None,
                                      height='30sp', text_color_focus="white", line_color_focus="white",
                                      text_color_normal=(213 / 255, 210 / 255, 210 / 255, 1))
        layout.add_widget(self.pass_input)

        button = MDRectangleFlatButton(text='Отправить', pos_hint={"center_x": .5}, _min_width=300)
        button.bind(on_press=self.check_passw)
        layout.add_widget(button)
        self.add_widget(layout)

    def check_passw(self, instance):
        password = self.pass_input.text
        if not password:
            MyBoxLayout().MDDialogs(text='Пароль должен содержать хоть какие-то символы!')
            return
        try:
            self.app.check_password(password)
            passpopup1.dismiss()
            MyBoxLayout().MDDialogs(text='Вы успешно вошли!', title='Информация')
        except PasswordHashInvalid:
            passpopup1.dismiss()
            MyBoxLayout().MDDialogs(text='Пароль неверный! Зарегистрируйтесь заново.')


class MyBoxLayout(BoxLayout):
    popup = None
    sent_code = None

    def press_save_autoriz(self):
        self.api_hash = self.ids.hash.text
        self.api_id = self.ids.id.text
        self.number = self.ids.number.text
        self.chat_id = self.ids.chat_id.text

        if not all([self.api_hash, self.api_id, self.number, self.chat_id]):
            self.MDDialogs(text='Заполните все поля!')
            return False
        else:
            self.app = Client(f"{self.chat_id}", api_id=self.api_id, api_hash=self.api_hash)
            try:
                self.app.connect()
                self.sent_code = self.app.send_code(self.number)
            except Exception:
                self.MDDialogs(text="Такого api_id или api_hash не существует!")
                return False
            global number, phone_code_hash, app
            number = self.number
            phone_code_hash = self.sent_code.phone_code_hash
            app = self.app
            return True

    def close(self, instance):
        self.popup.dismiss()

    def MDDialogs(self, title="Ошибка", text=''):
        self.popup = MDDialog(title=title, text=text, auto_dismiss=False,
                              buttons=[MDFlatButton(
                                  text="Закрыть",
                                  theme_text_color="Custom",
                                  text_color=MainApp().theme_cls.text_color, on_release=self.close)],
                              )
        self.popup.open()



class MainApp(MDApp):
    def build(self):
        Window.size = (500, 750)
        self.theme_cls.theme_style = 'Light'
        return Builder.load_file('my.kv')


MainApp().run()
