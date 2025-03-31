import sounddevice as sd
import numpy as np
import scipy.signal as signal
import torch
import threading
from queue import Queue
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

# Initialize model and feature extractor
model = Wav2Vec2ForSequenceClassification.from_pretrained(
    "r-f/wav2vec-english-speech-emotion-recognition"
)
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
    "r-f/wav2vec-english-speech-emotion-recognition"
)

# Audio configuration
SAMPLE_RATE = 16000
CHUNK_DURATION = 1  # Process every 2 seconds
CHUNK_SAMPLES = SAMPLE_RATE * CHUNK_DURATION

# Emotion label mapping (verify with model.config.label2id)
EMOTION_LABELS = {
    0: "angry",
    1: "calm",
    2: "disgust",
    3: "fearful",
    4: "happy",
    5: "neutral",
    6: "sad",
    7: "surprised"
}

# Audio buffer and queue
audio_queue = Queue()
audio_buffer = np.array([], dtype=np.float32)

def audio_callback(indata, frames, time, status):
    """Collect audio samples from the microphone"""
    audio_queue.put(indata.copy())



def apply_noise_reduction(audio_data, sample_rate=16000):
    """Apply basic noise reduction to audio signal"""
    # High-pass filter to remove low-frequency noise
    b, a = signal.butter(5, 100/(sample_rate/2), 'highpass')
    filtered_audio = signal.filtfilt(b, a, audio_data)
    
    # Optional: Simple noise gate (eliminate very quiet signals)
    noise_threshold = 0.005  # Adjust based on your environment
    gate_audio = np.where(np.abs(filtered_audio) < noise_threshold, 0, filtered_audio)
    
    return gate_audio

# Modify your process_audio_chunk function:
def process_audio_chunk(chunk):
    # Apply noise reduction
    clean_chunk = apply_noise_reduction(chunk, SAMPLE_RATE)
    
    inputs = feature_extractor(
        clean_chunk,
        sampling_rate=SAMPLE_RATE,
        return_tensors="pt",
        padding=True
    )
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_label = torch.argmax(predictions).item()
    
    return EMOTION_LABELS.get(predicted_label, "unknown")

# def process_audio_chunk(chunk):
    """Process audio through the emotion recognition model"""
    inputs = feature_extractor(
        chunk,
        sampling_rate=SAMPLE_RATE,
        return_tensors="pt",
        padding=True,
        # truncation=True
    )
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_label = torch.argmax(predictions).item()
    
    return EMOTION_LABELS.get(predicted_label, "unknown")

def shift_frustration_level(emotion):
    global frustration_level
    shift_down = ["angry", "disgust", "fearful", "sad"]
    shift_up = ["calm", "happy", "neutral", "surprised"]
    if emotion in shift_down and frustration_level > 1:
        frustration_level -= 1
    elif (emotion in shift_up and frustration_level < 3):
        frustration_level += 1
        
    print("Frustration Level: ", frustration_level)

def realtime_processing():
    """Process audio chunks from the queue"""
    global audio_buffer
    while True:
        # Get audio data from queue
        data = audio_queue.get()
        audio_buffer = np.append(audio_buffer, data.flatten())
        
        # Process when buffer has enough samples
        while len(audio_buffer) >= CHUNK_SAMPLES:
            # Extract chunk and update buffer
            process_chunk = audio_buffer[:CHUNK_SAMPLES]
            audio_buffer = audio_buffer[CHUNK_SAMPLES:]
            
            # Get and display emotion
            emotion = process_audio_chunk(process_chunk)
            shift_frustration_level(emotion)
            print(f"Recognized emotion: {emotion}")


if __name__ == "__main__":
    # Start audio stream
    stream = sd.InputStream(
        callback=audio_callback,
        channels=1,
        samplerate=SAMPLE_RATE,
        dtype=np.float32
    )
    global frustration_level
    frustration_level = 2
    
    with stream:
        print("Real-time emotion recognition started...")
        print("Press Ctrl+C to stop\n")
        
        # Start processing thread
        processing_thread = threading.Thread(
            target=realtime_processing,
            daemon=True
        )
        processing_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nStopped real-time processing")