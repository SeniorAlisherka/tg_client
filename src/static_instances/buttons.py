# src/static_instances/buttons.py
from src.datatypes.button import Button
import src.static_instances.button_actions as button_actions


main_1 = Button("1", "1) Who am I?", button_actions.main_1)
main_2 = Button("2", "2) Channels", button_actions.main_2)
main_q = Button("q", "q) Quit", button_actions.main_q)

channels_b = Button("b", "b) Back", button_actions.channels_b)

channel_1 = Button("1", "1) Supergroup ID", button_actions.channel_1)
channel_2 = Button("2", "2) Show missing students", button_actions.channel_2)
channel_b = Button("b", "b) Back", button_actions.channel_b)
