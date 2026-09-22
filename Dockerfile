FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir 'pydantic>=2.7,<3' 'pytest>=8,<9'
CMD ["bash", "scripts/reproduce.sh"]
