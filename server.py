import socket
import thread
import httplib
import sys, re


def inicio():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('',8000))
        server.listen(5)
        print "PRONTO PARA AS CONEXOES..."

    except Exception, error:
        print "\nNAO FOI POSSIVEL SE CONECTAR...\n"
        #server.close()
        sys.exit(3)
    
    while True:
        try:
            conexao, end_cliente = server.accept()
            #print "Servidor conectado com o cliente", end_cliente

            msg_conection = conexao.recv(4096)
            #print "mensagem recebida: ", msg_conection
            #msg_conection = msg_conection[:-1]
            #if not msg_conection: break
            thread.start_new_thread(solicitacao_cliente, (conexao, end_cliente, msg_conection))

        except KeyboardInterrupt:
            server.close()
            print "\n Servidor finalizado..."
            sys.exit(1)

def solicitacao_cliente(conexao, end_cliente, msg_conection):
    try:
        linha = msg_conection.split('\n')[0] #linha recebe parametro ate achar espaco
        url = linha.split(' ')[1]            #  url vai pegar o primeiro parametro passado
        http_posicao = url.find('://')       # procura o "http"
        #if (http_posicao == -1):
         #   aux = url
        #else:
        aux = url[(http_posicao+3):]         # armazena a url pretendida pelo cliente
        port_posicao = aux.find(':')        
        url_final = aux.find('/')            # encontra o final da url

        if (url_final == -1):
            url_final = len(aux)
        pag_web = ""
        porta = -1

        if (port_posicao == -1 or url_final < port_posicao):
            porta = 80
            pag_web = aux[:url_final]        # site requisitado pelo cliente

        servidor_Proxy(aux, pag_web, porta, conexao, end_cliente, msg_conection)
    except Exception, erro:
        pass

def servidor_Proxy(aux, pag_web, porta, conexao, end_cliente, msg_conection):
    ip_host = socket.gethostbyname(pag_web)
    conexao_site = httplib.HTTPConnection(pag_web)
    conexao_site.request("GET", "/")
    requisicao1 = conexao_site.getresponse()

    print "\nHost: ", pag_web
    print "\nHost_IP: ", ip_host
    print "\nStatus: ", requisicao1.status, requisicao1.reason

    conexao_site.close()
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((pag_web, porta))
        server.send(msg_conection)
        while True:
            msg = server.recv(4096)
            if(len(msg) > 0):
                conexao.send(msg)
                conexao_server(msg)
            else:
                break
        server.close()
        conexao.close()
    except socket.error, (value, message):
        server.close()
        conexao.close()
        sys.exit(2)

inicio()
