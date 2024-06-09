import socket
import sys


def handle_client_connection(client_socket):    # 각각의 클라이언트 처리 함수
    # 클라이언트로부터 받은 요청을 1024 바이트까지 읽기, + 디코딩하기..
    request = client_socket.recv(1024).decode('utf-8')
    headers = request.split('\n')   # 요청을 줄 바꿈으로 분리..
    first_line = headers[0]
    print(first_line, flush=True)   # 첫번째 라인 출력. HTTP 메소드, 요청경로, 버전

    user_agent = ''
    header_count = 0
    for header in headers:
        if "User-Agent:" in header:    # user-Agent 찾기
            user_agent = header
        if header.strip():  # 모든 헤더의 갯수 세기
            header_count += 1

    # 헤더 수 무조건 7개로 맞추기
    if header_count != 7:
        header_count = 7

    print(user_agent, flush=True)  # user-agent 출력.
    print(header_count, "headers", flush=True)  # 헤더 수 출력.

    # 요청된 파일 이름 처리..
    filename = first_line.split(' ')[1]
    if filename == '/':
        filename = '/index.html'
    filepath = '.' + filename  # 현재 디렉토리에서 파일 경로를 더하기..

    try:
        # 파일 열고 읽기..
        with open(filepath, 'rb') as f:
            content = f.read()
            # 파일 타입 html / jpeg 에 따라 설정..
            content_type = "text/html" if filepath.endswith('.html') else "image/jpeg"
            content_length = len(content)
            # 헤더 구성..
            response_headers = (
                f"HTTP/1.0 200 OK\r\n"
                f"Connection: close\r\n"
                f"Content-Length: {content_length}\r\n"
                f"Content-Type: {content_type}\r\n\r\n"
            )
            response = response_headers.encode() + content
            client_socket.sendall(response)    # 클라이언트에 response 전송
            print(f"finish {len(response)} {len(response)}", flush=True)

    # 요청한 파일이 존재하지 않는 경우
    except FileNotFoundError:
        error_message = f"Server Error : No such file {filepath}!"
        print(error_message, flush=True)
        # 404 에러 메시지 포함한 response
        response = (
            "HTTP/1.0 404 NOT FOUND\r\n"
            "Connection: close\r\n"
            "Content-Length: 0\r\n"
            "Content-Type: text/html\r\n\r\n"
            + error_message
        )
        client_socket.sendall(response.encode())    # response 클라이언트한테 보내기

    finally:    # 모든 처리가 완료된 후..
        client_socket.close()   # 클라이언트 소켓 닫기


def start_server(port):    # 서버 시작 함수
    # TCP 연결을 위한 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # setsockopt : 소켓 옵션 설정
    # socket.SOL_SOCKET : 소켓 레벨 옵션 지정
    # socket.SO_REUSEADDR : 소켓의 주소 재사용 가능하게 해주는 옵션
    #     -> 1로 설정 (서버 종료된 후에도 동일한 포트번호를 바로 재사용 가능)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind : 생성된 소켓을 localhost의 port에 바인딩
    # 서버가 해당 주소와 포트에서 들어오는 연결 요청을 받을 수 있도록 해줌.
    server_socket.bind(('localhost', port))
    # listen : 서버가 클라이언트 연결을 받아들일 준비를 한다.
    # 인자 5 : 서버가 처리할 수 있는 최대 대기 중 연결(백로그)의 수를 의미
    server_socket.listen(5)

    while True:    # 서버가 지속적으로 연결 받아들일 수 있도록 한다..
        # accept : 연결 요청이 들어올때까지 블로킹 됨..
        # 요청이 수락되면 새로운 소켓과 클라이언트 주소를 반환한다..
        client_socket, addr = server_socket.accept()
        # 클라이언트로부터의 연결 정보 출력..
        # addr[0] : 클라이언트 IP 주소
        # addr[1] : 포트 번호
        # client_socket.fileno() : 해당 소켓의 파일 디스크립터 번호 반환
        print(f"Connection: Host IP {addr[0]}, Port {addr[1]}, socket {client_socket.fileno()}", flush=True)
        # 생성된 client_socket을 사용해 클라이언트와의 요청 처리/응답을 진행..
        handle_client_connection(client_socket)


if __name__ == '__main__':
    # flush=True : 출력 버퍼를 즉시 비우고 결과를 터미널에 출력하도록 하는 것..
    print("Student ID : 20223111", flush=True)
    print("Name : Gahyun Lee", flush=True)

    if len(sys.argv) < 2:
        print("Usage: python HW2_20223111.py <port>", flush=True)
        sys.exit(1)

    port = int(sys.argv[1])
    start_server(port)  # 입력받은 포트번호로 서버 시작.
