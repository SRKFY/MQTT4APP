"""Script responsavel pelo protocolo mqtt e seu envio para o banco de dados."""
from paho.mqtt.client import Client


class Mqtt4App(Client):
    """Classe para acesso ao Broker e envio de dados ao Back4App.

    Como usar?

    # Instancia
    mqtt4app = Mqtt4App(
                        broker_address, port, qos,
                        topic_path, client_id, back_app_id,
                        back_rest_id, back_classlocation
                        )

    # Efetuar a conexao
    mqtt4app.connectToBroker(auth)

    # Mostrar dados inseridos
    print(mqtt4app)
    """

    def __init__(self, broker_address=None, port=1883,
                 qos=0, topic_path=None, client_id=None,
                 back_app_id=None, back_rest_id=None,
                 back_classlocation=None
                 ):
        """Obter dados para conexao, monitoramento e envio de dados.

        broker_address: Endereco do servidor Broker
        qos: Nivel de qualidade de servico
        port: Porta usada pelo Broker
        topic_path: Caminho do Topico
        client_id: identificacao da conexao para melhor organizacao
        back_app_id: App ID fornecido pelo Back4App
        back_rest_id: Rest ID fornecido pelo Back4App
        back_classlocation: Localizacao da tabela criada no Back4App
        """
        path_and_id = topic_path and client_id
        port_and_qos = port.isnumeric() and qos.isnumeric()
        back_requirements = back_app_id and back_rest_id and back_classlocation
        assert broker_address, 'Endereco do servidor Broker nao informado.'
        assert isinstance(broker_address, str), 'O broker_address deve ser String.' #NOQA
        assert path_and_id, 'O caminho do topic e o ID devem ser informados.'
        assert port_and_qos, 'A porta e Qos devem ser inteiros.'
        assert back_requirements, 'Os parametros Back4App devem ser inseridos.'
        super().__init__()
        self.client_id = client_id
        self.broker_address = broker_address
        self.port = int(port)
        self.qos = int(qos)
        self.auth = auth
        self.topic_path = topic_path if topic_path.endswith('/') else topic_path + '/' #NOQA
        self.on_connect = self.__subscribeTopics__
        self.on_message = self.__getData__

    def __str__(self):
        """Mostrar informacoes inseridas."""
        return """
        Broker: {}:{}
        Topic Path: {}{}
        Qos: {}
        """.format(self.broker_address, self.port, self.topic_path,
                   self.client_id, self.qos
                   )

    def connectToBroker(self, auth=None):
        """Conectar no servidor Broker.

        Sera verificado se o parametro 'auth' existe para realizar a
        autenticacao, mas caso nao exista, sera desconsiderado na conexao.

        auth: Dicionario de autenticacao
            Estrutura:
            {
                'username': username,
                'password': password
            }

        Tipo de retorno: None
        """
        if auth:
            user_passwd = auth.get('username') and auth.get('password')
            assert user_passwd, 'Usuario ou senha nao informados.'
            self.username_pw_set(**auth)

        self.connect(host=self.broker_address, port=self.port)
        self.loop_forever()

    def __subscribeTopics__(self, client, *args):
        """Realizar a inscricao em topicos.

        client: Instancia Client

        Tipo de retorno: None
        """
        print("Conectado com sucesso.")
        fullTopic = "{}{}/#".format(self.topic_path, self.client_id)
        print(fullTopic)
        client.subscribe(fullTopic, self.qos)

    def __getData__(self, client, userdata, msg=[]):
        """Obter dados referentes aos topicos e enviar para o banco de dados.

        client: Instancia de client
        msg: Dados referentes aos topicos

        Tipo de retorno: None
        """
        print(str(msg.topic))
        print(int(msg.payload))


def main(auth=None, *args):
    """Iniciar monitoramento e envio de dados.

    Tipo de retorno: None
    """
    mqtt4app = Mqtt4App(*args)
    mqtt4app.connectToBroker(auth)
    # print(mqtt4app)
    #


if __name__ == "__main__":
    import sys
    howto = """
    Como usar?

    \tpython [username:password] broker_address port qos topic_path client_id back_app_id back_rest_id back_classlocation
    """ # NOQA
    args = sys.argv[1:]
    auth = None
    args_vrf = len(args) is 8 or len(args) is 9
    assert args_vrf, "Existem parametros em falta.\n{}".format(howto)

    if ':' in args[0]:
        auth = dict(zip(['username', 'password'], args[0].split(':')))
        del args[0]
    main(auth, *args)
