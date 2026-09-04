from pathlib import Path
import random

from kivy.config import Config
Config.set('kivy', 'video', 'ffpyplayer')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.uix.behaviors import ButtonBehavior

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
WHITE = (1, 1, 1, 1)
MUTED = (.72, .75, .80, 1)
PINK = (1, .31, .70, 1)
CYAN = (.27, .84, 1, 1)
GREEN = (.20, 1, .40, 1)
BLACK = (.008, .01, .015, 1)


def asset(*parts):
    return ASSETS.joinpath(*parts)


def find_image(folder, stem):
    base = ASSETS / 'tabs' / folder
    for ext in ('.png', '.jpg', '.jpeg', '.webp', '.bmp'):
        p = base / f'{stem}{ext}'
        if p.exists():
            return p
    return None


def make_label(text, size, color=WHITE, bold=False, **kwargs):
    kwargs.setdefault('halign', 'center')
    kwargs.setdefault('valign', 'middle')
    return Label(text=text, font_size=size, color=color, bold=bold, **kwargs)


class FixedStage(FloatLayout):
    """Fill the entire live iOS viewport; do not letterbox or pillarbox."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stage = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.stage)
        with self.canvas.before:
            Color(*BLACK)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._layout, size=self._layout)
        Clock.schedule_once(self._layout, 0)
        Clock.schedule_once(self._layout, 0.2)

    def _layout(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.stage.pos = self.pos
        self.stage.size = self.size


class FittedImage(Image):
    def __init__(self, **kwargs):
        kwargs.setdefault('fit_mode', 'contain')
        kwargs.setdefault('size_hint', (1, 1))
        super().__init__(**kwargs)


class CleanVideo(FloatLayout):
    """Full-screen video that stretches to the complete landscape viewport."""

    def __init__(self, path, on_finished=None, double_tap_exit=False, **kwargs):
        super().__init__(**kwargs)
        self.path = Path(path)
        self.on_finished = on_finished
        self.double_tap_exit = double_tap_exit
        self.finished_once = False
        self.last_tap = -10.0
        self._poll = None
        self._show_event = None

        with self.canvas.before:
            Color(*BLACK)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._layout, size=self._layout)

        # The video stage fills the real iOS viewport. fit_mode='fill' deliberately
        # stretches the source so there are no side bars or top/bottom bars.
        self.stage = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.stage)
        self.video = Video(
            source=str(self.path),
            state='stop',
            options={'eos': 'stop'},
            volume=1.0,
            fit_mode='fill',
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
            opacity=0,
        )
        self.stage.add_widget(self.video)
        self.video.bind(on_eos=self._eos)
        self.video.bind(texture=self._texture_ready)
        Clock.schedule_once(self._layout, 0)
        Clock.schedule_once(self._layout, 0.2)

    def _layout(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.stage.pos = self.pos
        self.stage.size = self.size

    def _texture_ready(self, *_):
        if self.video.texture:
            self.video.opacity = 1

    def start(self):
        self.finished_once = False
        self.video.opacity = 0
        try:
            self.video.state = 'stop'
            self.video.unload()
        except Exception:
            pass
        if not self.path.exists():
            Clock.schedule_once(lambda dt: self.finish(), .2)
            return
        self.video.source = str(self.path)
        self._show_event = Clock.schedule_once(self._begin, .12)
        self._poll = Clock.schedule_interval(self._check_position, .08)

    def _begin(self, _dt):
        if not self.finished_once:
            try:
                self.video.state = 'play'
            except Exception:
                pass

    def _check_position(self, _dt):
        if self.finished_once:
            return False
        duration = float(getattr(self.video, 'duration', 0) or 0)
        position = float(getattr(self.video, 'position', 0) or 0)
        if duration > 1 and position >= max(0.1, duration - 0.15):
            self.finish()
            return False
        return True

    def _eos(self, *_):
        self.finish()

    def finish(self):
        if self.finished_once:
            return
        self.finished_once = True
        if self._poll:
            self._poll.cancel()
            self._poll = None
        self.video.opacity = 0
        try:
            self.video.state = 'stop'
        except Exception:
            pass
        if self.on_finished:
            Clock.schedule_once(lambda dt: self.on_finished(), 0.03)

    def stop(self):
        if self._poll:
            self._poll.cancel()
            self._poll = None
        self.finished_once = True
        try:
            self.video.opacity = 0
            self.video.state = 'stop'
            self.video.unload()
        except Exception:
            pass

    def on_touch_up(self, touch):
        if self.double_tap_exit and self.collide_point(*touch.pos):
            now = Clock.get_time()
            if now - self.last_tap < .42:
                self.finish()
                self.last_tap = -10
                return True
            self.last_tap = now
            return True
        return super().on_touch_up(touch)


class Boot(Screen):
    def on_enter(self, *_):
        self.clear_widgets()
        root = FixedStage()
        self.add_widget(root)
        box = BoxLayout(orientation='vertical', padding=28, spacing=8, size_hint=(1, 1))
        box.add_widget(make_label('VICE CITY DEVELOPMENT ENVIRONMENT', 16, GREEN, True,
                                  size_hint_y=None, height=38))
        out = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        lines = [
            '[BOOT] VICE CITY DEVELOPMENT ENVIRONMENT',
            '[BOOT] Initializing build pipeline...',
            '[BOOT] Starting asset registry...',
        ]
        names = ['world_streaming.cpp', 'city_runtime.cpp', 'vehicle_manager.cpp',
                 'character_system.cpp', 'weather_system.cpp', 'lighting_system.cpp',
                 'water_system.cpp', 'audio_engine.cpp', 'ui_system.cpp',
                 'camera_system.cpp', 'render_pipeline.cpp', 'shader_cache.bin']
        for _ in range(55):
            lines.append(
                f"[{random.choice(['BUILD','LOAD ','INIT ','LINK ','CACHE','SCAN '])}] "
                f"file: {random.choice(names)} | "
                f"{random.choice(['loading','initialized','linked','packed','ready'])}"
            )
        lines += [
            '[OK   ] renderer initialized', '[OK   ] interface initialized',
            '[OK   ] development environment ready', '------------------------------------------',
            'VICE CITY DEVELOPMENT BUILD', 'BUILD: ALPHA', 'REVISION: 4217',
            '------------------------------------------', '[ OK ]'
        ]
        self._lines = lines
        self._i = 0
        out.bind(minimum_height=out.setter('height'))
        box.add_widget(out)
        root.stage.add_widget(box)
        self._event = Clock.schedule_interval(lambda dt: self._tick(out), .035)

    def _tick(self, out):
        for _ in range(4):
            if self._i >= len(self._lines):
                break
            out.add_widget(make_label(self._lines[self._i], 11, GREEN,
                                      size_hint_y=None, height=18, halign='left'))
            self._i += 1
        if self._i >= len(self._lines):
            self._event.cancel()
            Clock.schedule_once(lambda dt: self.manager.switch_to(self.manager.get_screen('loading')), .12)
            return False
        return True


class Loading(Screen):
    def on_enter(self, *_):
        self.clear_widgets()
        self.player = CleanVideo(asset('videos', 'loading.mp4'), self.finished)
        self.add_widget(self.player)
        self.player.start()

    def finished(self):
        self.manager.current = 'menu'

    def on_leave(self, *_):
        if hasattr(self, 'player'):
            self.player.stop()


class MenuCard(ButtonBehavior, FloatLayout):
    """Uniform full-screen menu card."""

    def __init__(self, key, title, desc, image_path=None, background_path=None,
                 active=False, on_activate=None, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.active = active
        self.on_activate = on_activate

        with self.canvas.before:
            Color(0.01, 0.015, 0.025, 0.24)
            self.card_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        with self.canvas.after:
            Color(1, 1, 1, 0.34)
            self.border = Line(rounded_rectangle=(0, 0, 0, 0, 10), width=1.05)
        self.bind(pos=self._sync, size=self._sync)

        if image_path and Path(image_path).exists():
            self.art = Image(
                source=str(image_path),
                fit_mode='cover',
                size_hint=(1, 1),
                pos_hint={'x': 0, 'y': 0},
            )
            self.add_widget(self.art)

        with self.canvas.after:
            Color(0, 0, 0, 0.06)
            self.art_shade = Rectangle(pos=self.pos, size=self.size)
            Color(0.005, 0.008, 0.012, 0.58)
            self.text_panel = Rectangle(pos=self.pos, size=(self.width, self.height * .31))

        self.add_widget(make_label(
            title, 16 if key != 'DEVELOPER' else 14.5, WHITE, True,
            size_hint=(.94, .10), pos_hint={'x': .03, 'y': .085},
            text_size=(None, None)
        ))
        self.add_widget(make_label(
            desc, 7.6, (.82, .85, .89, 1), False,
            size_hint=(.94, .09), pos_hint={'x': .03, 'y': .025},
            text_size=(None, None)
        ))

    def _sync(self, *_):
        self.card_bg.pos = self.pos
        self.card_bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 10)
        self.art_shade.pos = self.pos
        self.art_shade.size = self.size
        self.text_panel.pos = (self.x, self.y)
        self.text_panel.size = (self.width, self.height * .31)

    def on_release(self):
        if self.active and self.on_activate:
            self.on_activate(self.key)


class Menu(Screen):
    def on_enter(self, *_):
        self.clear_widgets()
        root = FixedStage()
        self.add_widget(root)

        bg = find_image('story', 'background')
        if bg:
            root.stage.add_widget(Image(
                source=str(bg), fit_mode='cover', size_hint=(1, 1),
                pos_hint={'x': 0, 'y': 0}
            ))
        else:
            with root.stage.canvas.before:
                Color(*BLACK)
                Rectangle(pos=root.stage.pos, size=root.stage.size)

        content = FloatLayout(size_hint=(1, 1), pos=(0, 0))
        root.stage.add_widget(content)

        content.add_widget(make_label(
            'V I C E   C I T Y', 38, WHITE, True,
            size_hint=(1, .10), pos_hint={'center_x': .5, 'top': .965}
        ))
        content.add_widget(make_label(
            'INTERNAL ALPHA ENVIRONMENT   //   BUILD 0.6.13   //   REVISION 4217',
            9.2, (1, .72, .84, 1), False,
            size_hint=(1, .045), pos_hint={'center_x': .5, 'top': .885}
        ))
        content.add_widget(make_label(
            'ONLINE  /  DEV BUILD', 9.2, CYAN, True,
            size_hint=(None, .05), width=165,
            pos_hint={'right': .97, 'top': .955}
        ))

        tabs = [
            ('STORY', 'STORY MODE', 'PLAY THE CAMPAIGN / STORY VIDEO', 'story', 'story', True),
            ('CHARACTERS', 'CHARACTERS', 'LUCIA / JASON CHARACTER TEST', 'characters', 'characters', False),
            ('MAP', 'MAP', 'OPEN THE VICE CITY WORLD MAP', 'map', 'map', False),
            ('OPTIONS', 'OPTIONS', 'DISPLAY / GRAPHICS / GAME SETTINGS', 'options', 'options', False),
            ('DEVELOPER', 'DEVELOPER', 'DEV TOOLS / CONSOLE / BUILD PIPELINE', 'developer', 'developer', False),
        ]

        row = BoxLayout(
            orientation='horizontal', spacing=12,
            size_hint=(.94, .46),
            pos_hint={'center_x': .5, 'y': .255},
        )
        for key, title, desc, folder, stem, active in tabs:
            art = find_image(folder, stem)
            card_bg = find_image(folder, 'background')
            card = MenuCard(
                key, title, desc,
                image_path=art, background_path=card_bg,
                active=active, on_activate=self.activate,
            )
            row.add_widget(card)
        content.add_widget(row)

        content.add_widget(make_label(
            'SELECT A TAB   •   TAP TO OPEN', 9.2, WHITE, True,
            size_hint=(1, .045), pos_hint={'center_x': .5, 'y': .175}
        ))
        content.add_widget(make_label(
            'TOUCH-FIRST iOS BUILD  •  FULL-SCREEN LANDSCAPE', 8.1, MUTED,
            size_hint=(1, .035), pos_hint={'center_x': .5, 'y': .105}
        ))
        content.add_widget(make_label(
            'STORY MODE IS THE ONLY ACTIVE TAB IN THIS BUILD', 8,
            (1, .70, .80, 1),
            size_hint=(1, .03), pos_hint={'center_x': .5, 'y': .05}
        ))

    def activate(self, key):
        if key == 'STORY':
            self.manager.current = 'story'


class Story(Screen):
    def on_enter(self, *_):
        self.clear_widgets()
        self.player = CleanVideo(asset('videos', 'story.mp4'), self.done, double_tap_exit=True)
        self.add_widget(self.player)
        self.player.start()

    def done(self):
        self.manager.current = 'menu'

    def on_leave(self, *_):
        if hasattr(self, 'player'):
            self.player.stop()


class GTA6iOS(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)

        def sync_landscape(_dt):
            try:
                if Window.width < Window.height:
                    Window.rotation = 90
            except Exception:
                pass

        Clock.schedule_once(sync_landscape, 0)
        Clock.schedule_once(sync_landscape, .15)
        Window.bind(on_rotate=lambda _window, _rotation: Clock.schedule_once(sync_landscape, 0))

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(Boot(name='boot'))
        sm.add_widget(Loading(name='loading'))
        sm.add_widget(Menu(name='menu'))
        sm.add_widget(Story(name='story'))
        return sm


if __name__ == '__main__':
    GTA6iOS().run()
