for i in {1..20}; do
	python -m pytest -s --cov-report term-missing --cov=monolith monolith/classes/tests/test_notifications.py 
done
