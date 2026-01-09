# src/static_instances/menus.py
from src.datatypes.menu import Menu
import src.static_instances.button_factories as button_factories

main = Menu(
    title="Main menu:",
    buttons_factory=button_factories.main,
)

channels = Menu(
    title="Channels:",
    buttons_factory=button_factories.channels,
)

channel = Menu(
    title="Channel {name}:",
    buttons_factory=button_factories.channel,
)
