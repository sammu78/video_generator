import os
import time
from flask import Flask, render_template, request, send_file, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import imageio_ffmpeg as ffmpeg

load_dotenv()

app = Flask(__name__)

# Configure MoviePy to use imageio-ffmpeg's binary
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg.get_ffmpeg_exe()

HF_TOKEN = os.getenv("HF_TOKEN")
# Using the powerful FLUX.1-schnell model for high-quality images
client = InferenceClient(api_key=HF_TOKEN)
MODEL_ID = "black-forest-labs/FLUX.1-schnell"

def query_with_retry(prompt, retries=3, delay=5):
    """Query Hugging Face API with retries for rate limits or overloaded models."""
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt + 1}: Generating image for prompt: {prompt}")
            image = client.text_to_image(prompt, model=MODEL_ID)
            return image
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if "429" in str(e) or "overloaded" in str(e).lower():
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
            raise e

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        prompt = request.form.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        image_files = []
        # Generate 3 cinematic scenes for the video
        for i in range(1):
            # Adding variety to the prompt for each scene
            scene_prompt = f"{prompt}, scene {i+1}, cinematic lighting, high detail, 4k"
            image = query_with_retry(scene_prompt)
            file_name = f"scene_{i}.png"
            image.save(file_name)
            image_files.append(file_name)

        print("Creating video from images...")
        clips = []
        for img in image_files:
            clip = ImageClip(img).set_duration(3)
            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")
        output_file = "final_video.mp4"
        video.write_videofile(output_file, fps=24, codec="libx264")

        # Explicitly close clips to free memory
        for clip in clips:
            clip.close()
        video.close()

        # Cleanup intermediate images
        for img in image_files:
            try:
                os.remove(img)
            except:
                pass

        response = send_file(output_file, as_attachment=True)
        
        # We can't easily delete the final_video.mp4 here because send_file needs it.
        # However, for the next request, it will be overwritten.
        return response

    except Exception as e:
        print(f"Generation failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
