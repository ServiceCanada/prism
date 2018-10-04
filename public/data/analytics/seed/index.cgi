#!/Users/masterbee/perl5/perlbrew/perls/perl-5.16.3/bin/perl
use common::sense;

use Path::Tiny;
use YAML::XS 'LoadFile';
use Encode::Encoder qw(encoder);
use HTTP::Tiny;
use UUID::Tiny ':std';
use Digest::SHA qw(sha256_base64);
use Data::Dmp;

use lib path($0)->parent(5)->child('cgi-lib')->stringify;

use Encode::Base64;

# =================
# = PREPROCESSING =
# =================
my $config = LoadFile path($0)->sibling('index.yml')->stringify;
my $json = '{"reportName":"visits-and-pageviews","sortReportByCount":true,"reportDescription":{"anomalyDetection":false,"currentData":false,"dateFrom":"2018-09-01","sortBy":"visits","dateTo":"2018-09-30","reportSuiteID":"canadalivemain","elementDataEncoding":"utf8","locale":"en_US","metrics":[{"id":"visits"},{"id":"pageviews"}],"elements":[{"id":"accountsummary"}],"expedite":false}}';

my $response = HTTP::Tiny->new->request( 'POST', 'https://api5.omniture.com/admin/1.4/rest/?method=Report.Get', {
    headers => {
        'X-WSSE' => authentication( $config->{'creds'}->{'username'}, $config->{'creds'}->{'password'} ),
        'Content-Type' => 'application/json' 
    },
    content => $json
});

dd $response;


# ======================
# = HELPER SUBROUTINES =
# ======================

sub authentication
{
    my ( $username, $password ) = @_;
    
    my $nonce = create_uuid(UUID_V4);
    my $created = now_w3cdtf();
    
    return join( ' ', 'UsernameToken',
        'Username=\"'.$username.'\"',
        'PasswordDigest=\"'.sha256_base64( $nonce.$created.$password ).'\"',
        'Nonce=\"'.encoder($nonce)->iso_8859_1->base64.'\"',
        'Created=\"'.$created.'\"',
        'Algorithm=\"SHA256\"');   
}


sub now_w3cdtf {
    my ( $sec, $min, $hour, $mday, $mon, $year ) = gmtime();
    $mon++;
    $year += 1900;
 
    sprintf(
        '%04s-%02s-%02sT%02s:%02s:%02sZ',
        $year, $mon, $mday, $hour, $min, $sec,
    );
}



