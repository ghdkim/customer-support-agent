from __future__ import annotations

from agents import Runner
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper

from models import UserAccountContext


class CustomWorkflow(VoiceWorkflowBase):
    """Run the same multi-agent workflow for a transcribed voice turn."""

    def __init__(self, *, agent, session, context: UserAccountContext):
        self.agent = agent
        self.session = session
        self.context = context
        self.last_agent = agent
        self.transcription = ""

    async def run(self, transcription: str):
        self.transcription = transcription
        result = Runner.run_streamed(
            self.agent,
            transcription,
            session=self.session,
            context=self.context,
        )
        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            yield chunk
        self.last_agent = result.last_agent
