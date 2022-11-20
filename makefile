.PHONY: run
run:
	@echo "Running..."
	docker-compose build
	docker-compose run --rm app

