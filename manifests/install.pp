class graphite::install inherits graphite {

  package {
    realpath: ensure => installed;
    logtail: ensure => installed;
    logster: ensure => installed;
  }

  # Remove legacy version of logster (compiled, not packaged)
  file {"/usr/sbin/logster":
    ensure => absent,
  }
  # Remove legacy graphite scripts
  file {'remove-graphite-scripts':
    ensure  => absent,
    path    => '/usr/share/graphite-scripts',
    recurse => true,
    purge   => true,
    force   => true,
  }
  # Install SS Logster parsers
  file {"/usr/lib/python2.7/dist-packages/logster/parsers":
    recurse => true,
    owner => root,
    group => root,
    mode => 0755,
    source => "puppet:///modules/graphite/logster-parsers",
  }

  file {'/opt/graphite':
    ensure => 'directory',
  } ->
  file {'/opt/graphite/scripts':
    ensure => 'directory',
  } ->
  file {'/opt/graphite/scripts-daily':
    ensure => 'directory',
  } ->

  # Add bash graphite functions
  file {'/opt/graphite/graphite_functions':
    owner   => root,
    group   => root,
    mode    => 755,
    source  => "puppet:///modules/graphite/graphite_functions",
  }

  file {'/opt/graphite/graphite_functions.php':
      owner   => root,
      group   => root,
      mode    => 755,
      source  => "puppet:///modules/graphite/graphite_functions.php",
  }

  file { "/etc/cron.d/graphite-scripts":
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => 755,
    content => "* * * * *       root    run-parts /opt/graphite/scripts --arg=${graphite_server} --arg=${graphite_port} >/dev/null 2>&1\n",
    require => File['/opt/graphite/scripts'],
  }

  file { "/etc/cron.d/graphite-scripts-daily":
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => 755,
    content => "34 4 * * *       root    run-parts /opt/graphite/scripts-daily --arg=${graphite_server} --arg=${graphite_port} >/dev/null 2>&1\n",
    require => File['/opt/graphite/scripts-daily'],
  }

}
