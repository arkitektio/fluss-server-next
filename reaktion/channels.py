from kante.channel import build_channel
from reaktion.channel_signals import RunEventSignal

run_event_channel = build_channel(
    RunEventSignal
)
