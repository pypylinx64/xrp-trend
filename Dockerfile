FROM python:3.11

RUN useradd -m -u 1000 user
USER user
ENV ENV HOME=/home/user \
    PATH="/home/user/.local/bin:$PATH"

WORKDIR $HOME/app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN pip install -e .

COPY --chown=user . $HOME/app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
