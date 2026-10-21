"""واجهة رسومية أولية اختيارية باستخدام Tkinter من مكتبة Python القياسية."""
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from quran.quran_reader import QuranReader
from tafsir.tafsir_reader import TafsirReader

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def main():
    try:
        quran = QuranReader(DATA_DIR / "quran.json")
        tafsir = TafsirReader(DATA_DIR / "tafsir.json")
    except ValueError as error:
        messagebox.showerror("خطأ في البيانات", str(error))
        return

    root = tk.Tk()
    root.title("تيسير — المصحف الصوتي والتدبّر")
    root.geometry("850x600")
    root.configure(bg="#102C25")

    title = tk.Label(root, text="۞ تيسير ۞", font=("Geeza Pro", 28, "bold"),
                     fg="#E8D29B", bg="#102C25")
    title.pack(pady=(20, 5))
    subtitle = tk.Label(root, text="المصحف الصوتي والتدبّر",
                        font=("Geeza Pro", 15), fg="#D7E6DD", bg="#102C25")
    subtitle.pack()

    current = {"index": 0}
    verse_label = tk.Label(root, text="", wraplength=760, justify="center",
                           font=("Geeza Pro", 20), fg="#FFFFFF", bg="#17382E",
                           padx=25, pady=30)
    verse_label.pack(fill="both", expand=True, padx=25, pady=20)

    tafsir_label = tk.Label(root, text="", wraplength=760, justify="right",
                            font=("Geeza Pro", 13), fg="#E8D29B", bg="#102C25")
    tafsir_label.pack(fill="x", padx=25, pady=5)

    def render():
        if not quran.ayahs:
            verse_label.config(text="لم تُضف بيانات القرآن بعد.\nراجع README.md لإعداد البيانات.")
            tafsir_label.config(text="")
            return
        item = quran.ayahs[current["index"]]
        verse_label.config(text=f"{item['surah_name']} — الآية {item['ayah_number']}\n\n{item['text']}")
        tafsir_text = tafsir.get(item["surah_number"], item["ayah_number"])
        tafsir_label.config(text=("التفسير الميسّر: " + tafsir_text) if tafsir_text else "لا يتوفر تفسير لهذه الآية محلياً.")

    def move(amount):
        if quran.ayahs:
            current["index"] = max(0, min(len(quran.ayahs) - 1, current["index"] + amount))
            render()

    buttons = tk.Frame(root, bg="#102C25")
    buttons.pack(pady=(0, 20))
    tk.Button(buttons, text="السابق", command=lambda: move(-1), width=12).pack(side="right", padx=6)
    tk.Button(buttons, text="التالي", command=lambda: move(1), width=12).pack(side="right", padx=6)
    tk.Button(buttons, text="إغلاق", command=root.destroy, width=12).pack(side="right", padx=6)

    render()
    root.mainloop()

if __name__ == "__main__":
    main()
