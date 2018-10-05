#!/usr/bin/env perl
use common::sense;
use lib path($0)->parent(5)->child('cgi-lib')->stringify;

use cPanelUserConfig;

use Furl;   
use Digest::SHA;
use Path::Tiny;

use YAML::Tiny;
use JSON::MaybeXS;
use UUID::Tiny ':std';
use Encode::Encoder qw(encoder);
use MIME::Base64;
use POSIX;
use Mustache::Simple;

use Data::Dmp qw/dd dmp/;

# =================
# = PREPROCESSING =
# =================
my ( $config, $http, $json, $base, $stache, $from, $to ) = (
    YAML::Tiny->read( path($0)->sibling('index.yml')->stringify )->[0],
    Furl->new( timeout => 30, agent => 'Canada.ca Auditor v1.0' ),
    JSON::MaybeXS->new( utf8 => 1 ),
    path($0)->parent,
    Mustache::Simple->new,
    POSIX::strftime( '%Y-%m-%d', localtime( time() - (30*24*60*60) ) ),
    POSIX::strftime( '%Y-%m-%d', localtime( time() ) )
);

my ( $username, $secret ) = ( $config->{'http'}->{'creds'}->{'username'},  $config->{'http'}->{'creds'}->{'secret'} );

foreach my $resource ( @{ $config->{'catalog'} } )
{   
    say " [report] ".$resource->{'title'}." generating ";
    my $reportid = $http->post(
        $resource->{'prefetch'},
        [ 'X-WSSE' => generate( $username, $secret ) ],
        $stache->render( $base->child( $resource->{'content'} )->slurp_utf8, { to => $to, from => $from } )
    );
    
    my ( $wait ) = ( 1 );
    
    while( $wait )
    {
        my $report = $http->post(
            $resource->{'uri'},
            [ 'X-WSSE' => generate( $username, $secret ) ],
            $reportid->content
        );
        
        if ( $report->content =~ /"error":"report_not_ready"/ )
        {
            say "   ... report not ready waiting a few seconds";
            sleep $resource->{'sleep'};
            next;
        }
        
        $base->child( $resource->{'store'} )->absolute->spew_utf8( $report->content );
        $wait = 0;
    }
    say "      ... stored ";
    say "-"x40;
}

# ====================
# = HELPER FUNCTIONS =
# ====================

sub generate
{
    my( $username, $password ) = @_;
                
    my ( $nonce, $created ) = (
        uuid_to_string( create_uuid( UUID_V4 ) ),
        now_w3cdtf()
    );
    
    return join( ' ',
        'UsernameToken',
        'Username="'.$username.'",',
        'PasswordDigest="'.encode_base64( Digest::SHA::sha256( $nonce.$created.$password ) ).'",',
        'Nonce="'. encode_base64( $nonce ).'",',
        'Created="'.$created.'",',
        'Algorithm="SHA256"'
    );
}

sub now_w3cdtf {
    my ( $sec, $min, $hour, $mday, $mon, $year ) = gmtime();
    $mon++;
    $year += 1900;

    sprintf(
        '%04s-%02s-%02sT%02s:%02s:%02s.297Z',
        $year, $mon, $mday, $hour, $min, $sec,
    );
}