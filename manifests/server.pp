class graphite::server {

	package {
		graphite-web: ensure => installed;
		graphite-carbon: ensure => installed;
		libapache2-mod-wsgi: ensure => installed;
		python-mysqldb: ensure => installed;
		netcat-traditional: ensure => installed;
	 }

}
