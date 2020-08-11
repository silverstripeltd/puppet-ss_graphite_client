# Count all files/directories inside a directory.
# Find without '-type' is fast because it does not fstat() individual files.
# The speed of this script is proportional to the amount of nested directiories inside all $dirs.
class ss_graphite_client::file_counter(
	$dirs = [],
) {

	file { "/opt/graphite/scripts/file_counter":
		ensure => present,
		owner => root,
		group => root,
		mode => 0755,
		content => template('ss_graphite_client/file_counter.erb'),
		require => File['/opt/graphite/scripts'],
	}

}
