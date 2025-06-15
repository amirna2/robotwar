# Robot War - Makefile for easy development

.PHONY: help install run test clean lint format

help:
	@echo "Robot War Development Commands:"
	@echo "  install    - Install package in development mode"
	@echo "  run        - Run the game"
	@echo "  test       - Run tests" 
	@echo "  clean      - Clean build artifacts"
	@echo "  lint       - Run code linting"
	@echo "  format     - Format code"

install:
	pip install -e .

run:
	python3 -m robot_war.main

test:
	python3 -m coverage run -m unittest discover robot_war/tests/ -v
	python3 -m coverage report
	python3 -m coverage html

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 robot_war/ --max-line-length=100

format:
	black robot_war/ --line-length=100