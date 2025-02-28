FROM python:3.11

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

RUN python3 -m pip install -e .

CMD ["gunicorn", "app:server", "--workers", "4", "--bind", "0.0.0.0:7860"]
