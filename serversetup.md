sudo apt-get update

sudo apt-get upgrade

sudo timedatectl set-timezone UTC

sudo apt-get install apache2

sudo apt-get install libapache2-mod-wsgi

sudo apt-get install postgresql postgresql-contrib

sudo -u postgres createuser -P catalog

sudo -u postgres createdb -O catalog catalog

sudo apt-get install python-sqlalchemy python-pip

sudo apt-get install python-psycopg2 python-flask

sudo apt-get install python-pandas

sudo apt-get install python-boto3

sudo apt-get install git

cd /var/www/

sudo mkdir mlwebapp

sudo chown www-data:www-data mlwebapp/

sudo -u www-data git clone https://github.com/zacktwp/MLWebApp.git mlwebapp

#replace files with
engine = create_engine('postgresql://catalog:password@localhost/catalog')

sudo mv webapp.py __init__.py

#create catalog.wsgi
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/fullstack-nanodegree-vm/vagrant/catalog/")

from catalog import app as application

application.secret_key = 'YOUR_SECRET_KEY'

#create host conf file
sudo nano /etc/apache2/sites-available/catalog.conf

<VirtualHost *:80>
	ServerName http://34.228.239.32
	ServerAdmin admin@34.228.239.32
	WSGIDaemonProcess catalog user=www-data group=www-data threads=5
	WSGIProcessGroup catalog
	WSGIApplicationGroup %{GLOBAL}
	WSGIScriptAlias / /var/www/catalog.wsgi
	<Directory /var/www/mlwebapp/>
		Require all granted
	</Directory>
	Alias /static /var/www/mlwebapp/static
	<Directory /var/www/mlwebapp/static/>
		Require all granted
	</Directory>
	ErrorLog ${APACHE_LOG_DIR}/error.log
	LogLevel warn
	CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>


sudo a2dissite 000-default.conf

sudo a2ensite catalog.conf

sudo service apache2 restart

python __init__.py

#error logs
cd /var/log/apache2/
sudo nano error.log

sudo nano /var/log/apache2/error.log

sudo service apache2 restart
