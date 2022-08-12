def app(amb, start_response):
    arq = open('cadastro.html', 'rb')
    data = arq.read()
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    return [data]