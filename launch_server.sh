cd yakabible
./loaddb.sh
rm -rf static
./manage.py collectstatic
./manage.py runserver
