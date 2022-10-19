FROM python:3.9
WORKDIR /app
COPY . .
RUN python3 -m pip install requests discord.py python-dotenv
CMD ["python3", "./main.py"]