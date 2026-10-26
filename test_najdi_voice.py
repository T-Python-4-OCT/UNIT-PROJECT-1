import torch
import soundfile as sf
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

device = "mps" if torch.backends.mps.is_available() else "cpu"

print(f"جاري تحميل نموذج الصوت على: {device}")

model = ChatterboxMultilingualTTS.from_pretrained(device=device)

text = "يا هلا والله، حيّاك في تيسير. وش تبي أساعدك فيه؟"

print("جاري توليد الصوت النجدي...")

audio = model.generate(
    text,
    language_id="ar",
)

audio_data = audio.squeeze().detach().cpu().numpy()

sf.write("najdi_test.wav", audio_data, model.sr)

print("تم إنشاء الملف: najdi_test.wav")
