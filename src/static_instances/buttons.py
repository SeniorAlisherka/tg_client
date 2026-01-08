from src.datatypes.button import Button
import src.static_instances.actions as actions


button_main_1 = Button("1", "1) Who am I?", actions.action_main_1)
button_main_2 = Button("2", "2) Channels", actions.action_main_2)
button_main_q = Button("q", "q) Quit", actions.action_main_q)

button_channels_b = Button("b", "b) Back", actions.action_channels_b)
