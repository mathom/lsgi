from six.moves.urllib.parse import urlencode
from werkzeug.wrappers import Response
from werkzeug.urls import url_unquote
import base64
import logging
import six
import six
import sys

logger = logging.getLogger(__name__)


def handler(app, event, context, binary_support=True):

    try:
        environ = event_to_environ(event, context)
        with Response.from_app(app, environ) as response:
            result = {
                'statusCode': response.status_code,
            }

            if response.data:
                result.update(encode_response_data(response, binary_support))

            if 'multiValueHeaders' in event:
                result['multiValueHeaders'] = {}
                for key, value in response.headers:
                    result['multiValueHeaders'][key] = response.headers.getlist(key)
            if 'headers' in event:
                result['headers'] = {}
                for key, value in response.headers:
                    result['headers'][key] = value


            response.content = response.data

            return result

    except Exception:
        msg = 'Caught unhandled exception'
        logger.exception(msg)
        return {
            'statusCode': 500,
            'message': msg
        }


def encode_response_data(response, binary_support):
    result = {}

    if binary_support:
        mime = response.mimetype
        if mime.startswith("text/") or mime == "application/json":
            result['body'] = response.get_data(as_text=True)
        else:
            result['body'] = base64.b64encode(response.data).decode('utf-8')
            result['isBase64Encoded'] = True
    else:
        result['body'] = response.get_data(as_text=True)

    return result


def event_to_environ(event, context):
    environ = {
        'HTTPS': 'on',
        'PATH_INFO': url_unquote(event['path']),
        'REMOTE_ADDR': '127.0.0.1',
        'REQUEST_METHOD': event['httpMethod'],
        'SCRIPT_NAME': '',
        'SERVER_NAME': '',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'lambda.context': context,
        'lambda.event': event,
        'wsgi.errors': sys.stderr,
        'wsgi.multiprocess': False,
        'wsgi.multithread': False,
        'wsgi.run_once': False,
        'wsgi.url_scheme': 'https',
        'wsgi.version': (1, 0),
    }

    body = event['body']
    if body and event.get('isBase64Encoded', False):
        body = base64.b64decode(body)
    else:
        if isinstance(body, six.string_types):
            body = body.encode('utf-8')

    environ['wsgi.input'] = six.BytesIO(body)
    environ['CONTENT_LENGTH'] = str(len(body or ''))

    query_string = event.get('queryStringParameters', {})
    mv_query_string = event.get('multiValueQueryStringParameters', {})

    if mv_query_string:
        environ['QUERY_STRING'] = urlencode(mv_query_String, doseq=True)
    elif query_string:
        environ['QUERY_STRING'] = urlencode(query_string)

    headers = { h.upper().replace('-','_'): v
               for h,v in (event.get('headers') or {}).items() }  # headers can be None

    forwarded_for = headers.get('X_FORWARDED_FOR', '')
    if ',' in forwarded_for:
        environ['REMOTE_ADDR'] = forwarded_for.split(', ')[-2]

    for header, value in headers.items():
        if header == 'CONTENT_TYPE':
            environ[header] = value
        elif header == 'HOST':
            environ['SERVER_NAME'] = value
        elif header == 'X_FORWARDED_PROTO':
            environ['wsgi.url_scheme'] = value
        elif header == 'X_FORWARDED_PORT':
            environ['SERVER_PORT'] = value

        environ['HTTP_' + header] = value

    return environ
