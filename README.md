# Describe Image with AI

![01](https://static.wixstatic.com/media/9cda2b_b961cadae986429eb50e7d2aab42bbfe~mv2.png)
---
![02](https://static.wixstatic.com/media/9cda2b_42ddc64d17a84e6f8b73066c73e1cee9~mv2.png)
---
![03](https://static.wixstatic.com/media/9cda2b_7731dc527b82432897d4a18fd64b9d66~mv2.png)


# What it does
Upload an image and analyze it using AI. The app generates a structured JSON output with key attributes like descriptions, aspect ratio, and more. Currently compatible with Anthropic, with support for additional models coming soon.

# Objective
Transform images into intelligent, actionable content by using AI to extract information that can be leveraged to make informed business decisions.

# Technologies & Tools Used
Python, Streamlit, Anthropic API, Docker, GitHub, GitHub Co-Pilot, ChatGPT, Claude AI.

# Installing the App Manually
Make sure you install all the required Python packages (in the requirements.txt file)

# Running the App Locally
```
streamlit run app.py
```

Then visit localhost:8501 in your browser.

# Install the app via Docker

## Manually Install and Run the Image
```
docker run -p [yourport]:8501 intelligentcontentacademy/describeimagewithai:latest
```

The first time you run it, it will actually install all the required python packages.  I wanted to keep the image small, so I didn't want to install the packages in the image.  After the first install, if you just rerun the container, it will be very quick.

Use -d to run it detached (but the first time, you won't see the Python packages installing, so the app will take around 20 seconds to be able to be used after they are installed).

## Use Docker Compose to Install and Run the Image
You can get the file [here](https://github.com/intelligentcontentacademy/describe_image_with_ai/blob/master/docker-compose.yml) or create one yourself with the following code inside of it:
 
```
services:
  describeimagewithai:
    image: intelligentcontentacademy/describeimagewithai:latest
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=YOUR_API_KEY_HERE
```

Make sure you save the file as "docker-compose.yml".  Add your API key to Anthropic in the file if you want, or you can add it later in the app itself.

You can then execute that file using the following commands:
```
# Run it attached 
docker compose up 

# Run it detached (But you won't see the python packages being installed)
docker compose up -d
```

## Running the App
Once the container is running, just open up a browser and go to localhost:8501 (or whatever port you ended up using).

# Learn More
[Visit](https://www.intelligentcontentacademy.com) Intelligent Content Academy.