FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Nu include secrete în imagine — trimite-le la rulare cu -e
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
