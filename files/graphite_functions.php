<?php
/**
 * Please only use:
 *
 * $graphiteHost
 * $graphitePort
 * $prefix
 * send($key, $value) - send a single metric.
 * sendHash($hash) - pass an array of key => value metrics.
 */

if (!isset($_SERVER['argv'][1])) {
	throw new Exception('Pass graphite server address as a first parameter');
}
if (!isset($_SERVER['argv'][2])) {
	throw new Exception('Pass graphite server port as a second parameter');
}

error_reporting(0);

$graphiteHost = $_SERVER['argv'][1];
$graphitePort = $_SERVER['argv'][2];

$prefix = null;
$prefixFile = '/opt/graphite/prefix';
if (file_exists($prefixFile) && is_readable($prefixFile)) {
	$prefix = trim(file_get_contents($prefixFile));
}

if (!$prefix) {
  $name = trim(`hostname | cut -f1 -d\.`);
  $datacentre = trim(`hostname -f | cut -f2 -d\.`);
  $host = trim(`hostname -f | cut -f1 -d\.`);
  $prefix = sprintf('server.%s.%s', $datacentre, $host);
}

$time = time();

function send($key, $value)
{
	static $socket = null;
	global $graphiteHost, $graphitePort, $time;

	if (!$socket) {
		$socket = fsockopen($graphiteHost, $graphitePort);
	}

	$line = sprintf("%s %s %s\n", $key, $value, $time);
	echo($line);
	fwrite($socket, $line);
}

function sendHash($hash)
{
	foreach ($hash as $key => $value) {
		send($key, $value);
	}
}

// By convention, sending occurs at the very end of the graphite metric, so it should be ok
// to rely on PHP to fclose automatically on shutdown.
