# temporary until I can figure out the rest

all:
	docker build -t matthewtran .

run:
	docker run --name matt -d --rm -p 80:80 matthewtran

kill:
	docker kill matt
