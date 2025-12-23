FROM python:3.13.1-slim
WORKDIR /app

COPY requirements/dev.txt requirements.txt
RUN pip3 install -r requirements.txt

# Install required spaCy model for Presidio
RUN python -m spacy download en_core_web_sm \
&& python -m spacy download zh_core_web_sm \
&& python -m spacy download xx_ent_wiki_sm || true

COPY . .

# COPY docker-entrypoint.sh /docker-entrypoint.sh
# RUN chmod +x /docker-entrypoint.sh

# ENTRYPOINT ["/docker-entrypoint.sh"]
CMD uvicorn src.main:app --host=0.0.0.0 --reload