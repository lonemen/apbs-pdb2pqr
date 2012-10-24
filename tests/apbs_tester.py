#! /usr/bin/env python

import sys, os, re, datetime, subprocess, operator
from optparse import OptionParser
from ConfigParser import ConfigParser

sys.path.insert( 0, "../tools/manip" )
from inputgen import splitInput

from apbs_check_forces import check_forces
from apbs_check_results import check_results
from apbs_logger import Logger

float_pattern = r'([+-]?\d+\.\d+E[+-]\d+)'

def test_binary():
    try:
        binary = "apbs"
        subprocess.call( [binary, "--version"] )
        return binary
    except OSError:
        pass

    try:
        binary = os.path.abspath( "../bin/apbs" )
        subprocess.call( [binary, "--version"] )
        return binary
    except OSError:
        return ""



def process_serial( binary, input_file ):
    base_name = input_file.split('.')[0]
    output_name = '%s.out' % base_name
    output_file = open( output_name, 'w' )
    command = [ binary, input_file ]
    subprocess.call( command, stdout = output_file )
    output_file = open( output_name, 'r' )
    output_text = output_file.read()
    output_pattern = r'Global net (?:ELEC|APOL) energy \= ' + float_pattern
    output_results = [ float( r ) for r in re.findall( output_pattern, output_text ) ]
    return output_results



def process_parallel( binary, input_file, procs, logger ):

    logger.message( "Splitting the input file into %d separate files using the inputgen utility" % procs )
    logger.message( "" )

    base_name = input_file.split('.')[0]
    splitInput( input_file )
    results = None

    for proc in range( procs ):
        proc_input_file = '%s-PE%d.in' % ( base_name, proc )
        proc_results = process_serial( binary, proc_input_file )

        logger.message( 'Processor %d results:' % proc )
        for proc_result in proc_results:
            logger.message( '  %.12E' % proc_result )
        logger.message( '' )

        if results == None:
            results = proc_results
        else:
            results = [ r + p for ( r, p ) in zip( results, proc_results ) ]

    return results



def run_test( binary, test_files, test_name, test_directory, logger, ocd ):

    logger.log( '=' * 80 )
    logger.log( "Test Timestamp: %s" % str( datetime.datetime.now() ) )
    logger.log( "Test Name:      %s" % test_name )
    logger.log( "Test Directory: %s" % test_directory )

    net_time = datetime.timedelta( 0 )

    os.chdir( test_directory )

    for ( base_name, expected_results ) in test_files:

        input_file = '%s.in' % base_name

        if expected_results == 'forces':
            logger.message( '-' * 80 )
            logger.message( 'Testing forces from %s' % input_file )
            logger.message( '' )
            logger.log( 'Testing forces from %s' % input_file )
            start_time = datetime.datetime.now()
            check_forces( input_file, 'polarforces', 'apolarforces', logger )
        else:
            logger.message( '-' * 80 )
            logger.message( 'Testing input file %s' % input_file )
            logger.message( '' )
            logger.log( 'Testing %s' % input_file )
            start_time = datetime.datetime.now()

            computed_results = None
            match = re.search( r'\s*pdime((\s+\d+)+)', open( input_file, 'r' ).read() )
            if match:
                procs = reduce( operator.mul, [ int(p) for p in match.group( 1 ).split() ] )
                computed_results = process_parallel( binary, input_file, procs, logger )
            else:
                computed_results = process_serial( binary, input_file )
            expected_results = expected_results.split()
            for i in range( len( expected_results ) ):
                if expected_results[i] == '*':
                    continue
                computed_result = computed_results[i]
                expected_result = float( expected_results[i] )
                logger.message( "Testing computed result %.12E against expected result %12E" % ( computed_result, expected_result ) )
                check_results( computed_result, expected_result, input_file, logger, ocd )

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        net_time += elapsed_time

        logger.message( "Elapsed time: %f seconds" % elapsed_time.total_seconds() )
        logger.message( '-' * 80 )

    logger.message( "Total elapsed time: %d seconds" % net_time.total_seconds() )
    logger.message( "Test results have been logged" )
    logger.message( '-' * 80 )

    logger.log( "Time:           %d seconds" % net_time.total_seconds() )


def main():

    parser = OptionParser()
    parser.add_option(
        '-c', '--test_config', dest='test_config', type='string', default='test_cases.cfg',
        help="Set the test configuration file to FILE", metavar="FILE"
        )
    parser.add_option(
        '-t', '--target_test', dest='target_test', type='string', action='append', default=[],
        help="Set the test to run to TEST", metavar="TEST"
        )
    parser.add_option(
        '-o', '--ocd', action='store_true', dest='ocd',
        help="Run APBS in OCD mode"
        )
    parser.add_option(
        '-l', '--log_file', dest='log_file', type='string', default='test.log',
        help="Save the test log to FILE.", metavar="FILE"
        )
    ( options, args ) = parser.parse_args()

    message_fd = sys.stdout
    logfile_fd = None
    try:
        logfile_fd = open( options.log_file, 'w' )
    except IOError as err:
        parser.error( "Could't open log_file %s: %s" % ( options.log_file, err.strerror ) )
    logger = Logger( message_fd, logfile_fd )

    config = ConfigParser()
    config.read( options.test_config )

    binary = test_binary()
    if binary == '':
        parser.error( "Coulnd't detect an apbs binary in the path or local bin directory" )

    test_sections = []
    if 'all' in options.target_test or options.target_test == []:
        test_sections = config.sections()
        print "Testing all sections"
    else:
        test_sections = options.target_test

    print "The following sections will be tested: " + ', '.join( test_sections )
    print '=' * 80

    for test_name in test_sections:
        print "Running tests for " + test_name + " section"
        if test_name not in config.sections():
            print "  " + test_name + " section not found in " + options.test_config
            print "  skipping..."
            continue
        test_directory = config.get( test_name, 'input_dir' )
        config.remove_option( test_name, 'input_dir' )
        run_test( binary, config.items( test_name ), test_name, test_directory, logger, options.ocd )



if __name__ == '__main__':
    main()







