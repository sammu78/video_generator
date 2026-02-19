---
title: GenAI Video Generator
emoji: 🎬
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# GenAI Video Generator

A Flask application that generates cinematic videos using Hugging Face's FLUX.1 model.

## Features
- Generate high-quality images from text prompts.
- Combine images into a video with cinematic transitions.
- Easy deployment via Docker.

## Deployment on Hugging Face Spaces
1. Create a new Space on [Hugging Face](https://huggingface.co/new-space).
2. Select **Docker** as the SDK.
3. Link your GitHub repository.
4. Add your `HF_TOKEN` as a secret in the Space settings.
