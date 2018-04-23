#!/usr/bin/env python

"""Combine multiple flat-field reference images."""

from EMAN2 import *

import argparse
import ConfigParser

import glob
import os
import random
import time

__filename__ = "DE_combine_references.py"
__author__ = "Benjamin Bammes"
__copyright__ = "Copyright (c) 2012-2014 Direct Electron LP"
__credits__ = [ "Benjamin Bammes" ]
__description__ = "Combine multiple flat-field reference images."
__license__ = "GPL v.3"
__version__ = "2.0.0"
__maintainer__ = "Benjamin Bammes"
__email__ = "bbammes@directelectron.com"
__status__ = "Release"


###############################################################################
## Class: ConfigurationOptions
###############################################################################


class ConfigurationOptions :
    """Manages configuration options for this program."""
    
    
    ###############################################################################
    
    
    def __init__( self ) :
        """Initialize data attributes to default values."""
        
        # Create an empty dictionary to store the configuration options
        self._options = { }
        
        # Section: run
        options_run = [ ]
        options_run.append( { 'name' : "debug", 'type' : int, 'help' : "Print debugging information.", 'default' : 0 } )
        self._options[ 'run' ] = options_run
        
        # Section: input
        options_input = [ ]
        options_input.append( { 'name' : "ignorefirst", 'type' : int, 'help' : "Number of initial frames to ignore in each acquisition (only applicable if input contains raw frames).", 'default' : 0 } )
        options_input.append( { 'name' : "ignorelast", 'type' : int, 'help' : "Number of ending frames to ignore in each acquisition (only applicable if input contains raw frames).", 'default' : 0 } )
        options_input.append( { 'name' : "suffix", 'type' : str, 'help' : "Input directory/file name suffix.", 'default' : "" } )
        options_input.append( { 'name' : "type", 'type' : str, 'help' : "Type of input (directories = directories containing raw frames (default), stacks = stacks of raw frames).", 'default' : "directories" } )
        self._options[ 'input' ] = options_input
        
        # Section: output
        options_output = [ ]
        options_output.append( { 'name' : "normalizetime", 'type' : int, 'help' : "Normalize the dark reference to one second instead of one frame", 'default' : 0 } )
        self._options[ 'output' ] = options_output
        
        # Create a dictionary of option values
        self._values = { }
        for section in self._options.keys( ) :
            for option in self._options[ section ] :
                option_name = '%s_%s' % ( section, option[ 'name' ] )
                self._values[ option_name ] = option[ 'default' ] 
    
    
    ###############################################################################
    
    
    def combine( self, configfile_options, commandline_options ) :
        """Combine option values set by a configuration file and the command line, giving higher priority to the command line."""
        
        for option in configfile_options.keys( ) :
            self._values[ option ] = configfile_options[ option ]
        
        for option in commandline_options.keys( ) :
            self._values[ option ] = commandline_options[ option ]
    
    
    ###############################################################################
    
    
    def validate( self ) :
        """Validate all option values."""
        
        errors = [ ]
        warnings = [ ]
        
        # Section: run
        if self._values[ 'run_debug' ] not in [ 0, 1 ] :
            errors.append( "'run_debug' must be either 0 (disabled) or 1 (enabled)" )
        
        # Section: input
        if self._values[ 'input_ignorefirst' ] < 0 :
            errors.append( "'input_ignorefirst' must be >=0" )
        if self._values[ 'input_ignorelast' ] < 0 :
            errors.append( "'input_ignorelast' must be >=0" )
        if self._values[ 'input_type' ] not in [ "directories", "stacks" ] :
            errors.append( "'input_type' must be one of the following: 'directories','stacks'" )
        
        # Section: output
        if self._values[ 'output_normalizetime' ] not in [ 0, 1 ] :
            errors.append( "'output_normalizetime' must be either 0 (disabled) or 1 (enabled)" )
        
        # Return error
        return ( errors, warnings )
    
    
    ###############################################################################
    
    
    def get_options_list( self ) :
        """Return the dictionary of all options."""
        
        return self._options
    
    
    ###############################################################################
    
    
    def get_options_values( self ) :
        """Return the list of all option values."""
        
        return self._values


###############################################################################
## Main program execution
###############################################################################


def main( ) :
    """Main program execution from the command line."""
    
    # Set the program name and licensing information based on global variables at the beginning of this file
    program_name = "%s (v.%s)\n%s\nLicensed under %s" % ( __filename__, __version__, __copyright__, __license__ )
    
    # Print the program name and licensing information as soon as this program is run
    print program_name
    print ""
    
    # Create the configuration options
    configuration_options = ConfigurationOptions( )
    options_list = configuration_options.get_options_list( )
    
    # Setup command line interface and load options from command line
    argument_parser = argparse.ArgumentParser( description = "%s\n\ndescription: %s" % ( program_name, __description__ ) )
    argument_parser.add_argument( "--version", action = "version", version = program_name )
    argument_parser.add_argument( "--config_helphtml", action = "store_true", help = "Print the list of all configuration options in an HTML file (DE_combine_references.help.html)." )
    argument_parser.add_argument( "--config_helptext", action = "store_true", help = "Print the list of all configuration options in a text file (DE_combine_references.help.txt)." )
    argument_parser.add_argument( "--config_makefile", action = "store_true", help = "Make a DE_combine_references.cfg file containing all the default options." )
    sections = options_list.keys( )
    for section in sections :
        for option in options_list[ section ] :
            if option[ 'type' ] == str :
                argument_parser.add_argument( "--%s_%s" % ( section, option[ 'name' ] ), type = str, metavar="STR", help = option[ 'help' ] )
            elif option[ 'type' ] == int :
                argument_parser.add_argument( "--%s_%s" % ( section, option[ 'name' ] ), type = int, metavar="INT", help = option[ 'help' ] )
            elif option[ 'type' ] == float :
                argument_parser.add_argument( "--%s_%s" % ( section, option[ 'name' ] ), type = float, metavar="FLOAT", help = option[ 'help' ] )
    commandline_options = vars( argument_parser.parse_args( ) )
    for option in commandline_options.keys( ) :
        if commandline_options[ option ] is None :
            del commandline_options[ option ]
    
    # Print an HTML file containing the help information for all configuration options, if desired
    if commandline_options[ 'config_helphtml' ] :
        output_file = open( "DE_combine_references.help.html", "w" )
        output_file.write( "<html>\n<body>\n<table>\n<tbody>\n" )
        for section in options_list.keys( ) :
            output_file.write( "<tr><th colspan=\"2\">%s</th></tr>\n" % section )
            for option in options_list[ section ] :
                output_file.write( "<tr><td>%s</td><td>%s</td></tr>\n" % ( option[ 'name' ], option[ 'help' ] ) )
        output_file.write( "</tbody>\n</table>\n</body>\n</html>\n" )
        output_file.close( )
        print "done: created DE_combine_references.help.html"
        return
    
    # Print a text file containing the help information for all configuration options, if desired
    if commandline_options[ 'config_helptext' ] :
        output_file = open( "DE_combine_references.help.txt", "w" )
        for section in options_list.keys( ) :
            output_file.write( "%s\n" % section )
            output_file.write( "%s\n" % "".join( [ "-" for v in section ] ) )
            for option in options_list[ section ] :
                output_file.write( "%s\t%s\n" % ( option[ 'name' ], option[ 'help' ] ) )
            output_file.write( "\n" )
        output_file.close( )
        print "done: created DE_combine_references.help.txt"
        return
    
    # Write a new configuration file containing all default values, if desired
    if commandline_options[ 'config_makefile' ] :
        config_writer = ConfigParser.RawConfigParser( )
        if os.path.exists( "DE_combine_references.cfg" ) :
            print "error: DE_combine_references.cfg already exists"
            return
        sections = options_list.keys( )[ : ]
        sections.reverse( )
        for section in sections :
            config_writer.add_section( section )
            options = options_list[ section ][ : ]
            options.reverse( )
            for option in options :
                config_writer.set( section, option[ 'name' ], str( option[ 'default' ] ) )
        with open( "DE_combine_references.cfg", "w" ) as configfile :
            config_writer.write( configfile )
        print "done: created DE_combine_references.cfg"
        return
    
    # Load options from configuration file if it exists
    config_parser = ConfigParser.RawConfigParser( )
    if os.path.exists( "DE_combine_references.cfg" ) :
        config_parser.read( "DE_combine_references.cfg" )
        print "done: loaded DE_combine_references.cfg"
    configfile_options = { }
    for section in config_parser.sections( ) :
        for option in config_parser.options( section ) :
            option_value = config_parser.get( section, option )
            if section in options_list.keys( ) :
                for option_object in options_list[ section ] :
                    if option == option_object[ 'name' ] :
                        if option_object[ 'type' ] == str :
                            configfile_options[ "%s_%s" % ( section, option ) ] = str( option_value )
                        elif option_object[ 'type' ] == int :
                            configfile_options[ "%s_%s" % ( section, option ) ] = int( option_value )
                        elif option_object[ 'type' ] == float :
                            configfile_options[ "%s_%s" % ( section, option ) ] = float( option_value )
                        break
    
    # Combine and validate configuration file and command line options
    configuration_options.combine( configfile_options, commandline_options )
    ( errors, warnings ) = configuration_options.validate( )
    if len( errors ) > 0 :
        for error in errors :
            print "error: %s" % error
        return
    if len( warnings ) > 0 :
        for warning in warnings :
            print "warning: %s" % warning
    options = configuration_options.get_options_values( )
    
    # Do processing for both dark and gain references
    for reference_type in [ "dark", "gain" ] :
        print "begin: loading and processing %s references" % reference_type
        
        # Create empty stack to store input acquisition names
        reference_input_list = [ ]
        reference_input_list_raw = [ ]
        reference_input_list_sum = [ ]
        reference_input_list_final = [ ]
        reference_input_type = "none"
        
        # Find input directories
        if options[ 'input_type' ] == "directories" :
            input_list = glob.glob( "*_%s%s" % ( reference_type, options[ 'input_suffix' ] ) )
            for input_directory in input_list :
                if not os.path.exists( input_directory ) :
                    continue
                if not os.path.isdir( input_directory ) :
                    continue
                filenames = glob.glob( os.path.join( input_directory, "*[Rr]aw*.tif" ) )
                if not filenames or len( filenames ) < 1 :
                    filenames = glob.glob( os.path.join( input_directory, "*[Ss]um*.tif" ) )
                    if not filenames or len( filenames ) < 1 :
                        filenames = glob.glob( os.path.join( input_directory, "*[Ff]inal*.tif" ) )
                        if not filenames or len( filenames ) < 1 :
                            continue
                        else :
                            reference_input_list_final.append( input_directory )
                    else :
                        reference_input_list_sum.append( input_directory )
                else :
                    reference_input_list_raw.append( input_directory )
        
        # Find input stacks
        elif options[ 'input_type' ] == "stacks" :
            input_list = glob.glob( "*_%s%s_*.hdf" % ( reference_type, options[ 'input_suffix' ] ) )
            for input_stack in input_list :
                if not os.path.exists( input_stack ) :
                    continue
                try :
                    input_stack_count = EMUtil.get_image_count( input_stack )
                except :
                    continue
                if "raw" in input_stack or "Raw" in input_stack :
                    reference_input_list_raw.append( input_stack )
                if "sum" in input_stack or "Sum" in input_stack :
                    reference_input_list_sum.append( input_stack )
                if "final" in input_stack or "Final" in input_stack :
                    reference_input_list_final.append( input_stack )
        
        # Determine type of input
        if len( reference_input_list_raw ) > 0 :
            reference_input_list = reference_input_list_raw[ : ]
            reference_input_type = "raw"
            print "status: found %i %s acquisitions containing raw frames." % ( len( reference_input_list_raw ), reference_type )
        elif len( reference_input_list_sum ) > 0 :
            reference_input_list = reference_input_list_sum[ : ]
            reference_input_type = "sum"
            print "status: found %i %s acquisitions containing sum images." % ( len( reference_input_list_sum ), reference_type )
        elif len( reference_input_list_final ) > 0 :
            reference_input_list = reference_input_list_final[ : ]
            reference_input_type = "final"
            print "status: found %i %s acquisitions containing final images." % ( len( reference_input_list_final ), reference_type )
        else :
            print "status: could not find any %s acquisitions." % ( reference_type )
            continue
        
        # Show warning if frame processing is desired without having raw frame input
        if reference_input_type != "raw" :
            if options[ 'input_ignorefirst' ] > 0 :
                print "warning: no raw frames available - ignoring 'input_ignorefirst'."
            if options[ 'input_ignorelast' ] > 0 :
                print "warning: no raw frames available - ignoring 'input_ignorelast'."
        
        # Generate initial empty image
        if options[ 'input_type' ] == "directories" :
            if reference_input_type == "raw" :
                filenames_matching = glob.glob( os.path.join( reference_input_list[ 0 ], "*[Rr]aw*.tif" ) )
            elif reference_input_type == "sum" :
                filenames_matching = glob.glob( os.path.join( reference_input_list[ 0 ], "*[Ss]um*.tif" ) )
            elif reference_input_type == "final" :
                filenames_matching = glob.glob( os.path.join( reference_input_list[ 0 ], "*[Ff]inal*.tif" ) )
            else :
                filenames_matching = [ ]
            if not filenames_matching or len( filenames_matching ) < 1 :
                print "error: could not generate initial empty images"
                continue
            try :
                combined_image = EMData( filenames_matching[ 0 ] )
            except :
                print "error: could not generate initial empty images"
                continue
        elif options[ 'input_type' ] == "stacks" :
            try :
                combined_image = EMData( reference_input_list[ 0 ], 0 )
            except :
                print "error: could not generate initial empty images"
                continue
        combined_image.to_zero( )
        combined_sigma = combined_image.copy( )
        combined_total_acquisitions = 0
        combined_total_frames = 0
        combined_total_time = 0.
        
        # Process each input acquisition
        for reference_input in reference_input_list :
            print "status: processing %s" % reference_input
            
            # Get metadata from info.txt
            image_frames_total = 0
            image_frames_sum = 0
            image_time_total = 0.
            image_time_sum = 0.
            image_time_frame = 0.
            info_filename = ""
            if options[ 'input_type' ] == "directories" :
                info_filename = os.path.join( reference_input, "info.txt" )
            elif options[ 'input_type' ] == "stacks" :
                if reference_input_type == "raw" :
                    info_filename = "%s_info.txt" % reference_input[ : -8 ]
                elif reference_input_type == "sum" :
                    info_filename = "%s_info.txt" % reference_input[ : -13 ]
                elif reference_input_type == "final" :
                    info_filename = "%s_info.txt" % reference_input[ : -15 ]
            if len( info_filename ) > 0 and os.path.exists( info_filename ) :
                info_file = file( info_filename, "r" )
                for line in info_file :
                    if "Total Number of Frames" in line :
                        image_frames_total = int( line.split( "=" )[ 1 ].strip( ) )
                    if "Total Frames in Summed Image" in line :
                        image_frames_sum = int( line.split( "=" )[ 1 ].strip( ) )
                    if "Exposure Time in Seconds" in line :
                        image_time_total = float( line.split( "=" )[ 1 ].strip( ) )
                    if "Frame Time in Seconds" in line :
                        image_time_frame = float( line.split( "=" )[ 1 ].strip( ) )
                info_file.close( )
                image_time_sum = image_time_frame * float( image_frames_sum )
            
            # Check for necessary metadata
            if reference_input_type == "raw" :
                if options[ 'output_normalizetime' ] :
                    if image_time_frame <= 0. :
                        print "warning: skipping %s due to insufficient metadata" % reference_input
                        continue
            elif reference_input_type == "sum" :
                if image_frames_sum <= 0. :
                    print "warning: skipping %s due to insufficient metadata" % reference_input
                    continue
                if options[ 'output_normalizetime' ] :
                    if image_time_sum <= 0. :
                        print "warning: skipping %s due to insufficient metadata" % reference_input
                        continue
            elif reference_input_type == "final" :
                if image_frames_total <= 0. :
                    print "warning: skipping %s due to insufficient metadata" % reference_input
                    continue
                if options[ 'output_normalizetime' ] :
                    if image_time_total <= 0. :
                        print "warning: skipping %s due to insufficient metadata" % reference_input
                        continue
            
            # Create a list of frames/images to load for this acquisition
            input_filenames = [ ]
            input_indices = [ ]
            if options[ 'input_type' ] == "directories" :
                if reference_input_type == "raw" :
                    filenames_matching = glob.glob( os.path.join( reference_input, "*[Rr]aw*.tif" ) )
                elif reference_input_type == "sum" :
                    filenames_matching = glob.glob( os.path.join( reference_input, "*[Ss]um*.tif" ) )
                elif reference_input_type == "final" :
                    filenames_matching = glob.glob( os.path.join( reference_input, "*[Ff]inal*.tif" ) )
                else :
                    filenames_matching = [ ]
                if filenames_matching and len( filenames_matching ) > 0 :
                    filenames_sorted = [ ]
                    for filename in filenames_matching :
                        frame_index = int( os.path.basename( filename ).split( "_" )[ 1 ].split( "." )[ 0 ] )
                        filenames_sorted.append( [ frame_index, filename ] )
                    filenames_sorted.sort( )
                    filenames_sorted_start = 0
                    filenames_sorted_stop = len( filenames_sorted )
                    if reference_input_type == "raw" :
                        filenames_sorted_start += options[ 'input_ignorefirst' ]
                        filenames_sorted_stop -= options[ 'input_ignorelast' ]
                    for i in range( filenames_sorted_start, filenames_sorted_stop ) :
                        input_filenames.append( filenames_sorted[ i ][ 1 ] )
                        input_indices.append( 0 )
            elif options[ 'input_type' ] == "stacks" :
                filenames_sorted_start = 0
                filenames_sorted_stop = EMUtil.get_image_count( reference_input )
                if reference_input_type == "raw" :
                    filenames_sorted_start += options[ 'input_ignorefirst' ]
                    filenames_sorted_stop -= options[ 'input_ignorelast' ]
                for i in range( filenames_sorted_start, filenames_sorted_stop ) :
                    input_filenames.append( reference_input )
                    input_indices.append( i )
            
            # Add input frames/images to combined image
            for i in range( len( input_filenames ) ) :
                if options[ 'run_debug' ] :
                    print "debug: loading %s (%i)" % ( input_filenames[ i ], input_indices[ i ] )
                img = EMData( input_filenames[ i ], input_indices[ i ] )
                combined_image += img
                combined_sigma += img * img
                del img
                if reference_input_type == "raw" :
                    combined_total_frames += 1
                    combined_total_time += image_time_frame
                elif reference_input_type == "sum" :
                    combined_total_frames += image_frames_sum
                    combined_total_time += image_time_sum
                elif reference_input_type == "final" :
                    combined_total_frames += image_frames_total
                    combined_total_time += image_time_total
            
            # Increment number of acquisitions
            combined_total_acquisitions += 1
        
        # Generate average
        if options[ 'output_normalizetime' ] :
            if combined_total_time <= 0. :
                print "warning: no acquisitions loaded - skipping %s reference generation" % ( reference_type )
                continue
            reference_type += "_time"
            combined_image /= combined_total_time
            combined_sigma /= combined_total_time
        else :
            if combined_total_frames <= 0. :
                print "warning: no acquisitions loaded - skipping %s reference generation" % ( reference_type )
                continue
            combined_image /= combined_total_frames
            combined_sigma /= combined_total_frames
        combined_sigma = ( combined_sigma - combined_image * combined_image ).process( "threshold.belowtozero", { "minval" : 0. } ).sqrt( )
        
        # Write result
        combined_image.write_image( "%s_frame.tif" % reference_type )
        combined_sigma.write_image( "%s_sigma.tif" % reference_type )
        
        # Print completion message
        print "done: generated %s_frame.tif based on %i acquisitions with %i total frames." % ( reference_type, combined_total_acquisitions, combined_total_frames )
    
    # Print final message
    print "done: program complete"


if __name__ == "__main__" :
	main( )
