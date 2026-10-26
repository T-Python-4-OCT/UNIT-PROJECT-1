
"""وكيل LiveKit الصوتي لتطبيق تيسير."""

from pathlib import Path

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, silero

from voice.livekit_munsit_stt import LiveKitMunsitSTT
from voice.mac_livekit_tts import MacLiveKitTTS


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


class TaysirLiveKitAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "أنت المساعد الصوتي لتطبيق تيسير. "
                "تحدث باللغة العربية بوضوح واختصار. "
                "ساعد المستخدم في التنقل داخل التطبيق. "
                "لا تخترع آيات قرآنية أو تفسيرًا غير موثوق. "
                "عند طلب تلاوة القرآن، وجّه المستخدم إلى مشغل "
                "التلاوة الأصلي في التطبيق، ولا تولّد تلاوة اصطناعية."
            )
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=LiveKitMunsitSTT(),
        vad=silero.VAD.load(),
        llm=openai.LLM(
            model="qwen3:14b",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        ),
        tts=MacLiveKitTTS(voice="Majed"),
    )

    await ctx.connect()

    await session.start(
        room=ctx.room,
        agent=TaysirLiveKitAgent(),
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
