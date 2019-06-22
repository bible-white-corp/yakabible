rm -rf yakabible/static
python yakabible/manage.py collectstatic
pytest yakabible/ --cov=billapp
