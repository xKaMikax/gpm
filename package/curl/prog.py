import requests
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('url', nargs='?', default=None)
    parser.add_argument('-X', '--request', dest='method', default='GET')
    parser.add_argument('-H', '--header', dest='headers', action='append')
    parser.add_argument('-d', '--data', dest='data')
    parser.add_argument('-i', '--include', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-L', '--location', action='store_true')
    parser.add_argument('--help', action='help')

    args = parser.parse_args()

    if not args.url:
        print("curl: no URL specified!")
        sys.exit(1)

    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    headers_dict = {}
    if args.headers:
        for h in args.headers:
            if ':' in h:
                k, v = h.split(':', 1)
                headers_dict[k.strip()] = v.strip()

    method = args.method.upper()
    if args.data and method == 'GET':
        method = 'POST'

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers_dict,
            data=args.data,
            allow_redirects=args.location
        )

        if args.verbose:
            print(f"* Connected to {url}")
            print(f"> {method} {response.request.path_url} HTTP/1.1")
            for k, v in response.request.headers.items():
                print(f"> {k}: {v}")
            print(">")
            print(f"< HTTP/1.1 {response.status_code} {response.reason}")

        if args.include:
            for k, v in response.headers.items():
                print(f"{k}: {v}")
            print()

        print(response.text, end='')

    except Exception as e:
        print(f"curl: (7) Failed to connect: {e}", file=sys.stderr)
        sys.exit(7)

if __name__ == "__main__":
    main()
