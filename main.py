from __future__ import annotations

import asyncio
import hashlib
import io
import wave
from pathlib import Path

import dotenv
import numpy as np
import streamlit as st
from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    Runner,
    SQLiteSession,
)
from agents.voice import AudioInput, VoicePipeline

from models import UserAccountContext
from my_agents.triage_agent import triage_agent
from workflow import CustomWorkflow


dotenv.load_dotenv()

st.set_page_config(
    page_title="Customer Support Agent",
    page_icon="🎧",
    layout="wide",
)

st.markdown(
    """
<style>
    .block-container {padding-top: 1.25rem; padding-bottom: 1rem;}
    [data-testid="stChatMessage"] {border-radius: 14px; padding: 0.3rem 0.5rem;}
    .support-card {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.75rem;
    }
    .small-muted {opacity: 0.72; font-size: 0.9rem;}
</style>
""",
    unsafe_allow_html=True,
)

DB_PATH = str(Path(__file__).with_name("customer-support-memory.db"))
VOICE_SAMPLE_RATE = 24_000


def run_async(coro):
    """Run an async SDK call from Streamlit's synchronous script."""
    return asyncio.run(coro)


def initialise_state() -> None:
    if "support_session" not in st.session_state:
        st.session_state.support_session = SQLiteSession(
            "customer-support-chat",
            DB_PATH,
        )
    if "active_agent" not in st.session_state:
        st.session_state.active_agent = triage_agent
    if "customer_context" not in st.session_state:
        st.session_state.customer_context = UserAccountContext(
            customer_id=1,
            name="Derek",
            email="derek@example.com",
            tier="basic",
        )
    if "last_audio_hash" not in st.session_state:
        st.session_state.last_audio_hash = None
    if "last_voice_reply" not in st.session_state:
        st.session_state.last_voice_reply = None
    if "last_voice_transcript" not in st.session_state:
        st.session_state.last_voice_transcript = None


initialise_state()
session = st.session_state.support_session
context = st.session_state.customer_context


def content_to_text(message: dict) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
            elif isinstance(text, dict) and isinstance(text.get("value"), str):
                parts.append(text["value"])
        return "\n".join(parts)
    return str(content)


async def get_history() -> list[dict]:
    return await session.get_items()


def render_history(messages: list[dict]) -> None:
    if not messages:
        with st.chat_message("assistant"):
            st.markdown(
                "Hi Derek — I can help with **account, billing, order, or technical-support** questions."
            )
        return

    for message in messages:
        role = message.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = content_to_text(message)
        if not text:
            continue
        with st.chat_message(role):
            st.markdown(text.replace("$", "\\$"))


async def run_text_agent(message: str, placeholder) -> None:
    response = ""
    try:
        stream = Runner.run_streamed(
            st.session_state.active_agent,
            message,
            session=session,
            context=context,
        )
        async for event in stream.stream_events():
            if event.type == "raw_response_event" and getattr(
                event.data, "type", None
            ) == "response.output_text.delta":
                response += event.data.delta
                placeholder.markdown(response.replace("$", "\\$") + "▌")
            elif event.type == "agent_updated_stream_event":
                st.session_state.active_agent = event.new_agent
        st.session_state.active_agent = stream.last_agent
        placeholder.markdown((response or "Done.").replace("$", "\\$"))
    except InputGuardrailTripwireTriggered:
        placeholder.warning(
            "I can only help with account, billing, order, and technical-support requests."
        )
    except OutputGuardrailTripwireTriggered:
        placeholder.warning(
            "That response was blocked because it crossed a specialist boundary. Please rephrase the support request."
        )
    except Exception as exc:
        placeholder.error(f"The support request could not be completed: {exc}")


def uploaded_wav_to_array(audio_file) -> np.ndarray:
    raw = audio_file.getvalue()
    with wave.open(io.BytesIO(raw), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frames = wav_file.readframes(wav_file.getnframes())

    if sample_width != 2:
        raise ValueError("Expected 16-bit PCM audio from the browser recorder.")

    samples = np.frombuffer(frames, dtype=np.int16)
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1).astype(np.int16)
    return samples


def pcm_chunks_to_wav(chunks: list[np.ndarray], sample_rate: int) -> bytes:
    pcm = np.concatenate(chunks).astype(np.int16) if chunks else np.array([], dtype=np.int16)
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return output.getvalue()


async def run_voice_agent(audio_file) -> tuple[bytes, str, object]:
    audio_array = uploaded_wav_to_array(audio_file)
    workflow = CustomWorkflow(
        agent=st.session_state.active_agent,
        session=session,
        context=context,
    )
    pipeline = VoicePipeline(workflow=workflow)
    result = await pipeline.run(AudioInput(buffer=audio_array))

    chunks: list[np.ndarray] = []
    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            chunks.append(np.asarray(event.data, dtype=np.int16))

    return pcm_chunks_to_wav(chunks, VOICE_SAMPLE_RATE), workflow.transcription, workflow.last_agent


with st.sidebar:
    st.header("Support Console")
    st.caption("OpenAI Agents SDK · Triage + specialist handoffs")

    selected_tier = st.selectbox(
        "Customer tier",
        ["basic", "premium", "enterprise"],
        index=["basic", "premium", "enterprise"].index(context.tier),
    )
    context.tier = selected_tier

    st.metric("Active specialist", st.session_state.active_agent.name)

    if st.button("Reset conversation", use_container_width=True):
        run_async(session.clear_session())
        st.session_state.active_agent = triage_agent
        st.session_state.last_audio_hash = None
        st.session_state.last_voice_reply = None
        st.session_state.last_voice_transcript = None
        context.activity_log.clear()
        context.troubleshooting_steps.clear()
        st.rerun()

    with st.expander("Agent activity", expanded=False):
        if context.activity_log:
            for entry in context.activity_log[-15:]:
                st.caption(entry)
        else:
            st.caption("No tools or handoffs used yet.")

st.title("🎧 Customer Support Agent")
st.caption("Type a message or record a voice message. Both channels use the same session memory and specialist-agent workflow.")

text_column, voice_column = st.columns([1.65, 1], gap="large")

with text_column:
    st.subheader("💬 Text support")
    chat_panel = st.container(height=590, border=True)
    with chat_panel:
        render_history(run_async(get_history()))

    text_message = st.chat_input(
        "Ask about your account, billing, order, or a technical issue…",
        key="text_support_input",
    )

    if text_message:
        with chat_panel:
            with st.chat_message("user"):
                st.markdown(text_message)
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                run_async(run_text_agent(text_message, response_placeholder))
        st.rerun()

with voice_column:
    st.subheader("🎙️ Voice support")

    voice_panel = st.container(height=505, border=True)
    with voice_panel:
        st.markdown(
            """
<div class="support-card">
<strong>How it works</strong><br>
<span class="small-muted">Record a message, then the voice pipeline transcribes it, runs the same support agents, and returns spoken audio in your browser.</span>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.last_voice_transcript:
            st.caption("Latest transcription")
            st.info(st.session_state.last_voice_transcript)

        if st.session_state.last_voice_reply:
            st.caption("Latest spoken response")
            st.audio(st.session_state.last_voice_reply, format="audio/wav")
        else:
            st.markdown(
                "Record your first message using the microphone control at the bottom of this panel."
            )

    # This widget intentionally appears after the fixed-height voice panel,
    # keeping the recorder at the bottom rather than above the conversation.
    audio_input = st.audio_input(
        "Record a voice message",
        sample_rate=VOICE_SAMPLE_RATE,
        key="voice_support_input",
    )

    if audio_input:
        audio_bytes = audio_input.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            with st.status("Processing voice message…", expanded=True) as status:
                try:
                    status.write("Transcribing and routing your request")
                    reply_audio, transcript, last_agent = run_async(
                        run_voice_agent(audio_input)
                    )
                    st.session_state.last_voice_reply = reply_audio
                    st.session_state.last_voice_transcript = transcript
                    st.session_state.active_agent = last_agent
                    status.update(label="Voice response ready", state="complete")
                except InputGuardrailTripwireTriggered:
                    status.update(label="Voice request blocked", state="error")
                    st.warning(
                        "I can only help with account, billing, order, and technical-support requests."
                    )
                except OutputGuardrailTripwireTriggered:
                    status.update(label="Response blocked", state="error")
                    st.warning("The generated response crossed a specialist boundary.")
                except Exception as exc:
                    status.update(label="Voice processing failed", state="error")
                    st.error(f"The voice request could not be completed: {exc}")
            st.rerun()
