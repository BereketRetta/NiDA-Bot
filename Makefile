include .env

run:
	streamlit run app.py

build:
	docker build -t ${SERVICE_NAME} --build-arg ENVIRONMENT=${ENVIRONMENT} --build-arg PORT=${PORT} .

run-docker: 
	docker run -dit --env-file .env -p ${PORT}:${PORT} ${SERVICE_NAME}