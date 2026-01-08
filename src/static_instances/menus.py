from src.datatypes.menu import Menu
import src.static_instances.button_factories as button_factories


menu_main = Menu(
    title="Main menu:",
    buttons_factory=button_factories.buttons_factory_main,
)

menu_channels = Menu(
    title="Channels:",
    buttons_factory=button_factories.buttons_factory_channels,
)
