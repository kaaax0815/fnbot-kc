FROM python:3.8
WORKDIR /usr/src/app
COPY BenBotAsyncNoAds .
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD [ "python", "fortnite.py" ]