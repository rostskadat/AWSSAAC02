your_env_access_key_var = 'AWS_KVS_USER_ACCESS_KEY'
your_env_secret_key_var = 'AWS_KVS_USER_SECRET_KEY'
your_stream_name = 'my-video-stream-test'

def get_endpoint_boto():
    import boto3

    client = boto3.client('kinesisvideo')
    response = client.get_data_endpoint(
        StreamName=your_stream_name,
        APIName='PUT_MEDIA'
    )
    pp.pprint(response)
    endpoint = response.get('DataEndpoint', None)
    print("endpoint %s" % endpoint)
    if endpoint is None:
        raise Exception("endpoint none")
    return endpoint

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def get_host_from_endpoint(endpoint):
    # u'https://s-123abc78.kinesisvideo.us-east-2.amazonaws.com'
    if not endpoint.startswith('https://'):
        return None
    retv = endpoint[len('https://'):]
    return str(retv)

def get_region_from_endpoint(endpoint):
    # u'https://s-123abc78.kinesisvideo.us-east-2.amazonaws.com'
    if not endpoint.startswith('https://'):
        return None
    retv = endpoint[len('https://'):].split('.')[2]
    return str(retv)


class gen_request_parameters:
    def __init__(self):
        self._data = ''
        if True:
            localfile = '6-step_example.webm.360p.webm' # upload ok
            #localfile = 'big-buck-bunny_trailer.webm' # error fragment duration over limit
            with open(localfile, 'rb') as image:
                request_parameters = image.read()
                self._data = request_parameters
        self._pointer = 0
        self._size = len(self._data)
    def __iter__(self):
        return self
    def next(self):
        if self._pointer >= self._size:
            raise StopIteration  # signals "the end"
        left = self._size - self._pointer
        chunksz = 16000
        if left < 16000:
            chunksz = left
        pointer_start = self._pointer
        self._pointer += chunksz
        print("Data: chunk size %d" % chunksz)
        return self._data[pointer_start:self._pointer]


# ************* REQUEST VALUES *************
endpoint = get_endpoint_boto()

method = 'POST'
service = 'kinesisvideo'
host = get_host_from_endpoint(endpoint)
region = get_region_from_endpoint(endpoint)
##endpoint = 'https://**<the endpoint you get with get_data_endpoint>**/PutMedia'

endpoint += '/putMedia'

# POST requests use a content type header. For DynamoDB,
# the content is JSON.
content_type = 'application/json'
start_tmstp = repr(time.time())

# Read AWS access key from env. variables or configuration file. Best practice is NOT
# to embed credentials in code.
access_key = None # '*************************'
secret_key = None # '*************************'
while True: # scope
    k = os.getenv(your_env_access_key_var)
    if k is not None and type(k) is str and k.startswith('AKIA5'):
        access_key = k
    k = os.getenv(your_env_secret_key_var)
    if k is not None and type(k) is str and len(k) > 4:
        secret_key = k
    break # scope
if access_key is None or secret_key is None:
    print('No access key is available.')
    sys.exit()

# Create a date for headers and the credential string
t = datetime.datetime.utcnow()
amz_date = t.strftime('%Y%m%dT%H%M%SZ')
date_stamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope

# ************* TASK 1: CREATE A CANONICAL REQUEST *************
# http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

# Step 1 is to define the verb (GET, POST, etc.)--already done.

# Step 2: Create canonical URI--the part of the URI from domain to query
# string (use '/' if no path)
##canonical_uri = '/'
canonical_uri = '/putMedia' #endpoint[len('https://'):]

## Step 3: Create the canonical query string. In this example, request
# parameters are passed in the body of the request and the query string
# is blank.
canonical_querystring = ''

# Step 4: Create the canonical headers. Header names must be trimmed
# and lowercase, and sorted in code point order from low to high.
# Note that there is a trailing \n.
#'host:' + host + '\n' +
canonical_headers = ''
#canonical_headers += 'Accept: */*\r\n'
canonical_headers += 'connection:keep-alive\n'
canonical_headers += 'content-type:application/json\n'
canonical_headers += 'host:' + host + '\n'
canonical_headers += 'transfer-encoding:chunked\n'
#canonical_headers += 'x-amz-content-sha256: ' + 'UNSIGNED-PAYLOAD' + '\r\n'
canonical_headers += 'user-agent:AWS-SDK-KVS/2.0.2 GCC/7.4.0 Linux/4.15.0-46-generic x86_64\n'
canonical_headers += 'x-amz-date:' + amz_date + '\n'
canonical_headers += 'x-amzn-fragment-acknowledgment-required:1\n'
canonical_headers += 'x-amzn-fragment-timecode-type:ABSOLUTE\n'
canonical_headers += 'x-amzn-producer-start-timestamp:' + start_tmstp + '\n'
canonical_headers += 'x-amzn-stream-name:' + your_stream_name + '\n'

# Step 5: Create the list of signed headers. This lists the headers
# in the canonical_headers list, delimited with ";" and in alpha order.
# Note: The request can include any headers; canonical_headers and
# signed_headers include those that you want to be included in the
# hash of the request. "Host" and "x-amz-date" are always required.
# For DynamoDB, content-type and x-amz-target are also required.
#
#in original sample  after x-amz-date :  + 'x-amz-target;'
signed_headers = 'connection;content-type;host;transfer-encoding;user-agent;'
signed_headers += 'x-amz-date;x-amzn-fragment-acknowledgment-required;'
signed_headers += 'x-amzn-fragment-timecode-type;x-amzn-producer-start-timestamp;x-amzn-stream-name'

# Step 6: Create payload hash. In this example, the payload (body of
# the request) contains the request parameters.

# Step 7: Combine elements to create canonical request
canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers
canonical_request += '\n'
canonical_request += hashlib.sha256(''.encode('utf-8')).hexdigest()

# ************* TASK 2: CREATE THE STRING TO SIGN*************
# Match the algorithm to the hashing algorithm you use, either SHA-1 or
# SHA-256 (recommended)
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
string_to_sign = algorithm + '\n' + amz_date + '\n' + credential_scope + '\n' + hashlib.sha256(
    canonical_request.encode('utf-8')).hexdigest()

# ************* TASK 3: CALCULATE THE SIGNATURE *************
# Create the signing key using the function defined above.
signing_key = get_signature_key(secret_key, date_stamp, region, service)

# Sign the string_to_sign using the signing_key
signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'),
                     hashlib.sha256).hexdigest()

# ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
# Put the signature information in a header named Authorization.
authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', '
authorization_header += 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

# # Python note: The 'host' header is added automatically by the Python 'requests' library.
headers = {
    'Accept': '*/*',
    'Authorization': authorization_header,
    'connection': 'keep-alive',
    'content-type': content_type,
    #'host': host,
    'transfer-encoding': 'chunked',
    # 'x-amz-content-sha256': 'UNSIGNED-PAYLOAD',
    'user-agent': 'AWS-SDK-KVS/2.0.2 GCC/7.4.0 Linux/4.15.0-46-generic x86_64',
    'x-amz-date': amz_date,
    'x-amzn-fragment-acknowledgment-required': '1',
    'x-amzn-fragment-timecode-type': 'ABSOLUTE',
    'x-amzn-producer-start-timestamp': start_tmstp,
    'x-amzn-stream-name': your_stream_name,
    'Expect': '100-continue'
}

# ************* SEND THE REQUEST *************
print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
print('Request URL = ' + endpoint)

r = requests.post(endpoint, data=gen_request_parameters(), headers=headers)

print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
print('Response c