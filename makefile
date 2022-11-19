.PHONY: run
run:
	@echo "Running..."
	docker-compose down --remove-orphans && \
	docker-compose up --build --wait
