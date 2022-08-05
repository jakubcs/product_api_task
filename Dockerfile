FROM python:3.7-alpine

ARG OFFER_BASE_URL
ARG OFFER_AUTH_CODE

ENV PROJECT_DIR /usr/src/product_api_task
ENV OFFER_BASE_URL ${OFFER_BASE_URL}
ENV OFFER_AUTH_CODE ${OFFER_AUTH_CODE}

WORKDIR ${PROJECT_DIR}

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]

