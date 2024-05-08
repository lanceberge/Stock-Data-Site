build:
	docker build -t python-docker .

run:
	docker run -d -p 5000:5000 python-docker
