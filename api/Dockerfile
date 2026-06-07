FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip

COPY . .
RUN pip install --no-cache-dir .


FROM python:3.12-slim AS test_runner
WORKDIR /tmp
COPY --from=builder /venv /venv
COPY --from=builder /usr/src/app/tests tests
ENV PATH=/venv/bin:$PATH

RUN pip install pytest
RUN pytest tests


FROM python:3.12-slim AS service
WORKDIR /usr/src/app
COPY --from=test_runner /venv /venv
COPY --from=builder /usr/src/app/src/ /usr/src/app/
ENV PATH=/venv/bin:$PATH
ENV PYTHONPATH=/usr/src/app
