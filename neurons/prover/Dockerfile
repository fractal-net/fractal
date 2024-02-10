FROM opentensorfdn/bittensor:6.6.0

# COPY ../../. /app/fractal
COPY app.py /app/app.py
COPY entrypoint.sh /app/entrypoint.sh
WORKDIR /app

RUN git clone https://github.com/fractal-net/fractal.git /app/fractal

# install python, build essentials

RUN pip install -e /app/fractal
RUN pip install uvicorn[standard]

EXPOSE 8091

RUN chmod +x /app/entrypoint.sh

CMD ["./app/entrypoint.sh"]
#add your flag commands