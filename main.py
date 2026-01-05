import os
import tempfile
import librosa
from pydub import AudioSegment


FILES = [
    # "cancion1.mp3",
    # "cancion2.mp3",
    # "cancion3.mp3",
    # ...
    ]

CROSSFADE_MS = 6000
OUTPUT_FILE = "DJ_SET_FINAL.mp3"

def detect_bpm(path):
    audio = AudioSegment.from_file(path)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio.export(tmp.name, format="wav")
        y, sr = librosa.load(tmp.name, mono=True)

    os.remove(tmp.name)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return round(float(tempo))



def safe_bpm(bpm):
    """
    Evita BPM absurdos (muy común en música no electrónica)
    """
    if bpm < 60:
        return bpm * 2
    if bpm > 180:
        return bpm / 2
    return bpm


def change_tempo(audio, ratio):
    return audio._spawn(
        audio.raw_data,
        overrides={"frame_rate": int(audio.frame_rate * ratio)}
    ).set_frame_rate(audio.frame_rate)


def dj_mix(tracks, crossfade_ms):
    mix = tracks[0]
    for track in tracks[1:]:
        mix = mix.append(track, crossfade=crossfade_ms)
    return mix


def main():
    print("🎧 Auto-DJ iniciado...\n")

    base_bpm_raw = detect_bpm(FILES[0])
    base_bpm = safe_bpm(base_bpm_raw)

    print(f"🎚 BPM base: {base_bpm} (track 1)\n")

    processed_tracks = []

    for file in FILES:
        print(f"🔍 Procesando: {file}")

        audio = AudioSegment.from_file(file)

        bpm_raw = detect_bpm(file)
        bpm = safe_bpm(bpm_raw)

        print(f"   BPM detectado: {bpm_raw} → usado: {bpm}")

        ratio = base_bpm / bpm
        audio = change_tempo(audio, ratio)

        processed_tracks.append(audio)

    print("\n🔀 Mezclando tracks...")
    final_mix = dj_mix(processed_tracks, CROSSFADE_MS)

    print(f"💾 Exportando: {OUTPUT_FILE}")
    final_mix.export(OUTPUT_FILE, format="mp3", bitrate="320k")

    print("\n✅ DJ SET FINALIZADO")

if __name__ == "__main__":
    main()
