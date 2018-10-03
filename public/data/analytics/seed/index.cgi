#!/Users/masterbee/perl5/perlbrew/perls/perl-5.16.3/bin/perl
use common::sense;

use Path::Tiny;
use YAML::XS 'LoadFile';

use LWP::UserAgent;
use HTTP::Request;
use Data::Dmp;

use lib path($0)->parent(5)->child('cgi-lib')->stringify;

# =================
# = PREPROCESSING =
# =================
my $config = LoadFile path($0)->sibling('index.yml')->stringify;

my $json = '{"reportName":"visits-and-pageviews","sortReportByCount":true,"reportDescription":{"anomalyDetection":false,"currentData":false,"dateFrom":"2018-09-01","sortBy":"visits","dateTo":"2018-09-30","reportSuiteID":"canadalivemain","elementDataEncoding":"utf8","locale":"en_US","metrics":[{"id":"visits"},{"id":"pageviews"}],"elements":[{"id":"accountsummary"}],"expedite":false}}';
my $req = HTTP::Request->new( 'POST', 'https://api5.omniture.com/admin/1.4/rest/?method=Report.Queue' );

$req->header( 'Content-Type' => 'application/json' );
$req->content( $json );
 
# Set up the WSSE client
my $ua = LWP::UserAgent->new;
$ua->credentials('https://api5.omniture.com/admin/1.4/rest', '', $config->{creds}->{username}, $config->{creds}->{secret});


print "--Performing request now...-----------\n";
my $response = $ua->request( $req );
print "--Done with request-------------------\n";
 
dd $response;

if ($response->is_success) {
    print "It worked!->", $response->code, "\n";
    print "Body => ", $response->decoded_content, "\n";
}
else {
    print "It didn't work! -> ", $response->code, "\n";
}





