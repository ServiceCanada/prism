#!/usr/bin/env perl
use common::sense;

use Furl;   
use Digest::SHA;
use Path::Tiny;
use lib path($0)->parent(5)->child('cgi-lib')->stringify;

use YAML::Tiny;
use JSON::MaybeXS;
use UUID::Tiny ':std';
use Encode::Encoder qw(encoder);
use MIME::Base64;

use Data::Dmp qw/dd dmp/;

# =================
# = PREPROCESSING =
# =================
my $config = YAML::Tiny->read( path($0)->sibling('index.yml')->stringify )->[0];
my $http = Furl->new( timeout => 30, agent => 'Canada.ca Auditor v1.0' );
my ( $json, $report ) = (
        JSON::MaybeXS->new( utf8 => 1 ),
        {
            reportName => "visits-and-pageviews",
            sortReportByCount => JSON::MaybeXS::true,
            reportDescription => { 
                anomalyDetection => JSON::MaybeXS::false,
                currentData => JSON::MaybeXS::false,
                dateFrom => "2018-09-01",
                dateTo => "2018-09-30",
                sortBy => "visits",
                reportSuiteID => "canadalivemain",
                elementDataEncoding => "utf8",
                locale => "en_US",
                metrics => [ { id => "visits" },{ id => "pageviews" } ],
                elements => [ { id => "accountsummary" } ],
                expedite => JSON::MaybeXS::false
                }
            }
    );

my $res = $http->post(
    'https://api5.omniture.com/admin/1.4/rest/?method=Report.Queue',
    [ 'X-WSSE' => generate( $config->{'creds'}->{'username'}, $config->{'creds'}->{'secret'} ) ],
    encode_json( $report )
    );
    
die $res->status_line unless $res->is_success;
print $res->content;
# ====================
# = HELPER FUNCTIONS =
# ====================

sub generate
{
    my( $username, $password ) = @_;
    
    say "$password";
            
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